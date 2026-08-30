"""
SmartRail Configuration Module
==============================
Central configuration using Pydantic Settings.
All environment variables, thresholds, and defaults are defined here.
No hardcoded values anywhere else in the codebase.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.
    Every config value in the entire app flows through this class.
    """

    # ── App ───────────────────────────────────────────────
    APP_NAME: str = "SmartRail"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Database (PostgreSQL) ─────────────────────────────
    # asyncpg connection string for SQLAlchemy async engine
    DATABASE_URL: str = "postgresql+asyncpg://smartrail:smartrail@localhost:5432/smartrail"
    # sync connection string for Alembic migrations (alembic can't use async)
    DATABASE_URL_SYNC: str = "postgresql://smartrail:smartrail@localhost:5432/smartrail"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600  # 1 hour default cache TTL
    STATION_CACHE_TTL: int = 86400  # 24 hours (stations rarely change)
    JOURNEY_CACHE_TTL: int = 1800  # 30 minutes for journey search results

    # ── CORS ──────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ── Railway Graph Settings ────────────────────────────
    # Default minimum transfer time at a station (minutes)
    DEFAULT_MIN_TRANSFER_MINUTES: int = 30
    # Transfer times by station category
    TRANSFER_TIME_SMALL_STATION: int = 20   # Category D/E stations
    TRANSFER_TIME_JUNCTION: int = 30         # Category B/C junctions
    TRANSFER_TIME_MAJOR_STATION: int = 45    # Category A/A1 (New Delhi, Mumbai CST)

    # ── Journey Search Limits ─────────────────────────────
    MAX_CONNECTIONS_ALLOWED: int = 3
    DEFAULT_MAX_CONNECTIONS: int = 2
    DEFAULT_MIN_LAYOVER_MINUTES: int = 30
    DEFAULT_MAX_LAYOVER_MINUTES: int = 360  # 6 hours
    MAX_JOURNEYS_RETURNED: int = 20
    DIJKSTRA_TOP_K: int = 15  # Internal: how many paths Dijkstra explores

    # ── Layover Quality Thresholds (minutes) ──────────────
    # These classify how "good" a layover is
    LAYOVER_VERY_SHORT: int = 30     # < 30 min  → HIGH RISK
    LAYOVER_SHORT: int = 60          # 30-60 min → MODERATE RISK
    LAYOVER_GOOD_MIN: int = 60       # 1-3 hours → LOW RISK (ideal)
    LAYOVER_GOOD_MAX: int = 180
    LAYOVER_LONG_MAX: int = 360      # 3-6 hours → LOW RISK but inconvenient
    LAYOVER_VERY_LONG: int = 360     # > 6 hours → LONG LAYOVER

    # ── Journey Scoring Weights ───────────────────────────
    # These control how journeys are ranked (must sum to 1.0)
    SCORE_WEIGHT_TRAVEL_TIME: float = 0.35
    SCORE_WEIGHT_LAYOVER_QUALITY: float = 0.25
    SCORE_WEIGHT_RELIABILITY: float = 0.20
    SCORE_WEIGHT_PRICE: float = 0.15
    SCORE_WEIGHT_CONVENIENCE: float = 0.05

    # ── ML Model Settings ─────────────────────────────────
    ML_MODEL_DIR: str = "app/ml/models"
    DELAY_MODEL_PATH: str = "app/ml/models/delay_predictor.joblib"
    LSTM_MODEL_PATH: str = "app/ml/models/delay_propagation.pt"
    # Whether to use ML predictions (can be disabled for testing)
    ML_ENABLED: bool = True

    # ── Monte Carlo Risk Estimation ───────────────────────
    MONTE_CARLO_SIMULATIONS: int = 1000  # Number of delay scenarios to simulate

    # ── LLM (Ollama - Local) ─────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"  # Model to use for explanations
    LLM_ENABLED: bool = False  # Disabled by default, enable in Phase 2

    # ── Seed Data ─────────────────────────────────────────
    SEED_STATION_COUNT: int = 120
    SEED_TRAIN_COUNT: int = 75
    SEED_DELAY_RECORDS: int = 50000
    SEED_DAYS_OF_RUNS: int = 90

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached singleton of Settings.
    Using lru_cache means the .env file is read only once,
    and the same Settings object is reused across the entire app.
    """
    return Settings()
