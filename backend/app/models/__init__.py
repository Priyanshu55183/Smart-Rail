"""
Models Package — Central Registry
==================================
Importing all models here ensures SQLAlchemy's Base.metadata
knows about every table. Without this, Base.metadata.create_all()
would miss tables whose modules weren't imported.

Usage anywhere in the app:
    from app.models import Station, Train, TrainStop, TrainRun
"""

from app.models.station import Station
from app.models.train import Train
from app.models.train_stop import TrainStop
from app.models.train_run import TrainRun, TrainRunStatus
from app.models.availability import Availability
from app.models.delay import HistoricalDelay

__all__ = [
    "Station",
    "Train",
    "TrainStop",
    "TrainRun",
    "TrainRunStatus",
    "Availability",
    "HistoricalDelay",
]
