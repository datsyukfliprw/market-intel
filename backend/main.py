from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="Market Intel API",
    description="Backend API for the Market Intel platform.",
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Market Intel API",
        "docs": "/docs",
        "health": "/health",
    }
