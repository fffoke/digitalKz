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
from app.schemas.admin import TeacherApplicationItem, VerificationItem
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
        verification = Verification(
            user_id=user.id,
            iin=iin,
            doc_url=doc_url,
            status=ModerationStatus.approved,
        )
        self.db.add(verification)
        user.role = Role.student
        user.is_verified = True
        user.rank = user.rank or Rank.bastauysh
        self.db.add(user)
        self.notifications.create(user_id=user.id, type=NotificationType.role_granted)
        self.db.commit()
        self.db.refresh(verification)
        return verification

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

    def reject_verification(self, verification_id: int) -> None:
        ver = self.verifications.get(verification_id)
        if ver is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
        ver.status = ModerationStatus.rejected
        self.notifications.create(
            user_id=ver.user_id, type=NotificationType.role_rejected
        )

    def approve_teacher(self, application_id: int, note: str | None = None) -> User:
        application = self.applications.get(application_id)
        if application is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
        application.status = ModerationStatus.approved
        application.admin_note = note

        user = self.users.get(application.user_id)
        user.role = Role.teacher

        self.notifications.create(user_id=user.id, type=NotificationType.role_granted)
        return user

    def reject_teacher(self, application_id: int, note: str | None = None) -> None:
        application = self.applications.get(application_id)
        if application is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
        application.status = ModerationStatus.rejected
        application.admin_note = note
        self.notifications.create(
            user_id=application.user_id, type=NotificationType.role_rejected
        )

    # --- списки для модерации ---

    def pending_verifications(self) -> list[VerificationItem]:
        return [
            VerificationItem(
                id=v.id, user_id=u.id, user_name=u.name,
                user_email=u.email, iin=v.iin,
            )
            for v, u in self.verifications.list_pending()
        ]

    def pending_teacher_applications(self) -> list[TeacherApplicationItem]:
        return [
            TeacherApplicationItem(
                id=a.id, user_id=u.id, user_name=u.name, user_email=u.email,
                education=a.education, experience=a.experience,
                kazakh_level=a.kazakh_level, admin_note=a.admin_note,
            )
            for a, u in self.applications.list_pending()
        ]

    # --- внутреннее ---

    def _ensure_base_user(self, user: User) -> None:
        if user.role != Role.user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Роль уже назначена")
