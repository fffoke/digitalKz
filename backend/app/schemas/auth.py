"""Pydantic-схемы авторизации."""
from pydantic import BaseModel, ConfigDict, EmailStr

from app.db.enums import LanguageLevel, Rank, Role


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.student


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    username: str | None = None
    role: Role
    avatar: str | None = None
    bio: str | None = None
    level: LanguageLevel | None = None
    rank: Rank | None = None
    is_verified: bool
