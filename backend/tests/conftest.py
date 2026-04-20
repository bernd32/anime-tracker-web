from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.auth import reset_login_throttle
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    yield from _build_client(tmp_path, monkeypatch, authenticate=True)


@pytest.fixture()
def anonymous_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    yield from _build_client(tmp_path, monkeypatch, authenticate=False)


def _build_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    authenticate: bool,
) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_OWNER_USERNAME", "owner")
    monkeypatch.setenv("AUTH_OWNER_PASSWORD", "test-owner-password")
    monkeypatch.setenv("AUTH_SESSION_SECRET", "test-session-secret-with-sufficient-length")
    monkeypatch.setenv("AUTH_LOGIN_MAX_FAILURES", "5")
    monkeypatch.setenv("AUTH_LOGIN_WINDOW_SECONDS", "600")
    monkeypatch.setenv("AUTH_LOGIN_LOCKOUT_SECONDS", "900")
    get_settings.cache_clear()
    reset_login_throttle()

    import app.db.session as db_session_module

    db_session_module._engine = None
    db_session_module._SessionLocal = None

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    from app.main import app

    with TestClient(app) as test_client:
        if authenticate:
            response = test_client.post(
                "/api/v1/auth/login",
                json={"username": "owner", "password": "test-owner-password"},
            )
            assert response.status_code == 200, response.text
            test_client.headers.update(
                {"X-CSRF-Token": test_client.cookies.get("anime_tracker_csrf", "")}
            )
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    db_session_module._engine = None
    db_session_module._SessionLocal = None
    get_settings.cache_clear()
    reset_login_throttle()
