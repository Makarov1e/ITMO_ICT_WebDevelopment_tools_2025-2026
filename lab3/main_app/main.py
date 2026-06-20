"""Главное FastAPI-приложение (продолжение ЛР1).

Подзадача 2: эндпоинт `/parse/sync` вызывает сервис-парсер (в отдельном
контейнере) по HTTP и возвращает результат.
Подзадача 3: эндпоинт `/parse/async` ставит задачу парсинга в очередь Celery,
а `/parse/result/{task_id}` позволяет узнать статус и результат.
"""
from __future__ import annotations

import os

import httpx
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException

from common.db import init_db
from main_app.celery_app import celery
from main_app.tasks import parse_url_task

app = FastAPI(title="Lab3 Main App", version="1.0.0")

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8100")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "lab3-main"}


@app.post("/parse/sync")
def parse_sync(url: str) -> dict:
    """Синхронный вызов: проксирует запрос сервису-парсеру по HTTP."""
    try:
        response = httpx.post(f"{PARSER_URL}/parse", params={"url": url}, timeout=30)
        response.raise_for_status()
        return {"message": "Parsing completed (sync via parser service)",
                "result": response.json()}
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/parse/async")
def parse_async(url: str) -> dict:
    """Асинхронный вызов: ставит задачу парсинга в очередь Celery."""
    task = parse_url_task.delay(url)
    return {"message": "Task queued", "task_id": task.id}


@app.get("/parse/result/{task_id}")
def parse_result(task_id: str) -> dict:
    """Статус и результат фоновой задачи по её id."""
    result = AsyncResult(task_id, app=celery)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
