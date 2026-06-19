"""Список URL-адресов для параллельного парсинга (задача 2)."""

URLS = [
    "https://example.com",
    "https://www.python.org",
    "https://docs.python.org/3/",
    "https://pypi.org",
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://en.wikipedia.org/wiki/Concurrency_(computer_science)",
    "https://en.wikipedia.org/wiki/Thread_(computing)",
    "https://en.wikipedia.org/wiki/Process_(computing)",
    "https://en.wikipedia.org/wiki/Asynchronous_I/O",
    "https://en.wikipedia.org/wiki/Global_interpreter_lock",
]

# Число параллельных воркеров (потоков / процессов / корутин).
# Список URL делится на столько примерно равных частей.
WORKERS = 3


def split_into_chunks(items: list, n: int) -> list[list]:
    """Делит список `items` на `n` максимально равных частей.

    Например, 10 URL и 3 воркера → части по 4, 3, 3 элемента.
    """
    chunk = len(items) // n
    remainder = len(items) % n
    chunks: list[list] = []
    start = 0
    for i in range(n):
        # Первые `remainder` частей получают на один элемент больше
        size = chunk + (1 if i < remainder else 0)
        chunks.append(items[start:start + size])
        start += size
    # Убираем возможные пустые части (если воркеров больше, чем URL)
    return [c for c in chunks if c]
