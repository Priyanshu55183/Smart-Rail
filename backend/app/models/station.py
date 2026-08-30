"""
Station Model
=============
Represents an Indian railway station.

Key fields:
- code: Unique station code (e.g., "SBC", "NDLS", "HYB")
- station_category: A1 (mega), A, B, C, D, E (small halt)
- minimum_transfer_minutes: How long a passenger needs to transfer
  at THIS specific station. Major junctions need more time.
- is_junction: Whether multiple rail lines converge here
- latitude/longitude: For map display and distance calculation

The minimum_transfer_minutes field is what makes our Dijkstra
algorithm smarter than a naive implementation — it uses
station-specific transfer times instead of a fixed value.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Index
from app.database.postgres import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Station code — the unique identifier used everywhere in Indian Railways
    # Examples: SBC (Bengaluru), NDLS (New Delhi), HWH (Howrah)
    code = Column(String(10), unique=True, nullable=False, index=True)

    # Full station name
    # Example: "KSR Bengaluru City Junction"
    name = Column(String(200), nullable=False)

    # City and State for display and search
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)

    # Railway zone (India has 18 zones)
    # Examples: SWR (South Western), NR (Northern), ER (Eastern)
    zone = Column(String(10), nullable=True)

    # Station category determines its size and facilities
    # A1: Mega stations (New Delhi, Mumbai CST, Howrah)
    # A:  Major stations (Bangalore City, Secunderabad)
    # B:  Important junctions
    # C:  Medium stations
    # D:  Small stations
    # E:  Halts (minimal infrastructure)
    station_category = Column(String(5), nullable=False, default="C")

    # GPS coordinates for map visualization
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Whether this station is a junction (multiple rail lines meet)
    # Junctions have more connecting train options
    is_junction = Column(Boolean, default=False)

    # ⭐ CRITICAL for the route algorithm:
    # Minimum transfer time at this station (in minutes).
    # The Dijkstra algorithm uses this when checking if a connection is valid:
    #   next_train_departure >= prev_train_arrival + minimum_transfer_minutes
    #
    # Small halt: 15-20 min (just walk across platform)
    # Junction: 25-30 min (need to change platform)
    # Major station: 40-45 min (long platforms, crowds)
    minimum_transfer_minutes = Column(Integer, nullable=False, default=30)

    # Number of platforms (for display purposes)
    num_platforms = Column(Integer, nullable=True)

    # ── Indexes ───────────────────────────────────────────
    # These speed up queries significantly:
    # - Searching stations by name/city (autocomplete)
    # - Looking up stations by code (joins with train_stops)
    __table_args__ = (
        Index("ix_stations_city", "city"),
        Index("ix_stations_name_lower", "name"),
        Index("ix_stations_state", "state"),
    )

    def __repr__(self) -> str:
        return f"<Station {self.code} - {self.name}>"
