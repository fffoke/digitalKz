"""Ручки админ-панели (дашборд, модерация, преподаватели, ученики).

Зона ответственности: бэк-дев 2.
Бизнес-логику выносим в app/services/, доступ к БД — в app/db/repositories/.
"""
from fastapi import APIRouter

from app.routers.admin import moderation

router = APIRouter()
router.include_router(moderation.router)


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "admin"}
