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


class GroupMessageIn(BaseModel):
    text: str


class GroupMessageOut(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    sender_avatar: str | None = None
    text: str
    created_at: datetime
    is_mine: bool = False


class EntranceQuestionOut(BaseModel):
    """Вопрос вступительного теста для ученика — без правильного ответа."""
    type: str = "choice"
    text: str
    options: list[str] = []


class EntranceExamOut(BaseModel):
    questions: list[EntranceQuestionOut] = []
    voice_task: str | None = None


class LevelExamQuestionOut(BaseModel):
    """Вопрос экзамена на уровень для ученика (без правильного ответа)."""
    type: str = "choice"
    text: str
    options: list[str] = []
    audio_url: str | None = None   # для аудирования


class LevelExamOut(BaseModel):
    target_level: LanguageLevel | None = None
    voice_task: str | None = None
    questions: list[LevelExamQuestionOut] = []
    can_take: bool = True           # доступен ли досрочно (лимит раз в 2 недели)
    next_available_at: datetime | None = None
    configured: bool = True         # создан ли админом экзамен на этот уровень


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
    teacher_name: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None   # урок длится 1 час
    meet_link: str | None = None
    status: LessonStatus
    # оценка текущего ученика (если уже оценил)
    rated: bool = False
    my_score: int | None = None
    my_review: str | None = None


class HomeworkOut(BaseModel):
    id: int
    group_id: int
    group_name: str | None = None
    student_id: int
    student_name: str | None = None
    task: str
    submission: str | None = None
    submission_file: str | None = None
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
    teacher_groups: list[GroupOut] = []      # группы, которые ведёт преподаватель
