"""
Time-Dependent Dijkstra Router
================================
Finds the best multi-train paths through the railway graph.

How it differs from textbook Dijkstra:
1. TIME-DEPENDENT: Edges are only usable if you arrive in time.
   You can't board a train that departed before you arrived.

2. CONNECTION-AWARE: Tracks the number of train changes.
   Stops exploring a path if it exceeds max_connections.

3. TOP-K PATHS: Finds multiple good paths, not just the single best.
   Users want options: fastest, fewest changes, safest, etc.

Algorithm:
  1. Start from all departure nodes at the SOURCE station
  2. For each node, try all outgoing edges (TRAVEL or TRANSFER)
  3. TRAVEL edges: Continue on the same train to the next stop
  4. TRANSFER edges: Switch to a different train (increment connections)
  5. When we reach the DESTINATION station, record the path
  6. Continue until we've found top_k paths or explored everything

The raw paths are converted to structured segments:
  [TrainSegment, LayoverSegment, TrainSegment, ...]
"""

from dataclasses import dataclass, field
from typing import Optional
import heapq

from app.services.graph_builder import RailwayGraph, _time_to_minutes, _minutes_to_display
from app.config import get_settings

settings = get_settings()


@dataclass
class RawPath:
    """A raw path found by Dijkstra, before scoring."""
    # List of (node_id, edge_type) pairs in order
    nodes: list[str] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    total_time_minutes: int = 0
    num_connections: int = 0
    train_segments: list[dict] = field(default_factory=list)
    layovers: list[dict] = field(default_factory=list)


class DijkstraRouter:
    """
    Finds top-K paths from source to destination using
    a modified Dijkstra algorithm on the railway graph.

    Usage:
        router = DijkstraRouter(railway_graph)
        paths = router.find_paths("SBC", "NDLS", max_connections=2, top_k=15)
    """

    def __init__(self, rg: RailwayGraph):
        self.rg = rg

    def find_paths(
        self,
        source_code: str,
        dest_code: str,
        max_connections: int = 2,
        min_layover_minutes: int = 30,
        max_layover_minutes: int = 360,
        top_k: int = 15,
        departure_after_minutes: Optional[int] = None,
    ) -> list[RawPath]:
        """
        Find the top-K paths from source to destination.

        Args:
            source_code: Source station code (e.g., "SBC")
            dest_code: Destination station code (e.g., "NDLS")
            max_connections: Maximum number of train changes
            min_layover_minutes: Minimum layover at transfer stations
            max_layover_minutes: Maximum layover at transfer stations
            top_k: How many paths to find
            departure_after_minutes: Only consider departures after this time
                                      (minutes from midnight)

        Returns:
            List of RawPath objects, sorted by total travel time.
        """
        graph = self.rg.graph
        meta = self.rg.node_meta

        # Find all starting nodes (departures from source station)
        start_nodes = []
        for dep_minutes, node_id, train_number in self.rg.station_departures.get(source_code, []):
            if departure_after_minutes is not None and dep_minutes < departure_after_minutes:
                continue
            start_nodes.append((dep_minutes, node_id))

        if not start_nodes:
            return []

        # Priority queue: (total_time, node_id, connections_used, path_nodes, path_edges, current_train)
        # Using a min-heap sorted by total_time
        pq: list[tuple] = []
        found_paths: list[RawPath] = []
        visited_states: set[tuple] = set()

        for start_time, start_node in start_nodes:
            heapq.heappush(pq, (
                0,                  # total_time (relative to this departure)
                start_time,         # absolute time
                start_node,         # current node
                0,                  # connections used
                [start_node],       # path nodes
                [],                 # path edges
                meta[start_node]["train_number"],  # current train
            ))

        while pq and len(found_paths) < top_k:
            (total_time, abs_time, current, connections,
             path_nodes, path_edges, current_train) = heapq.heappop(pq)

            # State for deduplication: (node, connections, current_train)
            # Allows visiting the same node with different connection counts
            state = (current, connections, current_train)
            if state in visited_states:
                continue
            visited_states.add(state)

            current_meta = meta.get(current)
            if current_meta is None:
                continue

            # Check if we've reached the destination
            if current_meta["station_code"] == dest_code:
                raw_path = self._build_raw_path(path_nodes, path_edges)
                if raw_path is not None:
                    found_paths.append(raw_path)
                continue

            # Explore neighbors
            for neighbor in graph.successors(current):
                edge_data = graph[current][neighbor]
                edge_type = edge_data.get("edge_type", "TRAVEL")
                edge_weight = edge_data.get("weight", 0)

                neighbor_meta = meta.get(neighbor)
                if neighbor_meta is None:
                    continue

                new_connections = connections
                if edge_type == "TRANSFER":
                    new_connections = connections + 1
                    if new_connections > max_connections:
                        continue

                    # Validate layover bounds
                    wait = edge_data.get("wait_minutes", edge_weight)
                    if wait < min_layover_minutes or wait > max_layover_minutes:
                        continue

                new_total = total_time + edge_weight
                new_abs = abs_time + edge_weight
                new_train = (
                    neighbor_meta["train_number"]
                    if edge_type == "TRANSFER"
                    else current_train
                )

                new_state = (neighbor, new_connections, new_train)
                if new_state in visited_states:
                    continue

                heapq.heappush(pq, (
                    new_total,
                    new_abs,
                    neighbor,
                    new_connections,
                    path_nodes + [neighbor],
                    path_edges + [edge_data],
                    new_train,
                ))

        # Sort by total travel time
        found_paths.sort(key=lambda p: p.total_time_minutes)
        return found_paths[:top_k]

    def _build_raw_path(
        self, nodes: list[str], edges: list[dict]
    ) -> Optional[RawPath]:
        """
        Convert a list of nodes and edges into a structured RawPath
        with train segments and layovers.
        """
        if not nodes or not edges:
            return None

        meta = self.rg.node_meta
        path = RawPath(nodes=nodes, edges=edges)

        # Walk through edges and group into segments
        current_segment_start: Optional[str] = nodes[0]
        current_train: Optional[str] = meta[nodes[0]].get("train_number")
        connections = 0

        for i, edge in enumerate(edges):
            edge_type = edge.get("edge_type", "TRAVEL")
            from_node = nodes[i]
            to_node = nodes[i + 1]

            if edge_type == "TRANSFER":
                # End the current train segment
                from_meta = meta[from_node]
                start_meta = meta[current_segment_start]

                segment = self._build_train_segment(start_meta, from_meta)
                if segment:
                    path.train_segments.append(segment)

                # Record the layover
                to_meta = meta[to_node]
                layover = self._build_layover(from_meta, to_meta, edge)
                if layover:
                    path.layovers.append(layover)

                # Start new segment
                current_segment_start = to_node
                current_train = to_meta.get("train_number")
                connections += 1

        # Final train segment (from last transfer/start to destination)
        if current_segment_start and nodes:
            last_node = nodes[-1]
            start_meta = meta[current_segment_start]
            end_meta = meta[last_node]
            segment = self._build_train_segment(start_meta, end_meta)
            if segment:
                path.train_segments.append(segment)

        # Calculate totals
        if path.train_segments:
            first_dep = path.train_segments[0].get("departure_minutes", 0)
            last_arr = path.train_segments[-1].get("arrival_minutes", 0)
            path.total_time_minutes = last_arr - first_dep if last_arr and first_dep else 0

        path.num_connections = connections
        return path

    def _build_train_segment(self, start_meta: dict, end_meta: dict) -> Optional[dict]:
        """Build a train segment dict from start and end node metadata."""
        if not start_meta or not end_meta:
            return None

        dep_minutes = start_meta.get("departure_minutes")
        arr_minutes = end_meta.get("arrival_minutes")

        # For origin stop: use departure_minutes as arrival if arrival is missing
        if arr_minutes is None:
            arr_minutes = end_meta.get("departure_minutes")
        if dep_minutes is None:
            dep_minutes = start_meta.get("arrival_minutes")

        duration = (arr_minutes - dep_minutes) if (arr_minutes and dep_minutes) else 0

        # Calculate distance
        dist_start = start_meta.get("distance_from_source", 0) or 0
        dist_end = end_meta.get("distance_from_source", 0) or 0
        distance = dist_end - dist_start if dist_end >= dist_start else None

        # Mock fare based on distance (~₹0.45/km for SL class as base)
        fare = round(distance * 1.15, 0) if distance and distance > 0 else None

        dep_time = start_meta.get("departure_time")
        arr_time = end_meta.get("arrival_time")

        return {
            "train_number": start_meta["train_number"],
            "train_name": start_meta["train_name"],
            "train_type": start_meta["train_type"],
            "from_station_code": start_meta["station_code"],
            "from_station_name": start_meta["station_name"],
            "to_station_code": end_meta["station_code"],
            "to_station_name": end_meta["station_name"],
            "departure_time": dep_time.strftime("%H:%M") if dep_time else None,
            "arrival_time": arr_time.strftime("%H:%M") if arr_time else None,
            "departure_day_offset": start_meta.get("day_offset", 0),
            "arrival_day_offset": end_meta.get("day_offset", 0),
            "duration_minutes": duration,
            "departure_minutes": dep_minutes,
            "arrival_minutes": arr_minutes,
            "distance_km": distance,
            "fare": fare,
        }

    def _build_layover(
        self, arrival_meta: dict, departure_meta: dict, edge: dict
    ) -> Optional[dict]:
        """Build a layover dict from arrival and departure metadata."""
        arr_minutes = arrival_meta.get("arrival_minutes")
        dep_minutes = departure_meta.get("departure_minutes")

        if arr_minutes is None or dep_minutes is None:
            return None

        wait_minutes = dep_minutes - arr_minutes

        # Determine risk level based on layover duration
        station_code = arrival_meta["station_code"]
        station = self.rg.stations.get(station_code)
        min_transfer = station.minimum_transfer_minutes if station else 30

        risk_level = self._assess_layover_risk(wait_minutes, min_transfer)

        arr_time = arrival_meta.get("arrival_time")
        dep_time = departure_meta.get("departure_time")

        return {
            "station_code": station_code,
            "station_name": arrival_meta["station_name"],
            "arrival_time": arr_time.strftime("%H:%M") if arr_time else None,
            "departure_time": dep_time.strftime("%H:%M") if dep_time else None,
            "arrival_day_offset": arrival_meta.get("day_offset", 0),
            "departure_day_offset": departure_meta.get("day_offset", 0),
            "duration_minutes": wait_minutes,
            "duration_display": _minutes_to_display(wait_minutes),
            "risk_level": risk_level,
            "min_transfer_minutes": min_transfer,
            "arriving_train": arrival_meta["train_number"],
            "departing_train": departure_meta["train_number"],
        }

    def _assess_layover_risk(self, wait_minutes: int, min_transfer: int) -> str:
        """
        Classify layover risk based on duration vs minimum transfer time.

        Risk levels:
          HIGH_RISK:     wait < min_transfer + 15 (very tight)
          MODERATE_RISK: wait < 60 minutes
          LOW_RISK:      60 to 180 minutes (ideal)
          LONG_LAYOVER:  > 180 minutes (safe but inconvenient)
        """
        if wait_minutes < min_transfer + 15:
            return "HIGH_RISK"
        elif wait_minutes < settings.LAYOVER_SHORT:
            return "MODERATE_RISK"
        elif wait_minutes <= settings.LAYOVER_GOOD_MAX:
            return "LOW_RISK"
        else:
            return "LONG_LAYOVER"
