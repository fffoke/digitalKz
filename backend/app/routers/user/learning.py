"""Эндпоинты основной вкладки «Обучение»."""
import json
import os
import shutil
import tempfile
import uuid

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status

from app.core.deps import get_current_user, get_learning_service
from app.db.models.user import User
from app.schemas.learning import (
    EntranceExamOut,
    EntranceSubmitIn,
    ExamResultOut,
    GroupCreateIn,
    GroupMessageIn,
    GroupMessageOut,
    LevelExamOut,
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


@router.get("/entrance/exam", response_model=EntranceExamOut)
def entrance_exam(
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> EntranceExamOut:
    return service.entrance_exam(current)


@router.post("/entrance/submit", response_model=ExamResultOut)
def submit_entrance(
    data: EntranceSubmitIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> ExamResultOut:
    return service.submit_entrance(
        current, data.answers, data.listening_answers, data.reading_text
    )


@router.get("/level-exam", response_model=LevelExamOut)
def level_exam(
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> LevelExamOut:
    return service.level_exam(current)


@router.post("/level-exam/submit", response_model=ExamResultOut)
def submit_level_exam(
    answers: str = Form("{}"),               # JSON-строка ответов на вопросы
    audio: UploadFile | None = File(None),   # запись голосового задания
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> ExamResultOut:
    try:
        parsed = json.loads(answers or "{}")
    except json.JSONDecodeError:
        parsed = {}

    audio_path = None
    if audio is not None:
        suffix = os.path.splitext(audio.filename or "")[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(audio.file, tmp)
            audio_path = tmp.name
    try:
        return service.submit_level_exam(current, parsed, audio_path)
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


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


@router.post("/groups/{group_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_group(
    group_id: int,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> None:
    service.leave_group(current, group_id)


@router.post("/teacher/groups/{group_id}/start-lesson", response_model=LessonOut)
def start_lesson(
    group_id: int,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> LessonOut:
    return service.start_lesson(current, group_id)


# --- чат группы ---

@router.get("/groups/{group_id}/messages", response_model=list[GroupMessageOut])
def group_messages(
    group_id: int,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> list[GroupMessageOut]:
    return service.group_messages(current, group_id)


@router.post("/groups/{group_id}/messages", response_model=GroupMessageOut, status_code=status.HTTP_201_CREATED)
def post_group_message(
    group_id: int,
    data: GroupMessageIn,
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> GroupMessageOut:
    return service.post_group_message(current, group_id, data.text)


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
    request: Request,
    submission: str = Form(""),
    file: UploadFile | None = File(None),
    current: User = Depends(get_current_user),
    service: LearningService = Depends(get_learning_service),
) -> HomeworkOut:
    file_url = None
    if file is not None and file.filename:
        os.makedirs("uploads/homework", exist_ok=True)
        ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
        name = f"{uuid.uuid4().hex}{ext}"
        with open(os.path.join("uploads/homework", name), "wb") as f:
            shutil.copyfileobj(file.file, f)
        base = str(request.base_url).rstrip("/")
        file_url = f"{base}/uploads/homework/{name}"
    return service.submit_homework(current, homework_id, submission, file_url)


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
