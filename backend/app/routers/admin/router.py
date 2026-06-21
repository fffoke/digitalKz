"""Ручки админ-панели (дашборд, модерация).

Все ручки защищены require_admin (подключается в main.py).
"""
from fastapi import APIRouter, Depends

from app.core.deps import get_admin_service
from app.routers.admin import exams, materials, moderation
from app.schemas.admin import DashboardStats
from app.services.admin import AdminService

router = APIRouter()
router.include_router(moderation.router)
router.include_router(exams.router)
router.include_router(materials.router)


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(service: AdminService = Depends(get_admin_service)) -> DashboardStats:
    return service.dashboard()


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "admin"}
