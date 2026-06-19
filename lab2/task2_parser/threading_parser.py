"""Задача 2 — парсинг через THREADING.

Список URL делится на равные части (по числу потоков), и каждый поток
обрабатывает свою часть в цикле. Парсинг — I/O-bound задача: пока поток ждёт
ответ сети, GIL освобождается и работают другие потоки, поэтому threading даёт
ускорение по сравнению с последовательным выполнением.
"""
from __future__ import annotations

import threading
import time

import requests
from bs4 import BeautifulSoup

from db import init_db, save_page
from urls import URLS, WORKERS, split_into_chunks

APPROACH = "threading"


def parse_and_save(url: str) -> None:
    """Загружает страницу, извлекает <title> и сохраняет его в БД."""
    response = requests.get(url, timeout=15, headers={"User-Agent": "lab2-parser"})
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "(без заголовка)"
    page_id = save_page(APPROACH, url, title)
    print(f"[threading] #{page_id} {title}  <- {url}")


def worker(chunk: list[str]) -> None:
    """Обрабатывает свою часть списка URL по очереди."""
    for url in chunk:
        parse_and_save(url)


def main() -> None:
    init_db()
    chunks = split_into_chunks(URLS, WORKERS)
    print(f"[threading] {len(URLS)} URL разделены на {len(chunks)} частей: "
          f"{[len(c) for c in chunks]}")

    start_time = time.perf_counter()
    threads = [threading.Thread(target=worker, args=(chunk,)) for chunk in chunks]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    elapsed = time.perf_counter() - start_time

    print(f"\n[threading] обработано {len(URLS)} страниц в {len(chunks)} потоках "
          f"за {elapsed:.4f} c")


if __name__ == "__main__":
    main()
