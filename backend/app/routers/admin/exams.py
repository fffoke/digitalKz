"""Экзамены в админке: вступительный («первый») + экзамены на уровень.

Создание/редактирование вопросов + загрузка аудио для аудирования.
"""
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from app.core.deps import get_admin_service
from app.schemas.admin import ExamCreateIn, ExamListItem, ExamOut, ExamUpdateIn
from app.services.admin import AdminService

router = APIRouter(prefix="/exams", tags=["admin:exams"])


@router.post("/upload-audio")
def upload_audio(request: Request, file: UploadFile = File(...)) -> dict:
    """Загрузка аудио для вопроса-аудирования (файл/запись голоса) → URL."""
    os.makedirs("uploads/exam-audio", exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower() or ".webm"
    name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join("uploads/exam-audio", name), "wb") as f:
        shutil.copyfileobj(file.file, f)
    base = str(request.base_url).rstrip("/")
    return {"url": f"{base}/uploads/exam-audio/{name}"}


# --- вступительный экзамен (первый) ---

@router.get("/entrance", response_model=ExamOut)
def get_entrance(service: AdminService = Depends(get_admin_service)):
    return service.get_entrance_exam()


@router.put("/entrance", response_model=ExamOut)
def update_entrance(
    data: ExamUpdateIn,
    service: AdminService = Depends(get_admin_service),
):
    return service.update_entrance_exam(data)


# --- экзамены на повышение уровня ---

@router.get("", response_model=list[ExamListItem])
def list_exams(service: AdminService = Depends(get_admin_service)):
    return service.list_exams()


@router.post("", response_model=ExamOut, status_code=status.HTTP_201_CREATED)
def create_exam(
    data: ExamCreateIn,
    service: AdminService = Depends(get_admin_service),
):
    return service.create_exam(data)


@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, service: AdminService = Depends(get_admin_service)):
    return service.get_exam(exam_id)


@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(
    exam_id: int,
    data: ExamUpdateIn,
    service: AdminService = Depends(get_admin_service),
):
    return service.update_exam(exam_id, data)
