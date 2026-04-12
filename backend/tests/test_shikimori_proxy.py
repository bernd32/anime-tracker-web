import pytest

from app.core.config import Settings
from app.services.shikimori import ShikimoriService


def test_settings_accept_https_proxy():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="sqlite+pysqlite:///./test.db",
        SHIKIMORI_HTTPS_PROXY_URL="https://proxy.example:8443",
    )
    assert settings.shikimori_proxy_url == "https://proxy.example:8443"


def test_settings_accept_socks5_proxy():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="sqlite+pysqlite:///./test.db",
        SHIKIMORI_SOCKS5_PROXY_URL="socks5://proxy.example:1080",
    )
    assert settings.shikimori_proxy_url == "socks5://proxy.example:1080"


def test_settings_reject_multiple_proxy_types():
    with pytest.raises(ValueError):
        Settings(
            _env_file=None,
            DATABASE_URL="sqlite+pysqlite:///./test.db",
            SHIKIMORI_HTTPS_PROXY_URL="https://proxy.example:8443",
            SHIKIMORI_SOCKS5_PROXY_URL="socks5://proxy.example:1080",
        )


def test_build_client_uses_proxy(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    class DummyClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("app.services.shikimori.httpx.Client", DummyClient)

    settings = Settings(
        _env_file=None,
        DATABASE_URL="sqlite+pysqlite:///./test.db",
        SHIKIMORI_SOCKS5_PROXY_URL="socks5://proxy.example:1080",
    )

    ShikimoriService._build_client(settings)

    assert captured["timeout"] == settings.shikimori_request_timeout_seconds
    assert captured["proxy"] == "socks5://proxy.example:1080"
