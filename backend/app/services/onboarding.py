"""Бизнес-логика онбординга: выбор роли, верификация, выдача роли + «пуш».

Заявка не блокирует пользователя (он остаётся Role.user). При одобрении роль
меняется и создаётся уведомление role_granted → фронт показывает пуш.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import ModerationStatus, NotificationType, Rank, Role
from app.db.models.notification import Notification
from app.db.models.user import TeacherApplication, User, Verification
from app.db.repositories.notification import NotificationRepository
from app.db.repositories.teacher_application import TeacherApplicationRepository
from app.db.repositories.user import UserRepository
from app.db.repositories.verification import VerificationRepository
from app.schemas.onboarding import RoleStatusOut, TeacherApplyIn


class OnboardingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.verifications = VerificationRepository(db)
        self.applications = TeacherApplicationRepository(db)
        self.notifications = NotificationRepository(db)

    # --- пользователь ---

    def role_status(self, user: User) -> RoleStatusOut:
        ver = self.verifications.latest_for_user(user.id)
        app_ = self.applications.latest_for_user(user.id)
        return RoleStatusOut(
            role=user.role,
            verification_status=ver.status if ver else None,
            teacher_application_status=app_.status if app_ else None,
        )

    def submit_verification(
        self, user: User, iin: str, doc_url: str | None
    ) -> Verification:
        self._ensure_base_user(user)
        return self.verifications.create(user_id=user.id, iin=iin, doc_url=doc_url)

    def apply_teacher(self, user: User, data: TeacherApplyIn) -> TeacherApplication:
        self._ensure_base_user(user)
        return self.applications.create(
            user_id=user.id,
            education=data.education,
            experience=data.experience,
            kazakh_level=data.kazakh_level,
        )

    def list_notifications(
        self, user: User, filter: str = "all"
    ) -> list[Notification]:
        types = {
            "follows": [NotificationType.follow],
            "mentions": [NotificationType.mention],
        }.get(filter)
        return self.notifications.list_for_user(user.id, types)

    # --- модерация (админка) ---

    def approve_verification(self, verification_id: int) -> User:
        ver = self.verifications.get(verification_id)
        if ver is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
        ver.status = ModerationStatus.approved

        user = self.users.get(ver.user_id)
        user.role = Role.student
        user.is_verified = True
        if user.rank is None:
            user.rank = Rank.bastauysh

        self.notifications.create(user_id=user.id, type=NotificationType.role_granted)
        return user

    def approve_teacher(self, application_id: int) -> User:
        application = self.applications.get(application_id)
        if application is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
        application.status = ModerationStatus.approved

        user = self.users.get(application.user_id)
        user.role = Role.teacher

        self.notifications.create(user_id=user.id, type=NotificationType.role_granted)
        return user

    # --- внутреннее ---

    def _ensure_base_user(self, user: User) -> None:
        if user.role != Role.user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Роль уже назначена")
