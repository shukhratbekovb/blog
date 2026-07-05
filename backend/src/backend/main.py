from fastapi import FastAPI

from backend.api.v1.auth import router as auth_router
from backend.api.v1.posts import router as posts_router
from backend.api.v1.feed import router as feed_router
from backend.api.v1.tags import router as tag_router
from backend.api.v1.user import router as user_router

# Создали обьект приложения FastAPI
# это сердце нашего приложения
app = FastAPI(
    title="DevTalks API",  # название приложение отображается в Swagger UI
    description="Платформа для технических статей",  # Описание проекта можно использовать Markdown
    version="0.1.0",
    # docs_url="/docs", ссылка на Swagger
    # redoc_url="/redoc", ссылка на ReDoc
)


@app.get("/")
async def root():
    return {"message": "DevTalks API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


# uvicorn backend.main:app --reload
# backend.main -> модуль пайтона в котором FastAPI приложение
# app -> название обьекта FastAPI
# --reload -> перезагрузка при измении файлов

app.include_router(auth_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(feed_router, prefix="/api/v1")
app.include_router(tag_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
