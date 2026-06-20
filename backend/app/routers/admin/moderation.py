"""Модерация заявок на роли — тонкий слой над OnboardingService."""
from fastapi import APIRouter, Depends

from app.core.deps import get_onboarding_service
from app.schemas.auth import UserOut
from app.services.onboarding import OnboardingService

router = APIRouter(prefix="/moderation", tags=["admin:moderation"])


@router.post("/verifications/{verification_id}/approve", response_model=UserOut)
def approve_verification(
    verification_id: int,
    service: OnboardingService = Depends(get_onboarding_service),
):
    return service.approve_verification(verification_id)


@router.post("/teacher-applications/{application_id}/approve", response_model=UserOut)
def approve_teacher(
    application_id: int,
    service: OnboardingService = Depends(get_onboarding_service),
):
    return service.approve_teacher(application_id)
