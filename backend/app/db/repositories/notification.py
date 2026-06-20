"""Репозиторий уведомлений."""
from sqlalchemy import select

from app.db.enums import NotificationType
from app.db.models.notification import Notification
from app.db.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    def list_for_user(
        self, user_id: int, types: list[NotificationType] | None = None
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if types:
            stmt = stmt.where(Notification.type.in_(types))
        return list(self.db.scalars(stmt.order_by(Notification.id.desc())))

    def create(self, *, user_id: int, type: NotificationType) -> Notification:
        return self.add(Notification(user_id=user_id, type=type))
