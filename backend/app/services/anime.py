from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationAppError
from app.db.models import Anime, AnimeSeason, AnimeStatus
from app.repositories.anime import AnimeRepository
from app.schemas.anime import (
    AnimeCreateRequest,
    AnimeItem,
    AnimeListMeta,
    AnimeListQuery,
    AnimeListResponse,
    AnimeResponse,
    AnimeUpdateRequest,
    RandomPickResponse,
)
from app.schemas.common import ScopeInfo
from app.utils.normalization import normalize_comment, normalize_name, normalize_season, normalize_text, scope_kind_for_year
from app.utils.urls import validate_optional_url


class AnimeService:
    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def list_anime(self, query: AnimeListQuery) -> AnimeListResponse:
        self._validate_scope(query.scope_kind, query.scope_year)
        search_normalized = normalize_name(query.search or "") if query.search else None
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            items = repo.list(
                scope_kind=query.scope_kind,
                scope_year=query.scope_year,
                season=query.season,
                search_normalized=search_normalized,
                status=query.status,
                downloaded=query.downloaded,
            )
            total = repo.count(
                scope_kind=query.scope_kind,
                scope_year=query.scope_year,
                season=query.season,
                search_normalized=search_normalized,
                status=query.status,
                downloaded=query.downloaded,
            )
            return AnimeListResponse(
                items=[self._to_schema(item) for item in items],
                meta=AnimeListMeta(
                    total=total,
                    scope=ScopeInfo(kind=query.scope_kind, year=query.scope_year if query.scope_kind == "year" else None),
                    search=query.search,
                ),
            )

    def get_anime(self, anime_id: int) -> AnimeResponse:
        with self.session_factory() as session:
            anime = AnimeRepository(session).get(anime_id)
            if anime is None:
                raise NotFoundError(message="Anime not found.", details={"anime_id": anime_id})
            return AnimeResponse(item=self._to_schema(anime))

    def create_anime(self, payload: AnimeCreateRequest) -> AnimeResponse:
        data = self._normalize_payload(payload.model_dump())
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            if repo.exists_by_identity(
                name_normalized=data["name_normalized"],
                year=data["year"],
                season=data["season"],
            ):
                raise ConflictError(
                    code="anime_conflict",
                    message="An anime with the same name, year, and season already exists.",
                    details={"name": data["name"], "year": data["year"], "season": data["season"].value},
                )
            anime = Anime(**data)
            try:
                repo.add(anime)
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ConflictError(
                    code="anime_conflict",
                    message="An anime with the same name, year, and season already exists.",
                ) from exc
            return AnimeResponse(item=self._to_schema(anime))

    def update_anime(self, anime_id: int, payload: AnimeUpdateRequest) -> AnimeResponse:
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            anime = repo.get(anime_id)
            if anime is None:
                raise NotFoundError(message="Anime not found.", details={"anime_id": anime_id})
            current = {
                "name": anime.name,
                "year": anime.year,
                "season": anime.season.value,
                "status": anime.status.value,
                "type": anime.type,
                "comment": anime.comment,
                "url": anime.url,
                "downloaded": anime.downloaded,
            }
            merged = {**current, **payload.model_dump(exclude_none=True)}
            data = self._normalize_payload(merged)
            if repo.exists_by_identity(
                name_normalized=data["name_normalized"],
                year=data["year"],
                season=data["season"],
                exclude_id=anime_id,
            ):
                raise ConflictError(
                    code="anime_conflict",
                    message="An anime with the same name, year, and season already exists.",
                )
            for key, value in data.items():
                setattr(anime, key, value)
            try:
                session.flush()
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ConflictError(
                    code="anime_conflict",
                    message="An anime with the same name, year, and season already exists.",
                ) from exc
            session.refresh(anime)
            return AnimeResponse(item=self._to_schema(anime))

    def delete_anime(self, anime_id: int) -> None:
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            anime = repo.get(anime_id)
            if anime is None:
                raise NotFoundError(message="Anime not found.", details={"anime_id": anime_id})
            repo.delete(anime)
            session.commit()

    def random_pick(self, query: AnimeListQuery) -> RandomPickResponse:
        self._validate_scope(query.scope_kind, query.scope_year)
        search_normalized = normalize_name(query.search or "") if query.search else None
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            candidates, item = repo.random_unwatched(
                scope_kind=query.scope_kind,
                scope_year=query.scope_year,
                season=query.season,
                search_normalized=search_normalized,
            )
            return RandomPickResponse(
                item=self._to_schema(item) if item else None,
                meta={
                    "candidate_count": len(candidates),
                    "scope": {"kind": query.scope_kind, "year": query.scope_year if query.scope_kind == "year" else None},
                },
            )

    def _normalize_payload(self, raw: dict[str, object]) -> dict[str, object]:
        name = normalize_text(str(raw.get("name", "")))
        if not name:
            raise ValidationAppError(message="Anime name cannot be empty.", details={"field": "name"})
        year = int(raw.get("year", 0))
        if year < 1960 or year > 2100:
            raise ValidationAppError(message="Year must be between 1960 and 2100.", details={"field": "year"})
        season = normalize_season(str(raw.get("season", "other")), year)
        status = AnimeStatus(str(raw.get("status", "unwatched")))
        type_ = normalize_text(str(raw.get("type", "")))
        comment = normalize_comment(str(raw.get("comment", "")))
        url = validate_optional_url(str(raw.get("url", "")))
        downloaded = bool(raw.get("downloaded", False))
        return {
            "name": name,
            "name_normalized": normalize_name(name),
            "year": year,
            "season": season,
            "status": status,
            "type": type_,
            "comment": comment,
            "url": url,
            "downloaded": downloaded,
        }

    def _to_schema(self, anime: Anime | None) -> AnimeItem | None:
        if anime is None:
            return None
        return AnimeItem(
            id=anime.id,
            name=anime.name,
            year=anime.year,
            season=anime.season,
            status=anime.status,
            type=anime.type,
            comment=anime.comment,
            url=anime.url,
            downloaded=anime.downloaded,
            scope=ScopeInfo(kind=scope_kind_for_year(anime.year), year=anime.year if anime.year >= 2010 else None),
            created_at=anime.created_at,
            updated_at=anime.updated_at,
        )

    def _validate_scope(self, scope_kind: str, scope_year: int | None) -> None:
        if scope_kind not in {"all", "pre2010", "year"}:
            raise ValidationAppError(message="Invalid scope_kind.", details={"field": "scope_kind"})
        if scope_kind == "year" and scope_year is None:
            raise ValidationAppError(message="scope_year is required when scope_kind='year'.", details={"field": "scope_year"})
        if scope_kind != "year" and scope_year is not None:
            raise ValidationAppError(message="scope_year is only allowed when scope_kind='year'.", details={"field": "scope_year"})
