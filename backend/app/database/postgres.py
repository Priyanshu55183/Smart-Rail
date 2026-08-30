"""
PostgreSQL Database Connection
==============================
Async SQLAlchemy engine + session factory.
Every database operation in the app goes through this module.

How it works:
1. create_async_engine() → Opens a connection pool to PostgreSQL
2. async_sessionmaker() → Factory that creates session objects
3. get_db() → FastAPI dependency that gives each request its own session
4. Base → Every model (Station, Train, etc.) inherits from this
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.config import get_settings

settings = get_settings()

# ── Async Engine ──────────────────────────────────────────
# This is the connection POOL to PostgreSQL.
# pool_size=20 means 20 connections are kept open and reused.
# max_overflow=10 means 10 extra connections can be created under load.
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# ── Session Factory ───────────────────────────────────────
# Each API request gets its own session (isolated transaction).
# expire_on_commit=False means objects remain usable after commit.
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model Class ─────────────────────────────────────
class Base(DeclarativeBase):
    """
    Every database model inherits from this.
    Example: class Station(Base): ...
    SQLAlchemy uses this to know which tables to create.
    """
    pass


# ── FastAPI Dependency ────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injected into FastAPI routes.
    
    Usage in a route:
        @router.get("/stations")
        async def list_stations(db: AsyncSession = Depends(get_db)):
            ...
    
    The session is automatically closed after the request finishes,
    even if an error occurs (thanks to the finally block).
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Lifecycle Helpers ─────────────────────────────────────
async def init_db() -> None:
    """
    Creates all tables defined by models that inherit from Base.
    Called once when the app starts up.
    In production, you'd use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Closes all connections in the pool.
    Called when the app shuts down.
    """
    await engine.dispose()
