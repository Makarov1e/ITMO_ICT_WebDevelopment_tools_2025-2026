"""Сервис-парсер (подзадача 1.4) — отдельное FastAPI-приложение.

Запускается в собственном контейнере и предоставляет HTTP-эндпоинт `/parse`,
по которому можно вызвать парсер. Главное приложение обращается сюда по сети.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from common.db import init_db
from common.parser import parse_and_save

app = FastAPI(title="Lab3 Parser Service", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    """Гарантируем, что таблица parsed_pages существует."""
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "lab3-parser"}


@app.post("/parse")
def parse(url: str) -> dict:
    """Загружает страницу по URL, парсит заголовок и сохраняет в БД."""
    try:
        result = parse_and_save(url, approach="http")
        return {"message": "Parsing completed", "result": result}
    except Exception as exc:  # сетевые ошибки, недоступный сайт и т.п.
        raise HTTPException(status_code=500, detail=str(exc)) from exc
