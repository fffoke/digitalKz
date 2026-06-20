"""Схемы онбординга: статус роли, заявки, уведомления."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.enums import LanguageLevel, ModerationStatus, NotificationType, Role


class RoleStatusOut(BaseModel):
    """Что показывать во вкладке «Обучение»."""
    role: Role
    verification_status: ModerationStatus | None = None
    teacher_application_status: ModerationStatus | None = None


class TeacherApplyIn(BaseModel):
    education: str
    experience: str
    kazakh_level: LanguageLevel


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationType
    actor_id: int | None = None
    post_id: int | None = None
    is_read: bool
    created_at: datetime
