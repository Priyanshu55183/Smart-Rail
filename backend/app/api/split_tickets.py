"""
Split-Ticket API Endpoints
===========================
Provides high-probability confirmed split-booking alternatives ("Hacker Fare")
when direct train tickets are on waitlist.

Endpoints:
  GET /api/split-tickets/find?from=SBC&to=NDLS&date=2026-09-15&class=3A
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.database.redis import cache_get, cache_set
from app.schemas.split_ticket import SplitTicketResponse
from app.services.split_ticket_service import SplitTicketService
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/find", response_model=SplitTicketResponse)
async def find_split_tickets(
    from_station: str = Query(..., alias="from", description="Source station code (e.g. SBC)"),
    to_station: str = Query(..., alias="to", description="Destination station code (e.g. NDLS)"),
    date_str: str = Query(..., alias="date", description="Journey date YYYY-MM-DD"),
    travel_class: str = Query("3A", alias="class", description="Travel class: SL, 3A, 2A, 1A, CC, 2S"),
    db: AsyncSession = Depends(get_db),
):
    """
    ⚡ DISCOVER SPLIT-TICKETING CONFIRMED BERTHS
    
    Decomposes intermediate stops along routes between origin and destination.
    Identifies intermediate junction points where booking Leg 1 + Leg 2
    yields 100% CONFIRMED seats on the exact same train or fast connection.
    
    Example:
      GET /api/split-tickets/find?from=SBC&to=NDLS&date=2026-09-15&class=3A
    """
    from_code = from_station.strip().upper()
    to_code = to_station.strip().upper()
    travel_class = travel_class.strip().upper()

    if from_code == to_code:
        raise HTTPException(400, "Source and destination cannot be the same station")

    cache_key = f"smartrail:split_tickets:{from_code}:{to_code}:{date_str}:{travel_class}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return SplitTicketResponse(**cached)

    try:
        service = SplitTicketService(db)
        response = await service.find_split_tickets(
            from_code=from_code,
            to_code=to_code,
            journey_date=date_str,
            travel_class=travel_class,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Split-ticket calculation error: {str(e)}")

    # Cache results for 30 minutes
    await cache_set(cache_key, response.model_dump(), ttl=settings.JOURNEY_CACHE_TTL)
    return response
