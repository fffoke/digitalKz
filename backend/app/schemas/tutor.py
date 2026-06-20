"""Схемы AI-собеседника."""
from pydantic import BaseModel

from app.db.enums import SessionStatus, TaskDifficulty, TaskStatus, TurnRole


# --- онбординг интересов ---
class InterestsIn(BaseModel):
    motivation: str
    interests: list[str] = []
    contexts: list[str] = []
    case_text: str | None = None


class InterestsOut(BaseModel):
    onboarded: bool
    motivation: str | None = None
    interests: list[str] = []
    contexts: list[str] = []
    case_text: str | None = None


# --- задания ---
class CustomTaskIn(BaseModel):
    title: str | None = None
    description: str
    difficulty: TaskDifficulty = TaskDifficulty.medium


class TaskOut(BaseModel):
    id: int
    title: str
    scenario: str
    description: str | None = None
    context: str | None = None
    difficulty: TaskDifficulty
    status: TaskStatus
    score: int | None = None
    speaking_score: int | None = None

    model_config = {"from_attributes": True}


# --- сессия диалога ---
class TurnOut(BaseModel):
    id: int
    role: TurnRole
    text: str | None = None
    transcript: str | None = None
    audio_url: str | None = None

    model_config = {"from_attributes": True}


class ResultOut(BaseModel):
    task_score: int
    language_score: int
    feedback: str | None = None

    model_config = {"from_attributes": True}


class StartOut(BaseModel):
    """Ответ на старт задания: созданная сессия + первое сообщение ИИ."""
    session: "SessionOut"
    ai_text: str


class SessionOut(BaseModel):
    id: int
    task_id: int
    status: SessionStatus
    task: TaskOut
    turns: list[TurnOut] = []
    result: ResultOut | None = None


class MessageOut(BaseModel):
    """Ответ на голосовое: расшифровка + реплика ИИ + созданный turn ученика."""
    transcript: str
    ai_text: str
    turn: TurnOut


class DifficultyStat(BaseModel):
    difficulty: TaskDifficulty
    done: int
    avg_speaking: int


class StatsOut(BaseModel):
    """Статистика ученика для подвкладки в профиле."""
    total: int                 # всего заданий
    done: int                  # пройдено
    avg_speaking: int          # средний SpeakingScore
    best_speaking: int         # лучший SpeakingScore
    avg_task: int              # средний % выполнения
    by_difficulty: list[DifficultyStat] = []
