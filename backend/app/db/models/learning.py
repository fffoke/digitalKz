"""Обучение: группы, план, уроки, оценки, домашние задания."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.db.enums import (
    HomeworkStatus,
    LanguageLevel,
    LessonStatus,
    Schedule,
    StageStatus,
)


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    level: Mapped[LanguageLevel] = mapped_column(Enum(LanguageLevel))
    schedule: Mapped[Schedule] = mapped_column(Enum(Schedule))
    invite_code: Mapped[str | None] = mapped_column(String(40), unique=True, index=True)
    # текущий преподаватель (null = группа без преподавателя)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    # текущее положение по плану
    current_section: Mapped[int] = mapped_column(Integer, default=1)
    current_stage: Mapped[int] = mapped_column(Integer, default=1)


class GroupMember(Base, TimestampMixin):
    __tablename__ = "group_members"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class Section(Base):
    """Секция плана обучения (общая для уровня)."""
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[LanguageLevel] = mapped_column(Enum(LanguageLevel))
    order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))


class Stage(Base):
    """Этап внутри секции."""
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), index=True)
    order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))


class GroupStageProgress(Base, TimestampMixin):
    """Статус этапа для конкретной группы (карта прогресса)."""
    __tablename__ = "group_stage_progress"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), primary_key=True)
    status: Mapped[StageStatus] = mapped_column(
        Enum(StageStatus), default=StageStatus.locked
    )


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    zoom_link: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[LessonStatus] = mapped_column(
        Enum(LessonStatus), default=LessonStatus.scheduled
    )


class LessonRating(Base, TimestampMixin):
    __tablename__ = "lesson_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer)  # 1..5
    review: Mapped[str | None] = mapped_column(Text)
    anonymous: Mapped[bool] = mapped_column(default=False)


class Homework(Base, TimestampMixin):
    __tablename__ = "homeworks"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    task: Mapped[str] = mapped_column(Text)
    submission: Mapped[str | None] = mapped_column(Text)
    status: Mapped[HomeworkStatus] = mapped_column(
        Enum(HomeworkStatus), default=HomeworkStatus.assigned
    )
    grade: Mapped[int | None] = mapped_column(Integer)
    feedback: Mapped[str | None] = mapped_column(Text)
    # проверяет следующий преподаватель группы
    graded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
