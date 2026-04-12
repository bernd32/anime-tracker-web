from datetime import UTC, datetime, timedelta

from app.services.shikimori import LruCache, MemoryCacheItem, ensure_utc


def test_ensure_utc_accepts_naive_datetime():
    naive = datetime.now() + timedelta(minutes=5)
    normalized = ensure_utc(naive)
    assert normalized.tzinfo is UTC


def test_lru_cache_handles_naive_expiry_values():
    cache = LruCache()
    cache.put("frieren", MemoryCacheItem(payload={"score": "8.9"}, expires_at=datetime.now() + timedelta(minutes=5)))

    item = cache.get("frieren")
    assert item is not None
    assert item.expires_at.tzinfo is UTC
