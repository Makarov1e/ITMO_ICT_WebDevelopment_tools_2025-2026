"""Работа с БД для ЛР3.

Результаты парсинга сохраняются в таблицу `parsed_pages` (как и в ЛР2).
Подключение к PostgreSQL берётся из переменной окружения DB_DSN — в Docker она
указывает на сервис `db`. Используется короткоживущее соединение на операцию,
что безопасно при работе из разных процессов (FastAPI и Celery-worker).
"""
from __future__ import annotations

import os
import time

import psycopg2

DB_DSN = os.getenv(
    "DB_DSN",
    "postgresql://postgres:postgres@db:5432/hackathon_fastapi",
)


def get_conn():
    """Открывает новое соединение с БД."""
    return psycopg2.connect(DB_DSN)


def init_db(retries: int = 10, delay: float = 2.0) -> None:
    """Создаёт таблицу parsed_pages. С ретраями — БД в контейнере поднимается не мгновенно."""
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS parsed_pages (
                        id         SERIAL PRIMARY KEY,
                        url        TEXT NOT NULL,
                        title      TEXT NOT NULL,
                        approach   TEXT NOT NULL,
                        parsed_at  TIMESTAMP NOT NULL DEFAULT now()
                    )
                    """
                )
            return
        except psycopg2.OperationalError as exc:  # БД ещё не готова
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Не удалось подключиться к БД: {last_error}")


def save_page(approach: str, url: str, title: str) -> int:
    """Сохраняет результат парсинга и возвращает id новой записи."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO parsed_pages (url, title, approach) "
            "VALUES (%s, %s, %s) RETURNING id",
            (url, title, approach),
        )
        return cur.fetchone()[0]
