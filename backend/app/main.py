"""Точка входа FastAPI — подключает роутеры пользователя и админки."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.admin.router import router as admin_router
from app.routers.user.router import router as user_router

app = FastAPI(title="ТІЛДЕС API")

# Vue dev-серверы (Vite): user-web и admin-web
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
