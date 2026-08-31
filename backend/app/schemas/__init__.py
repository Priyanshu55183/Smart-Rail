"""Schemas package — Pydantic request/response models."""

from app.schemas.station import StationResponse, StationSearchResponse, StationBrief
from app.schemas.train import (
    TrainResponse, TrainStopResponse, TrainScheduleResponse,
    DirectTrainResponse, DirectTrainSearchResponse,
)
from app.schemas.journey import (
    JourneyResponse, JourneySearchRequest, JourneySearchResponse,
    JourneyScore, TrainSegment, LayoverSegment, LayoverInfo,
)

__all__ = [
    "StationResponse", "StationSearchResponse", "StationBrief",
    "TrainResponse", "TrainStopResponse", "TrainScheduleResponse",
    "DirectTrainResponse", "DirectTrainSearchResponse",
    "JourneyResponse", "JourneySearchRequest", "JourneySearchResponse",
    "JourneyScore", "TrainSegment", "LayoverSegment", "LayoverInfo",
]
