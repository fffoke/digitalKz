"""Назначить пользователя администратором по email.

Запуск (в контейнере backend):
    python -m app.scripts.make_admin you@example.kz
"""
import sys

from app.db.enums import Role
from app.db.repositories.user import UserRepository
from app.db.session import SessionLocal


def main() -> None:
    if len(sys.argv) < 2:
        print("Использование: python -m app.scripts.make_admin <email>")
        sys.exit(1)
    email = sys.argv[1]
    db = SessionLocal()
    try:
        user = UserRepository(db).get_by_email(email)
        if user is None:
            print(f"Пользователь {email} не найден")
            sys.exit(1)
        user.role = Role.admin
        db.commit()
        print(f"OK: {email} теперь администратор (role=admin)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
