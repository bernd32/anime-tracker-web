from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.repositories.anime import AnimeRepository
from app.schemas.stats import StatsResponse, TypeCount


class StatsService:
    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_stats(self) -> StatsResponse:
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            total, completed = repo.totals()
            pre_total, pre_completed = repo.pre2010_totals()
            year_rows = repo.list_year_counts()
            status_counts = repo.status_counts()
            completion_percent = round((completed / total * 100.0), 2) if total else 0.0
            return StatsResponse(
                totals={
                    "total": total,
                    "completed": completed,
                    "completion_percent": completion_percent,
                },
                by_status={
                    "unwatched": status_counts.get("unwatched", 0),
                    "watching": status_counts.get("watching", 0),
                    "completed": status_counts.get("completed", 0),
                },
                by_type=[TypeCount(type=type_, count=count) for type_, count in repo.type_counts()],
                by_scope={
                    "pre2010": {"total": pre_total, "completed": pre_completed},
                    "years": [
                        {"year": year, "total": total_count, "completed": completed_count}
                        for year, total_count, completed_count in year_rows
                        if year >= 2010
                    ],
                },
            )
