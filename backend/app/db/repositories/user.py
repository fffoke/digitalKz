"""Репозиторий пользователей — только запросы к таблице users."""
from sqlalchemy import select

from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, *, name: str, email: str, password_hash: str) -> User:
        # роль не передаём — БД проставит Role.user по умолчанию
        return self.add(User(name=name, email=email, password_hash=password_hash))
