"""Эндпоинты AI-собеседника — тонкий слой над TutorService."""
from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.core.deps import get_current_user, get_tutor_service
from app.db.models.user import User
from app.schemas.tutor import (
    CustomTaskIn,
    InterestsIn,
    InterestsOut,
    MessageOut,
    ResultOut,
    SessionOut,
    StartOut,
    StatsOut,
    TaskOut,
)
from app.services.tutor import TutorService

router = APIRouter(tags=["tutor"])


# --- онбординг интересов ---

@router.get("/me/interests", response_model=InterestsOut)
def get_interests(
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> InterestsOut:
    return service.get_interests(current)


@router.post("/me/interests", response_model=InterestsOut)
def save_interests(
    data: InterestsIn,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> InterestsOut:
    return service.save_interests(current, data)


@router.get("/me/stats", response_model=StatsOut)
def my_stats(
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> StatsOut:
    return service.stats(current)


# --- задания ---

@router.post("/tasks/generate", response_model=list[TaskOut])
def generate_tasks(
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> list[TaskOut]:
    return service.generate_tasks(current)


@router.post("/tasks/custom", response_model=TaskOut)
def create_custom_task(
    data: CustomTaskIn,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> TaskOut:
    return service.create_custom_task(current, data)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> list[TaskOut]:
    return service.list_tasks(current)


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> TaskOut:
    return service.get_task(current, task_id)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> None:
    service.delete_task(current, task_id)


# --- сессия диалога ---

@router.post("/tasks/{task_id}/start", response_model=StartOut)
def start_task(
    task_id: int,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> StartOut:
    session, ai_text = service.start_task(current, task_id)
    return StartOut(session=_session_out(service, session), ai_text=ai_text)


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> SessionOut:
    session = service.get_session(current, session_id)
    return _session_out(service, session)


@router.post("/sessions/{session_id}/message", response_model=MessageOut)
def send_message(
    session_id: int,
    request: Request,
    audio: UploadFile = File(...),
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> MessageOut:
    base = str(request.base_url)
    return service.send_message(current, session_id, audio, base)


@router.post("/sessions/{session_id}/finish", response_model=ResultOut)
def finish_session(
    session_id: int,
    current: User = Depends(get_current_user),
    service: TutorService = Depends(get_tutor_service),
) -> ResultOut:
    return service.finish_session(current, session_id)


def _session_out(service: TutorService, session) -> SessionOut:
    return SessionOut(
        id=session.id,
        task_id=session.task_id,
        status=session.status,
        task=service.tasks.get(session.task_id),
        turns=service.list_turns(session.id),
        result=service.get_result(session.id),
    )
