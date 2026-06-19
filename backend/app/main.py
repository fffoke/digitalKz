# """Точка входа FastAPI — подключает роутеры пользователя и админки."""
# from fastapi import FastAPI

# from app.routers.user import router as user_router
# from app.routers.admin import router as admin_router

# app = FastAPI(title="ТІЛДЕС API")

# app.include_router(user_router.router, prefix="/api", tags=["user"])
# app.include_router(admin_router.router, prefix="/api/admin", tags=["admin"])


# @app.get("/health")
# def health() -> dict[str, str]:
#     return {"status": "ok"}

