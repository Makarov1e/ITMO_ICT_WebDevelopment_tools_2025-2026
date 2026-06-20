"""Ядро парсера (общее для сервиса-парсера и Celery-воркера).

Логика та же, что в ЛР2: загрузить HTML, извлечь <title>, сохранить в БД.
"""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from common.db import save_page


def parse_and_save(url: str, approach: str = "http") -> dict:
    """Загружает страницу по URL, извлекает заголовок и сохраняет его в БД.

    Возвращает словарь с результатом; `approach` помечает, каким путём вызван
    парсер (http — синхронно из сервиса, celery — из фоновой задачи).
    """
    response = requests.get(url, timeout=15, headers={"User-Agent": "lab3-parser"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "(без заголовка)"
    page_id = save_page(approach, url, title)
    print(f"[{approach}] #{page_id} {title}  <- {url}", flush=True)
    return {"id": page_id, "url": url, "title": title, "approach": approach}
