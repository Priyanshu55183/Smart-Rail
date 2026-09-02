"""
SmartRail — FastAPI Application Entry Point
============================================
This is the main file. Running `uvicorn app.main:app` starts the server.

Startup sequence:
1. Create FastAPI app with metadata
2. Configure CORS for frontend communication
3. On startup: connect to PostgreSQL, Redis, create tables, load ML models
4. On shutdown: close all connections gracefully
5. Register all API routers (health, stations, trains, journeys)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.postgres import init_db, close_db
from app.database.redis import init_redis, close_redis
from app.seed.seed_loader import seed_all

# Import all models so Base.metadata knows about them
import app.models  # noqa: F401

settings = get_settings()


# ── Lifespan (Startup & Shutdown) ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on app startup and shutdown.
    
    Startup:
      - Initialize PostgreSQL connection pool
      - Create database tables (if they don't exist)
      - Initialize Redis connection
      - Load ML models into memory (when enabled)
    
    Shutdown:
      - Close all database connections
      - Close Redis connection
      - Free ML model memory
    """
    # ── STARTUP ───────────────────────────────────────
    print(f"🚂 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # 1. Database
    print("📦 Connecting to PostgreSQL...")
    await init_db()
    print("✅ PostgreSQL connected & tables created")

    # 1b. Seed data (idempotent — skips if already seeded)
    await seed_all()

    # 2. Redis
    print("🔴 Connecting to Redis...")
    try:
        await init_redis()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   App will work without caching")

    # 3. ML Models (loaded later in Phase 3)
    if settings.ML_ENABLED:
        print("🧠 ML models will be loaded when available")

    print(f"🚀 {settings.APP_NAME} is ready!")
    print(f"   Docs: http://localhost:8000/docs")

    yield  # App is running, serving requests

    # ── SHUTDOWN ──────────────────────────────────────
    print(f"🛑 Shutting down {settings.APP_NAME}...")
    await close_db()
    await close_redis()
    print("👋 Goodbye!")


# ── Create FastAPI App ────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Intelligent multi-train journey planner for Indian Railways. "
        "Uses graph algorithms, ML delay prediction, and LLM explainability "
        "to find and rank the best journeys."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ── CORS Middleware ───────────────────────────────────────
# Allows the Next.js frontend (localhost:3000) to call the API.
# Without this, browser security would block cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register API Routers ─────────────────────────────────
# Each router handles a group of related endpoints.
# They are imported here and mounted with a URL prefix.
from app.api.health import router as health_router
from app.api.stations import router as stations_router
from app.api.trains import router as trains_router
from app.api.journeys import router as journeys_router

app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(stations_router, prefix="/api/stations", tags=["Stations"])
app.include_router(trains_router, prefix="/api/trains", tags=["Trains"])
app.include_router(journeys_router, prefix="/api/journeys", tags=["Journeys"])


# ── Root Endpoint ─────────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint — confirms the API is running."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }
