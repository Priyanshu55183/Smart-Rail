"""
Train Model
===========
Represents a train service in Indian Railways.

Key fields:
- train_number: Unique 5-digit code (e.g., "12627" for Karnataka Express)
- train_type: RAJDHANI, SHATABDI, DURONTO, EXPRESS, MAIL, PASSENGER, VANDE_BHARAT
  → Used as a feature in ML delay prediction (premium trains = fewer delays)
- runs_on_days: "Mon,Tue,Wed,Thu,Fri,Sat,Sun" — which days the train operates
  → The Dijkstra algorithm checks this to only consider trains running on the search date
- source/destination station: The train's full route endpoints

The train_type is especially important for the XGBoost delay predictor.
In our training data, we'll see patterns like:
- RAJDHANI: avg delay ~8 min (priority trains, fewer stops)
- MAIL/EXPRESS: avg delay ~25 min (more stops, lower priority)
- PASSENGER: avg delay ~40 min (stops at every station)
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from app.database.postgres import Base


class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Unique 5-digit train number (e.g., "12627")
    train_number = Column(String(10), unique=True, nullable=False, index=True)

    # Full train name (e.g., "Karnataka Express")
    train_name = Column(String(200), nullable=False)

    # Train type — affects delay prediction and user preference
    # RAJDHANI: Premium, Delhi-centric, fully AC
    # SHATABDI: Day trains, chair car, fast
    # DURONTO: Non-stop between major cities
    # VANDE_BHARAT: Modern semi-high-speed
    # SUPERFAST: Avg speed > 55 km/h, surcharge applies
    # EXPRESS: Standard express trains
    # MAIL: Older classification, similar to express
    # PASSENGER: Slow, stops everywhere
    train_type = Column(String(30), nullable=False, default="EXPRESS")

    # Which days the train runs
    # Format: "Mon,Tue,Wed,Thu,Fri,Sat,Sun" for daily
    # Or: "Mon,Wed,Fri" for specific days
    runs_on_days = Column(String(50), nullable=False, default="Mon,Tue,Wed,Thu,Fri,Sat,Sun")

    # Source and destination station IDs (the train's full route endpoints)
    source_station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    destination_station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)

    # Total distance of the route in km
    total_distance_km = Column(Float, nullable=True)

    # Average speed (used for rough ETA calculations)
    avg_speed_kmph = Column(Float, nullable=True)

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_trains_type", "train_type"),
        Index("ix_trains_source", "source_station_id"),
        Index("ix_trains_destination", "destination_station_id"),
    )

    def runs_on(self, day_name: str) -> bool:
        """
        Check if train runs on a given day.
        day_name should be like 'Mon', 'Tue', etc.
        """
        return day_name in self.runs_on_days.split(",")

    def __repr__(self) -> str:
        return f"<Train {self.train_number} - {self.train_name}>"
