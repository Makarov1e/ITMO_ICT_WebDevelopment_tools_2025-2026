"""Точка входа FastAPI-приложения хакатон-системы."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routers import auth, solutions, tasks, teams, users

app = FastAPI(
    title="Hackathon API (FastAPI + SQLModel)",
    description="Лабораторная работа 1: серверное приложение на FastAPI с ручной JWT-аутентификацией.",
    version="1.0.0",
)

# Подключаем роутеры предметных областей
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(teams.router)
app.include_router(solutions.router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "service": "hackathon-fastapi"}
