"""Точка входа FastAPI — подключает роутеры пользователя и админки."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastapi import Depends

from app.core.deps import require_admin
from app.routers.admin.router import router as admin_router
from app.routers.user.router import router as user_router

app = FastAPI(title="ТІЛДЕС API")

# раздача загруженных файлов (аватары и т.п.)
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dev: любой origin (localhost + телефон по локальной сети).
# Авторизация через Bearer-токен в заголовке, а не куки — для прода сузить список.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin", dependencies=[Depends(require_admin)])


@app.on_event("startup")
def _warmup_whisper() -> None:
    """Грузим модель распознавания в фоне, чтобы первое голосовое не ждало загрузку."""
    import threading

    from app.services.transcription import warmup

    threading.Thread(target=warmup, daemon=True).start()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
