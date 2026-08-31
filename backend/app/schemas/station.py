"""
Station Schemas (Pydantic)
==========================
Define the shape of station-related API requests and responses.

Why Pydantic schemas separate from SQLAlchemy models?
1. Models define database structure (internal)
2. Schemas define API contract (external — what users see)

Example: The Station model has `id` (internal DB ID) but the API 
response uses `code` as the identifier. Schemas let you control
exactly what fields are exposed and how they're formatted.

Pydantic also validates input automatically:
- If someone sends latitude="hello" instead of a float → 422 error
- If a required field is missing → 422 error with field name
"""

from pydantic import BaseModel, Field
from typing import Optional


class StationResponse(BaseModel):
    """
    Schema for a single station in API responses.
    Used by: GET /api/stations/search, GET /api/stations/{code}
    """
    code: str = Field(..., description="Unique station code", example="SBC")
    name: str = Field(..., description="Full station name", example="KSR Bengaluru City Junction")
    city: str = Field(..., description="City name", example="Bengaluru")
    state: str = Field(..., description="State name", example="Karnataka")
    zone: Optional[str] = Field(None, description="Railway zone", example="SWR")
    station_category: str = Field("C", description="Category: A1, A, B, C, D, E")
    latitude: Optional[float] = Field(None, example=12.9716)
    longitude: Optional[float] = Field(None, example=77.5946)
    is_junction: bool = Field(False, description="Whether multiple rail lines converge here")
    minimum_transfer_minutes: int = Field(30, description="Min transfer time at this station")
    num_platforms: Optional[int] = Field(None, example=10)

    model_config = {"from_attributes": True}  # Allows creating from SQLAlchemy model


class StationSearchResponse(BaseModel):
    """
    Schema for station search results.
    Returns a list of matching stations.
    Used by: GET /api/stations/search?q=bang
    """
    query: str = Field(..., description="The search query that was sent")
    count: int = Field(..., description="Number of results found")
    stations: list[StationResponse] = Field(..., description="List of matching stations")


class StationBrief(BaseModel):
    """
    Minimal station info used inside journey responses.
    Only code + name — no need for full details in journey listings.
    """
    code: str
    name: str
    city: str

    model_config = {"from_attributes": True}
