"""Пользователи, верификация, подписки, заявки преподавателей."""
from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.db.enums import LanguageLevel, ModerationStatus, Rank, Role


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    username: Mapped[str | None] = mapped_column(String(60), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)

    avatar: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)

    level: Mapped[LanguageLevel | None] = mapped_column(Enum(LanguageLevel))
    rank: Mapped[Rank | None] = mapped_column(Enum(Rank))

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)


class Verification(Base, TimestampMixin):
    """Верификация личности ученика: ИИН + удостоверение → модерация."""
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    iin: Mapped[str] = mapped_column(String(12))
    doc_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[ModerationStatus] = mapped_column(
        Enum(ModerationStatus), default=ModerationStatus.pending
    )


class Follow(Base, TimestampMixin):
    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class TeacherApplication(Base, TimestampMixin):
    """Анкета-резюме кандидата в преподаватели."""
    __tablename__ = "teacher_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    education: Mapped[str | None] = mapped_column(Text)
    experience: Mapped[str | None] = mapped_column(Text)
    kazakh_level: Mapped[LanguageLevel | None] = mapped_column(Enum(LanguageLevel))
    status: Mapped[ModerationStatus] = mapped_column(
        Enum(ModerationStatus), default=ModerationStatus.pending
    )
