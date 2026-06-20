"""Бизнес-логика профиля: просмотр своего/чужого, редактирование."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.schemas.profile import ProfileOut, ProfileUpdateIn


class ProfileService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def _to_out(self, user: User, *, is_me: bool = False) -> ProfileOut:
        return ProfileOut(
            id=user.id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            bio=user.bio,
            role=user.role,
            level=user.level,
            rank=user.rank,
            is_verified=user.is_verified,
            followers=self.users.followers_count(user.id),
            following=self.users.following_count(user.id),
            posts_count=self.users.posts_count(user.id),
            is_me=is_me,
        )

    def my_profile(self, user: User) -> ProfileOut:
        return self._to_out(user, is_me=True)

    def get_public(self, username: str) -> ProfileOut:
        user = self.users.get_by_username(username)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
        return self._to_out(user)

    def update(self, user: User, data: ProfileUpdateIn) -> ProfileOut:
        if data.username is not None and data.username != user.username:
            taken = self.users.get_by_username(data.username)
            if taken is not None and taken.id != user.id:
                raise HTTPException(status.HTTP_409_CONFLICT, "Имя пользователя занято")
            user.username = data.username
        if data.name is not None:
            user.name = data.name
        if data.bio is not None:
            user.bio = data.bio
        if data.avatar is not None:
            user.avatar = data.avatar

        self.users.add(user)
        return self._to_out(user, is_me=True)
