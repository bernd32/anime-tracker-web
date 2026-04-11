from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.repositories.anime import AnimeRepository
from app.repositories.year_scaffold import YearScaffoldRepository
from app.schemas.years import DeleteYearResponse, YearListItem, YearListResponse, YearScaffoldResponse


class YearService:
    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def list_years(self) -> YearListResponse:
        with self.session_factory() as session:
            anime_repo = AnimeRepository(session)
            scaffold_repo = YearScaffoldRepository(session)
            scaffold_years = set(scaffold_repo.list_years())
            counts = anime_repo.list_year_counts()
            item_map: dict[int, YearListItem] = {}
            for year, total, completed in counts:
                if year < 2010:
                    continue
                item_map[year] = YearListItem(
                    year=year,
                    has_entries=total > 0,
                    has_scaffold=year in scaffold_years,
                    counts={"total": total, "completed": completed},
                )
            for year in scaffold_years:
                if year not in item_map:
                    item_map[year] = YearListItem(
                        year=year,
                        has_entries=False,
                        has_scaffold=True,
                        counts={"total": 0, "completed": 0},
                    )
            return YearListResponse(items=sorted(item_map.values(), key=lambda item: item.year, reverse=True))

    def create_scaffold(self, year: int) -> YearScaffoldResponse:
        with self.session_factory() as session:
            repo = YearScaffoldRepository(session)
            created = False
            if repo.get(year) is None:
                repo.create(year)
                session.commit()
                created = True
            return YearScaffoldResponse(
                year=year,
                created=created,
                seasons=["winter", "spring", "summer", "fall", "other"],
            )

    def delete_year(self, year: int) -> DeleteYearResponse:
        with self.session_factory() as session:
            anime_repo = AnimeRepository(session)
            scaffold_repo = YearScaffoldRepository(session)
            deleted_anime_count = anime_repo.delete_year(year)
            deleted_scaffold = scaffold_repo.delete(year)
            session.commit()
            return DeleteYearResponse(
                year=year,
                deleted_anime_count=deleted_anime_count,
                deleted_scaffold=deleted_scaffold,
            )
