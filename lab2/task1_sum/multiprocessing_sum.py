"""Задача 1 — подход MULTIPROCESSING.

Каждая подзадача выполняется в отдельном процессе со своим интерпретатором
и своим GIL, поэтому вычисления идут по-настоящему параллельно на нескольких
ядрах CPU. На CPU-bound задаче это даёт реальное ускорение.
"""
from __future__ import annotations

import time
from multiprocessing import Pool

from config import WORKERS, calculate_sum, get_total, split_ranges


def worker(bounds: tuple[int, int]) -> int:
    """Обёртка для Pool.map: распаковывает (start, end) и считает сумму."""
    start, end = bounds
    return calculate_sum(start, end)


def main() -> None:
    total = get_total()
    ranges = split_ranges(total, WORKERS)

    start_time = time.perf_counter()
    with Pool(processes=WORKERS) as pool:
        partials = pool.map(worker, ranges)
    result = sum(partials)
    elapsed = time.perf_counter() - start_time

    print(f"[multiprocessing] сумма 1..{total} = {result}")
    print(f"[multiprocessing] процессов: {WORKERS}, время: {elapsed:.4f} c")


if __name__ == "__main__":
    # Защита входной точки обязательна для multiprocessing (особенно на macOS/Windows)
    main()
