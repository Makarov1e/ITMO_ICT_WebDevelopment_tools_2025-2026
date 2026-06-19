"""Задача 2 — парсинг через MULTIPROCESSING.

Список URL делится на равные части (по числу процессов), и каждый процесс
обрабатывает свою часть в цикле. Для I/O-bound задачи процессы тоже дают
ускорение, но цена выше: создание процессов и межпроцессное взаимодействие
дороже, чем потоки.
"""
from __future__ import annotations

import time
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup

from db import init_db, save_page
from urls import URLS, WORKERS, split_into_chunks

APPROACH = "multiprocessing"


def parse_and_save(url: str) -> None:
    """Загружает страницу, извлекает <title> и сохраняет его в БД."""
    response = requests.get(url, timeout=15, headers={"User-Agent": "lab2-parser"})
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "(без заголовка)"
    page_id = save_page(APPROACH, url, title)
    print(f"[multiprocessing] #{page_id} {title}  <- {url}")


def worker(chunk: list[str]) -> None:
    """Обрабатывает свою часть списка URL по очереди (в отдельном процессе)."""
    for url in chunk:
        parse_and_save(url)


def main() -> None:
    init_db()
    chunks = split_into_chunks(URLS, WORKERS)
    print(f"[multiprocessing] {len(URLS)} URL разделены на {len(chunks)} частей: "
          f"{[len(c) for c in chunks]}")

    start_time = time.perf_counter()
    # Каждый процесс получает свою часть списка
    with Pool(processes=len(chunks)) as pool:
        pool.map(worker, chunks)
    elapsed = time.perf_counter() - start_time

    print(f"\n[multiprocessing] обработано {len(URLS)} страниц в {len(chunks)} процессах "
          f"за {elapsed:.4f} c")


if __name__ == "__main__":
    main()
