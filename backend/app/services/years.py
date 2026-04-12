from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.repositories.anime import AnimeRepository
from app.schemas.years import DeleteYearResponse, YearListItem, YearListResponse


class YearService:
    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def list_years(self) -> YearListResponse:
        with self.session_factory() as session:
            anime_repo = AnimeRepository(session)
            counts = anime_repo.list_year_counts()
            items: list[YearListItem] = []
            for year, total, completed in counts:
                if year < 2010:
                    continue
                items.append(
                    YearListItem(
                    year=year,
                    has_entries=total > 0,
                    counts={"total": total, "completed": completed},
                )
                )
            return YearListResponse(items=sorted(items, key=lambda item: item.year, reverse=True))

    def delete_year(self, year: int) -> DeleteYearResponse:
        with self.session_factory() as session:
            anime_repo = AnimeRepository(session)
            deleted_anime_count = anime_repo.delete_year(year)
            session.commit()
            return DeleteYearResponse(
                year=year,
                deleted_anime_count=deleted_anime_count,
            )
