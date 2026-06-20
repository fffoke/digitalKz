"""Перечисления домена ТІЛДЕС."""
from enum import StrEnum


class Role(StrEnum):
    user = "user"          # базовая роль сразу после регистрации
    student = "student"    # после верификации личности
    teacher = "teacher"    # после одобрения анкеты + созвона
    admin = "admin"


class LanguageLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"


class Rank(StrEnum):
    bastauysh = "Бастауыш"
    orta = "Орта"
    jetik = "Жетік"
    sheber = "Шебер"
    ustaz = "Ұстаз"


class ModerationStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Schedule(StrEnum):
    once_week = "once_week"
    three_week = "three_week"
    intensive = "intensive"


class LessonStatus(StrEnum):
    scheduled = "scheduled"
    open = "open"          # за 6 ч до урока открыт чат/Zoom
    completed = "completed"
    cancelled = "cancelled"


class HomeworkStatus(StrEnum):
    assigned = "assigned"
    submitted = "submitted"
    graded = "graded"


class StageStatus(StrEnum):
    locked = "locked"
    current = "current"
    done = "done"


class ExamType(StrEnum):
    entrance = "entrance"   # вступительный, 25 вопросов
    level = "level"         # на повышение уровня, 20 вопросов


class DuelStatus(StrEnum):
    waiting = "waiting"     # ждёт соперника в очереди
    active = "active"       # соперник найден, оба отвечают
    finished = "finished"   # судья вынес вердикт


class NotificationType(StrEnum):
    like = "like"
    follow = "follow"
    comment = "comment"
    mention = "mention"
    repost = "repost"
    role_granted = "role_granted"        # одобрили роль ученика/преподавателя
    role_rejected = "role_rejected"      # заявку отклонили


class ReportReason(StrEnum):
    spam = "spam"
    abuse = "abuse"
    language = "language"   # не казахский язык
    other = "other"


# --- AI-собеседник ---

class TaskDifficulty(StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class TaskStatus(StrEnum):
    new = "new"
    in_progress = "in_progress"
    done = "done"


class SessionStatus(StrEnum):
    active = "active"
    finished = "finished"


class TurnRole(StrEnum):
    user = "user"   # реплика ученика (голос → расшифровка)
    ai = "ai"       # ответ собеседника
