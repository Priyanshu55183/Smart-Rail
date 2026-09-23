"""
PostgreSQL / Supabase Database Connection
==========================================
Async SQLAlchemy engine + session factory.
Supports both local PostgreSQL and hosted Supabase instances (direct & pooler).

Key Features for Supabase:
1. URL Normalization: Converts `postgresql://` or `postgres://` to `postgresql+asyncpg://`
2. SSL Handling: Removes `sslmode=require` query param (which asyncpg rejects) and
   supplies `connect_args={"ssl": "require"}` for Supabase/remote cloud DBs
3. Pooler Compatibility: Disables prepared statement caching (`statement_cache_size=0`)
   when connecting via Supabase transaction pooler (port 6543)
4. Fallback Compatibility: Local development with standard PostgreSQL remains 100% seamless
"""

import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import AsyncGenerator, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger("smartrail.database")
settings = get_settings()


def parse_and_configure_database_url(raw_url: str) -> Tuple[str, Dict[str, Any], str, bool]:
    """
    Normalizes a database URL and prepares driver-specific connect_args.
    
    Handles:
    - Scheme translation (postgresql:// -> postgresql+asyncpg://)
    - Query parameter cleaning (e.g. stripping 'sslmode' which asyncpg doesn't accept)
    - SSL auto-detection for Supabase and remote cloud hosts
    - Transaction pooler detection (Supabase port 6543) to disable statement caching
    
    Returns:
        (cleaned_url, connect_args, host, use_ssl)
    """
    parsed = urlparse(raw_url)
    scheme = parsed.scheme or "postgresql"

    # Async engine requires an asyncpg driver scheme
    if scheme in ("postgresql", "postgres"):
        scheme = "postgresql+asyncpg"
    elif "postgresql" in scheme and not scheme.startswith("postgresql+asyncpg"):
        scheme = "postgresql+asyncpg"

    # Parse query parameters
    query_params = parse_qs(parsed.query)

    # asyncpg expects 'ssl' rather than 'sslmode'. If user pastes '?sslmode=require'
    # from Supabase dashboard, strip it from query string so asyncpg doesn't error.
    sslmode_vals = query_params.pop("sslmode", None)
    sslmode_val = sslmode_vals[0].lower() if sslmode_vals else None

    # Clean query string
    new_query = urlencode(query_params, doseq=True)
    clean_url = urlunparse((
        scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))

    # Determine SSL requirement
    host = (parsed.hostname or "").lower()
    is_local = host in (
        "localhost",
        "127.0.0.1",
        "postgres",
        "0.0.0.0",
        "host.docker.internal",
    ) or host.endswith(".local")

    connect_args: Dict[str, Any] = {}

    if settings.DB_SSL_REQUIRE is True:
        use_ssl = True
    elif settings.DB_SSL_REQUIRE is False:
        use_ssl = False
    elif sslmode_val in ("require", "verify-ca", "verify-full"):
        use_ssl = True
    elif "ssl" in query_params and query_params["ssl"][0].lower() in ("true", "require", "1"):
        use_ssl = True
    else:
        # Cloud/Supabase hosts need SSL; local Docker/localhost does not
        use_ssl = (not is_local) and bool(host)

    if use_ssl:
        connect_args["ssl"] = "require"

    # Handle prepared statements with connection poolers
    # Supabase port 6543 (transaction pooler) requires statement_cache_size=0
    if settings.DB_STATEMENT_CACHE_SIZE is not None:
        connect_args["statement_cache_size"] = settings.DB_STATEMENT_CACHE_SIZE
    elif parsed.port == 6543 or "pooler.supabase.com" in host:
        connect_args["statement_cache_size"] = 0

    return clean_url, connect_args, host, use_ssl


def get_sync_database_url() -> str:
    """
    Returns a sync PostgreSQL connection string (for Alembic or sync scripts).
    If DATABASE_URL_SYNC is provided in settings, returns that.
    Otherwise, converts DATABASE_URL from postgresql+asyncpg:// to postgresql://.
    """
    if settings.DATABASE_URL_SYNC:
        return settings.DATABASE_URL_SYNC

    parsed = urlparse(settings.DATABASE_URL)
    scheme = "postgresql"
    return urlunparse((
        scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))


# Configure database connection
CLEAN_DATABASE_URL, CONNECT_ARGS, DB_HOST, DB_USES_SSL = parse_and_configure_database_url(
    settings.DATABASE_URL
)

# ── Async Engine ──────────────────────────────────────────
# Connection POOL to PostgreSQL / Supabase.
engine: AsyncEngine = create_async_engine(
    CLEAN_DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    connect_args=CONNECT_ARGS,
)

# ── Session Factory ───────────────────────────────────────
# Each API request gets its own session (isolated transaction).
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
    """
    masked_host = DB_HOST if DB_HOST else "configured-host"
    ssl_label = "SSL: required" if DB_USES_SSL else "SSL: disabled"
    print(f"📦 Connecting to Database at '{masked_host}' ({ssl_label})...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database connected & tables verified/created successfully.")
    except Exception as exc:
        print(f"❌ Database connection failed: {exc}")
        if "supabase.co" in DB_HOST or "pooler.supabase.com" in DB_HOST:
            print("💡 Supabase Troubleshooting Tip:")
            print("   1. Verify your database password in .env (if it has special chars like @, %, encode them).")
            print("   2. Check that your Supabase project is active (not paused).")
            print("   3. Ensure you are using the Session Pooler (port 5432) or Transaction Pooler (port 6543).")
        raise


async def close_db() -> None:
    """
    Closes all connections in the pool.
    Called when the app shuts down.
    """
    await engine.dispose()
