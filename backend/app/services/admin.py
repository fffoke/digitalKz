"""Бизнес-логика админ-панели: сводная статистика для дашборда."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.enums import ModerationStatus, Role, TaskStatus
from app.db.models.tutor import Session as TutorSession
from app.db.models.tutor import Task
from app.db.models.user import TeacherApplication, User, Verification
from app.schemas.admin import DashboardStats


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _count(self, stmt) -> int:
        return self.db.scalar(stmt) or 0

    def dashboard(self) -> DashboardStats:
        c = self._count
        return DashboardStats(
            users=c(select(func.count()).select_from(User)),
            students=c(select(func.count()).select_from(User).where(User.role == Role.student)),
            teachers=c(select(func.count()).select_from(User).where(User.role == Role.teacher)),
            pending_verifications=c(
                select(func.count()).select_from(Verification)
                .where(Verification.status == ModerationStatus.pending)
            ),
            pending_applications=c(
                select(func.count()).select_from(TeacherApplication)
                .where(TeacherApplication.status == ModerationStatus.pending)
            ),
            ai_sessions=c(select(func.count()).select_from(TutorSession)),
            tasks_done=c(
                select(func.count()).select_from(Task).where(Task.status == TaskStatus.done)
            ),
        )
