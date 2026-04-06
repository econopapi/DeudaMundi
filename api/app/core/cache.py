from __future__ import annotations

import json
from typing import Any

import redis
from app.core.config import settings

CACHE_TTL_RANKINGS_SECONDS = 60 * 60 * 24
CACHE_TTL_COUNTRIES_SECONDS = 60 * 60 * 6
CACHE_TTL_GLOBE_DATA_SECONDS = 60 * 60 * 24
READ_CACHE_PREFIXES = (
    "countries:",
    "rankings:",
    "globe-data:",
)

_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def get_cache_json(key: str) -> dict[str, Any] | None:
    try:
        raw = get_redis_client().get(key)
        if not raw:
            return None
        loaded = json.loads(raw)
        return loaded if isinstance(loaded, dict) else None
    except Exception:  # noqa: BLE001
        return None


def set_cache_json(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    try:
        get_redis_client().setex(key, ttl_seconds, json.dumps(value))
    except Exception:  # noqa: BLE001
        return


def invalidate_cache_by_prefixes(prefixes: tuple[str, ...]) -> int:
    try:
        client = get_redis_client()
        keys_to_delete: set[str] = set()

        for prefix in prefixes:
            for key in client.scan_iter(match=f"{prefix}*"):
                keys_to_delete.add(str(key))

        if not keys_to_delete:
            return 0

        return int(client.delete(*keys_to_delete))
    except Exception:  # noqa: BLE001
        return 0


def invalidate_read_caches() -> int:
    return invalidate_cache_by_prefixes(READ_CACHE_PREFIXES)
