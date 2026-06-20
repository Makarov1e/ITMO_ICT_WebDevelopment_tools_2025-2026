"""Конфигурация Celery (подзадача 3).

Брокер и хранилище результатов — Redis. Адреса берутся из переменных окружения,
в Docker они указывают на сервис `redis`. Список задач подключается через
`include`, чтобы воркер их зарегистрировал.
"""
from __future__ import annotations

import os

from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "lab3",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["main_app.tasks"],
)

# Отслеживать статус STARTED, чтобы клиент видел, что задача в работе
celery.conf.update(task_track_started=True)
