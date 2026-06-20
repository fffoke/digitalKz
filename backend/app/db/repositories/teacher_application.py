"""Репозиторий анкет преподавателей."""
from sqlalchemy import select

from app.db.enums import LanguageLevel, ModerationStatus
from app.db.models.user import TeacherApplication
from app.db.repositories.base import BaseRepository


class TeacherApplicationRepository(BaseRepository[TeacherApplication]):
    model = TeacherApplication

    def latest_for_user(self, user_id: int) -> TeacherApplication | None:
        return self.db.scalar(
            select(TeacherApplication)
            .where(TeacherApplication.user_id == user_id)
            .order_by(TeacherApplication.id.desc())
        )

    def create(
        self,
        *,
        user_id: int,
        education: str,
        experience: str,
        kazakh_level: LanguageLevel,
    ) -> TeacherApplication:
        return self.add(
            TeacherApplication(
                user_id=user_id,
                education=education,
                experience=experience,
                kazakh_level=kazakh_level,
                status=ModerationStatus.pending,
            )
        )
