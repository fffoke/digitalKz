"""Репозиторий заявок на верификацию личности (ученик)."""
from sqlalchemy import select

from app.db.enums import ModerationStatus
from app.db.models.user import Verification
from app.db.repositories.base import BaseRepository


class VerificationRepository(BaseRepository[Verification]):
    model = Verification

    def latest_for_user(self, user_id: int) -> Verification | None:
        return self.db.scalar(
            select(Verification)
            .where(Verification.user_id == user_id)
            .order_by(Verification.id.desc())
        )

    def create(self, *, user_id: int, iin: str, doc_url: str | None) -> Verification:
        return self.add(
            Verification(
                user_id=user_id,
                iin=iin,
                doc_url=doc_url,
                status=ModerationStatus.pending,
            )
        )
