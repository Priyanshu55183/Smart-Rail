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

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.database.postgres import get_db
from app.database.redis import (
    cache_get, cache_set, station_search_key,
)
from app.models.station import Station
from app.schemas.station import StationResponse, StationSearchResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/search", response_model=StationSearchResponse)
async def search_stations(
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search stations by name, code, or city.
    
    Examples:
      /api/stations/search?q=bang     → KSR Bengaluru, Bangalore Cantt, ...
      /api/stations/search?q=NDLS     → New Delhi
      /api/stations/search?q=mumbai   → Mumbai CST, Mumbai Central, ...
    """
    query_lower = q.strip().lower()

    # 1. Check Redis cache
    cache_key = station_search_key(query_lower)
    cached = await cache_get(cache_key)
    if cached is not None:
        return StationSearchResponse(**cached)

    # 2. Query PostgreSQL with fuzzy matching
    # Match against code, name, and city using ILIKE (case-insensitive LIKE)
    search_pattern = f"%{query_lower}%"
    stmt = (
        select(Station)
        .where(
            or_(
                func.lower(Station.code).contains(query_lower),
                func.lower(Station.name).contains(query_lower),
                func.lower(Station.city).contains(query_lower),
            )
        )
        # Sort: exact code match first, then junctions, then alphabetical
        .order_by(
            # Exact code match gets priority (0 sorts before 1)
            (func.lower(Station.code) != query_lower.upper()).asc(),
            Station.is_junction.desc(),  # Junctions are more important
            Station.name.asc(),
        )
        .limit(limit)
    )

    result = await db.execute(stmt)
    stations = result.scalars().all()

    # 3. Build response
    station_list = [StationResponse.model_validate(s) for s in stations]
    response = StationSearchResponse(
        query=q,
        count=len(station_list),
        stations=station_list,
    )

    # 4. Cache in Redis for 24 hours
    await cache_set(cache_key, response.model_dump(), ttl=settings.STATION_CACHE_TTL)

    return response


@router.get("/{code}", response_model=StationResponse)
async def get_station(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full details for a specific station by its code.
    
    Example: GET /api/stations/SBC → Full details for Bengaluru City
    """
    code_upper = code.strip().upper()

    # Check cache first
    cache_key = f"station:detail:{code_upper}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return StationResponse(**cached)

    # Query DB
    stmt = select(Station).where(Station.code == code_upper)
    result = await db.execute(stmt)
    station = result.scalar_one_or_none()

    if station is None:
        raise HTTPException(
            status_code=404,
            detail=f"Station with code '{code_upper}' not found"
        )

    response = StationResponse.model_validate(station)

    # Cache for 24h
    await cache_set(cache_key, response.model_dump(), ttl=settings.STATION_CACHE_TTL)

    return response
