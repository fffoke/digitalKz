"""Репозиторий пользователей — только запросы к таблице users."""
from sqlalchemy import func, select

from app.db.models.post import Post
from app.db.models.user import Follow, User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, *, name: str, email: str, password_hash: str) -> User:
        # роль не передаём — БД проставит Role.user по умолчанию
        return self.add(User(name=name, email=email, password_hash=password_hash))

    # --- счётчики для профиля ---

    def followers_count(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
        ) or 0

    def following_count(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        ) or 0

    def posts_count(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Post).where(Post.author_id == user_id)
        ) or 0
