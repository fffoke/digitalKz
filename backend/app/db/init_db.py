"""Быстрое создание всех таблиц для разработки (без Alembic).

Запуск:  python -m app.db.init_db

Для прода/командной работы используй миграции Alembic (alembic upgrade head).
"""
from app.db.base import Base
from app.db.session import engine
import app.db.models  # noqa: F401  регистрирует все модели в Base.metadata


def main() -> None:
    Base.metadata.create_all(engine)
    print("Таблицы созданы ✓")


if __name__ == "__main__":
    main()
