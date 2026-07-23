from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.scan_runs import router as scan_runs_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for the Market Intel platform.",
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(scan_runs_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }
