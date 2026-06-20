"""Выбор роли во вкладке «Обучение»: верификация ученика, заявка преподавателя.

Ключевая идея: заявка НЕ блокирует пользователя. Он остаётся Role.user и спокойно
пользуется приложением (лента, профиль, директ). Когда модератор одобрит — роль
сменится и прилетит уведомление (type=role_granted) → фронт покажет «пуш».
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.enums import ModerationStatus, Role
from app.db.models.notification import Notification
from app.db.models.user import TeacherApplication, User, Verification
from app.db.session import get_db
from app.schemas.onboarding import NotificationOut, RoleStatusOut, TeacherApplyIn

router = APIRouter(tags=["onboarding"])


@router.get("/me/role-status", response_model=RoleStatusOut)
def role_status(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoleStatusOut:
    ver = db.scalar(
        select(Verification)
        .where(Verification.user_id == current.id)
        .order_by(Verification.id.desc())
    )
    app_ = db.scalar(
        select(TeacherApplication)
        .where(TeacherApplication.user_id == current.id)
        .order_by(TeacherApplication.id.desc())
    )
    return RoleStatusOut(
        role=current.role,
        verification_status=ver.status if ver else None,
        teacher_application_status=app_.status if app_ else None,
    )


@router.post("/verification", status_code=status.HTTP_201_CREATED)
def submit_verification(
    iin: str = Form(...),
    doc_photo: UploadFile | None = File(None),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Заявка стать учеником: ИИН + удостоверение → на модерацию."""
    if current.role != Role.user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Роль уже назначена")
    ver = Verification(
        user_id=current.id,
        iin=iin,
        doc_url=doc_photo.filename if doc_photo else None,
        status=ModerationStatus.pending,
    )
    db.add(ver)
    db.commit()
    return {"status": "pending"}


@router.post("/teacher/apply", status_code=status.HTTP_201_CREATED)
def teacher_apply(
    data: TeacherApplyIn,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Заявка стать преподавателем: анкета-резюме → модерация + созвон."""
    if current.role != Role.user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Роль уже назначена")
    application = TeacherApplication(
        user_id=current.id,
        education=data.education,
        experience=data.experience,
        kazakh_level=data.kazakh_level,
        status=ModerationStatus.pending,
    )
    db.add(application)
    db.commit()
    return {"status": "pending"}


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notification]:
    """Уведомления пользователя (включая role_granted — «пуш» о новой роли)."""
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == current.id)
            .order_by(Notification.id.desc())
        )
    )
