"""Зависимости FastAPI: сборка сервисов, текущий пользователь, проверка ролей.

Здесь связываем слои: get_db → Service(db) → роутер получает готовый сервис.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.enums import Role
from app.db.models.user import User
from app.db.session import get_db
from app.services.auth import AuthService
from app.services.duel import DuelService
from app.services.onboarding import OnboardingService
from app.services.profile import ProfileService
from app.services.tutor import TutorService

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_onboarding_service(db: Session = Depends(get_db)) -> OnboardingService:
    return OnboardingService(db)


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


def get_duel_service(db: Session = Depends(get_db)) -> DuelService:
    return DuelService(db)


def get_tutor_service(db: Session = Depends(get_db)) -> TutorService:
    return TutorService(db)


def get_learning_service(db: Session = Depends(get_db)) -> "LearningService":
    from app.services.learning import LearningService
    return LearningService(db)


def get_admin_service(db: Session = Depends(get_db)) -> "AdminService":
    from app.services.admin import AdminService
    return AdminService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
) -> User:
    token = credentials.credentials if credentials else None
    return service.authenticate(token)


def require_teacher(current: User = Depends(get_current_user)) -> User:
    if current.role != Role.teacher:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только для преподавателей")
    return current


def require_admin(current: User = Depends(get_current_user)) -> User:
    if current.role != Role.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только для администраторов")
    return current
