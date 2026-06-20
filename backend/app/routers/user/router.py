"""Агрегатор ручек пользовательского интерфейса (обучение, лента, группы).

Зона ответственности: бэк-дев 1.
Бизнес-логику выносим в app/services/, доступ к БД — в app/db/repositories/.
По мере готовности подключай сюда новые модули: posts, groups, exams, ...
"""
from fastapi import APIRouter

from app.routers.user import auth, onboarding

router = APIRouter()
router.include_router(auth.router)
router.include_router(onboarding.router)


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "user"}
