"""Задача 2 — парсинг через ASYNC (asyncio + aiohttp).

Список URL делится на равные части (по числу корутин-воркеров): каждый воркер
последовательно проходит свою часть, а сами воркеры выполняются конкурентно
через asyncio.gather. Для I/O-bound задач это наиболее лёгкий по ресурсам подход:
все запросы идут в одном потоке, без накладных расходов на потоки/процессы.
Загрузка асинхронная (aiohttp), а запись в БД (синхронный psycopg2) вынесена
в пул потоков через asyncio.to_thread, чтобы не блокировать цикл событий.
"""
from __future__ import annotations

import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup

from db import init_db, save_page
from urls import URLS, WORKERS, split_into_chunks

APPROACH = "async"


async def parse_and_save(session: aiohttp.ClientSession, url: str) -> None:
    """Асинхронно загружает страницу, извлекает <title> и сохраняет его в БД."""
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
        html = await response.text()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "(без заголовка)"
    page_id = await asyncio.to_thread(save_page, APPROACH, url, title)
    print(f"[async] #{page_id} {title}  <- {url}")


async def worker(session: aiohttp.ClientSession, chunk: list[str]) -> None:
    """Обрабатывает свою часть списка URL по очереди."""
    for url in chunk:
        await parse_and_save(session, url)


async def main() -> None:
    init_db()
    chunks = split_into_chunks(URLS, WORKERS)
    print(f"[async] {len(URLS)} URL разделены на {len(chunks)} частей: "
          f"{[len(c) for c in chunks]}")

    start_time = time.perf_counter()
    headers = {"User-Agent": "lab2-parser"}
    async with aiohttp.ClientSession(headers=headers) as session:
        # Воркеры (по числу частей) выполняются конкурентно
        await asyncio.gather(*(worker(session, chunk) for chunk in chunks))
    elapsed = time.perf_counter() - start_time

    print(f"\n[async] обработано {len(URLS)} страниц в {len(chunks)} корутинах-воркерах "
          f"за {elapsed:.4f} c")


if __name__ == "__main__":
    asyncio.run(main())
