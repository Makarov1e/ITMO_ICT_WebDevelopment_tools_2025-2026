"""Общий модуль работы с БД для задачи 2 (парсинг).

Результаты парсинга сохраняются в **ту же БД, что и в лабораторной №1**
(`hackathon_fastapi`) — в отдельную таблицу `parsed_pages`. Для устойчивости
к потокам и процессам каждое сохранение открывает собственное короткоживущее
соединение через psycopg2 (никаких общих между процессами объектов соединения).
"""
from __future__ import annotations

import os

import psycopg2

# Подключение к БД из ЛР1. Можно переопределить переменной окружения DB_DSN.
DB_DSN = os.getenv(
    "DB_DSN",
    "postgresql://postgres:123@localhost:5432/hackathon_fastapi",
)


def get_conn():
    """Открывает новое соединение с БД."""
    return psycopg2.connect(DB_DSN)


def init_db() -> None:
    """Создаёт таблицу parsed_pages, если её ещё нет."""
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


def save_page(approach: str, url: str, title: str) -> int:
    """Сохраняет результат парсинга и возвращает id новой записи."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO parsed_pages (url, title, approach) "
            "VALUES (%s, %s, %s) RETURNING id",
            (url, title, approach),
        )
        return cur.fetchone()[0]


def clear_pages() -> None:
    """Очищает таблицу (удобно перед чистым замером)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE parsed_pages RESTART IDENTITY")
