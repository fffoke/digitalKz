"""Языковые дуэли 1v1."""
from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.db.enums import DuelStatus


class Duel(Base, TimestampMixin):
    __tablename__ = "duels"

    id: Mapped[int] = mapped_column(primary_key=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    player2_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)

    prompt: Mapped[str | None] = mapped_column(Text)
    answer1: Mapped[str | None] = mapped_column(Text)
    answer2: Mapped[str | None] = mapped_column(Text)

    status: Mapped[DuelStatus] = mapped_column(
        Enum(DuelStatus), default=DuelStatus.waiting, index=True
    )
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    score1: Mapped[int | None] = mapped_column(Integer)
    score2: Mapped[int | None] = mapped_column(Integer)
