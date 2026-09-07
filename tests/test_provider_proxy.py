import io
import ipaddress
from unittest.mock import MagicMock, patch

import pytest

from aegislog.providers import (
    ProviderError,
    _PinnedHTTPSProxyConnection,
    _post_json,
    _validated_proxy_endpoint,
)


def test_proxy_requires_credential_free_https_origin():
    with pytest.raises(ProviderError, match="credential-free HTTPS origin"):
        _validated_proxy_endpoint("http://proxy.example:8080")
    with pytest.raises(ProviderError, match="credential-free HTTPS origin"):
        _validated_proxy_endpoint("https://user:pass@proxy.example:8443")
    with pytest.raises(ProviderError, match="credential-free HTTPS origin"):
        _validated_proxy_endpoint("https://proxy.example:8443/path")


def test_post_json_proxy_uses_only_prevalidated_provider_and_proxy_addresses():
    provider = __import__("urllib.parse").parse.urlparse("https://provider.example/v1")
    proxy = __import__("urllib.parse").parse.urlparse("https://proxy.example:8443")
    response = MagicMock()
    response.status = 200
    response.getheader.return_value = None
    response.read.return_value = b'{"ok": true}'
    connection = MagicMock()
    connection.getresponse.return_value = response

    with patch(
        "aegislog.providers._validated_endpoint",
        return_value=(provider, {ipaddress.ip_address("93.184.216.34")}),
    ), patch(
        "aegislog.providers._validated_proxy_endpoint",
        return_value=(proxy, {ipaddress.ip_address("10.10.0.25")}),
    ), patch(
        "aegislog.providers._PinnedHTTPSProxyConnection", return_value=connection
    ) as connection_cls:
        result = _post_json(
            "https://provider.example/v1",
            {},
            {},
            proxy_url="https://proxy.example:8443",
        )

    assert result == {"ok": True}
    connection_cls.assert_called_once_with(
        "provider.example",
        443,
        "93.184.216.34",
        "proxy.example",
        8443,
        "10.10.0.25",
        45,
    )


def test_proxy_transport_fails_over_across_prevalidated_proxy_addresses():
    provider = __import__("urllib.parse").parse.urlparse("https://provider.example/v1")
    proxy = __import__("urllib.parse").parse.urlparse("https://proxy.example")
    first = MagicMock()
    first.request.side_effect = OSError("synthetic proxy connect failure")
    response = MagicMock()
    response.status = 200
    response.getheader.return_value = None
    response.read.return_value = b'{"ok": true}'
    second = MagicMock()
    second.getresponse.return_value = response

    with patch(
        "aegislog.providers._validated_endpoint",
        return_value=(provider, {ipaddress.ip_address("93.184.216.34")}),
    ), patch(
        "aegislog.providers._validated_proxy_endpoint",
        return_value=(
            proxy,
            {
                ipaddress.ip_address("10.10.0.25"),
                ipaddress.ip_address("10.10.0.26"),
            },
        ),
    ), patch(
        "aegislog.providers._PinnedHTTPSProxyConnection", side_effect=[first, second]
    ) as connection_cls:
        assert _post_json(
            "https://provider.example/v1",
            {},
            {},
            proxy_url="https://proxy.example",
        ) == {"ok": True}

    assert connection_cls.call_count == 2
    attempted_proxy_addresses = [call.args[5] for call in connection_cls.call_args_list]
    assert attempted_proxy_addresses == ["10.10.0.25", "10.10.0.26"]


def test_local_provider_refuses_explicit_proxy(monkeypatch):
    monkeypatch.setenv("AEGISLOG_HTTPS_PROXY", "https://proxy.example")
    parsed = __import__("urllib.parse").parse.urlparse("http://127.0.0.1:11434/api/generate")
    with patch(
        "aegislog.providers._validated_endpoint",
        return_value=(parsed, {ipaddress.ip_address("127.0.0.1")}),
    ):
        with pytest.raises(ProviderError, match="only for remote HTTPS providers"):
            _post_json(
                "http://127.0.0.1:11434/api/generate",
                {},
                {},
                allow_local=True,
            )


def test_proxy_connect_targets_provider_ip_but_preserves_provider_host_for_tls():
    context = MagicMock()
    raw_socket = MagicMock()
    proxy_tls = MagicMock()
    provider_tls = MagicMock()
    context.wrap_socket.side_effect = [proxy_tls, provider_tls]
    tunnel_response = MagicMock()
    tunnel_response.status = 200

    connection = _PinnedHTTPSProxyConnection(
        "provider.example",
        443,
        "93.184.216.34",
        "proxy.example",
        8443,
        "10.10.0.25",
        45,
    )
    connection._context = context

    with patch("aegislog.providers.socket.create_connection", return_value=raw_socket), patch(
        "aegislog.providers.http.client.HTTPResponse", return_value=tunnel_response
    ):
        connection.connect()

    proxy_tls.sendall.assert_called_once()
    request = proxy_tls.sendall.call_args.args[0].decode("ascii")
    assert request.startswith("CONNECT 93.184.216.34:443 HTTP/1.1\r\n")
    assert "Host: provider.example:443\r\n" in request
    assert context.wrap_socket.call_args_list[0].kwargs["server_hostname"] == "proxy.example"
    assert context.wrap_socket.call_args_list[1].kwargs["server_hostname"] == "provider.example"
    assert connection.sock is provider_tls
