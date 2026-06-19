"""Общие параметры для задачи 1 (сумма чисел).

По заданию требуется посчитать сумму всех чисел от 1 до 10_000_000_000_000 (10^13).
Полный перебор 10^13 чисел в чистом Python занял бы десятки часов, поэтому для
наглядного замера производительности используется уменьшенное значение `TOTAL`,
которое можно переопределить аргументом командной строки:

    python threading_sum.py 1000000000

Алгоритм при этом честно суммирует числа в цикле (а не по формуле Гаусса) —
именно так создаётся CPU-bound нагрузка, на которой видна разница между
threading, multiprocessing и async.
"""
from __future__ import annotations

import sys

# Номинальное значение из задания (10^13)
NOMINAL_TOTAL = 10_000_000_000_000

# Значение по умолчанию для реальных замеров (10^8) — переопределяется аргументом
DEFAULT_TOTAL = 100_000_000

# Число параллельных подзадач (потоков / процессов / корутин)
WORKERS = 8


def get_total() -> int:
    """Возвращает верхнюю границу суммы: из argv[1] или значение по умолчанию."""
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    return DEFAULT_TOTAL


def split_ranges(total: int, workers: int) -> list[tuple[int, int]]:
    """Делит отрезок [1, total] на `workers` непрерывных диапазонов (start, end)."""
    chunk = total // workers
    ranges: list[tuple[int, int]] = []
    start = 1
    for i in range(workers):
        # Последняя подзадача забирает остаток от целочисленного деления
        end = total if i == workers - 1 else start + chunk - 1
        ranges.append((start, end))
        start = end + 1
    return ranges


def calculate_sum(start: int, end: int) -> int:
    """Считает сумму целых чисел на отрезке [start, end] перебором в цикле."""
    total = 0
    for number in range(start, end + 1):
        total += number
    return total
