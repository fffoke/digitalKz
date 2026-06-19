"""Контент из админки: материалы по уровням и экзамены."""
from __future__ import annotations

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.db.enums import ExamType, LanguageLevel


class Material(Base, TimestampMixin):
    """Учебный материал. Создаётся в админке, потребляется учеником."""
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[LanguageLevel] = mapped_column(Enum(LanguageLevel), index=True)
    section: Mapped[int | None] = mapped_column(Integer)
    stage: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class Exam(Base, TimestampMixin):
    """Экзамен. entrance — вступительный (25 вопросов);
    level — на повышение до target_level (20 вопросов + голос).

    questions хранит JSON-массив вопросов:
    [{ "type": "choice|voice|reading", "text": "...", "options": [...], "answer": "..." }]
    """
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ExamType] = mapped_column(Enum(ExamType), index=True)
    target_level: Mapped[LanguageLevel | None] = mapped_column(Enum(LanguageLevel))
    title: Mapped[str] = mapped_column(String(200))
    questions: Mapped[list] = mapped_column(JSON, default=list)
    voice_task: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class ExamAttempt(Base, TimestampMixin):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    # распознанная речь (whisper) + вердикт LLM
    transcript: Mapped[str | None] = mapped_column(Text)
    verdict: Mapped[str | None] = mapped_column(Text)
    result_level: Mapped[LanguageLevel | None] = mapped_column(Enum(LanguageLevel))
    score: Mapped[int | None] = mapped_column(Integer)
