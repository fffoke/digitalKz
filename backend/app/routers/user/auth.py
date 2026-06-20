"""Эндпоинты аутентификации — тонкий слой над AuthService."""
from fastapi import APIRouter, Depends, status

from app.core.deps import get_auth_service, get_current_user
from app.db.models.user import User
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterIn,
    service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    return TokenOut(access_token=service.register(data))


@router.post("/login", response_model=TokenOut)
def login(
    data: LoginIn,
    service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    return TokenOut(access_token=service.login(data))


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)) -> User:
    return current
