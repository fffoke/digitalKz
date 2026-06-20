"""Модерация заявок на роли — тонкий слой над OnboardingService.

Ученик: только ИИН → approve/reject. Преподаватель: анкета + мини-собеседование
(заметка администратора) → approve/reject.
"""
from fastapi import APIRouter, Depends

from app.core.deps import get_onboarding_service
from app.schemas.admin import (
    ApproveTeacherIn,
    RejectIn,
    TeacherApplicationItem,
    VerificationItem,
)
from app.schemas.auth import UserOut
from app.services.onboarding import OnboardingService

router = APIRouter(prefix="/moderation", tags=["admin:moderation"])


# --- ученики (верификация по ИИН) ---

@router.get("/verifications", response_model=list[VerificationItem])
def list_verifications(service: OnboardingService = Depends(get_onboarding_service)):
    return service.pending_verifications()


@router.post("/verifications/{verification_id}/approve", response_model=UserOut)
def approve_verification(
    verification_id: int,
    service: OnboardingService = Depends(get_onboarding_service),
):
    return service.approve_verification(verification_id)


@router.post("/verifications/{verification_id}/reject", status_code=204)
def reject_verification(
    verification_id: int,
    service: OnboardingService = Depends(get_onboarding_service),
):
    service.reject_verification(verification_id)


# --- преподаватели (анкета + мини-собеседование) ---

@router.get("/teacher-applications", response_model=list[TeacherApplicationItem])
def list_teacher_applications(service: OnboardingService = Depends(get_onboarding_service)):
    return service.pending_teacher_applications()


@router.post("/teacher-applications/{application_id}/approve", response_model=UserOut)
def approve_teacher(
    application_id: int,
    data: ApproveTeacherIn | None = None,
    service: OnboardingService = Depends(get_onboarding_service),
):
    return service.approve_teacher(application_id, data.note if data else None)


@router.post("/teacher-applications/{application_id}/reject", status_code=204)
def reject_teacher(
    application_id: int,
    data: RejectIn | None = None,
    service: OnboardingService = Depends(get_onboarding_service),
):
    service.reject_teacher(application_id, data.note if data else None)
