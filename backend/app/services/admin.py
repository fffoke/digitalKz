"""Бизнес-логика админ-панели: статистика, экзамены."""
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.enums import ExamType, ModerationStatus, Role, TaskStatus
from app.db.models.content import Exam, Material
from app.db.models.tutor import Session as TutorSession
from app.db.models.tutor import Task
from app.db.models.user import TeacherApplication, User, Verification
from app.schemas.admin import (
    DashboardStats,
    ExamCreateIn,
    ExamListItem,
    ExamOut,
    ExamUpdateIn,
    MaterialIn,
    MaterialItem,
)

ENTRANCE_TITLE = "Вступительный тест"


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

    # --- экзамены ---

    def _to_out(self, exam: Exam) -> ExamOut:
        return ExamOut(
            id=exam.id, title=exam.title, type=exam.type,
            target_level=exam.target_level, questions=exam.questions or [],
            voice_task=exam.voice_task,
        )

    def get_entrance_exam(self) -> ExamOut:
        """Вступительный («первый») экзамен — создаём, если ещё нет."""
        exam = self.db.scalar(select(Exam).where(Exam.type == ExamType.entrance))
        if exam is None:
            exam = Exam(
                title=ENTRANCE_TITLE,
                type=ExamType.entrance,
                target_level=None,
                questions=[],
                voice_task="Прочитайте короткий текст на казахском.",
            )
            self.db.add(exam)
            self.db.commit()
            self.db.refresh(exam)
        return self._to_out(exam)

    def update_entrance_exam(self, data: ExamUpdateIn) -> ExamOut:
        exam = self.db.scalar(select(Exam).where(Exam.type == ExamType.entrance))
        if exam is None:
            self.get_entrance_exam()
            exam = self.db.scalar(select(Exam).where(Exam.type == ExamType.entrance))
        if data.title:
            exam.title = data.title
        exam.questions = [q.model_dump() for q in data.questions]
        exam.voice_task = data.voice_task
        self.db.commit()
        self.db.refresh(exam)
        return self._to_out(exam)

    def list_exams(self) -> list[ExamListItem]:
        # только экзамены на повышение уровня (вступительный редактируется отдельно)
        exams = self.db.scalars(
            select(Exam).where(Exam.type == ExamType.level).order_by(Exam.id)
        ).all()
        return [
            ExamListItem(
                id=e.id, title=e.title, type=e.type,
                target_level=e.target_level, questions_count=len(e.questions or []),
            )
            for e in exams
        ]

    def get_exam(self, exam_id: int) -> ExamOut:
        exam = self.db.get(Exam, exam_id)
        if exam is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Экзамен не найден")
        return self._to_out(exam)

    def create_exam(self, data: ExamCreateIn) -> ExamOut:
        """Экзамен на повышение уровня (level)."""
        exam = Exam(
            title=data.title,
            type=ExamType.level,
            target_level=data.target_level,
            questions=[q.model_dump() for q in data.questions],
            voice_task=data.voice_task,
        )
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return self._to_out(exam)

    def update_exam(self, exam_id: int, data: ExamUpdateIn) -> ExamOut:
        exam = self.db.get(Exam, exam_id)
        if exam is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Экзамен не найден")
        if data.title:
            exam.title = data.title
        exam.questions = [q.model_dump() for q in data.questions]
        exam.voice_task = data.voice_task
        self.db.commit()
        self.db.refresh(exam)
        return self._to_out(exam)

    # --- материалы ---

    def _material_out(self, m: Material) -> MaterialItem:
        return MaterialItem(
            id=m.id, level=m.level, section=m.section,
            stage=m.stage, title=m.title, content=m.content,
        )

    def list_materials(self, level=None) -> list[MaterialItem]:
        stmt = select(Material).order_by(Material.level, Material.id)
        if level is not None:
            stmt = stmt.where(Material.level == level)
        return [self._material_out(m) for m in self.db.scalars(stmt).all()]

    def create_material(self, data: MaterialIn, author_id: int | None = None) -> MaterialItem:
        m = Material(
            level=data.level, section=data.section, stage=data.stage,
            title=data.title, content=data.content, author_id=author_id,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._material_out(m)

    def update_material(self, material_id: int, data: MaterialIn) -> MaterialItem:
        m = self.db.get(Material, material_id)
        if m is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Материал не найден")
        m.level = data.level
        m.section = data.section
        m.stage = data.stage
        m.title = data.title
        m.content = data.content
        self.db.commit()
        self.db.refresh(m)
        return self._material_out(m)

    def delete_material(self, material_id: int) -> None:
        m = self.db.get(Material, material_id)
        if m is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Материал не найден")
        self.db.delete(m)
        self.db.commit()
