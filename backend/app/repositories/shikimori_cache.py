from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ShikimoriCache


class ShikimoriCacheRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_valid(self, search_key: str) -> ShikimoriCache | None:
        now = datetime.now(UTC)
        stmt = select(ShikimoriCache).where(
            ShikimoriCache.search_key == search_key,
            ShikimoriCache.expires_at > now,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_latest(self, search_key: str) -> ShikimoriCache | None:
        stmt = select(ShikimoriCache).where(ShikimoriCache.search_key == search_key)
        return self.session.execute(stmt).scalar_one_or_none()

    def upsert(self, *, search_key: str, payload: dict, expires_at: datetime) -> ShikimoriCache:
        existing = self.session.get(ShikimoriCache, search_key)
        if existing:
            existing.payload = payload
            existing.expires_at = expires_at
            self.session.flush()
            self.session.refresh(existing)
            return existing
        cache = ShikimoriCache(search_key=search_key, payload=payload, expires_at=expires_at)
        self.session.add(cache)
        self.session.flush()
        self.session.refresh(cache)
        return cache

    def delete(self, search_key: str) -> None:
        existing = self.session.get(ShikimoriCache, search_key)
        if existing is not None:
            self.session.delete(existing)
            self.session.flush()
