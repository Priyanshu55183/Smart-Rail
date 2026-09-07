"""
Database Seed Loader
====================
Populates the SmartRail database with realistic Indian Railways data.

What it loads:
  1. ~120 Stations  (from stations_data.py)
  2. ~75 Trains     (from trains_data.py)
  3. ~600 TrainStops (stop-by-stop schedules for each train)
  4. ~6750 TrainRuns (90 days of daily train run records)
  5. ~50,000 HistoricalDelay records (for ML training in Phase 3)

Idempotent: Checks if data exists before inserting.
Can be run via: python -m app.seed.seed_loader

The delay generation uses realistic patterns:
  - RAJDHANI trains: avg 8 min delay
  - SUPERFAST trains: avg 15 min delay
  - EXPRESS trains: avg 25 min delay
  - Winter months (Dec-Jan): +40% delay in NR/NCR zones (fog)
  - Monsoon months (Jul-Sep): +30% delay in WR/CR zones (rain)
"""

import asyncio
import random
from datetime import date, time, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import async_session_factory, init_db
from app.models import Station, Train, TrainStop, TrainRun, HistoricalDelay
from app.models.train_run import TrainRunStatus
from app.seed.stations_data import STATIONS_DATA
from app.seed.trains_data import TRAINS_DATA
from app.config import get_settings

settings = get_settings()

# Reproducible randomness for consistent seed data
random.seed(42)


async def seed_all() -> None:
    """
    Main entry point. Seeds everything in order
    (stations first, then trains depend on station IDs).
    """
    async with async_session_factory() as session:
        # Step 1: Check / seed stations
        station_map = await seed_stations(session)
        print(f"   ✅ {len(station_map)} stations verified")

        # Step 2: Trains + Stops (idempotent — adds any missing trains)
        train_map = await seed_trains_and_stops(session, station_map)
        print(f"   ✅ {len(train_map)} trains verified with schedules")

        # Step 3: Train Runs (90 days)
        run_count = await seed_train_runs(session, train_map)
        print(f"   ✅ {run_count} train run records verified")

        # Step 4: Historical Delays
        delay_count = await seed_historical_delays(session, train_map, station_map)
        print(f"   ✅ {delay_count} historical delay records verified")

        await session.commit()
        print("🎉 Database seed complete!")


async def seed_stations(session: AsyncSession) -> dict[str, int]:
    """
    Load stations from STATIONS_DATA.
    Returns: {station_code: station_id}
    """
    station_map: dict[str, int] = {}
    existing = await session.execute(select(Station))
    for s in existing.scalars().all():
        station_map[s.code] = s.id

    for data in STATIONS_DATA:
        code, name, city, state, zone, category, lat, lon, is_junction, min_transfer, platforms = data
        if code in station_map:
            continue

        station = Station(
            code=code,
            name=name,
            city=city,
            state=state,
            zone=zone,
            station_category=category,
            latitude=lat,
            longitude=lon,
            is_junction=is_junction,
            minimum_transfer_minutes=min_transfer,
            num_platforms=platforms,
        )
        session.add(station)
        await session.flush()  # Get the auto-generated ID
        station_map[code] = station.id

    return station_map


async def seed_trains_and_stops(
    session: AsyncSession, station_map: dict[str, int]
) -> dict[str, int]:
    """
    Load trains and their stop schedules from TRAINS_DATA.
    Returns: {train_number: train_id}
    """
    train_map: dict[str, int] = {}
    existing_trains = await session.execute(select(Train))
    for t in existing_trains.scalars().all():
        train_map[t.train_number] = t.id

    for train_data in TRAINS_DATA:
        number = train_data["number"]
        if number in train_map:
            continue
        name = train_data["name"]
        train_type = train_data["type"]
        runs_on = train_data["runs_on"]
        stops = train_data["stops"]

        # Determine source and destination from first/last stops
        source_code = stops[0][0]
        dest_code = stops[-1][0]
        source_id = station_map.get(source_code)
        dest_id = station_map.get(dest_code)

        # Total distance
        total_distance = stops[-1][5] if stops[-1][5] else None

        # Average speed (distance / time in hours)
        if total_distance and len(stops) >= 2:
            first_dep = stops[0][2]  # departure time string
            last_arr = stops[-1][1]  # arrival time string
            last_day = stops[-1][3]  # day offset
            if first_dep and last_arr:
                dep_parts = first_dep.split(":")
                arr_parts = last_arr.split(":")
                dep_min = int(dep_parts[0]) * 60 + int(dep_parts[1])
                arr_min = last_day * 1440 + int(arr_parts[0]) * 60 + int(arr_parts[1])
                total_min = arr_min - dep_min
                if total_min > 0:
                    avg_speed = (total_distance / total_min) * 60
                else:
                    avg_speed = None
            else:
                avg_speed = None
        else:
            avg_speed = None

        train = Train(
            train_number=number,
            train_name=name,
            train_type=train_type,
            runs_on_days=runs_on,
            source_station_id=source_id,
            destination_station_id=dest_id,
            total_distance_km=total_distance,
            avg_speed_kmph=round(avg_speed, 1) if avg_speed else None,
        )
        session.add(train)
        await session.flush()
        train_map[number] = train.id

        # Add stops
        for seq, stop_data in enumerate(stops, start=1):
            s_code, arr_str, dep_str, day_offset, halt_min, distance = stop_data

            station_id = station_map.get(s_code)
            if station_id is None:
                print(f"   ⚠️  Station '{s_code}' not found for train {number}, skipping stop")
                continue

            arr_time = _parse_time(arr_str)
            dep_time = _parse_time(dep_str)

            stop = TrainStop(
                train_id=train.id,
                station_id=station_id,
                stop_sequence=seq,
                arrival_time=arr_time,
                departure_time=dep_time,
                day_offset=day_offset,
                halt_minutes=halt_min,
                distance_from_source=distance,
                platform_number=str(random.randint(1, 8)),
            )
            session.add(stop)

    return train_map


async def seed_train_runs(
    session: AsyncSession, train_map: dict[str, int]
) -> int:
    """
    Create TrainRun records for 90 days from today.
    ~2% of runs are marked as CANCELLED for realism.
    """
    today = date.today()
    count = 0

    existing_runs_res = await session.execute(select(TrainRun.train_id, TrainRun.journey_date))
    existing_runs = set(existing_runs_res.all())

    for number, train_id in train_map.items():
        # Get the train to check which days it runs
        result = await session.execute(
            select(Train).where(Train.id == train_id)
        )
        train = result.scalar_one()

        for day_offset in range(settings.SEED_DAYS_OF_RUNS):
            run_date = today + timedelta(days=day_offset)
            if (train_id, run_date) in existing_runs:
                continue

            day_name = run_date.strftime("%a")

            if not train.runs_on(day_name):
                continue

            # 2% chance of cancellation
            status = TrainRunStatus.CANCELLED.value if random.random() < 0.02 else TrainRunStatus.SCHEDULED.value

            run = TrainRun(
                train_id=train_id,
                journey_date=run_date,
                status=status,
            )
            session.add(run)
            existing_runs.add((train_id, run_date))
            count += 1

    return count


async def seed_historical_delays(
    session: AsyncSession,
    train_map: dict[str, int],
    station_map: dict[str, int],
) -> int:
    """
    Generate ~50,000 realistic historical delay records if not already seeded.
    Delay patterns: Rajdhani ~8min, Express ~25min, Passenger ~40min.
    """
    delay_count_res = await session.execute(select(func.count()).select_from(HistoricalDelay))
    existing_delays = delay_count_res.scalar() or 0
    if existing_delays >= 1000:
        return existing_delays
    # Load station zones for seasonal patterns
    station_zones: dict[int, str] = {}
    result = await session.execute(select(Station))
    for station in result.scalars().all():
        station_zones[station.id] = station.zone or "NR"

    # Delay characteristics by train type
    delay_profiles = {
        "RAJDHANI":     {"mean": 8,  "std": 6},
        "VANDE_BHARAT": {"mean": 5,  "std": 4},
        "SHATABDI":     {"mean": 10, "std": 7},
        "DURONTO":      {"mean": 12, "std": 8},
        "SUPERFAST":    {"mean": 15, "std": 12},
        "EXPRESS":      {"mean": 25, "std": 18},
        "MAIL":         {"mean": 30, "std": 20},
        "PASSENGER":    {"mean": 40, "std": 25},
    }

    # Cause categories with weights
    causes = ["CONGESTION", "FOG", "MONSOON", "TECHNICAL", "OPERATIONAL", "CAUTION_ORDER", "OTHER"]
    cause_weights_default = [0.30, 0.10, 0.10, 0.15, 0.15, 0.10, 0.10]

    # Indian holidays (approximate dates — for is_holiday flag)
    holidays = {
        (1, 26), (3, 8), (8, 15), (10, 2), (11, 1), (11, 14), (12, 25),
        (1, 1), (1, 14), (3, 29), (4, 14), (5, 1), (10, 24), (10, 31),
    }

    today = date.today()
    count = 0
    target_count = settings.SEED_DELAY_RECORDS
    batch_size = 1000
    batch = []

    # Get all trains with their stops
    train_ids = list(train_map.values())
    train_type_map: dict[int, str] = {}
    result = await session.execute(select(Train))
    for train in result.scalars().all():
        train_type_map[train.id] = train.train_type

    # Get train stops
    stops_result = await session.execute(
        select(TrainStop).where(TrainStop.arrival_time.isnot(None))
    )
    all_stops = stops_result.scalars().all()

    if not all_stops:
        return 0

    while count < target_count:
        # Pick a random stop
        stop = random.choice(all_stops)
        train_id = stop.train_id
        station_id = stop.station_id
        train_type = train_type_map.get(train_id, "EXPRESS")
        zone = station_zones.get(station_id, "NR")

        # Pick a random date in the past 180 days
        days_ago = random.randint(1, 180)
        record_date = today - timedelta(days=days_ago)
        month = record_date.month
        day_of_week = record_date.weekday()

        # Base delay from train type
        profile = delay_profiles.get(train_type, delay_profiles["EXPRESS"])
        base_delay = random.gauss(profile["mean"], profile["std"])

        # Seasonal modifier
        seasonal_multiplier = 1.0
        if month in (12, 1) and zone in ("NR", "NCR", "NER", "NWR"):
            seasonal_multiplier = 1.4  # Winter fog
        elif month in (7, 8, 9) and zone in ("WR", "CR", "SR", "KR"):
            seasonal_multiplier = 1.3  # Monsoon
        elif month in (4, 5) and zone in ("NR", "NCR", "WR"):
            seasonal_multiplier = 1.1  # Summer heat

        # Holiday modifier
        is_holiday = (month, record_date.day) in holidays
        if is_holiday:
            seasonal_multiplier *= 1.2

        delay = int(base_delay * seasonal_multiplier)
        delay = max(-5, delay)  # Allow slight early arrivals (rare)

        # Pick cause based on delay level
        if delay <= 0:
            cause = None
        elif month in (12, 1) and zone in ("NR", "NCR", "NER"):
            cause = "FOG"
        elif month in (7, 8, 9) and zone in ("WR", "CR", "SR"):
            cause = "MONSOON"
        else:
            cause = random.choices(causes, weights=cause_weights_default, k=1)[0]

        # Calculate actual arrival
        if stop.arrival_time:
            sched_minutes = stop.arrival_time.hour * 60 + stop.arrival_time.minute
            actual_minutes = sched_minutes + delay
            actual_hour = (actual_minutes // 60) % 24
            actual_min = actual_minutes % 60
            actual_arrival = time(actual_hour, actual_min)
        else:
            actual_arrival = None

        record = HistoricalDelay(
            train_id=train_id,
            station_id=station_id,
            date=record_date,
            scheduled_arrival=stop.arrival_time,
            actual_arrival=actual_arrival,
            delay_minutes=delay,
            cause_category=cause,
            day_of_week=day_of_week,
            month=month,
            is_holiday=is_holiday,
        )
        batch.append(record)
        count += 1

        # Flush in batches for performance
        if len(batch) >= batch_size:
            session.add_all(batch)
            await session.flush()
            batch = []

    # Flush remaining
    if batch:
        session.add_all(batch)
        await session.flush()

    return count


def _parse_time(time_str: str | None) -> time | None:
    """Parse 'HH:MM' string to a time object."""
    if time_str is None:
        return None
    parts = time_str.split(":")
    return time(int(parts[0]), int(parts[1]))


# ── CLI Entry Point ──────────────────────────────────────────
async def main():
    """Run seeder standalone: python -m app.seed.seed_loader"""
    print("🔧 Initializing database...")
    await init_db()
    await seed_all()


if __name__ == "__main__":
    asyncio.run(main())
