"""Бизнес-логика выдачи ролей (со-владение бэк-девов).

Используется админкой при одобрении заявки: меняет роль и создаёт
уведомление role_granted, через которое фронт показывает «пуш».
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import ModerationStatus, NotificationType, Rank, Role
from app.db.models.notification import Notification
from app.db.models.user import TeacherApplication, User, Verification


def approve_verification(db: Session, verification_id: int) -> User:
    ver = db.get(Verification, verification_id)
    if ver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    ver.status = ModerationStatus.approved

    user = db.get(User, ver.user_id)
    user.role = Role.student
    user.is_verified = True
    if user.rank is None:
        user.rank = Rank.bastauysh

    db.add(Notification(user_id=user.id, type=NotificationType.role_granted))
    db.commit()
    return user


def approve_teacher(db: Session, application_id: int) -> User:
    application = db.get(TeacherApplication, application_id)
    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    application.status = ModerationStatus.approved

    user = db.get(User, application.user_id)
    user.role = Role.teacher

    db.add(Notification(user_id=user.id, type=NotificationType.role_granted))
    db.commit()
    return user


def reject(db: Session, user_id: int) -> None:
    """Отклонение заявки: роль остаётся user, прилетает уведомление."""
    db.add(Notification(user_id=user_id, type=NotificationType.role_rejected))
    db.commit()
