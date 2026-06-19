"""Ручки пользовательского интерфейса (обучение, лента, группы).

Зона ответственности: бэк-дев 1.
Бизнес-логику выносим в app/services/, доступ к БД — в app/db/repositories/.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "user"}
