"""
TrainRun Model
==============
A specific instance of a train running on a specific date.

Difference between Train and TrainRun:
- Train: "12627 Karnataka Express" (the concept, the schedule)
- TrainRun: "12627 running on 25-Aug-2026" (a specific day's run)

Why separate?
- A train can be CANCELLED on specific dates (festivals, maintenance)
- Special trains run only on certain dates
- We track status per day: is it running? was it cancelled? diverted?

The Dijkstra algorithm checks train_runs to:
1. Only consider trains actually running on the search date
2. Skip cancelled trains
3. Handle special/holiday trains
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Index, Enum
from app.database.postgres import Base
import enum


class TrainRunStatus(str, enum.Enum):
    """Status of a specific train run on a specific date."""
    SCHEDULED = "SCHEDULED"   # Normal — the train is planned to run
    RUNNING = "RUNNING"       # Currently in progress
    COMPLETED = "COMPLETED"   # Finished its journey
    CANCELLED = "CANCELLED"   # Not running today (weather, maintenance, etc.)
    DIVERTED = "DIVERTED"     # Running but on a different route
    SPECIAL = "SPECIAL"       # Special/festival train not in regular schedule


class TrainRun(Base):
    __tablename__ = "train_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Which train this run belongs to
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)

    # The date this train departs from its source station
    journey_date = Column(Date, nullable=False)

    # Current status of this specific run
    status = Column(
        String(20),
        nullable=False,
        default=TrainRunStatus.SCHEDULED.value,
    )

    # ── Indexes ───────────────────────────────────────────
    # (journey_date) — "Find all trains running on Aug 25"
    # (train_id, journey_date) — "Is train 12627 running on Aug 25?"
    __table_args__ = (
        Index("ix_train_runs_date", "journey_date"),
        Index("ix_train_runs_train_date", "train_id", "journey_date", unique=True),
    )

    def __repr__(self) -> str:
        return f"<TrainRun train={self.train_id} date={self.journey_date} status={self.status}>"
