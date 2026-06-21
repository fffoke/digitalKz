"""Схемы админ-панели: модерация заявок, дашборд, экзамены."""
from pydantic import BaseModel

from app.db.enums import ExamType, LanguageLevel


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


# --- экзамены ---

class ExamQuestion(BaseModel):
    """Вопрос экзамена. type: choice (варианты) | listening (аудио→текст) | reading."""
    type: str = "choice"
    text: str
    options: list[str] = []
    answer: str | None = None
    audio_url: str | None = None   # для listening: что слушает ученик


class ExamOut(BaseModel):
    id: int
    title: str
    type: ExamType
    target_level: LanguageLevel | None = None
    questions: list[ExamQuestion] = []
    voice_task: str | None = None


class ExamListItem(BaseModel):
    id: int
    title: str
    type: ExamType
    target_level: LanguageLevel | None = None
    questions_count: int


class ExamUpdateIn(BaseModel):
    title: str | None = None
    questions: list[ExamQuestion] = []
    voice_task: str | None = None


class ExamCreateIn(BaseModel):
    title: str
    target_level: LanguageLevel | None = None
    questions: list[ExamQuestion] = []
    voice_task: str | None = None


# --- материалы ---

class MaterialIn(BaseModel):
    level: LanguageLevel
    section: int | None = None
    stage: int | None = None
    title: str
    content: str


class MaterialItem(BaseModel):
    id: int
    level: LanguageLevel
    section: int | None = None
    stage: int | None = None
    title: str
    content: str