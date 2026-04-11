from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Integer, Select, delete, func, select
from sqlalchemy.orm import Session

from app.db.models import Anime, AnimeSeason, AnimeStatus


class AnimeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, anime: Anime) -> Anime:
        self.session.add(anime)
        self.session.flush()
        self.session.refresh(anime)
        return anime

    def get(self, anime_id: int) -> Anime | None:
        return self.session.get(Anime, anime_id)

    def delete(self, anime: Anime) -> None:
        self.session.delete(anime)
        self.session.flush()

    def exists_by_identity(self, *, name_normalized: str, year: int, season: AnimeSeason, exclude_id: int | None = None) -> bool:
        stmt = select(Anime.id).where(
            Anime.name_normalized == name_normalized,
            Anime.year == year,
            Anime.season == season,
        )
        if exclude_id is not None:
            stmt = stmt.where(Anime.id != exclude_id)
        return self.session.execute(stmt.limit(1)).scalar_one_or_none() is not None

    def list(
        self,
        *,
        scope_kind: str,
        scope_year: int | None,
        season: AnimeSeason | None,
        search_normalized: str | None,
        status: AnimeStatus | None,
        downloaded: bool | None,
    ) -> Sequence[Anime]:
        stmt: Select[tuple[Anime]] = select(Anime)
        stmt = self._apply_scope(stmt, scope_kind=scope_kind, scope_year=scope_year)
        if season is not None:
            stmt = stmt.where(Anime.season == season)
        if search_normalized:
            pattern = f"%{search_normalized}%"
            stmt = stmt.where(Anime.name_normalized.like(pattern))
        if status is not None:
            stmt = stmt.where(Anime.status == status)
        if downloaded is not None:
            stmt = stmt.where(Anime.downloaded == downloaded)
        stmt = stmt.order_by(Anime.year.desc(), Anime.season.asc(), Anime.name.asc())
        return self.session.execute(stmt).scalars().all()

    def count(
        self,
        *,
        scope_kind: str,
        scope_year: int | None,
        season: AnimeSeason | None,
        search_normalized: str | None,
        status: AnimeStatus | None,
        downloaded: bool | None,
    ) -> int:
        stmt = select(func.count()).select_from(Anime)
        stmt = self._apply_scope(stmt, scope_kind=scope_kind, scope_year=scope_year)
        if season is not None:
            stmt = stmt.where(Anime.season == season)
        if search_normalized:
            stmt = stmt.where(Anime.name_normalized.like(f"%{search_normalized}%"))
        if status is not None:
            stmt = stmt.where(Anime.status == status)
        if downloaded is not None:
            stmt = stmt.where(Anime.downloaded == downloaded)
        return int(self.session.execute(stmt).scalar_one())

    def random_unwatched(
        self,
        *,
        scope_kind: str,
        scope_year: int | None,
        season: AnimeSeason | None,
        search_normalized: str | None,
    ) -> tuple[list[Anime], Anime | None]:
        stmt = select(Anime).where(Anime.status == AnimeStatus.UNWATCHED)
        stmt = self._apply_scope(stmt, scope_kind=scope_kind, scope_year=scope_year)
        if season is not None:
            stmt = stmt.where(Anime.season == season)
        if search_normalized:
            stmt = stmt.where(Anime.name_normalized.like(f"%{search_normalized}%"))
        candidates = self.session.execute(stmt.order_by(Anime.name.asc())).scalars().all()
        if not candidates:
            return candidates, None
        pick_stmt = stmt.order_by(func.random()).limit(1)
        item = self.session.execute(pick_stmt).scalar_one()
        return candidates, item

    def delete_year(self, year: int) -> int:
        result = self.session.execute(delete(Anime).where(Anime.year == year))
        self.session.flush()
        return int(result.rowcount or 0)

    def list_year_counts(self) -> list[tuple[int, int, int]]:
        completed_case = func.sum(func.cast(Anime.status == AnimeStatus.COMPLETED, Integer))
        stmt = (
            select(Anime.year, func.count(Anime.id), completed_case)
            .group_by(Anime.year)
            .order_by(Anime.year.desc())
        )
        rows = self.session.execute(stmt).all()
        return [(int(year), int(total), int(completed or 0)) for year, total, completed in rows]

    def status_counts(self) -> dict[str, int]:
        stmt = select(Anime.status, func.count(Anime.id)).group_by(Anime.status)
        rows = self.session.execute(stmt).all()
        return {status.value if hasattr(status, 'value') else str(status): int(count) for status, count in rows}

    def type_counts(self) -> list[tuple[str, int]]:
        stmt = select(Anime.type, func.count(Anime.id)).group_by(Anime.type).order_by(func.count(Anime.id).desc(), Anime.type.asc())
        return [(type_ or "", int(count)) for type_, count in self.session.execute(stmt).all()]

    def totals(self) -> tuple[int, int]:
        total_stmt = select(func.count(Anime.id))
        completed_stmt = select(func.count(Anime.id)).where(Anime.status == AnimeStatus.COMPLETED)
        return (
            int(self.session.execute(total_stmt).scalar_one()),
            int(self.session.execute(completed_stmt).scalar_one()),
        )

    def pre2010_totals(self) -> tuple[int, int]:
        total_stmt = select(func.count(Anime.id)).where(Anime.year < 2010)
        completed_stmt = select(func.count(Anime.id)).where(Anime.year < 2010, Anime.status == AnimeStatus.COMPLETED)
        return (
            int(self.session.execute(total_stmt).scalar_one()),
            int(self.session.execute(completed_stmt).scalar_one()),
        )

    def _apply_scope(self, stmt: Select, *, scope_kind: str, scope_year: int | None) -> Select:
        if scope_kind == "pre2010":
            return stmt.where(Anime.year < 2010)
        if scope_kind == "year":
            return stmt.where(Anime.year == scope_year)
        return stmt
