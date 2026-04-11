from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()

    import app.db.session as db_session_module

    db_session_module._engine = None
    db_session_module._SessionLocal = None

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    db_session_module._engine = None
    db_session_module._SessionLocal = None
    get_settings.cache_clear()
