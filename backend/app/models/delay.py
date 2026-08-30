"""
HistoricalDelay Model
=====================
Training data for the XGBoost delay prediction model.

Each row records: "Train X at station Y on date Z was delayed by N minutes."

Example:
  Train 12627 | Station SC (Secunderabad) | 20-Aug-2026
  Scheduled arrival: 08:50
  Actual arrival:    09:12
  Delay: 22 minutes
  Cause: CONGESTION

The ML pipeline uses these records to learn patterns:
  - "Trains in Northern Railway zone are delayed more in December (fog)"
  - "Rajdhani trains recover time on long stretches"
  - "Delays cascade: if a train is 30min late at stop 5, it's usually 25min late at stop 8"
  - "Monsoon season (Jul-Sep) increases delays in Western zone by ~40%"

Pre-computed fields (day_of_week, month, is_holiday) save the ML pipeline
from having to compute these features at training time.

We generate ~50,000 of these records in seed data with realistic patterns.
"""

from sqlalchemy import Column, Integer, String, Date, Time, Float, Boolean, ForeignKey, Index
from app.database.postgres import Base


class HistoricalDelay(Base):
    __tablename__ = "historical_delays"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Which train and station
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)

    # Date of this record
    date = Column(Date, nullable=False)

    # Scheduled vs actual arrival
    scheduled_arrival = Column(Time, nullable=False)
    actual_arrival = Column(Time, nullable=True)

    # Delay in minutes (negative = arrived early, 0 = on time, positive = late)
    delay_minutes = Column(Integer, nullable=False, default=0)

    # Root cause category — helps the ML model learn cause-specific patterns
    # FOG: Winter fog in North India (Dec-Jan, NR/NCR/NER zones)
    # MONSOON: Heavy rain (Jul-Sep, WR/CR/SR zones)
    # CONGESTION: Track/platform congestion at busy junctions
    # TECHNICAL: Loco failure, signal fault, brake issue
    # OPERATIONAL: Crew change delay, rake shortage
    # CAUTION_ORDER: Speed restrictions on track
    # OTHER: Miscellaneous causes
    cause_category = Column(String(30), nullable=True, default="OTHER")

    # ── Pre-computed ML Features ──────────────────────────
    # These are stored directly so the ML training pipeline
    # doesn't need to recompute them from the date field.
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    month = Column(Integer, nullable=False)         # 1-12
    is_holiday = Column(Boolean, default=False)      # Festival/national holiday

    # ── Indexes ───────────────────────────────────────────
    # (train_id, station_id) — "All delays for train 12627 at Secunderabad"
    # (train_id) — "All delays for train 12627 (any station)"
    # (station_id) — "All delays at Secunderabad (any train)"
    # (date) — "All delays on a specific date"
    __table_args__ = (
        Index("ix_delays_train_station", "train_id", "station_id"),
        Index("ix_delays_train", "train_id"),
        Index("ix_delays_station", "station_id"),
        Index("ix_delays_date", "date"),
        Index("ix_delays_month", "month"),
    )

    def __repr__(self) -> str:
        return (
            f"<Delay train={self.train_id} station={self.station_id} "
            f"date={self.date} delay={self.delay_minutes}min>"
        )
