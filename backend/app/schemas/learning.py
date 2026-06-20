"""Схемы основной вкладки обучения."""
from datetime import datetime

from pydantic import BaseModel

from app.db.enums import (
    HomeworkStatus,
    LanguageLevel,
    LessonStatus,
    Rank,
    Role,
    Schedule,
    StageStatus,
)


class EntranceSubmitIn(BaseModel):
    answers: dict[str, str] = {}
    listening_answers: dict[str, str] = {}
    reading_text: str | None = None


class ExamResultOut(BaseModel):
    score: int
    level: LanguageLevel
    verdict: str


class GroupCreateIn(BaseModel):
    name: str | None = None
    schedule: Schedule


class InviteJoinIn(BaseModel):
    invite_code: str


class LessonScheduleIn(BaseModel):
    starts_at: datetime


class HomeworkSubmitIn(BaseModel):
    submission: str


class HomeworkGradeIn(BaseModel):
    grade: int
    feedback: str | None = None


class RatingIn(BaseModel):
    score: int
    review: str | None = None
    anonymous: bool = False


class GroupOut(BaseModel):
    id: int
    name: str
    level: LanguageLevel
    schedule: Schedule
    invite_code: str | None = None
    teacher_id: int | None = None
    current_section: int
    current_stage: int
    members_count: int
    is_member: bool = False


class StageOut(BaseModel):
    section: int
    stage: int
    title: str
    status: StageStatus


class LessonOut(BaseModel):
    id: int
    group_id: int
    teacher_id: int
    starts_at: datetime
    meet_link: str | None = None
    status: LessonStatus


class HomeworkOut(BaseModel):
    id: int
    group_id: int
    student_id: int
    task: str
    submission: str | None = None
    status: HomeworkStatus
    grade: int | None = None
    feedback: str | None = None


class LearningOverviewOut(BaseModel):
    role: Role
    level: LanguageLevel | None = None
    rank: Rank | None = None
    needs_entrance_test: bool
    current_group: GroupOut | None = None
    available_groups: list[GroupOut] = []
    progress: list[StageOut] = []
    lessons: list[LessonOut] = []
    homeworks: list[HomeworkOut] = []
    open_teacher_groups: list[GroupOut] = []
