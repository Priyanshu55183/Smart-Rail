"""
Journey Search Service — The Orchestrator
==========================================
This is the BRAIN of SmartRail. It ties together:
  1. GraphBuilder → Builds the railway network
  2. DijkstraRouter → Finds multi-train paths
  3. JourneyScorer → Ranks and tags results

Pipeline:
  Request → Build Graph → Find Paths → Score → Tag → Response

This module is called from the /api/journeys endpoint.
"""

import uuid
from datetime import date, time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased

from app.models import Station, Train, TrainStop, TrainRun, TrainRunStatus
from app.services.graph_builder import GraphBuilder, RailwayGraph, _time_to_minutes, _minutes_to_display
from app.services.dijkstra import DijkstraRouter, RawPath
from app.services.scorer import JourneyScorer
from app.schemas.journey import (
    JourneySearchRequest,
    JourneySearchResponse,
    JourneyResponse,
    JourneyScore,
    TrainSegment,
    LayoverSegment,
    LayoverInfo,
)
from app.config import get_settings

settings = get_settings()


class JourneySearchService:
    """
    Orchestrates the entire journey search pipeline.

    Usage (from the API endpoint):
        service = JourneySearchService(db_session)
        response = await service.search(search_request)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.scorer = JourneyScorer()

    async def search(self, request: JourneySearchRequest) -> JourneySearchResponse:
        """
        The main search pipeline.

        Steps:
        1. Validate source and destination stations exist
        2. Build the railway graph for the search date
        3. Find direct trains (simple query, no graph needed)
        4. Find connecting journeys via Dijkstra
        5. Score and rank all journeys
        6. Tag smart recommendations
        7. Build the response
        """
        # ── Step 1: Validate stations ────────────────────────
        source = await self._get_station(request.from_station)
        dest = await self._get_station(request.to_station)

        if source is None:
            return self._empty_response(request, f"Station '{request.from_station}' not found")
        if dest is None:
            return self._empty_response(request, f"Station '{request.to_station}' not found")

        # Parse date
        try:
            journey_date = date.fromisoformat(request.date)
        except ValueError:
            return self._empty_response(request, "Invalid date format")

        # Parse departure time filter
        dep_after_minutes = None
        if request.departure_time:
            try:
                parts = request.departure_time.split(":")
                dep_after_minutes = int(parts[0]) * 60 + int(parts[1])
            except (ValueError, IndexError):
                pass

        # ── Step 2: Build the railway graph ──────────────────
        builder = GraphBuilder(self.db)
        graph = await builder.build(journey_date, request.from_station, request.to_station)

        # ── Step 3: Find direct trains ───────────────────────
        direct_journeys = await self._find_direct_trains(
            source, dest, journey_date, dep_after_minutes
        )

        # ── Step 4: Find connecting journeys via Dijkstra ────
        connecting_journeys = []
        if request.max_connections > 0:
            router = DijkstraRouter(graph)
            raw_paths = router.find_paths(
                source_code=request.from_station,
                dest_code=request.to_station,
                max_connections=request.max_connections,
                min_layover_minutes=request.min_layover_minutes,
                max_layover_minutes=request.max_layover_minutes,
                top_k=settings.DIJKSTRA_TOP_K,
                departure_after_minutes=dep_after_minutes,
            )

            for path in raw_paths:
                journey = self._raw_path_to_journey_dict(path, source, dest, request.date)
                if journey:
                    connecting_journeys.append(journey)

        # ── Step 5: Score and rank ───────────────────────────
        all_journeys = direct_journeys + connecting_journeys

        if all_journeys:
            all_journeys = self.scorer.score_journeys(all_journeys)
            all_journeys = self.scorer.tag_recommendations(all_journeys)

        # ── Step 6: Build response ───────────────────────────
        journey_responses = []
        for j in all_journeys:
            jr = self._dict_to_journey_response(j)
            if jr:
                journey_responses.append(jr)

        # Find tagged recommendations
        best_overall = next((j for j in journey_responses if "BEST_OVERALL" in j.tags), None)
        fastest = next((j for j in journey_responses if "FASTEST" in j.tags), None)
        cheapest = next((j for j in journey_responses if "CHEAPEST" in j.tags), None)
        safest = next((j for j in journey_responses if "SAFEST" in j.tags), None)

        return JourneySearchResponse(
            query=request,
            direct_trains_count=len(direct_journeys),
            connecting_journeys_count=len(connecting_journeys),
            best_overall=best_overall,
            fastest=fastest,
            cheapest=cheapest,
            safest=safest,
            journeys=journey_responses,
        )

    # ── Direct Train Search ──────────────────────────────────

    async def _find_direct_trains(
        self,
        source: Station,
        dest: Station,
        journey_date: date,
        dep_after_minutes: Optional[int] = None,
    ) -> list[dict]:
        """
        Find all direct trains between two stations.
        Similar to the /api/trains/direct endpoint but returns dicts
        for the scoring pipeline.
        """
        FromStop = aliased(TrainStop)
        ToStop = aliased(TrainStop)

        stmt = (
            select(Train, FromStop, ToStop)
            .join(FromStop, FromStop.train_id == Train.id)
            .join(ToStop, ToStop.train_id == Train.id)
            .where(
                and_(
                    FromStop.station_id == source.id,
                    ToStop.station_id == dest.id,
                    FromStop.stop_sequence < ToStop.stop_sequence,
                )
            )
            .order_by(FromStop.departure_time)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        day_name = journey_date.strftime("%a")
        journeys = []

        for train, from_stop, to_stop in rows:
            if not train.runs_on(day_name):
                continue

            # Check for cancellation
            run_stmt = select(TrainRun).where(
                and_(
                    TrainRun.train_id == train.id,
                    TrainRun.journey_date == journey_date,
                )
            )
            run_result = await self.db.execute(run_stmt)
            train_run = run_result.scalar_one_or_none()
            if train_run and train_run.status == TrainRunStatus.CANCELLED.value:
                continue

            # Time filter
            if dep_after_minutes and from_stop.departure_time:
                dep_mins = _time_to_minutes(from_stop.departure_time, from_stop.day_offset)
                if dep_mins < dep_after_minutes:
                    continue

            # Calculate duration
            dep_minutes = _time_to_minutes(from_stop.departure_time, from_stop.day_offset) if from_stop.departure_time else 0
            arr_minutes = _time_to_minutes(to_stop.arrival_time, to_stop.day_offset) if to_stop.arrival_time else 0
            duration = arr_minutes - dep_minutes

            # Distance
            dist_from = from_stop.distance_from_source or 0
            dist_to = to_stop.distance_from_source or 0
            distance = dist_to - dist_from if dist_to >= dist_from else None

            # Fare (mock)
            fare = round(distance * 1.15, 0) if distance and distance > 0 else None

            segment = {
                "train_number": train.train_number,
                "train_name": train.train_name,
                "train_type": train.train_type,
                "from_station_code": source.code,
                "from_station_name": source.name,
                "to_station_code": dest.code,
                "to_station_name": dest.name,
                "departure_time": from_stop.departure_time.strftime("%H:%M") if from_stop.departure_time else None,
                "arrival_time": to_stop.arrival_time.strftime("%H:%M") if to_stop.arrival_time else None,
                "departure_day_offset": from_stop.day_offset,
                "arrival_day_offset": to_stop.day_offset,
                "duration_minutes": duration,
                "distance_km": distance,
                "fare": fare,
            }

            journey = {
                "journey_id": f"J-{source.code}-{dest.code}-{train.train_number}",
                "total_duration_minutes": duration,
                "total_duration_display": _minutes_to_display(duration),
                "total_layover_minutes": 0,
                "num_connections": 0,
                "total_fare": fare,
                "overall_risk": "NONE",
                "overall_success_probability": 1.0,
                "from_station": source.code,
                "from_station_name": source.name,
                "to_station": dest.code,
                "to_station_name": dest.name,
                "date": journey_date.isoformat(),
                "train_segments": [segment],
                "layovers": [],
                "tags": [],
            }

            journeys.append(journey)

        return journeys

    # ── Path Conversion ──────────────────────────────────────

    def _raw_path_to_journey_dict(
        self,
        path: RawPath,
        source: Station,
        dest: Station,
        date_str: str,
    ) -> Optional[dict]:
        """Convert a Dijkstra RawPath into a journey dict for scoring."""
        if not path.train_segments:
            return None

        # Check this isn't a duplicate of a direct train
        if path.num_connections == 0 and len(path.train_segments) == 1:
            return None  # Already covered by direct train search

        total_duration = path.total_time_minutes
        total_layover = sum(l.get("duration_minutes", 0) for l in path.layovers)
        total_fare = sum(s.get("fare", 0) or 0 for s in path.train_segments)

        # Overall risk = worst risk among layovers
        risk_order = {"HIGH_RISK": 0, "MODERATE_RISK": 1, "LONG_LAYOVER": 2, "LOW_RISK": 3}
        overall_risk = "NONE"
        if path.layovers:
            worst = min(path.layovers, key=lambda l: risk_order.get(l.get("risk_level", "LOW_RISK"), 3))
            overall_risk = worst.get("risk_level", "LOW_RISK")

        # Compute success probability (rule-based placeholder; ML replaces this)
        success_prob = self._estimate_success_probability(path.layovers)

        # Generate unique ID
        train_nums = "-".join(s["train_number"] for s in path.train_segments)
        journey_id = f"J-{source.code}-{dest.code}-{train_nums}-{uuid.uuid4().hex[:4]}"

        return {
            "journey_id": journey_id,
            "total_duration_minutes": total_duration,
            "total_duration_display": _minutes_to_display(total_duration),
            "total_layover_minutes": total_layover,
            "num_connections": path.num_connections,
            "total_fare": total_fare if total_fare > 0 else None,
            "overall_risk": overall_risk,
            "overall_success_probability": success_prob,
            "from_station": source.code,
            "from_station_name": source.name,
            "to_station": dest.code,
            "to_station_name": dest.name,
            "date": date_str,
            "train_segments": path.train_segments,
            "layovers": path.layovers,
            "tags": [],
        }

    def _estimate_success_probability(self, layovers: list[dict]) -> float:
        """
        Rule-based connection success probability.
        Placeholder for the Monte Carlo estimator in Phase 3.

        P(all connections succeed) = product of individual probabilities.
        Individual probability based on layover risk:
          HIGH_RISK:     0.60
          MODERATE_RISK: 0.82
          LOW_RISK:      0.95
          LONG_LAYOVER:  0.98
        """
        if not layovers:
            return 1.0

        risk_probs = {
            "HIGH_RISK": 0.60,
            "MODERATE_RISK": 0.82,
            "LOW_RISK": 0.95,
            "LONG_LAYOVER": 0.98,
        }

        prob = 1.0
        for layover in layovers:
            risk = layover.get("risk_level", "LOW_RISK")
            prob *= risk_probs.get(risk, 0.90)

        return round(prob, 2)

    # ── Response Building ────────────────────────────────────

    def _dict_to_journey_response(self, j: dict) -> Optional[JourneyResponse]:
        """Convert a scored journey dict into a JourneyResponse schema."""
        try:
            # Build segments list (alternating TRAIN and LAYOVER)
            segments = []
            train_segs = j.get("train_segments", [])
            layovers = j.get("layovers", [])

            for i, seg in enumerate(train_segs):
                # Add train segment
                segments.append(TrainSegment(
                    train_number=seg["train_number"],
                    train_name=seg["train_name"],
                    train_type=seg["train_type"],
                    from_station_code=seg["from_station_code"],
                    from_station_name=seg["from_station_name"],
                    to_station_code=seg["to_station_code"],
                    to_station_name=seg["to_station_name"],
                    departure_time=seg.get("departure_time", "00:00"),
                    arrival_time=seg.get("arrival_time", "00:00"),
                    departure_day_offset=seg.get("departure_day_offset", 0),
                    arrival_day_offset=seg.get("arrival_day_offset", 0),
                    duration_minutes=seg.get("duration_minutes", 0),
                    distance_km=seg.get("distance_km"),
                    fare=seg.get("fare"),
                    predicted_delay_minutes=None,  # ML fills this in Phase 3
                ))

                # Add layover after this segment (if not the last segment)
                if i < len(layovers):
                    lay = layovers[i]
                    segments.append(LayoverSegment(
                        layover=LayoverInfo(
                            station_code=lay["station_code"],
                            station_name=lay["station_name"],
                            arrival_time=lay.get("arrival_time", "00:00"),
                            arrival_day_offset=lay.get("arrival_day_offset", 0),
                            departure_time=lay.get("departure_time", "00:00"),
                            departure_day_offset=lay.get("departure_day_offset", 0),
                            duration_minutes=lay.get("duration_minutes", 0),
                            duration_display=lay.get("duration_display", "0m"),
                            risk_level=lay.get("risk_level", "LOW_RISK"),
                            success_probability=self._estimate_success_probability([lay]),
                            min_transfer_minutes=lay.get("min_transfer_minutes", 30),
                        )
                    ))

            # Build score
            score_data = j.get("score", {})
            score = JourneyScore(
                composite=score_data.get("composite", 0),
                travel_time_score=score_data.get("travel_time_score", 0),
                layover_score=score_data.get("layover_score", 0),
                reliability_score=score_data.get("reliability_score", 0),
                price_score=score_data.get("price_score", 0),
                convenience_score=score_data.get("convenience_score", 0),
            )

            return JourneyResponse(
                journey_id=j["journey_id"],
                total_duration_minutes=j.get("total_duration_minutes", 0),
                total_duration_display=j.get("total_duration_display", "0m"),
                total_layover_minutes=j.get("total_layover_minutes", 0),
                num_connections=j.get("num_connections", 0),
                total_fare=j.get("total_fare"),
                overall_risk=j.get("overall_risk", "NONE"),
                overall_success_probability=j.get("overall_success_probability"),
                score=score,
                tags=j.get("tags", []),
                segments=segments,
                from_station=j["from_station"],
                from_station_name=j["from_station_name"],
                to_station=j["to_station"],
                to_station_name=j["to_station_name"],
                date=j["date"],
            )
        except Exception as e:
            print(f"⚠️  Error building journey response: {e}")
            return None

    # ── Helpers ───────────────────────────────────────────────

    async def _get_station(self, code: str) -> Optional[Station]:
        """Look up a station by code."""
        result = await self.db.execute(
            select(Station).where(Station.code == code.strip().upper())
        )
        return result.scalar_one_or_none()

    def _empty_response(self, request: JourneySearchRequest, reason: str) -> JourneySearchResponse:
        """Return an empty response (no results)."""
        return JourneySearchResponse(
            query=request,
            direct_trains_count=0,
            connecting_journeys_count=0,
            journeys=[],
        )
