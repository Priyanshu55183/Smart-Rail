"""
TrainStop Model
===============
THE MOST IMPORTANT TABLE — represents one stop on a train's route.

Example: Train 12627 (Karnataka Express) route:
  Stop 1: SBC (Bengaluru) | depart 21:40 | day_offset 0
  Stop 2: JTJ (Jolarpettai) | arrive 00:15, depart 00:20 | day_offset 1
  Stop 3: RU  (Renigunta)   | arrive 03:10, depart 03:15 | day_offset 1
  Stop 4: SC  (Secunderabad) | arrive 08:50, depart 09:05 | day_offset 1
  ...
  Stop 12: NDLS (New Delhi) | arrive 05:35 | day_offset 2

How the Dijkstra algorithm uses this:
1. It reads all stops for all trains
2. Each consecutive pair of stops becomes a TRAVEL EDGE in the graph:
   (SBC, 21:40) --Train12627--> (JTJ, 00:15+1day)
3. At each station, it checks: "Are there other trains departing after I arrive?"
4. Those become TRANSFER EDGES (if layover >= minimum_transfer_time)

Why day_offset matters:
- A train departing Monday 21:40 arriving Tuesday 00:15
  → The arrival has day_offset=1 (next day)
- Without day_offset, the algorithm would think 00:15 is BEFORE 21:40
  → It would incorrectly calculate a negative travel time
"""

from sqlalchemy import Column, Integer, String, Time, ForeignKey, Index
from app.database.postgres import Base


class TrainStop(Base):
    __tablename__ = "train_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Which train this stop belongs to
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)

    # Which station this stop is at
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)

    # Position in the route (1 = first stop, 2 = second, etc.)
    # Used to determine direction and sequence of travel
    stop_sequence = Column(Integer, nullable=False)

    # Arrival time at this station (NULL for the first stop — train originates here)
    # Stored as TIME type (e.g., 08:50:00)
    arrival_time = Column(Time, nullable=True)

    # Departure time from this station (NULL for the last stop — train terminates here)
    # Stored as TIME type (e.g., 09:05:00)
    departure_time = Column(Time, nullable=True)

    # ⭐ DAY OFFSET — Critical for overnight trains
    # 0 = same day as train's journey start
    # 1 = next day
    # 2 = two days after
    #
    # Example: Train departs Day 0 at 23:00, arrives Day 1 at 06:00
    # Without this, 06:00 < 23:00 would confuse the algorithm.
    # With day_offset=1, we know it's actually +24h later.
    day_offset = Column(Integer, nullable=False, default=0)

    # How long the train halts at this station (minutes)
    # halt = departure_time - arrival_time
    # Used for display: "2 min halt" vs "15 min halt"
    halt_minutes = Column(Integer, nullable=True, default=0)

    # Distance from the source station (km)
    # Used for fare calculation and progress tracking
    distance_from_source = Column(Integer, nullable=True, default=0)

    # Platform number (for passenger info)
    platform_number = Column(String(5), nullable=True)

    # ── Indexes ───────────────────────────────────────────
    # These are CRITICAL for performance:
    # 1. (station_id) — "Find all trains stopping at Hyderabad"
    # 2. (station_id, departure_time) — "Find trains departing Hyderabad after 18:30"
    # 3. (train_id, stop_sequence) — "Get the ordered route of train 12627"
    __table_args__ = (
        Index("ix_train_stops_station", "station_id"),
        Index("ix_train_stops_station_departure", "station_id", "departure_time"),
        Index("ix_train_stops_train_sequence", "train_id", "stop_sequence"),
        Index("ix_train_stops_train_station", "train_id", "station_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<TrainStop train={self.train_id} station={self.station_id} "
            f"seq={self.stop_sequence} arr={self.arrival_time} dep={self.departure_time} "
            f"day+{self.day_offset}>"
        )
