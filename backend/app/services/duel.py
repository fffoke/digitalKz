"""Бизнес-логика дуэлей: матчмейкинг по рейтингу, ответы, судья, рейтинг.

MVP: судья — простая эвристика (`_score`). Позже заменим на LLM-судью,
который сравнивает расшифровки голосовых ответов (whisper) и выносит вердикт.
"""
import random

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import DuelStatus
from app.db.models.duel import Duel
from app.db.models.user import User
from app.db.repositories.duel import DuelRepository
from app.db.repositories.user import UserRepository

RATING_DELTA = 25

PROMPTS = [
    "Бүгінгі күніңізді бір сөйлеммен сипаттаңыз.",
    "«Достық» туралы сөйлем құрыңыз.",
    "Сүйікті тағамыңыз туралы айтып беріңіз.",
    "Қазақ тілін неге үйренесіз?",
    "Демалыс күніңізді қалай өткізесіз?",
    "Туған қалаңызды сипаттаңыз.",
]


class DuelService:
    def __init__(self, db: Session) -> None:
        self.duels = DuelRepository(db)
        self.users = UserRepository(db)

    def find_match(self, user: User) -> Duel:
        """Найти соперника или встать в очередь."""
        waiting = self.duels.my_waiting(user.id)
        if waiting is not None:
            return waiting  # уже ждём

        opponent_duel = self.duels.closest_waiting_opponent(user.id, user.duel_rating)
        if opponent_duel is not None:
            opponent_duel.player2_id = user.id
            opponent_duel.status = DuelStatus.active
            opponent_duel.prompt = random.choice(PROMPTS)
            return self.duels.add(opponent_duel)

        return self.duels.create_waiting(user.id)

    def get(self, duel_id: int) -> Duel:
        duel = self.duels.get(duel_id)
        if duel is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Дуэль не найдена")
        return duel

    def submit_answer(self, duel_id: int, user: User, text: str) -> Duel:
        duel = self.get(duel_id)
        if duel.status != DuelStatus.active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Дуэль не активна")

        if user.id == duel.player1_id:
            duel.answer1 = text
        elif user.id == duel.player2_id:
            duel.answer2 = text
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Вы не участник дуэли")

        if duel.answer1 and duel.answer2:
            self._finish(duel)
        else:
            self.duels.add(duel)
        return duel

    def leaderboard(self) -> list[User]:
        return self.users.top_by_duel_rating()

    def my_duels(self, user: User) -> list[Duel]:
        return self.duels.my_duels(user.id)

    # --- внутреннее ---

    def _finish(self, duel: Duel) -> None:
        duel.score1 = self._score(duel.answer1, duel.prompt)
        duel.score2 = self._score(duel.answer2, duel.prompt)
        duel.winner_id = (
            duel.player1_id if duel.score1 >= duel.score2 else duel.player2_id
        )
        duel.status = DuelStatus.finished

        loser_id = (
            duel.player2_id if duel.winner_id == duel.player1_id else duel.player1_id
        )
        winner = self.users.get(duel.winner_id)
        loser = self.users.get(loser_id)
        winner.duel_rating += RATING_DELTA
        loser.duel_rating = max(0, loser.duel_rating - RATING_DELTA)

        self.duels.add(duel)

    def _score(self, answer: str | None, prompt: str | None) -> int:
        """MVP-эвристика: длина ответа (потом — вердикт LLM)."""
        return min(len((answer or "").split()), 30)
