from .health import router as health_router
from .predictions import router as predictions_router
from .alerts import router as alerts_router
from .redistribution import router as redistribution_router
from .phcs import router as phcs_router
from .requests import router as requests_router
from .daily import router as daily_router
from .auth import router as auth_router
from .results import router as results_router

__all__ = [
    "health_router",
    "predictions_router",
    "alerts_router",
    "redistribution_router",
    "phcs_router",
    "requests_router",
    "daily_router",
    "auth_router",
    "results_router"
]
