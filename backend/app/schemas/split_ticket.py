"""
Split-Ticket Schemas (Pydantic)
================================
Defines models for the Break-Journey / Split-Ticket Optimizer ("Hacker Fare" Engine).
When direct journeys are Waitlisted, split-ticketing allows booking
sub-segments on the same train (or quick connections) with guaranteed
CONFIRMED seats.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SplitLeg(BaseModel):
    """Represents one leg/ticket of a split booking."""
    leg_number: int = Field(..., example=1)
    train_number: str = Field(..., example="12627")
    train_name: str = Field(..., example="Karnataka Express")
    train_type: str = Field(..., example="SUPERFAST")
    from_station_code: str = Field(..., example="SBC")
    from_station_name: str = Field(..., example="KSR Bengaluru City Junction")
    to_station_code: str = Field(..., example="BPL")
    to_station_name: str = Field(..., example="Bhopal Junction")
    departure_time: str = Field(..., example="19:20")
    arrival_time: str = Field(..., example="15:35")
    travel_class: str = Field(..., example="3A")
    status: str = Field(..., example="AVAILABLE")
    available_seats: int = Field(..., example=18)
    status_display: str = Field(..., example="AVAILABLE 18")
    confirmation_probability: float = Field(..., example=1.0)
    fare: float = Field(..., example=1140.0)
    distance_km: int = Field(..., example=1450)


class SplitTicketOption(BaseModel):
    """
    A complete split-ticket recommendation comparing direct vs split booking.
    """
    option_id: str = Field(..., example="SPLIT-SBC-NDLS-BPL-12627")
    is_same_train: bool = Field(
        True,
        description="True if both legs are on the same train (berth change only, zero layover risk)"
    )
    intermediate_station_code: str = Field(..., example="BPL")
    intermediate_station_name: str = Field(..., example="Bhopal Junction")
    travel_class: str = Field(..., example="3A")
    
    # Legs of the journey
    leg1: SplitLeg
    leg2: SplitLeg
    
    # Comparison with direct booking
    direct_status: str = Field(..., example="WAITLIST")
    direct_status_display: str = Field(..., example="WL 35")
    direct_fare: float = Field(..., example=1850.0)
    direct_confirmation_probability: float = Field(..., example=0.42)
    
    # Split metrics
    total_split_fare: float = Field(..., example=2020.0)
    fare_difference: float = Field(..., example=170.0, description="Additional cost in INR for guaranteed seat")
    overall_confirmation_probability: float = Field(..., example=1.0)
    guaranteed_confirmed: bool = Field(
        True,
        description="True if both legs have confirmed (AVAILABLE or RAC) status"
    )
    berth_action_tip: str = Field(
        ...,
        example="Stay on same train! Switch berth at Bhopal Junction (15 min halt)."
    )


class SplitTicketResponse(BaseModel):
    """Response payload for split-ticket search."""
    from_station: str
    from_station_name: str
    to_station: str
    to_station_name: str
    date: str
    travel_class: str
    direct_status_summary: str
    options_count: int
    best_option: Optional[SplitTicketOption] = None
    options: List[SplitTicketOption] = []
