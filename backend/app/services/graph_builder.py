"""
Railway Graph Builder
=====================
Converts the railway database into a time-dependent directed graph
that the Dijkstra algorithm can search.

Graph Structure:
================
NODES: Each node is a (station_code, time_minutes, day_offset) tuple.
       Every TrainStop becomes two nodes:
         - An ARRIVAL node   (station, arrival_time, day_offset)
         - A DEPARTURE node  (station, departure_time, day_offset)

EDGES: Two types:
  1. TRAVEL edges (same train, consecutive stops):
       (SBC, dep=21:40, day=0) --12627--> (YPR, arr=22:05, day=0)
     Weight = travel time in minutes.

  2. TRANSFER edges (different trains, same station):
       (SC, arr=09:15 via 12627) --> (SC, dep=15:45 via 12723)
     Weight = waiting time.
     Only created if wait >= station.minimum_transfer_minutes.

Why time-dependent?
  Because a train can only be boarded at its departure time.
  A graph edge from SBC at 21:40 is ONLY usable if you arrive by 21:40.
  This naturally prevents impossible connections.

Performance:
  ~120 stations × ~75 trains × ~8 stops/train = ~600 stops
  = ~600 departure nodes + ~600 arrival nodes = ~1200 nodes
  = ~525 travel edges + ~thousands of transfer edges
  NetworkX handles this in <100ms.
"""

from datetime import time, date
from typing import Optional
from collections import defaultdict
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Station, Train, TrainStop
from app.config import get_settings

settings = get_settings()


def _time_to_minutes(t: time, day_offset: int = 0) -> int:
    """
    Convert a time + day_offset to total minutes from day 0 midnight.
    This creates a linear timeline that handles overnight trains.

    Example:
      21:40 day 0 → 0*1440 + 21*60 + 40 = 1300 minutes
      06:15 day 1 → 1*1440 + 6*60 + 15  = 1815 minutes
    """
    return day_offset * 1440 + t.hour * 60 + t.minute


def _minutes_to_display(minutes: int) -> str:
    """Convert minutes to 'Xh Ym' display format."""
    if minutes < 0:
        return "0m"
    hours = minutes // 60
    mins = minutes % 60
    if hours == 0:
        return f"{mins}m"
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


class RailwayGraph:
    """
    The built graph containing the NetworkX DiGraph plus lookup tables.
    Passed to the Dijkstra router for pathfinding.
    """

    def __init__(self):
        # The directed graph
        self.graph: nx.DiGraph = nx.DiGraph()

        # Station code → Station model (for transfer times, names)
        self.stations: dict[str, Station] = {}

        # station_code → list of (departure_time_minutes, node_id, train_info)
        # Used by Dijkstra to find departures from a station after a given time
        self.station_departures: dict[str, list[tuple]] = defaultdict(list)

        # node_id → metadata dict (train_number, station_code, time, etc.)
        self.node_meta: dict[str, dict] = {}

        # train_number → Train model
        self.trains: dict[str, Train] = {}

        # Stats
        self.num_travel_edges: int = 0
        self.num_transfer_edges: int = 0


class GraphBuilder:
    """
    Builds a RailwayGraph from the database.

    Usage:
        builder = GraphBuilder(db_session)
        graph = await builder.build(journey_date)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def build(
        self,
        journey_date: date,
        source_code: Optional[str] = None,
        dest_code: Optional[str] = None,
    ) -> RailwayGraph:
        """
        Build the full railway graph for a given date.

        Steps:
        1. Load all stations (for transfer times and metadata)
        2. Load all trains running on this date
        3. Load all TrainStops for those trains
        4. Create TRAVEL edges (consecutive stops on same train)
        5. Create TRANSFER edges (different trains at same station)
        """
        rg = RailwayGraph()

        # Step 1: Load stations
        await self._load_stations(rg)

        # Step 2: Load trains and stops
        day_name = journey_date.strftime("%a")  # "Mon", "Tue", etc.
        await self._load_trains_and_stops(rg, day_name)

        # Step 3: Create transfer edges
        self._create_transfer_edges(rg)

        return rg

    async def _load_stations(self, rg: RailwayGraph) -> None:
        """Load all stations into the graph's lookup table."""
        result = await self.db.execute(select(Station))
        for station in result.scalars().all():
            rg.stations[station.code] = station

    async def _load_trains_and_stops(
        self, rg: RailwayGraph, day_name: str
    ) -> None:
        """
        Load all trains running on this day, along with their stops.
        Create TRAVEL edges between consecutive stops.
        """
        # Load all trains
        result = await self.db.execute(select(Train))
        all_trains = result.scalars().all()

        # Filter to trains running on this day of week
        running_trains = [t for t in all_trains if t.runs_on(day_name)]

        if not running_trains:
            return

        train_ids = [t.id for t in running_trains]
        train_id_to_model = {t.id: t for t in running_trains}

        # Store train models by number
        for t in running_trains:
            rg.trains[t.train_number] = t

        # Load all stops for running trains, ordered by train_id + sequence
        stops_stmt = (
            select(TrainStop)
            .where(TrainStop.train_id.in_(train_ids))
            .order_by(TrainStop.train_id, TrainStop.stop_sequence)
        )
        result = await self.db.execute(stops_stmt)
        all_stops = result.scalars().all()

        # Group stops by train_id
        train_stops: dict[int, list[TrainStop]] = defaultdict(list)
        for stop in all_stops:
            train_stops[stop.train_id].append(stop)

        # Process each train's stops → create nodes + travel edges
        for train_id, stops in train_stops.items():
            train = train_id_to_model[train_id]
            self._process_train_stops(rg, train, stops)

    def _process_train_stops(
        self, rg: RailwayGraph, train: Train, stops: list[TrainStop]
    ) -> None:
        """
        Create nodes and TRAVEL edges for one train.

        For each consecutive pair of stops:
          (station_A, departure) --(train)--> (station_B, arrival)
        """
        prev_node_id: Optional[str] = None
        prev_stop: Optional[TrainStop] = None

        for stop in stops:
            station = rg.stations.get(self._get_station_code(rg, stop))
            if station is None:
                continue

            station_code = station.code

            # Create a unique node for this train at this station
            node_id = f"{train.train_number}:{station_code}:{stop.stop_sequence}"

            # Determine times
            dep_minutes = None
            arr_minutes = None
            if stop.departure_time:
                dep_minutes = _time_to_minutes(stop.departure_time, stop.day_offset)
            if stop.arrival_time:
                arr_minutes = _time_to_minutes(stop.arrival_time, stop.day_offset)

            # Node metadata
            meta = {
                "train_number": train.train_number,
                "train_name": train.train_name,
                "train_type": train.train_type,
                "station_code": station_code,
                "station_name": station.name,
                "stop_sequence": stop.stop_sequence,
                "arrival_time": stop.arrival_time,
                "departure_time": stop.departure_time,
                "arrival_minutes": arr_minutes,
                "departure_minutes": dep_minutes,
                "day_offset": stop.day_offset,
                "distance_from_source": stop.distance_from_source or 0,
                "halt_minutes": stop.halt_minutes or 0,
                "platform_number": stop.platform_number,
                "station_id": stop.station_id,
                "train_id": stop.train_id,
            }

            rg.graph.add_node(node_id, **meta)
            rg.node_meta[node_id] = meta

            # Register departure for transfer edge creation
            if dep_minutes is not None:
                rg.station_departures[station_code].append(
                    (dep_minutes, node_id, train.train_number)
                )

            # Create TRAVEL edge from previous stop to this stop
            if prev_node_id is not None and arr_minutes is not None:
                prev_dep = rg.node_meta[prev_node_id].get("departure_minutes")
                if prev_dep is not None:
                    travel_time = arr_minutes - prev_dep
                    if travel_time > 0:
                        rg.graph.add_edge(
                            prev_node_id,
                            node_id,
                            weight=travel_time,
                            edge_type="TRAVEL",
                            train_number=train.train_number,
                            train_name=train.train_name,
                            train_type=train.train_type,
                        )
                        rg.num_travel_edges += 1

            prev_node_id = node_id
            prev_stop = stop

    def _create_transfer_edges(self, rg: RailwayGraph) -> None:
        """
        Create TRANSFER edges between different trains at the same station.

        For each station:
          For each arriving train (node with arrival_time):
            Find departing trains (different train) where:
              departure >= arrival + minimum_transfer_minutes
            Create edge with weight = waiting time.

        Sort departures by time for efficient lookup.
        """
        # Sort departures at each station by time
        for code in rg.station_departures:
            rg.station_departures[code].sort(key=lambda x: x[0])

        # For every node that has an arrival (i.e., is NOT the first stop)
        for node_id, meta in rg.node_meta.items():
            arr_minutes = meta.get("arrival_minutes")
            if arr_minutes is None:
                continue  # First stop — train originates, no arrival

            station_code = meta["station_code"]
            train_number = meta["train_number"]

            # Get station's minimum transfer time
            station = rg.stations.get(station_code)
            if station is None:
                continue
            min_transfer = station.minimum_transfer_minutes

            # Find valid departures at this station from DIFFERENT trains
            earliest_departure = arr_minutes + min_transfer

            for dep_minutes, dep_node_id, dep_train_number in rg.station_departures[station_code]:
                # Skip same train (you're already on it!)
                if dep_train_number == train_number:
                    continue

                # Too early — need to wait at least min_transfer minutes
                if dep_minutes < earliest_departure:
                    continue

                # Too late — cap at max layover to avoid unreasonable waits
                wait_time = dep_minutes - arr_minutes
                if wait_time > settings.DEFAULT_MAX_LAYOVER_MINUTES:
                    break  # Sorted, so all subsequent are even later

                # Valid transfer!
                rg.graph.add_edge(
                    node_id,
                    dep_node_id,
                    weight=wait_time,
                    edge_type="TRANSFER",
                    station_code=station_code,
                    station_name=station.name,
                    wait_minutes=wait_time,
                    min_transfer=min_transfer,
                )
                rg.num_transfer_edges += 1

    def _get_station_code(self, rg: RailwayGraph, stop: TrainStop) -> Optional[str]:
        """Look up station code from station_id."""
        for code, station in rg.stations.items():
            if station.id == stop.station_id:
                return code
        return None
