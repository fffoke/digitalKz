"""Эндпоинты основной вкладки «Обучение»."""
from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_user, get_learning_service
from app.db.models.user import User
from app.schemas.learning import (
    EntranceSubmitIn,
    ExamResultOut,
    GroupCreateIn,
    GroupOut,
    HomeworkOut,
    HomeworkGradeIn,
    HomeworkSubmitIn,
    InviteJoinIn,
    LearningOverviewOut,
    LessonOut,
    LessonScheduleIn,
    RatingIn,
)
from app.services.learning import LearningService

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/overview", response_model=LearningOverviewOut)
def overview(
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> LearningOverviewOut:
    return service.overview(current)


@router.post("/entrance/submit", response_model=ExamResultOut)
def submit_entrance(
    data: EntranceSubmitIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> ExamResultOut:
    return service.submit_entrance(
        current, data.answers, data.listening_answers, data.reading_text
    )


@router.post("/level-exam/submit", response_model=ExamResultOut)
def submit_level_exam(
    data: EntranceSubmitIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> ExamResultOut:
    return service.submit_level_exam(current, data.answers, data.reading_text)


@router.get("/groups", response_model=list[GroupOut])
def groups(
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> list[GroupOut]:
    return service.available_groups(current)


@router.post("/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
    data: GroupCreateIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> GroupOut:
    return service.create_group(current, data)


@router.post("/groups/{group_id}/join", response_model=GroupOut)
def join_group(
    group_id: int,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> GroupOut:
    return service.join_group(current, group_id)


@router.post("/groups/join-by-code", response_model=GroupOut)
def join_by_code(
    data: InviteJoinIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> GroupOut:
    return service.join_by_code(current, data.invite_code)


@router.get("/lessons", response_model=list[LessonOut])
def lessons(
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> list[LessonOut]:
    return service.lessons(current)


@router.post("/teacher/groups/{group_id}/lessons", response_model=LessonOut)
def schedule_lesson(
    group_id: int,
    data: LessonScheduleIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> LessonOut:
    return service.schedule_lesson(current, group_id, data.starts_at)


@router.post("/teacher/lessons/{lesson_id}/complete", response_model=LessonOut)
def complete_lesson(
    lesson_id: int,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> LessonOut:
    return service.complete_lesson(current, lesson_id)


@router.get("/homeworks", response_model=list[HomeworkOut])
def homeworks(
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> list[HomeworkOut]:
    return service.homeworks(current)


@router.post("/homeworks/{homework_id}/submit", response_model=HomeworkOut)
def submit_homework(
    homework_id: int,
    data: HomeworkSubmitIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> HomeworkOut:
    return service.submit_homework(current, homework_id, data.submission)


@router.post("/teacher/homeworks/{homework_id}/grade", response_model=HomeworkOut)
def grade_homework(
    homework_id: int,
    data: HomeworkGradeIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> HomeworkOut:
    return service.grade_homework(current, homework_id, data.grade, data.feedback)


@router.post("/lessons/{lesson_id}/rate", status_code=status.HTTP_204_NO_CONTENT)
def rate_lesson(
    lesson_id: int,
    data: RatingIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> None:
    service.rate_lesson(current, lesson_id, data.score, data.review, data.anonymous)
