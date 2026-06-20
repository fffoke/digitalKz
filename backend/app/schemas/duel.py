"""Схемы дуэлей."""
from pydantic import BaseModel

from app.db.enums import DuelStatus


class DuelOut(BaseModel):
    id: int
    status: DuelStatus
    prompt: str | None = None
    player1_id: int
    player2_id: int | None = None
    answer1: str | None = None
    answer2: str | None = None
    winner_id: int | None = None
    score1: int | None = None
    score2: int | None = None


class AnswerIn(BaseModel):
    text: str


class LeaderboardEntry(BaseModel):
    id: int
    name: str
    username: str | None = None
    avatar: str | None = None
    duel_rating: int
