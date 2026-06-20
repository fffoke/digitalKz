"""Репозиторий дуэлей."""
from sqlalchemy import func, select

from app.db.enums import DuelStatus
from app.db.models.duel import Duel
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class DuelRepository(BaseRepository[Duel]):
    model = Duel

    def my_waiting(self, user_id: int) -> Duel | None:
        """Уже стою в очереди?"""
        return self.db.scalar(
            select(Duel).where(
                Duel.player1_id == user_id, Duel.status == DuelStatus.waiting
            )
        )

    def closest_waiting_opponent(self, user_id: int, rating: int) -> Duel | None:
        """Ждущая дуэль соперника с ближайшим рейтингом."""
        return self.db.scalar(
            select(Duel)
            .join(User, Duel.player1_id == User.id)
            .where(Duel.status == DuelStatus.waiting, Duel.player1_id != user_id)
            .order_by(func.abs(User.duel_rating - rating))
            .limit(1)
        )

    def create_waiting(self, user_id: int) -> Duel:
        return self.add(Duel(player1_id=user_id, status=DuelStatus.waiting))

    def my_duels(self, user_id: int) -> list[Duel]:
        return list(
            self.db.scalars(
                select(Duel)
                .where((Duel.player1_id == user_id) | (Duel.player2_id == user_id))
                .order_by(Duel.id.desc())
            )
        )
