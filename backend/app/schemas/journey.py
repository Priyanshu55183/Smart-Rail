"""
Journey Schemas (Pydantic)
==========================
The most important schemas — define how multi-train journeys
are represented in the API response.

A journey consists of SEGMENTS that alternate:
  [TRAIN] → [LAYOVER] → [TRAIN] → [LAYOVER] → [TRAIN]

Example: Bangalore → Hyderabad → Delhi
  Segment 1: TRAIN   (SBC → HYB via Train 12345, depart 06:30, arrive 18:20)
  Segment 2: LAYOVER (HYB, 2h 15m, 🟢 LOW RISK, 94% success probability)
  Segment 3: TRAIN   (HYB → NDLS via Train 67890, depart 20:35, arrive 08:45)

The JourneyScore breaks down the ranking:
  - travel_time_score: How fast compared to other options
  - layover_score: Quality of connections
  - reliability_score: ML-predicted delay risk
  - price_score: Cost comparison
  - convenience_score: Fewer changes = better

This is what the frontend reads to render the visual timeline.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ── Layover Risk Levels ───────────────────────────────────
class LayoverInfo(BaseModel):
    """
    Details about a layover (connection) between two trains.
    The ML risk estimator populates success_probability.
    """
    station_code: str = Field(..., example="HYB")
    station_name: str = Field(..., example="Hyderabad Deccan")

    # Previous train's arrival
    arrival_time: str = Field(..., example="18:20")
    arrival_day_offset: int = Field(0)

    # Next train's departure
    departure_time: str = Field(..., example="20:35")
    departure_day_offset: int = Field(0)

    # Layover duration
    duration_minutes: int = Field(..., example=135, description="Layover in minutes")
    duration_display: str = Field(..., example="2h 15m", description="Human-readable")

    # Risk assessment (from ML + rules)
    risk_level: str = Field(
        ..., example="LOW",
        description="HIGH_RISK, MODERATE_RISK, LOW_RISK, LONG_LAYOVER"
    )

    # ML-predicted connection success probability (0.0 to 1.0)
    # Populated by the Monte Carlo risk estimator
    success_probability: Optional[float] = Field(
        None, example=0.94,
        description="P(connection_success) from ML model"
    )

    # Minimum transfer time at this station
    min_transfer_minutes: int = Field(30, description="Station-specific minimum")


# ── Class Availability Schema ─────────────────────────────
class ClassAvailability(BaseModel):
    """Availability and fare for a specific travel class."""
    travel_class: str = Field(..., example="3A", description="SL, 3A, 2A, 1A, CC, 2S")
    class_name: str = Field(..., example="AC 3 Tier")
    fare: float = Field(..., example=1250.0)
    status: str = Field(..., example="AVAILABLE", description="AVAILABLE, RAC, WAITLIST, REGRET")
    available_seats: int = Field(..., example=24, description="Positive=available seats, negative/number=WL")
    status_display: str = Field(..., example="AVAILABLE 24", description="Formatted status: AVAILABLE 24, WL 12, RAC 6")
    confirmation_probability: Optional[float] = Field(None, example=0.88, description="0.0 to 1.0 for WL/RAC")


# ── Journey Segment (Train or Layover) ────────────────────
class TrainSegment(BaseModel):
    """A train ride portion of the journey."""
    segment_type: Literal["TRAIN"] = "TRAIN"

    train_number: str = Field(..., example="12345")
    train_name: str = Field(..., example="Karnataka Express")
    train_type: str = Field(..., example="SUPERFAST")

    from_station_code: str = Field(..., example="SBC")
    from_station_name: str = Field(..., example="KSR Bengaluru City Junction")
    to_station_code: str = Field(..., example="HYB")
    to_station_name: str = Field(..., example="Hyderabad Deccan")

    departure_time: str = Field(..., example="06:30")
    arrival_time: str = Field(..., example="18:20")

    departure_day_offset: int = Field(0)
    arrival_day_offset: int = Field(0)

    duration_minutes: int = Field(..., example=710)
    distance_km: Optional[int] = Field(None, example=785)

    # Fare for this segment
    fare: Optional[float] = Field(None, example=850.0)

    # ML delay prediction for arrival at destination
    predicted_delay_minutes: Optional[int] = Field(
        None, example=12,
        description="XGBoost-predicted delay at arrival station"
    )

    # Class-wise Seat Availability & Waitlist status
    availabilities: list[ClassAvailability] = Field(default_factory=list)


class LayoverSegment(BaseModel):
    """A layover (waiting) portion of the journey."""
    segment_type: Literal["LAYOVER"] = "LAYOVER"
    layover: LayoverInfo


# ── Journey Score Breakdown ───────────────────────────────
class JourneyScore(BaseModel):
    """
    Multi-criteria score breakdown.
    Each dimension is 0-100, composite is a weighted average.
    
    This is what makes SmartRail smarter than a simple train search:
    it doesn't just find routes — it RANKS them intelligently.
    """
    composite: float = Field(..., example=87.5, description="Overall score 0-100")
    travel_time_score: float = Field(..., example=82.0)
    layover_score: float = Field(..., example=90.0)
    reliability_score: float = Field(..., example=94.0)
    price_score: float = Field(..., example=78.0)
    convenience_score: float = Field(..., example=85.0)


# ── Complete Journey ──────────────────────────────────────
class JourneyResponse(BaseModel):
    """
    A complete multi-train journey.
    This is the main response object that the frontend renders.
    
    Contains:
    - Segments: alternating TRAIN and LAYOVER pieces
    - Score: multi-criteria ranking breakdown
    - Summary stats: total time, connections, price, risk
    """
    journey_id: str = Field(..., example="J-SBC-NDLS-001")

    # Summary
    total_duration_minutes: int = Field(..., example=1575)
    total_duration_display: str = Field(..., example="26h 15m")
    total_layover_minutes: int = Field(..., example=135)
    num_connections: int = Field(..., example=1)
    total_fare: Optional[float] = Field(None, example=2350.0)

    # Overall risk (worst risk among all connections)
    overall_risk: str = Field(..., example="LOW")
    overall_success_probability: Optional[float] = Field(None, example=0.94)

    # Ranking
    score: JourneyScore

    # Tags for smart recommendations
    # ["BEST_OVERALL", "FASTEST", "CHEAPEST", "SAFEST", "FEWEST_CHANGES"]
    tags: list[str] = Field(default_factory=list)

    # The journey itself — alternating TRAIN and LAYOVER segments
    segments: list[TrainSegment | LayoverSegment]

    # Source and destination for display
    from_station: str = Field(..., example="SBC")
    from_station_name: str = Field(..., example="KSR Bengaluru City Junction")
    to_station: str = Field(..., example="NDLS")
    to_station_name: str = Field(..., example="New Delhi")
    date: str = Field(..., example="2026-08-25")


# ── Search Request ────────────────────────────────────────
class JourneySearchRequest(BaseModel):
    """
    Parameters for the journey search endpoint.
    GET /api/journeys?from=SBC&to=NDLS&date=2026-08-25&max_connections=2
    """
    from_station: str = Field(..., description="Source station code")
    to_station: str = Field(..., description="Destination station code")
    date: str = Field(..., description="Journey date YYYY-MM-DD")
    departure_time: Optional[str] = Field(None, description="Earliest departure HH:MM")
    max_connections: int = Field(2, ge=0, le=3, description="Max number of train changes")
    min_layover_minutes: int = Field(30, ge=15, description="Minimum layover time")
    max_layover_minutes: int = Field(360, le=720, description="Maximum layover time")
    sort_by: str = Field("best", description="best|fastest|cheapest|safest|fewest_changes")


class JourneySearchResponse(BaseModel):
    """
    Full search response with direct trains + connecting journeys.
    """
    query: JourneySearchRequest
    direct_trains_count: int
    connecting_journeys_count: int

    # Smart recommendations
    best_overall: Optional[JourneyResponse] = None
    fastest: Optional[JourneyResponse] = None
    cheapest: Optional[JourneyResponse] = None
    safest: Optional[JourneyResponse] = None

    # All results
    journeys: list[JourneyResponse]
