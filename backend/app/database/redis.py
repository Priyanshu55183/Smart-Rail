"""
Redis Cache Connection
======================
Async Redis client for caching search results, station data, and journey queries.

Why Redis?
- Station searches: Cached for 24h (stations don't change often)
- Journey searches: Cached for 30min (availability changes)
- Train schedules: Cached for 24h

Flow:
1. API receives request → Check Redis first
2. Cache HIT → Return instantly (< 1ms)
3. Cache MISS → Query PostgreSQL → Store in Redis → Return
"""

import json
from typing import Optional, Any
from redis.asyncio import Redis, ConnectionPool

from app.config import get_settings

settings = get_settings()

# ── Connection Pool ───────────────────────────────────────
# A pool of connections to Redis, reused across requests.
_pool: Optional[ConnectionPool] = None
_redis: Optional[Redis] = None


async def init_redis() -> Redis:
    """
    Initialize Redis connection pool.
    Called once when the app starts up.
    """
    global _pool, _redis
    _pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        decode_responses=True,  # Return strings instead of bytes
    )
    _redis = Redis(connection_pool=_pool)
    # Test the connection
    await _redis.ping()
    return _redis


async def close_redis() -> None:
    """Close Redis connection pool on shutdown."""
    global _redis, _pool
    if _redis:
        await _redis.close()
    if _pool:
        await _pool.disconnect()


def get_redis() -> Redis:
    """
    FastAPI dependency to get the Redis client.
    Usage:
        @router.get("/stations")
        async def search(redis: Redis = Depends(get_redis)):
            cached = await redis_get(redis, "stations:BLR")
    """
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis


# ── Cache Helpers ─────────────────────────────────────────
# These wrap Redis commands with JSON serialization so you can
# cache Python dicts/lists directly without manual JSON handling.

async def cache_get(key: str) -> Optional[Any]:
    """
    Get a value from cache. Returns None on cache miss or Redis failure.
    Automatically deserializes JSON.
    """
    try:
        redis = get_redis()
        value = await redis.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """
    Set a value in cache with optional TTL (seconds).
    Silently skips on Redis failure.
    """
    try:
        redis = get_redis()
        ttl = ttl or settings.CACHE_TTL_SECONDS
        serialized = json.dumps(value, default=str)
        await redis.set(key, serialized, ex=ttl)
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    """Delete a specific cache key."""
    try:
        redis = get_redis()
        await redis.delete(key)
    except Exception:
        pass


async def cache_delete_pattern(pattern: str) -> None:
    """
    Delete all keys matching a pattern.
    Example: cache_delete_pattern("journey:SBC:*") 
    → Clears all cached journeys from Bangalore.
    """
    redis = get_redis()
    async for key in redis.scan_iter(match=pattern):
        await redis.delete(key)


# ── Cache Key Builders ────────────────────────────────────
# Consistent key naming prevents key collisions.

def station_search_key(query: str) -> str:
    """Key for station search results. E.g., 'station:search:bang'"""
    return f"station:search:{query.lower().strip()}"


def train_schedule_key(train_number: str) -> str:
    """Key for a train's full schedule. E.g., 'train:schedule:12345'"""
    return f"train:schedule:{train_number}"


def journey_search_key(
    source: str, dest: str, date: str,
    max_conn: int = 2
) -> str:
    """
    Key for journey search results.
    E.g., 'journey:SBC:NDLS:2026-08-25:2'
    """
    return f"journey:{source}:{dest}:{date}:{max_conn}"


def direct_trains_key(source: str, dest: str, date: str) -> str:
    """Key for direct train search. E.g., 'direct:SBC:NDLS:2026-08-25'"""
    return f"direct:{source}:{dest}:{date}"
