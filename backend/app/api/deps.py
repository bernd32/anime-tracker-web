from contextlib import contextmanager
from collections.abc import Iterator

from fastapi import Header, Request
from sqlalchemy.orm import Session

from app.core.auth import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
    OwnerSession,
    read_owner_session,
    validate_csrf,
)
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.db.session import get_session_factory
from app.services.anime import AnimeService
from app.services.import_export import ImportExportService
from app.services.preferences import PreferencesService
from app.services.shikimori import ShikimoriService
from app.services.stats import StatsService
from app.services.years import YearService


@contextmanager
def session_context() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def get_anime_service() -> AnimeService:
    return AnimeService(session_context)


def get_stats_service() -> StatsService:
    return StatsService(session_context)


def get_year_service() -> YearService:
    return YearService(session_context)


def get_import_export_service() -> ImportExportService:
    return ImportExportService(session_context)


def get_shikimori_service() -> ShikimoriService:
    return ShikimoriService(session_context, get_settings())


def get_preferences_service() -> PreferencesService:
    return PreferencesService(session_context)


def get_optional_owner_session(request: Request) -> OwnerSession | None:
    settings = get_settings()
    return read_owner_session(request.cookies.get(SESSION_COOKIE_NAME), settings)


def require_owner_session(request: Request) -> OwnerSession:
    settings = get_settings()
    session = read_owner_session(request.cookies.get(SESSION_COOKIE_NAME), settings)
    if session is None:
        raise UnauthorizedError(
            code="authentication_required",
            message="Sign in is required to modify the backlog.",
        )
    return session


def require_owner_write_access(
    request: Request,
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
) -> OwnerSession:
    session = require_owner_session(request)
    validate_csrf(session, request.cookies.get(CSRF_COOKIE_NAME), csrf_header)
    return session
