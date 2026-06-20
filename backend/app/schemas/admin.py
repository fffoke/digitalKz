"""Схемы админ-панели: модерация заявок, дашборд."""
from pydantic import BaseModel

from app.db.enums import LanguageLevel


class VerificationItem(BaseModel):
    """Заявка ученика на верификацию (для списка модерации)."""
    id: int
    user_id: int
    user_name: str
    user_email: str
    iin: str


class TeacherApplicationItem(BaseModel):
    """Анкета преподавателя (для мини-собеседования)."""
    id: int
    user_id: int
    user_name: str
    user_email: str
    education: str | None = None
    experience: str | None = None
    kazakh_level: LanguageLevel | None = None
    admin_note: str | None = None


class RejectIn(BaseModel):
    note: str | None = None


class ApproveTeacherIn(BaseModel):
    note: str | None = None  # итог мини-собеседования


class DashboardStats(BaseModel):
    users: int
    students: int
    teachers: int
    pending_verifications: int
    pending_applications: int
    ai_sessions: int
    tasks_done: int


# class CreateMaterial