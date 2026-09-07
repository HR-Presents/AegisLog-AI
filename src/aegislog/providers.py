from __future__ import annotations

import http.client
import ipaddress
import json
import os
import socket
import ssl
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .sanitize import redact_sensitive


@dataclass(frozen=True)
class AIResponse:
    provider: str
    model: str
    text: str


class ProviderError(RuntimeError):
    pass


MAX_RESPONSE_BYTES = 2_000_000
REMOTE_AI_OPT_IN_ENV = "AEGISLOG_ALLOW_REMOTE_AI"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _remote_ai_enabled() -> bool:
    return os.environ.get(REMOTE_AI_OPT_IN_ENV, "").strip().lower() in _TRUE_VALUES


def _require_remote_ai_opt_in() -> None:
    if not _remote_ai_enabled():
        raise ProviderError(
            "Remote AI is disabled by default to keep analysis local. "
            f"Set {REMOTE_AI_OPT_IN_ENV}=1 only if you explicitly consent to sending redacted analysis context "
            "to a remote provider."
        )


def _resolved_addresses(hostname: str, port: int) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    try:
        return {
            ipaddress.ip_address(item[4][0])
            for item in socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError) as exc:
        raise ProviderError("provider hostname could not be resolved") from exc


def _validated_endpoint(
    url: str, allow_local: bool
) -> tuple[urllib.parse.ParseResult, set[ipaddress.IPv4Address | ipaddress.IPv6Address]]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ProviderError("provider URL must be HTTP(S) without embedded credentials")
    if parsed.scheme != "https" and not allow_local:
        raise ProviderError("remote AI providers require HTTPS")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    addresses = _resolved_addresses(parsed.hostname, port)
    if not addresses:
        raise ProviderError("provider hostname resolved without usable addresses")
    unsafe = any(
        ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved
        for ip in addresses
    )
    if unsafe and not allow_local:
        raise ProviderError(
            "remote provider URL resolves to a local/private address; local HTTP is only supported for local providers"
        )
    if allow_local and parsed.scheme == "http" and not all(ip.is_loopback for ip in addresses):
        raise ProviderError("plain HTTP is restricted to loopback provider addresses")
    return parsed, addresses


def _validated_proxy_endpoint(
    url: str,
) -> tuple[urllib.parse.ParseResult, set[ipaddress.IPv4Address | ipaddress.IPv6Address]]:
    parsed = urllib.parse.urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise ProviderError(
            "explicit AI proxy must be a credential-free HTTPS origin without path, query, or fragment"
        )
    port = parsed.port or 443
    addresses = _resolved_addresses(parsed.hostname, port)
    if not addresses:
        raise ProviderError("proxy hostname resolved without usable addresses")
    return parsed, addresses


def _validate_url(url: str, allow_local: bool) -> str:
    """Backward-compatible validator used by existing callers and tests."""
    _validated_endpoint(url, allow_local)
    return url.rstrip("/")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Compatibility helper: redirects remain explicitly unsupported."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError("provider redirects are disabled")


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host: str, port: int, address: str, timeout: int):
        super().__init__(host, port, timeout=timeout)
        self._address = address

    def connect(self) -> None:
        self.sock = socket.create_connection((self._address, self.port), self.timeout)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host: str, port: int, address: str, timeout: int):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._address = address

    def connect(self) -> None:
        raw = socket.create_connection((self._address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(raw, server_hostname=self.host)


class _PinnedHTTPSProxyConnection(http.client.HTTPSConnection):
    def __init__(
        self,
        provider_host: str,
        provider_port: int,
        provider_address: str,
        proxy_host: str,
        proxy_port: int,
        proxy_address: str,
        timeout: int,
    ):
        super().__init__(provider_host, provider_port, timeout=timeout, context=ssl.create_default_context())
        self._provider_address = provider_address
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._proxy_address = proxy_address

    def connect(self) -> None:
        raw = socket.create_connection((self._proxy_address, self._proxy_port), self.timeout)
        proxy_tls = self._context.wrap_socket(raw, server_hostname=self._proxy_host)
        target = f"{self._provider_address}:{self.port}"
        host_header = f"{self.host}:{self.port}"
        request = f"CONNECT {target} HTTP/1.1\r\nHost: {host_header}\r\nConnection: keep-alive\r\n\r\n"
        proxy_tls.sendall(request.encode("ascii"))
        response = http.client.HTTPResponse(proxy_tls)
        response.begin()
        if response.status != 200:
            response.close()
            proxy_tls.close()
            raise ProviderError(f"HTTPS proxy CONNECT returned HTTP {response.status}")
        response.close()
        self.sock = self._context.wrap_socket(proxy_tls, server_hostname=self.host)


def _read_json_response(response: http.client.HTTPResponse) -> dict:
    if 300 <= response.status < 400:
        raise ProviderError("provider redirects are disabled")
    if not 200 <= response.status < 300:
        raise ProviderError(f"provider returned HTTP {response.status}")
    declared = response.getheader("Content-Length")
    if declared:
        try:
            declared_size = int(declared)
        except ValueError as exc:
            raise ProviderError("provider returned an invalid Content-Length") from exc
        if declared_size > MAX_RESPONSE_BYTES:
            raise ProviderError("provider response exceeds the 2 MB safety limit")
    body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ProviderError("provider response exceeds the 2 MB safety limit")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderError("provider returned malformed JSON") from exc
    if not isinstance(data, dict):
        raise ProviderError("provider returned a non-object JSON response")
    return data


def _post_json(
    url: str,
    payload: dict,
    headers: dict[str, str],
    timeout: int = 45,
    allow_local: bool = False,
    proxy_url: str | None = None,
) -> dict:
    # Enforce local-first behavior at the shared transport boundary so alternate or future
    # remote provider adapters cannot bypass consent by calling the transport directly.
    # This check occurs before DNS resolution or socket creation, so disabled remote AI has
    # no provider-network side effect at all.
    if not allow_local:
        _require_remote_ai_opt_in()

    parsed, addresses = _validated_endpoint(url, allow_local)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = urllib.parse.urlunparse(("", "", parsed.path or "/", parsed.params, parsed.query, ""))
    request_headers = {"Content-Type": "application/json", "Host": parsed.netloc, **headers}
    body = json.dumps(payload).encode("utf-8")

    configured_proxy = proxy_url or os.environ.get("AEGISLOG_HTTPS_PROXY")
    proxy: tuple[
        urllib.parse.ParseResult,
        set[ipaddress.IPv4Address | ipaddress.IPv6Address],
    ] | None = None
    if configured_proxy:
        if parsed.scheme != "https" or allow_local:
            raise ProviderError("explicit AI proxy is supported only for remote HTTPS providers")
        proxy = _validated_proxy_endpoint(configured_proxy)

    # Resolve and validate once, then attempt only the addresses from those exact validated sets.
    # Destination CONNECT targets are provider IPs, not hostnames, so an explicit proxy cannot
    # perform a second destination DNS resolution that bypasses the provider-address validation.
    connection_errors: list[str] = []
    for address in sorted((str(item) for item in addresses), key=str):
        proxy_addresses = [None]
        if proxy is not None:
            proxy_addresses = sorted((str(item) for item in proxy[1]), key=str)
        for proxy_address in proxy_addresses:
            if proxy is None:
                connection_cls = _PinnedHTTPSConnection if parsed.scheme == "https" else _PinnedHTTPConnection
                connection = connection_cls(parsed.hostname, port, address, timeout)
                attempt = address
            else:
                proxy_parsed = proxy[0]
                proxy_port = proxy_parsed.port or 443
                connection = _PinnedHTTPSProxyConnection(
                    parsed.hostname,
                    port,
                    address,
                    proxy_parsed.hostname,
                    proxy_port,
                    proxy_address,
                    timeout,
                )
                attempt = f"proxy {proxy_address} -> provider {address}"
            try:
                connection.request("POST", path, body=body, headers=request_headers)
                response = connection.getresponse()
                return _read_json_response(response)
            except ProviderError:
                raise
            except (OSError, http.client.HTTPException, TimeoutError, ssl.SSLError) as exc:
                connection_errors.append(f"{attempt}: {exc}")
            finally:
                connection.close()

    details = "; ".join(connection_errors) if connection_errors else "no validated address was attempted"
    raise ProviderError(f"provider connection failed for all validated addresses: {details}")


def openai_compatible(prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    # Keep the adapter-level guard as defense in depth; the shared transport independently
    # enforces the same consent requirement for every remote caller.
    _require_remote_ai_opt_in()
    api_key = os.environ.get("AEGISLOG_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("No API key found. Set AEGISLOG_API_KEY or OPENAI_API_KEY.")
    root = (base_url or os.environ.get("AEGISLOG_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    safe_prompt = redact_sensitive(prompt)
    data = _post_json(
        f"{root}/chat/completions",
        {"model": model, "messages": [{"role": "user", "content": safe_prompt}], "temperature": 0.1},
        {"Authorization": f"Bearer {api_key}"},
    )
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("Provider returned an unexpected response shape") from exc
    if not isinstance(text, str):
        raise ProviderError("Provider returned non-text message content")
    return AIResponse("openai-compatible", model, text)


def ollama(prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    root = (base_url or os.environ.get("AEGISLOG_OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
    data = _post_json(
        f"{root}/api/generate",
        {"model": model, "prompt": redact_sensitive(prompt), "stream": False},
        {},
        allow_local=True,
    )
    text = data.get("response")
    if not isinstance(text, str):
        raise ProviderError("Ollama returned an unexpected response shape")
    return AIResponse("ollama", model, text)


def run_provider(provider: str, prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    name = provider.strip().lower()
    if name in {"openai", "openai-compatible"}:
        return openai_compatible(prompt, model or "gpt-4.1-mini", base_url)
    if name == "ollama":
        return ollama(prompt, model or "llama3.2", base_url)
    raise ProviderError(f"Unsupported AI provider: {provider}")