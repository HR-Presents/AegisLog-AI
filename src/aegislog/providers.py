from __future__ import annotations

import ipaddress
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class AIResponse:
    provider: str
    model: str
    text: str


class ProviderError(RuntimeError):
    pass


def _validate_url(url: str, allow_local: bool) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ProviderError("provider URL must be HTTP(S) without embedded credentials")
    try:
        addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))}
    except (OSError, ValueError) as exc:
        raise ProviderError("provider hostname could not be resolved") from exc
    unsafe = any(ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved for ip in addresses)
    if unsafe and not allow_local: raise ProviderError("remote provider URL resolves to a local/private address; use Ollama for local models")
    return url.rstrip("/")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError("provider redirects are disabled")


def _post_json(url: str, payload: dict, headers: dict[str, str], timeout: int = 45, allow_local: bool = False) -> dict:
    safe_url = _validate_url(url, allow_local)
    request = urllib.request.Request(safe_url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", **headers}, method="POST")
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except ProviderError:
        raise
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        raise ProviderError(str(exc)) from exc


def openai_compatible(prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    api_key = os.environ.get("AEGISLOG_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key: raise ProviderError("No API key found. Set AEGISLOG_API_KEY or OPENAI_API_KEY.")
    root = (base_url or os.environ.get("AEGISLOG_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    data = _post_json(f"{root}/chat/completions", {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, {"Authorization": f"Bearer {api_key}"})
    try: text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc: raise ProviderError("Provider returned an unexpected response shape") from exc
    return AIResponse("openai-compatible", model, text)


def ollama(prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    root = (base_url or os.environ.get("AEGISLOG_OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
    data = _post_json(f"{root}/api/generate", {"model": model, "prompt": prompt, "stream": False}, {}, allow_local=True)
    text = data.get("response")
    if not isinstance(text, str): raise ProviderError("Ollama returned an unexpected response shape")
    return AIResponse("ollama", model, text)


def run_provider(provider: str, prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    name = provider.strip().lower()
    if name in {"openai", "openai-compatible"}: return openai_compatible(prompt, model or "gpt-4.1-mini", base_url)
    if name == "ollama": return ollama(prompt, model or "llama3.2", base_url)
    raise ProviderError(f"Unsupported AI provider: {provider}")
