"""
Journey API Endpoints
=====================
THE MAIN AI ENDPOINT — orchestrates the intelligent journey search.

Endpoints:
  GET /api/journeys?from=SBC&to=NDLS&date=2026-08-25&max_connections=2
  GET /api/journeys/{journey_id}

What happens when a user searches:
  1. Parse and validate search parameters
  2. Check Redis cache for this exact search
  3. Call JourneyService which runs:
     a. Graph building (railway network as time-dependent graph)
     b. Direct train search (simple case)
     c. Time-dependent Dijkstra (finds multi-train paths)
     d. Connection validation (layover >= min transfer time)
     e. ML delay prediction (XGBoost predicts delays at each station)
     f. Risk estimation (Monte Carlo: P(connection_success))
     g. Journey scoring (multi-criteria: time, layover, price, reliability)
     h. Ranking and recommendation tagging (BEST, FASTEST, CHEAPEST, SAFEST)
  4. Cache results in Redis
  5. Return ranked journeys with segments and scores

This endpoint is the PRODUCT — everything else supports it.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.database.redis import cache_get, cache_set, journey_search_key
from app.schemas.journey import (
    JourneySearchRequest, JourneySearchResponse, JourneyResponse,
)
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("", response_model=JourneySearchResponse)
async def search_journeys(
    from_station: str = Query(..., alias="from", description="Source station code"),
    to_station: str = Query(..., alias="to", description="Destination station code"),
    date_str: str = Query(..., alias="date", description="Journey date YYYY-MM-DD"),
    departure_time: str = Query(None, description="Earliest departure HH:MM"),
    max_connections: int = Query(2, ge=0, le=3, description="Max train changes"),
    min_layover: int = Query(30, ge=15, alias="min_layover", description="Min layover minutes"),
    max_layover: int = Query(360, le=720, alias="max_layover", description="Max layover minutes"),
    sort_by: str = Query("best", description="best|fastest|cheapest|safest|fewest_changes"),
    db: AsyncSession = Depends(get_db),
):
    """
    🧠 INTELLIGENT JOURNEY SEARCH — The core AI endpoint.
    
    Finds and ranks the best direct and multi-train journeys.
    Uses graph algorithms, ML delay prediction, and multi-criteria scoring.
    
    Example:
      GET /api/journeys?from=SBC&to=NDLS&date=2026-08-25&max_connections=2
      
    Returns:
      - Smart recommendations (Best Overall, Fastest, Cheapest, Safest)
      - Ranked list of journeys with scores
      - Each journey has TRAIN and LAYOVER segments
      - Each layover has ML risk prediction and success probability
    """
    from_code = from_station.strip().upper()
    to_code = to_station.strip().upper()

    if from_code == to_code:
        raise HTTPException(400, "Source and destination cannot be the same")

    # Build search request
    search_request = JourneySearchRequest(
        from_station=from_code,
        to_station=to_code,
        date=date_str,
        departure_time=departure_time,
        max_connections=max_connections,
        min_layover_minutes=min_layover,
        max_layover_minutes=max_layover,
        sort_by=sort_by,
    )

    # Check cache
    cache_key = journey_search_key(from_code, to_code, date_str, max_connections)
    cached = await cache_get(cache_key)
    if cached is not None:
        return JourneySearchResponse(**cached)

    # ── Run the AI Journey Search Pipeline ────────────────
    # This import is here to avoid circular imports.
    try:
        from app.services.journey_service import JourneySearchService

        service = JourneySearchService(db)
        response = await service.search(search_request)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

    # Cache results for 30 minutes
    await cache_set(cache_key, response.model_dump(), ttl=settings.JOURNEY_CACHE_TTL)

    return response


@router.get("/{journey_id}", response_model=JourneyResponse)
async def get_journey_detail(
    journey_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information for a specific journey.
    
    The journey_id is generated during search and cached.
    This endpoint retrieves the full journey with ML predictions.
    """
    # Check cache for this specific journey
    cache_key = f"journey:detail:{journey_id}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return JourneyResponse(**cached)

    raise HTTPException(
        404,
        f"Journey '{journey_id}' not found. "
        "Journeys are generated from search results and cached temporarily."
    )
