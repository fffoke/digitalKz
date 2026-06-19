"""Зависимости FastAPI: текущий пользователь, проверка ролей."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.enums import Role
from app.db.models.user import User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный токен")
    user = db.get(User, user_id)
    if user is None or user.is_banned:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь недоступен")
    return user


def require_teacher(current: User = Depends(get_current_user)) -> User:
    if current.role != Role.teacher:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только для преподавателей")
    return current
