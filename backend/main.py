"""
BRICS Smart Health & Supply Chain Resilience - FastAPI Application.
Integrates Multi-Horizon Forecasting, Network Redistribution,
PostgreSQL PHC Community Portal, and Daily Orchestration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.database import init_db
from .api import (
    health_router,
    daily_router,
    results_router,
    auth_router,
    requests_router,
    alerts_router,
    predictions_router,
    redistribution_router,
    phcs_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Operational API layer for multi-horizon demand forecasting, disease outbreak alerts, health supply chain redistribution, and PostgreSQL PHC portal.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
# Allows known frontend development URLs and supports credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all modular API routes
app.include_router(health_router)
app.include_router(daily_router)
app.include_router(results_router)
app.include_router(auth_router)
app.include_router(requests_router)
app.include_router(alerts_router)
app.include_router(predictions_router)
app.include_router(redistribution_router)
app.include_router(phcs_router)


@app.get("/", tags=["Root"])
def root_info():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "database": "PostgreSQL (connected)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
