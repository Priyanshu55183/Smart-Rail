"""
Train API Endpoints
===================
Handles direct train search, train details, and full schedule lookup.

Endpoints:
  GET /api/trains/direct?from=SBC&to=NDLS&date=2026-08-25  → Direct trains
  GET /api/trains/{train_number}                            → Train details
  GET /api/trains/{train_number}/schedule                   → Full stop list

How direct train search works:
  1. Find all train_stops where station = source (e.g., SBC)
  2. For each of those trains, check if they also stop at destination (e.g., NDLS)
  3. Verify source stop_sequence < destination stop_sequence (right direction!)
  4. Check train_runs to make sure the train isn't cancelled on that date
  5. Calculate duration considering day_offsets (overnight trains)
  6. Return sorted by departure time

Why stop_sequence matters:
  Train 12345 might stop at both SBC (stop #3) and HYB (stop #7).
  If user searches SBC → HYB, stop 3 < stop 7 ✅ (correct direction)
  If user searches HYB → SBC, stop 7 > stop 3 ❌ (wrong direction, skip)
"""

from datetime import date, time, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased

from app.database.postgres import get_db
from app.database.redis import cache_get, cache_set, direct_trains_key, train_schedule_key
from app.models import Station, Train, TrainStop, TrainRun, TrainRunStatus
from app.schemas.train import (
    TrainResponse, TrainStopResponse, TrainScheduleResponse,
    DirectTrainResponse, DirectTrainSearchResponse,
)
from app.config import get_settings

router = APIRouter()
settings = get_settings()


def _calculate_duration(
    dep_time: time, arr_time: time,
    dep_day_offset: int, arr_day_offset: int
) -> int:
    """
    Calculate travel duration in minutes, handling overnight trains.
    
    Example: depart 23:00 day 0, arrive 06:00 day 1
    = (1*1440 + 360) - (0*1440 + 1380) = 1800 - 1380 = 420 minutes (7 hours)
    """
    dep_total = dep_day_offset * 1440 + dep_time.hour * 60 + dep_time.minute
    arr_total = arr_day_offset * 1440 + arr_time.hour * 60 + arr_time.minute
    return arr_total - dep_total


def _time_to_str(t: Optional[time]) -> Optional[str]:
    """Convert time object to 'HH:MM' string."""
    if t is None:
        return None
    return t.strftime("%H:%M")


@router.get("/direct", response_model=DirectTrainSearchResponse)
async def search_direct_trains(
    from_station: str = Query(..., alias="from", description="Source station code"),
    to_station: str = Query(..., alias="to", description="Destination station code"),
    date_str: str = Query(..., alias="date", description="Date YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    """
    Find all direct trains between two stations on a given date.
    
    Example: GET /api/trains/direct?from=SBC&to=HYB&date=2026-08-25
    """
    from_code = from_station.strip().upper()
    to_code = to_station.strip().upper()

    # Validate: source != destination
    if from_code == to_code:
        raise HTTPException(400, "Source and destination cannot be the same")

    # Parse date
    try:
        journey_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

    # Check cache
    cache_key = direct_trains_key(from_code, to_code, date_str)
    cached = await cache_get(cache_key)
    if cached is not None:
        return DirectTrainSearchResponse(**cached)

    # Look up station IDs
    from_station_obj = await db.execute(
        select(Station).where(Station.code == from_code)
    )
    from_station_obj = from_station_obj.scalar_one_or_none()
    if not from_station_obj:
        raise HTTPException(404, f"Station '{from_code}' not found")

    to_station_obj = await db.execute(
        select(Station).where(Station.code == to_code)
    )
    to_station_obj = to_station_obj.scalar_one_or_none()
    if not to_station_obj:
        raise HTTPException(404, f"Station '{to_code}' not found")

    # Find trains that stop at BOTH stations (in the right direction)
    # We alias TrainStop to join it twice — once for source, once for dest
    FromStop = aliased(TrainStop)
    ToStop = aliased(TrainStop)

    stmt = (
        select(Train, FromStop, ToStop)
        .join(FromStop, FromStop.train_id == Train.id)
        .join(ToStop, ToStop.train_id == Train.id)
        .where(
            and_(
                FromStop.station_id == from_station_obj.id,
                ToStop.station_id == to_station_obj.id,
                # Source stop must come BEFORE destination stop (right direction)
                FromStop.stop_sequence < ToStop.stop_sequence,
            )
        )
        .order_by(FromStop.departure_time)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Filter by train runs (check if train is running on this date)
    direct_trains = []
    day_name = journey_date.strftime("%a")  # "Mon", "Tue", etc.

    for train, from_stop, to_stop in rows:
        # Check if train runs on this day of week
        if not train.runs_on(day_name):
            continue

        # Check if train run exists and is not cancelled
        run_stmt = select(TrainRun).where(
            and_(
                TrainRun.train_id == train.id,
                TrainRun.journey_date == journey_date,
            )
        )
        run_result = await db.execute(run_stmt)
        train_run = run_result.scalar_one_or_none()

        status = "SCHEDULED"
        if train_run:
            if train_run.status == TrainRunStatus.CANCELLED.value:
                continue  # Skip cancelled trains
            status = train_run.status

        # Calculate duration
        duration = _calculate_duration(
            from_stop.departure_time, to_stop.arrival_time,
            from_stop.day_offset, to_stop.day_offset,
        )

        # Calculate distance
        distance = None
        if to_stop.distance_from_source and from_stop.distance_from_source:
            distance = to_stop.distance_from_source - from_stop.distance_from_source

        # Mock fares based on distance (realistic Indian Railways pricing)
        fare_sl = round(distance * 0.45, 0) if distance else None   # ~₹0.45/km
        fare_3a = round(distance * 1.15, 0) if distance else None   # ~₹1.15/km
        fare_2a = round(distance * 1.70, 0) if distance else None   # ~₹1.70/km

        direct_trains.append(DirectTrainResponse(
            train_number=train.train_number,
            train_name=train.train_name,
            train_type=train.train_type,
            from_station=from_code,
            to_station=to_code,
            departure_time=_time_to_str(from_stop.departure_time),
            arrival_time=_time_to_str(to_stop.arrival_time),
            departure_day_offset=from_stop.day_offset,
            arrival_day_offset=to_stop.day_offset,
            duration_minutes=duration,
            distance_km=distance,
            fare_sleeper=fare_sl,
            fare_3ac=fare_3a,
            fare_2ac=fare_2a,
            status=status,
        ))

    response = DirectTrainSearchResponse(
        from_station=from_code,
        to_station=to_code,
        date=date_str,
        count=len(direct_trains),
        trains=direct_trains,
    )

    # Cache for 30 minutes
    await cache_set(cache_key, response.model_dump(), ttl=settings.JOURNEY_CACHE_TTL)

    return response


@router.get("/{train_number}", response_model=TrainResponse)
async def get_train(
    train_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details for a specific train by number."""
    stmt = select(Train).where(Train.train_number == train_number)
    result = await db.execute(stmt)
    train = result.scalar_one_or_none()

    if not train:
        raise HTTPException(404, f"Train '{train_number}' not found")

    return TrainResponse.model_validate(train)


@router.get("/{train_number}/schedule", response_model=TrainScheduleResponse)
async def get_train_schedule(
    train_number: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the full schedule (all stops) for a train.
    Returns stops in order with arrival/departure times and day offsets.
    """
    # Check cache
    cache_key = train_schedule_key(train_number)
    cached = await cache_get(cache_key)
    if cached is not None:
        return TrainScheduleResponse(**cached)

    # Get train
    stmt = select(Train).where(Train.train_number == train_number)
    result = await db.execute(stmt)
    train = result.scalar_one_or_none()

    if not train:
        raise HTTPException(404, f"Train '{train_number}' not found")

    # Get all stops in order
    stops_stmt = (
        select(TrainStop, Station)
        .join(Station, TrainStop.station_id == Station.id)
        .where(TrainStop.train_id == train.id)
        .order_by(TrainStop.stop_sequence)
    )
    stops_result = await db.execute(stops_stmt)
    stop_rows = stops_result.all()

    stops = [
        TrainStopResponse(
            station_code=station.code,
            station_name=station.name,
            stop_sequence=stop.stop_sequence,
            arrival_time=_time_to_str(stop.arrival_time),
            departure_time=_time_to_str(stop.departure_time),
            day_offset=stop.day_offset,
            halt_minutes=stop.halt_minutes,
            distance_from_source=stop.distance_from_source,
            platform_number=stop.platform_number,
        )
        for stop, station in stop_rows
    ]

    response = TrainScheduleResponse(
        train=TrainResponse.model_validate(train),
        stops=stops,
        total_stops=len(stops),
    )

    # Cache for 24 hours
    await cache_set(cache_key, response.model_dump(), ttl=settings.STATION_CACHE_TTL)

    return response
