"""
Station API Endpoints
=====================
Handles station search (autocomplete) and station details.

Endpoints:
  GET /api/stations/search?q=bang  → Search stations by name/code/city
  GET /api/stations/{code}         → Get full details for a station

Search flow:
  1. User types "Bang" in the search box
  2. Frontend calls GET /api/stations/search?q=Bang (debounced, 300ms)
  3. This endpoint checks Redis cache → if HIT, return instantly
  4. If MISS → query PostgreSQL with ILIKE matching
  5. Cache the result in Redis for 24 hours
  6. Return top matches

Why Redis caching matters here:
  - Station data barely changes (maybe once a year)
  - The same searches ("del", "mum", "bang") happen thousands of times
  - Redis serves in ~1ms vs PostgreSQL's ~30-50ms
  - That 30ms difference makes autocomplete feel snappy
"""

import time
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.postgres import get_db, async_session_factory
from app.database.redis import (
    cache_get, cache_set, station_search_key,
)
from app.models.station import Station
from app.schemas.station import StationResponse, StationSearchResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# ── In-Memory Station Cache ───────────────────────────────
# Stations dataset is ~127 items. Caching all stations in memory
# avoids a 3-second network round-trip to remote Supabase instances
# on every keystroke, reducing response times to < 1ms.
_all_stations_cache: list[StationResponse] = []
_stations_by_code: dict[str, StationResponse] = {}
_cache_timestamp: float = 0.0
CACHE_LIFETIME_SECONDS = 3600.0  # 1 hour

CITY_ALIASES = {
    "bang": "bengaluru",
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "calcutta": "kolkata",
    "madras": "chennai",
    "trivandrum": "thiruvananthapuram",
    "cochin": "kochi",
    "banaras": "varanasi",
    "benares": "varanasi",
    "allahabad": "prayagraj",
    "baroda": "vadodara",
    "poona": "pune",
    "calicut": "kozhikode",
    "delhi": "new delhi",
}

CATEGORY_RANKS = {"A1": 0, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


async def get_or_load_all_stations(db: Optional[AsyncSession] = None) -> list[StationResponse]:
    """
    Returns all stations from the in-memory cache if fresh,
    otherwise loads them from PostgreSQL in a single quick query.
    """
    global _all_stations_cache, _stations_by_code, _cache_timestamp

    now = time.time()
    if _all_stations_cache and (now - _cache_timestamp < CACHE_LIFETIME_SECONDS):
        return _all_stations_cache

    # Load from DB
    if db is not None:
        stmt = select(Station)
        res = await db.execute(stmt)
        stations = res.scalars().all()
    else:
        async with async_session_factory() as session:
            stmt = select(Station)
            res = await session.execute(stmt)
            stations = res.scalars().all()

    loaded = [StationResponse.model_validate(s) for s in stations]
    _all_stations_cache = loaded
    _stations_by_code = {s.code.upper(): s for s in loaded}
    _cache_timestamp = now
    return _all_stations_cache


@router.get("/search", response_model=StationSearchResponse)
async def search_stations(
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search stations by name, code, or city with sub-millisecond response.
    """
    query_clean = q.strip()
    query_lower = query_clean.lower()
    query_upper = query_clean.upper()

    # 1. Check Redis cache first if available
    cache_key = station_search_key(query_lower)
    cached = await cache_get(cache_key)
    if cached is not None:
        return StationSearchResponse(**cached)

    # 2. Get stations from ultra-fast in-memory cache
    all_stations = await get_or_load_all_stations(db)

    # Build search terms (including city aliases like bangalore -> bengaluru)
    alias_targets = [query_lower]
    for alias_key, target in CITY_ALIASES.items():
        if alias_key in query_lower:
            alias_targets.append(target)

    scored_stations = []

    for s in all_stations:
        code = s.code.upper()
        name_lower = s.name.lower()
        city_lower = s.city.lower()
        state_lower = s.state.lower()

        score = None
        if code == query_upper:
            score = 0  # Exact code match (e.g. SBC, NDLS)
        elif code.startswith(query_upper):
            score = 1  # Code starts with query (e.g. SB...)
        elif query_upper in code:
            score = 2  # Code contains query
        elif any(target in city_lower for target in alias_targets) or city_lower.startswith(query_lower):
            score = 3  # City match or alias match
        elif query_lower in name_lower:
            score = 4  # Name contains query
        elif any(target in state_lower for target in alias_targets):
            score = 5  # State contains query

        if score is not None:
            # Ranking tuple:
            # 1. score (lower = better)
            # 2. is_junction (junctions first)
            # 3. station category rank (A1 > A > B > C)
            # 4. name alphabetical
            cat_rank = CATEGORY_RANKS.get(s.station_category, 9)
            scored_stations.append((
                score,
                0 if s.is_junction else 1,
                cat_rank,
                s.name,
                s,
            ))

    scored_stations.sort(key=lambda item: (item[0], item[1], item[2], item[3]))
    top_matches = [item[4] for item in scored_stations[:limit]]

    response = StationSearchResponse(
        query=q,
        count=len(top_matches),
        stations=top_matches,
    )

    # 3. Cache in Redis for future hits
    await cache_set(cache_key, response.model_dump(), ttl=settings.STATION_CACHE_TTL)

    return response


@router.get("/{code}", response_model=StationResponse)
async def get_station(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full details for a specific station by its code in < 1ms.
    """
    code_upper = code.strip().upper()

    # Fast in-memory lookup
    if _stations_by_code and code_upper in _stations_by_code:
        return _stations_by_code[code_upper]

    # Check Redis cache
    cache_key = f"station:detail:{code_upper}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return StationResponse(**cached)

    # Query DB / load in-memory cache
    all_stations = await get_or_load_all_stations(db)
    if code_upper in _stations_by_code:
        return _stations_by_code[code_upper]

    raise HTTPException(
        status_code=404,
        detail=f"Station with code '{code_upper}' not found",
    )

