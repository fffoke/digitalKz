"""Модерация заявок на роли (выдаёт роль + триггерит уведомление-«пуш»)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserOut
from app.services import onboarding

router = APIRouter(prefix="/moderation", tags=["admin:moderation"])


@router.post("/verifications/{verification_id}/approve", response_model=UserOut)
def approve_verification(verification_id: int, db: Session = Depends(get_db)):
    return onboarding.approve_verification(db, verification_id)


@router.post("/teacher-applications/{application_id}/approve", response_model=UserOut)
def approve_teacher(application_id: int, db: Session = Depends(get_db)):
    return onboarding.approve_teacher(db, application_id)
