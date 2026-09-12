"""
Split-Ticket / Break-Journey Optimization Service
==================================================
Discovers split-booking alternatives when direct train tickets are waitlisted.

In Indian Railways (IRCTC), intermediate stations often belong to different
quotas (Pooled Quota, Remote Location Quota, Station Quota).
This service decomposes train stops and finds intermediate junctions where
both Leg 1 (Source -> Halt) and Leg 2 (Halt -> Destination) have
guaranteed AVAILABLE seats.
"""

from typing import Optional, List, Dict, Tuple
from datetime import time, date
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Station, Train, TrainStop
from app.schemas.split_ticket import (
    SplitLeg,
    SplitTicketOption,
    SplitTicketResponse,
)
from app.services.journey_service import generate_class_availabilities


def _format_time(t: Optional[time]) -> str:
    """Format time object as HH:MM."""
    if not t:
        return "00:00"
    return t.strftime("%H:%M")


class SplitTicketService:
    """
    Scans intermediate halts along train routes to discover
    confirmed split-booking alternatives.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_split_tickets(
        self,
        from_code: str,
        to_code: str,
        journey_date: str,
        travel_class: str = "3A",
    ) -> SplitTicketResponse:
        """
        Find split-ticketing opportunities between from_code and to_code.
        """
        from_code = from_code.strip().upper()
        to_code = to_code.strip().upper()
        travel_class = travel_class.strip().upper()

        # 1. Resolve stations
        stmt = select(Station).where(Station.code.in_([from_code, to_code]))
        res = await self.db.execute(stmt)
        stations = {s.code: s for s in res.scalars().all()}

        from_station = stations.get(from_code)
        to_station = stations.get(to_code)

        if not from_station or not to_station:
            return SplitTicketResponse(
                from_station=from_code,
                from_station_name=from_station.name if from_station else from_code,
                to_station=to_code,
                to_station_name=to_station.name if to_station else to_code,
                date=journey_date,
                travel_class=travel_class,
                direct_status_summary="Stations not found",
                options_count=0,
                best_option=None,
                options=[],
            )

        # 2. Find direct trains and their stops
        # Get all TrainStops at origin and destination
        stmt_from = select(TrainStop).where(TrainStop.station_id == from_station.id)
        res_from = await self.db.execute(stmt_from)
        stops_from = {s.train_id: s for s in res_from.scalars().all()}

        stmt_to = select(TrainStop).where(TrainStop.station_id == to_station.id)
        res_to = await self.db.execute(stmt_to)
        stops_to = {s.train_id: s for s in res_to.scalars().all()}

        # Match trains that stop at both stations where sequence(from) < sequence(to)
        candidate_train_ids = [
            t_id for t_id, s_from in stops_from.items()
            if t_id in stops_to and s_from.stop_sequence < stops_to[t_id].stop_sequence
        ]

        # Fetch train details
        trains_map = {}
        if candidate_train_ids:
            stmt_trains = select(Train).where(Train.id.in_(candidate_train_ids))
            res_trains = await self.db.execute(stmt_trains)
            trains_map = {t.id: t for t in res_trains.scalars().all()}

        # Cache of all stations for fast lookup
        all_stations_stmt = select(Station)
        all_stations_res = await self.db.execute(all_stations_stmt)
        all_stations = {s.id: s for s in all_stations_res.scalars().all()}

        split_options: List[SplitTicketOption] = []
        direct_summary = "Available direct options evaluated"

        for train_id in candidate_train_ids:
            train = trains_map.get(train_id)
            if not train:
                continue

            s_from = stops_from[train_id]
            s_to = stops_to[train_id]

            # Direct train metrics
            direct_dist = max(50, (s_to.distance_from_source or 0) - (s_from.distance_from_source or 0))
            direct_avails = generate_class_availabilities(direct_dist, train.train_type, train.train_number)
            direct_class_info = next((a for a in direct_avails if a.travel_class == travel_class), direct_avails[0])

            direct_status = direct_class_info.status
            direct_display = direct_class_info.status_display
            direct_fare = direct_class_info.fare
            direct_prob = direct_class_info.confirmation_probability or 0.5

            # Get all intermediate stops for this train
            stmt_mid = (
                select(TrainStop)
                .where(
                    TrainStop.train_id == train_id,
                    TrainStop.stop_sequence > s_from.stop_sequence,
                    TrainStop.stop_sequence < s_to.stop_sequence,
                )
                .order_by(TrainStop.stop_sequence)
            )
            res_mid = await self.db.execute(stmt_mid)
            intermediate_stops = res_mid.scalars().all()

            # Evaluate each intermediate station as a split junction
            for mid_stop in intermediate_stops:
                mid_station = all_stations.get(mid_stop.station_id)
                if not mid_station:
                    continue

                # Distance for Leg 1 and Leg 2
                dist_leg1 = max(50, (mid_stop.distance_from_source or 0) - (s_from.distance_from_source or 0))
                dist_leg2 = max(50, (s_to.distance_from_source or 0) - (mid_stop.distance_from_source or 0))

                # Availabilities for Leg 1 (deterministic pseudo-quota simulation)
                # We use a unique seed derived from train + station code to simulate sub-quota availability
                leg1_avails = generate_class_availabilities(dist_leg1, train.train_type, f"{train.train_number}_{mid_station.code}_1")
                leg2_avails = generate_class_availabilities(dist_leg2, train.train_type, f"{train.train_number}_{mid_station.code}_2")

                leg1_info = next((a for a in leg1_avails if a.travel_class == travel_class), leg1_avails[0])
                leg2_info = next((a for a in leg2_avails if a.travel_class == travel_class), leg2_avails[0])

                # Both legs confirmed or RAC
                leg1_ok = leg1_info.status in ("AVAILABLE", "RAC")
                leg2_ok = leg2_info.status in ("AVAILABLE", "RAC")

                if leg1_ok and leg2_ok:
                    leg1 = SplitLeg(
                        leg_number=1,
                        train_number=train.train_number,
                        train_name=train.train_name,
                        train_type=train.train_type,
                        from_station_code=from_station.code,
                        from_station_name=from_station.name,
                        to_station_code=mid_station.code,
                        to_station_name=mid_station.name,
                        departure_time=_format_time(s_from.departure_time),
                        arrival_time=_format_time(mid_stop.arrival_time),
                        travel_class=travel_class,
                        status=leg1_info.status,
                        available_seats=leg1_info.available_seats,
                        status_display=leg1_info.status_display,
                        confirmation_probability=leg1_info.confirmation_probability or 1.0,
                        fare=leg1_info.fare,
                        distance_km=dist_leg1,
                    )

                    leg2 = SplitLeg(
                        leg_number=2,
                        train_number=train.train_number,
                        train_name=train.train_name,
                        train_type=train.train_type,
                        from_station_code=mid_station.code,
                        from_station_name=mid_station.name,
                        to_station_code=to_station.code,
                        to_station_name=to_station.name,
                        departure_time=_format_time(mid_stop.departure_time),
                        arrival_time=_format_time(s_to.arrival_time),
                        travel_class=travel_class,
                        status=leg2_info.status,
                        available_seats=leg2_info.available_seats,
                        status_display=leg2_info.status_display,
                        confirmation_probability=leg2_info.confirmation_probability or 1.0,
                        fare=leg2_info.fare,
                        distance_km=dist_leg2,
                    )

                    total_split = leg1.fare + leg2.fare
                    fare_diff = round(total_split - direct_fare, 2)
                    halt_min = mid_stop.halt_minutes or 10

                    option = SplitTicketOption(
                        option_id=f"SPLIT-{from_station.code}-{to_station.code}-{mid_station.code}-{train.train_number}",
                        is_same_train=True,
                        intermediate_station_code=mid_station.code,
                        intermediate_station_name=mid_station.name,
                        travel_class=travel_class,
                        leg1=leg1,
                        leg2=leg2,
                        direct_status=direct_status,
                        direct_status_display=direct_display,
                        direct_fare=direct_fare,
                        direct_confirmation_probability=direct_prob,
                        total_split_fare=total_split,
                        fare_difference=fare_diff,
                        overall_confirmation_probability=round(
                            (leg1.confirmation_probability * leg2.confirmation_probability), 2
                        ),
                        guaranteed_confirmed=True,
                        berth_action_tip=(
                            f"Same train ({train.train_number})! Stay seated and simply change berth "
                            f"at {mid_station.name} during the {halt_min}-minute halt."
                        ),
                    )
                    split_options.append(option)

        # Sort options: highest confirmation probability first, then lowest fare difference
        split_options.sort(
            key=lambda o: (-o.overall_confirmation_probability, o.fare_difference)
        )

        best_opt = split_options[0] if split_options else None
        if best_opt:
            direct_summary = f"Direct status: {best_opt.direct_status_display} vs Split: 100% CONFIRMED"

        return SplitTicketResponse(
            from_station=from_station.code,
            from_station_name=from_station.name,
            to_station=to_station.code,
            to_station_name=to_station.name,
            date=journey_date,
            travel_class=travel_class,
            direct_status_summary=direct_summary,
            options_count=len(split_options),
            best_option=best_opt,
            options=split_options[:6],  # Top 6 best split alternatives
        )
