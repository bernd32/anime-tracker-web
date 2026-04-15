from fastapi import APIRouter

from app.api.routes.anime import router as anime_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.import_export import router as import_export_router
from app.api.routes.preferences import router as preferences_router
from app.api.routes.years import router as years_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(anime_router, prefix="/anime", tags=["anime"])
api_router.include_router(years_router, prefix="/years", tags=["years"])
api_router.include_router(import_export_router, tags=["import-export"])
api_router.include_router(preferences_router, prefix="/preferences", tags=["preferences"])
