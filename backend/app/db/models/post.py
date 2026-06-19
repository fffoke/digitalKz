"""Лента: посты, лайки, репосты, комментарии, жалобы."""
from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.db.enums import ModerationStatus, ReportReason


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    # только казахский: пост проходит языковую модерацию
    moderation: Mapped[ModerationStatus] = mapped_column(
        Enum(ModerationStatus), default=ModerationStatus.approved
    )


class Like(Base, TimestampMixin):
    __tablename__ = "likes"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class Repost(Base, TimestampMixin):
    __tablename__ = "reposts"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)


class Report(Base, TimestampMixin):
    """Жалоба на пост или на пользователя (одно из полей заполнено)."""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"), index=True)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[ReportReason] = mapped_column(Enum(ReportReason))
    status: Mapped[ModerationStatus] = mapped_column(
        Enum(ModerationStatus), default=ModerationStatus.pending
    )
