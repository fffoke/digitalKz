"""Бизнес-логика аутентификации.

Сервис — класс, который держит внутри репозиторий и не знает про FastAPI
(кроме HTTPException для ошибок). Роутер просто вызывает его методы.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.schemas.auth import LoginIn, RegisterIn


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def register(self, data: RegisterIn) -> str:
        """Создаёт пользователя (Role.user) и возвращает JWT (автологин)."""
        if self.users.email_exists(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email уже зарегистрирован")
        user = self.users.create(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        return create_access_token(user.id)

    def login(self, data: LoginIn) -> str:
        user = self.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль"
            )
        return create_access_token(user.id)

    def authenticate(self, token: str | None) -> User:
        """Возвращает пользователя по Bearer-токену или бросает 401."""
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Не авторизован")
        user_id = decode_token(token)
        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный токен")
        user = self.users.get(user_id)
        if user is None or user.is_banned:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь недоступен")
        return user
