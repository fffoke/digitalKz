"""Учебные материалы в админке: CRUD по уровням."""
from fastapi import APIRouter, Depends, status

from app.core.deps import get_admin_service, require_admin
from app.db.enums import LanguageLevel
from app.db.models.user import User
from app.schemas.admin import MaterialIn, MaterialItem
from app.services.admin import AdminService

router = APIRouter(prefix="/materials", tags=["admin:materials"])


@router.get("", response_model=list[MaterialItem])
def list_materials(
    level: LanguageLevel | None = None,
    service: AdminService = Depends(get_admin_service),
):
    return service.list_materials(level)


@router.post("", response_model=MaterialItem, status_code=status.HTTP_201_CREATED)
def create_material(
    data: MaterialIn,
    current: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return service.create_material(data, author_id=current.id)


@router.put("/{material_id}", response_model=MaterialItem)
def update_material(
    material_id: int,
    data: MaterialIn,
    service: AdminService = Depends(get_admin_service),
):
    return service.update_material(material_id, data)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int,
    service: AdminService = Depends(get_admin_service),
):
    service.delete_material(material_id)
