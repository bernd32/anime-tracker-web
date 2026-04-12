from __future__ import annotations

import logging
from collections import OrderedDict
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

import httpx
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.db.models import Anime
from app.repositories.anime import AnimeRepository
from app.repositories.shikimori_cache import ShikimoriCacheRepository
from app.schemas.shikimori import ShikimoriCacheMeta, ShikimoriInfo, ShikimoriInfoResponse
from app.utils.normalization import normalize_name

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MemoryCacheItem:
    payload: dict[str, Any]
    expires_at: datetime


class LruCache:
    def __init__(self, capacity: int = 128) -> None:
        self.capacity = capacity
        self._items: OrderedDict[str, MemoryCacheItem] = OrderedDict()

    def get(self, key: str) -> MemoryCacheItem | None:
        return self._get(key, include_expired=False)

    def get_stale(self, key: str) -> MemoryCacheItem | None:
        return self._get(key, include_expired=True)

    def _get(self, key: str, *, include_expired: bool) -> MemoryCacheItem | None:
        item = self._items.get(key)
        if item is None:
            return None
        self._items.move_to_end(key)
        expires_at = ensure_utc(item.expires_at)
        if expires_at <= datetime.now(UTC) and not include_expired:
            del self._items[key]
            return None
        if expires_at is not item.expires_at:
            item = MemoryCacheItem(payload=item.payload, expires_at=expires_at)
            self._items[key] = item
        return item

    def put(self, key: str, value: MemoryCacheItem) -> None:
        self._items[key] = MemoryCacheItem(payload=value.payload, expires_at=ensure_utc(value.expires_at))
        self._items.move_to_end(key)
        while len(self._items) > self.capacity:
            self._items.popitem(last=False)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class ShikimoriService:
    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        settings: Settings,
        client: httpx.Client | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings
        self.client = client or self._build_client(settings)
        self.cache = LruCache(capacity=128)

    @staticmethod
    def _build_client(settings: Settings) -> httpx.Client:
        kwargs: dict[str, Any] = {
            "timeout": settings.shikimori_request_timeout_seconds,
        }
        if settings.shikimori_proxy_url:
            kwargs["proxy"] = settings.shikimori_proxy_url
        return httpx.Client(**kwargs)

    def get_info(self, anime_id: int, *, force_refresh: bool = False) -> ShikimoriInfoResponse:
        with self.session_factory() as session:
            anime = AnimeRepository(session).get(anime_id)
            if anime is None:
                raise NotFoundError(message="Anime not found.", details={"anime_id": anime_id})
            search_key = normalize_name(anime.name)
            cache_repo = ShikimoriCacheRepository(session)
            if not force_refresh:
                in_memory = self.cache.get(search_key)
                if in_memory is not None:
                    return self._build_response(anime.id, search_key, in_memory.payload, "memory", in_memory.expires_at)
                db_cache = cache_repo.get_valid(search_key)
                if db_cache is not None:
                    expires_at = ensure_utc(db_cache.expires_at)
                    self.cache.put(search_key, MemoryCacheItem(payload=db_cache.payload, expires_at=expires_at))
                    return self._build_response(anime.id, search_key, db_cache.payload, "database", expires_at)
            try:
                payload, expires_at = self._fetch_from_network(anime)
            except ExternalServiceError:
                stale_memory = self.cache.get_stale(search_key)
                if stale_memory is not None:
                    return self._build_response(
                        anime.id,
                        search_key,
                        stale_memory.payload,
                        "memory",
                        stale_memory.expires_at,
                        stale=True,
                    )
                stale_db = cache_repo.get_latest(search_key)
                if stale_db is not None:
                    expires_at = ensure_utc(stale_db.expires_at)
                    self.cache.put(search_key, MemoryCacheItem(payload=stale_db.payload, expires_at=expires_at))
                    return self._build_response(
                        anime.id,
                        search_key,
                        stale_db.payload,
                        "database",
                        expires_at,
                        stale=True,
                    )
                raise

            cache_entry = cache_repo.upsert(search_key=search_key, payload=payload, expires_at=expires_at)
            session.commit()
            cache_expires_at = ensure_utc(cache_entry.expires_at)
            self.cache.put(search_key, MemoryCacheItem(payload=cache_entry.payload, expires_at=cache_expires_at))
            return self._build_response(anime.id, search_key, cache_entry.payload, "network", cache_expires_at)

    def _fetch_from_network(self, anime: Anime) -> tuple[dict[str, Any], datetime]:
        escaped = anime.name.replace('"', '\\"')
        query = (
            '{ animes(search: "%s", limit: 1, kind: "!special") {'
            ' russian japanese score episodes airedOn { date }'
            ' fansubbers studios { name } genres { name } description }}'
        ) % escaped
        try:
            response = self.client.post(
                str(self.settings.shikimori_graphql_url),
                json={"query": query},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": self.settings.shikimori_user_agent,
                    "Referer": "https://shikimori.one/",
                },
            )
            response.raise_for_status()
            data = response.json()
            first = ((data.get("data") or {}).get("animes") or [{}])[0]
            payload = {
                "russian": first.get("russian"),
                "japanese": first.get("japanese"),
                "score": first.get("score"),
                "episodes": first.get("episodes"),
                "aired_on": ((first.get("airedOn") or {}).get("date")),
                "fansubbers": [str(item) for item in (first.get("fansubbers") or [])],
                "studios": [item.get("name") for item in (first.get("studios") or []) if item and item.get("name")],
                "genres": [item.get("name") for item in (first.get("genres") or []) if item and item.get("name")],
                "description": first.get("description"),
            }
            expires_at = datetime.now(UTC) + timedelta(seconds=self.settings.shikimori_cache_ttl_seconds)
            return payload, expires_at
        except httpx.HTTPError as exc:
            logger.exception("Shikimori request failed", exc_info=exc)
            raise ExternalServiceError(message="Failed to fetch data from Shikimori.") from exc

    def _build_response(
        self,
        anime_id: int,
        search_key: str,
        payload: dict[str, Any],
        source: str,
        expires_at: datetime,
        *,
        stale: bool = False,
    ) -> ShikimoriInfoResponse:
        return ShikimoriInfoResponse(
            anime_id=anime_id,
            search_key=search_key,
            cache=ShikimoriCacheMeta(source=source, expires_at=ensure_utc(expires_at), stale=stale),
            result=ShikimoriInfo.model_validate(payload),
        )
