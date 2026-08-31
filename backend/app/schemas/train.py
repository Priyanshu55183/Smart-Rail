"""
Train Schemas (Pydantic)
========================
Define API request/response shapes for trains and schedules.

Key schemas:
- TrainResponse: Basic train info (number, name, type)
- TrainStopResponse: One stop in a train's schedule (arrival, departure, day_offset)
- TrainScheduleResponse: Full schedule = train info + all stops
- DirectTrainResponse: Direct train search result = train + from/to stops + fare
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import time


class TrainResponse(BaseModel):
    """Basic train information."""
    train_number: str = Field(..., example="12627")
    train_name: str = Field(..., example="Karnataka Express")
    train_type: str = Field(..., example="SUPERFAST")
    runs_on_days: str = Field(..., example="Mon,Tue,Wed,Thu,Fri,Sat,Sun")
    total_distance_km: Optional[float] = Field(None, example=2444)
    avg_speed_kmph: Optional[float] = Field(None, example=55.2)

    model_config = {"from_attributes": True}


class TrainStopResponse(BaseModel):
    """
    One stop in a train's schedule.
    This is what users see when they view a full train route.
    """
    station_code: str = Field(..., example="SC")
    station_name: str = Field(..., example="Secunderabad Junction")
    stop_sequence: int = Field(..., example=5)
    arrival_time: Optional[str] = Field(None, example="08:50")
    departure_time: Optional[str] = Field(None, example="09:05")
    day_offset: int = Field(0, description="0=same day, 1=next day, 2=day after")
    halt_minutes: Optional[int] = Field(None, example=15)
    distance_from_source: Optional[int] = Field(None, example=785)
    platform_number: Optional[str] = Field(None, example="1")


class TrainScheduleResponse(BaseModel):
    """
    Full schedule of a train — train details + every stop in order.
    Used by: GET /api/trains/{train_number}/schedule
    """
    train: TrainResponse
    stops: list[TrainStopResponse]
    total_stops: int


class DirectTrainResponse(BaseModel):
    """
    A single direct train between two stations.
    Used by: GET /api/trains/direct?from=SBC&to=NDLS&date=2026-08-25

    Combines:
    - Train info (number, name, type)
    - Departure from source station
    - Arrival at destination station  
    - Duration in minutes
    - Day offset (how many days the journey takes)
    - Fare (mocked for MVP)
    """
    train_number: str
    train_name: str
    train_type: str

    from_station: str  # station code
    to_station: str    # station code

    departure_time: str  # "21:40"
    arrival_time: str    # "05:35"

    departure_day_offset: int = 0
    arrival_day_offset: int = 0

    duration_minutes: int  # Total travel time in minutes
    distance_km: Optional[int] = None

    # Fare info (per class)
    fare_sleeper: Optional[float] = None
    fare_3ac: Optional[float] = None
    fare_2ac: Optional[float] = None

    status: str = "SCHEDULED"  # From TrainRun


class DirectTrainSearchResponse(BaseModel):
    """
    Response for direct train search.
    Used by: GET /api/trains/direct
    """
    from_station: str
    to_station: str
    date: str
    count: int
    trains: list[DirectTrainResponse]
