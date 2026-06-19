"""Задача 1 — подход ASYNC (asyncio).

asyncio выполняет корутины в одном потоке через кооперативную многозадачность.
Она эффективна для I/O-bound задач (ожидание сети, диска), но для CPU-bound
вычислений выигрыша не даёт: пока корутина считает сумму, она не отдаёт
управление циклу событий, поэтому подзадачи выполняются фактически
последовательно. Этот скрипт демонстрирует отсутствие ускорения.
"""
from __future__ import annotations

import asyncio
import time

from config import WORKERS, calculate_sum, get_total, split_ranges


async def worker(start: int, end: int) -> int:
    """Корутина-обёртка над синхронным подсчётом суммы."""
    return calculate_sum(start, end)


async def main() -> None:
    total = get_total()
    ranges = split_ranges(total, WORKERS)

    start_time = time.perf_counter()
    # gather запускает корутины конкурентно, но из-за CPU-bound характера
    # они не выполняются параллельно
    partials = await asyncio.gather(*(worker(start, end) for start, end in ranges))
    result = sum(partials)
    elapsed = time.perf_counter() - start_time

    print(f"[async]          сумма 1..{total} = {result}")
    print(f"[async]          корутин: {WORKERS}, время: {elapsed:.4f} c")


if __name__ == "__main__":
    asyncio.run(main())
