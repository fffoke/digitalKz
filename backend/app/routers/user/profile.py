"""Эндпоинты профиля — тонкий слой над ProfileService."""
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_profile_service
from app.db.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdateIn
from app.services.profile import ProfileService

router = APIRouter(tags=["profile"])


@router.get("/me/profile", response_model=ProfileOut)
def my_profile(
    current: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.my_profile(current)


@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    data: ProfileUpdateIn,
    current: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.update(current, data)


@router.get("/users/{username}", response_model=ProfileOut)
def public_profile(
    username: str,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.get_public(username)
