"""Эндпоинты профиля — тонкий слой над ProfileService."""
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.core.deps import get_current_user, get_profile_service
from app.db.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdateIn
from app.services.profile import ProfileService

router = APIRouter(tags=["profile"])

AVATAR_DIR = "uploads/avatars"


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


@router.post("/profile/avatar", response_model=ProfileOut)
def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    os.makedirs(AVATAR_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(AVATAR_DIR, name), "wb") as f:
        shutil.copyfileobj(file.file, f)
    # абсолютный URL по адресу, которым браузер достучался до API
    base = str(request.base_url).rstrip("/")
    url = f"{base}/uploads/avatars/{name}"
    return service.update(current, ProfileUpdateIn(avatar=url))


@router.get("/users/{username}", response_model=ProfileOut)
def public_profile(
    username: str,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.get_public(username)
