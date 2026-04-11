from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.core.config import get_settings
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
