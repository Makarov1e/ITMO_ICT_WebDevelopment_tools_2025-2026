"""Задача 1 — подход THREADING.

Сумма чисел считается несколькими потоками. Из-за GIL потоки в CPython
не выполняют Python-байткод по-настоящему параллельно, поэтому на CPU-bound
задаче ускорения почти нет — этот скрипт как раз демонстрирует данный эффект.
"""
from __future__ import annotations

import threading
import time

from config import WORKERS, calculate_sum, get_total, split_ranges


def main() -> None:
    total = get_total()
    ranges = split_ranges(total, WORKERS)

    # Каждый поток кладёт свой результат в общий список по своему индексу
    partials: list[int] = [0] * WORKERS
    threads: list[threading.Thread] = []

    def worker(index: int, start: int, end: int) -> None:
        partials[index] = calculate_sum(start, end)

    start_time = time.perf_counter()
    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(i, start, end))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    result = sum(partials)
    elapsed = time.perf_counter() - start_time

    print(f"[threading]      сумма 1..{total} = {result}")
    print(f"[threading]      потоков: {WORKERS}, время: {elapsed:.4f} c")


if __name__ == "__main__":
    main()
