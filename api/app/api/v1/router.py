from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.countries import router as countries_router
from app.api.v1.endpoints.globe_data import router as globe_data_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.rankings import router as rankings_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(globe_data_router, tags=["countries"])
api_router.include_router(countries_router, tags=["countries"])
api_router.include_router(rankings_router, tags=["rankings"])
api_router.include_router(admin_router, tags=["admin"])
