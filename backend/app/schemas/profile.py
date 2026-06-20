"""Схемы профиля пользователя."""
from pydantic import BaseModel

from app.db.enums import LanguageLevel, Rank, Role


class ProfileOut(BaseModel):
    id: int
    name: str
    username: str | None = None
    avatar: str | None = None
    bio: str | None = None
    role: Role
    level: LanguageLevel | None = None
    rank: Rank | None = None
    is_verified: bool
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    is_me: bool = False


class ProfileUpdateIn(BaseModel):
    name: str | None = None
    username: str | None = None
    bio: str | None = None
    avatar: str | None = None
