"""Репозитории AI-собеседника — только запросы к БД (никакой бизнес-логики)."""
from sqlalchemy import select

from app.db.enums import SessionStatus
from app.db.models.tutor import LearningProfile, Result, Session, Task, Turn
from app.db.repositories.base import BaseRepository


class LearningProfileRepository(BaseRepository[LearningProfile]):
    model = LearningProfile

    def get_by_user(self, user_id: int) -> LearningProfile | None:
        return self.db.scalar(
            select(LearningProfile).where(LearningProfile.user_id == user_id)
        )


class TaskRepository(BaseRepository[Task]):
    model = Task

    def list_for_user(self, user_id: int) -> list[Task]:
        return list(
            self.db.scalars(
                select(Task).where(Task.user_id == user_id).order_by(Task.id.desc())
            )
        )

    def add_many(self, tasks: list[Task]) -> list[Task]:
        self.db.add_all(tasks)
        self.db.commit()
        for t in tasks:
            self.db.refresh(t)
        return tasks


class SessionRepository(BaseRepository[Session]):
    model = Session

    def list_for_task(self, task_id: int) -> list[Session]:
        return list(self.db.scalars(select(Session).where(Session.task_id == task_id)))

    def get_active_for_task(self, user_id: int, task_id: int) -> Session | None:
        """Незавершённая сессия задания — чтобы возобновить диалог, а не плодить новые."""
        return self.db.scalar(
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.task_id == task_id,
                Session.status == SessionStatus.active,
            )
            .order_by(Session.id.desc())
        )


class TurnRepository(BaseRepository[Turn]):
    model = Turn

    def list_for_session(self, session_id: int) -> list[Turn]:
        return list(
            self.db.scalars(
                select(Turn).where(Turn.session_id == session_id).order_by(Turn.id)
            )
        )


class ResultRepository(BaseRepository[Result]):
    model = Result

    def get_by_session(self, session_id: int) -> Result | None:
        return self.db.scalar(
            select(Result).where(Result.session_id == session_id)
        )
