"""AI-собеседник: профиль обучения, задания, сессии диалога, реплики, результат.

Контекст диалога хранится здесь (в Turn), а не в LLM — перед каждым ответом
история пересобирается из БД. Поля latency_ms/audio_seconds оставлены под будущую
аналитику админки (дёшево заполнять, сразу даёт метрики).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.db.enums import SessionStatus, TaskDifficulty, TaskStatus, TurnRole


class LearningProfile(Base, TimestampMixin):
    """Ответы онбординга: зачем учит, что интересно, где пригодится.
    Из этого LLM генерит персональные задания."""
    __tablename__ = "learning_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    motivation: Mapped[str | None] = mapped_column(String(40))      # work/move/family/...
    interests: Mapped[list[str]] = mapped_column(JSON, default=list)  # темы
    contexts: Mapped[list[str]] = mapped_column(JSON, default=list)   # где пригодится
    case_text: Mapped[str | None] = mapped_column(Text)              # свободное описание кейса
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)


class Task(Base, TimestampMixin):
    """Задание-сценарий. `scenario` — системный промпт для собеседника."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    scenario: Mapped[str] = mapped_column(Text)          # роль + цель + правила для ИИ
    description: Mapped[str | None] = mapped_column(Text)     # понятная цель для пользователя
    context: Mapped[str | None] = mapped_column(String(300))  # короткий тег для карточки
    difficulty: Mapped[TaskDifficulty] = mapped_column(
        Enum(TaskDifficulty), default=TaskDifficulty.medium
    )
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.new)
    score: Mapped[int | None] = mapped_column(Integer)            # выполнение задания (task_score)
    speaking_score: Mapped[int | None] = mapped_column(Integer)  # SpeakingScore — качество речи 0..100


class Session(Base, TimestampMixin):
    """Один проход задания — диалог с ИИ."""
    __tablename__ = "tutor_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.active
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Turn(Base, TimestampMixin):
    """Реплика в диалоге. user → transcript (расшифровка голоса), ai → text."""
    __tablename__ = "turns"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("tutor_sessions.id"), index=True)
    role: Mapped[TurnRole] = mapped_column(Enum(TurnRole))
    text: Mapped[str | None] = mapped_column(Text)          # ответ ИИ
    transcript: Mapped[str | None] = mapped_column(Text)    # расшифровка реплики ученика
    audio_url: Mapped[str | None] = mapped_column(String(500))
    # под аналитику (необязательны)
    audio_seconds: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)


class Result(Base, TimestampMixin):
    """Оценка сессии от ИИ-экзаменатора."""
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("tutor_sessions.id"), unique=True, index=True
    )
    task_score: Mapped[int] = mapped_column(Integer)       # выполнение задания 0..100
    language_score: Mapped[int] = mapped_column(Integer)   # качество казахского 0..100
    feedback: Mapped[str | None] = mapped_column(Text)     # разбор
