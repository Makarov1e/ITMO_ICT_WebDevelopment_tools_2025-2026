"""Фоновые задачи Celery (подзадача 3).

Задача `parse_url_task` выполняет парсинг в фоне на стороне воркера: загружает
страницу, извлекает заголовок и сохраняет его в БД.
"""
from __future__ import annotations

from common.parser import parse_and_save
from main_app.celery_app import celery


@celery.task(name="parse_url")
def parse_url_task(url: str) -> dict:
    """Фоновая задача парсинга URL."""
    return parse_and_save(url, approach="celery")
