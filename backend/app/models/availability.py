"""
Availability Model
==================
Tracks seat availability and fares for a specific train run
between two stations.

Example row:
  Train 12627 on 25-Aug-2026
  From: SBC (Bengaluru)
  To:   NDLS (New Delhi)
  Class: 3A (AC 3-Tier)
  Quota: GN (General)
  Available: 42 seats
  Fare: ₹1,850
  Status: AVAILABLE

This feeds into the Journey Scoring Engine:
- The PRICE component uses fare data to score journeys
- "Cheapest" sort option compares fares across journeys
- Future: demand prediction can forecast if seats will fill up

For MVP, availability is MOCKED with realistic fare data.
Later, an authorized data provider can supply real availability.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from app.database.postgres import Base


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Which train run (specific train + specific date)
    train_run_id = Column(Integer, ForeignKey("train_runs.id"), nullable=False)

    # Origin and destination for this availability check
    station_from_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    station_to_id = Column(Integer, ForeignKey("stations.id"), nullable=False)

    # Travel class
    # SL: Sleeper (cheapest berth class)
    # 3A: AC 3-Tier
    # 2A: AC 2-Tier
    # 1A: AC First Class (most expensive)
    # CC: Chair Car (Shatabdi/Vande Bharat)
    # 2S: Second Sitting (unreserved seated)
    travel_class = Column(String(5), nullable=False, default="SL")

    # Booking quota
    # GN: General
    # TQ: Tatkal (last-minute, higher fare)
    # LD: Ladies
    # HP: Handicapped
    quota = Column(String(5), nullable=False, default="GN")

    # Number of available seats (negative = waitlist position)
    # -5 means WL 5 (waitlisted, 5th in queue)
    available_seats = Column(Integer, nullable=False, default=0)

    # Fare in INR (₹)
    fare = Column(Float, nullable=False, default=0.0)

    # Status
    # AVAILABLE: Seats are available for booking
    # RAC: Reservation Against Cancellation (shared berth)
    # WAITLIST: No seats, queued
    # NOT_AVAILABLE: Cannot be booked
    status = Column(String(20), nullable=False, default="AVAILABLE")

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_availability_run", "train_run_id"),
        Index("ix_availability_route", "station_from_id", "station_to_id"),
        Index("ix_availability_class", "travel_class"),
    )

    def __repr__(self) -> str:
        return (
            f"<Availability run={self.train_run_id} "
            f"{self.travel_class} seats={self.available_seats} ₹{self.fare}>"
        )
