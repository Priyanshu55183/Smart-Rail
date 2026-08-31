"""
Health Check Endpoint
=====================
GET /api/health

Returns the status of the backend and its dependencies.
Used by:
- Docker HEALTHCHECK to know if the container is healthy
- Frontend to show "API connected" / "API down"
- Monitoring tools to alert if the service is down

Checks:
1. API itself (always "ok" if this responds)
2. PostgreSQL connection (can we query the DB?)
3. Redis connection (can we ping Redis?)
4. ML models loaded (are predictions available?)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.postgres import get_db
from app.database.redis import get_redis
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Returns service health status.
    
    Response example:
    {
        "status": "healthy",
        "app": "SmartRail",
        "version": "1.0.0",
        "services": {
            "api": "ok",
            "postgres": "ok",
            "redis": "ok",
            "ml_models": "not_loaded"
        }
    }
    """
    services = {
        "api": "ok",
        "postgres": "unknown",
        "redis": "unknown",
        "ml_models": "disabled",
    }

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        services["postgres"] = "ok"
    except Exception as e:
        services["postgres"] = f"error: {str(e)[:100]}"

    # Check Redis
    try:
        redis = get_redis()
        await redis.ping()
        services["redis"] = "ok"
    except Exception:
        services["redis"] = "not_connected"

    # Check ML models
    if settings.ML_ENABLED:
        services["ml_models"] = "not_loaded"  # Updated when models load

    # Overall status
    all_ok = services["postgres"] == "ok"  # Redis is optional
    status = "healthy" if all_ok else "degraded"

    return {
        "status": status,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": services,
    }
