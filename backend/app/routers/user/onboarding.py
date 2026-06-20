"""Эндпоинты онбординга — тонкий слой над OnboardingService."""
from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.deps import get_current_user, get_onboarding_service
from app.db.models.user import User
from app.schemas.onboarding import NotificationOut, RoleStatusOut, TeacherApplyIn
from app.services.onboarding import OnboardingService

router = APIRouter(tags=["onboarding"])


@router.get("/me/role-status", response_model=RoleStatusOut)
def role_status(
    current: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> RoleStatusOut:
    return service.role_status(current)


@router.post("/verification", status_code=status.HTTP_201_CREATED)
def submit_verification(
    iin: str = Form(...),
    doc_photo: UploadFile | None = File(None),
    current: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> dict:
    ver = service.submit_verification(
        current, iin, doc_photo.filename if doc_photo else None
    )
    return {"status": ver.status}


@router.post("/teacher/apply", status_code=status.HTTP_201_CREATED)
def teacher_apply(
    data: TeacherApplyIn,
    current: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> dict:
    application = service.apply_teacher(current, data)
    return {"status": application.status}


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    filter: str = "all",  # all | follows | mentions
    current: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> list:
    return service.list_notifications(current, filter)
