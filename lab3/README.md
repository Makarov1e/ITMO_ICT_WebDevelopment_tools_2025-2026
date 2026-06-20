# Лабораторная работа 3. Docker, источники данных и очереди

**Студент:** Макаров Егор

**Цель:** упаковать FastAPI-приложение в Docker, интегрировать парсер данных с
БД, вызывать парсер через API (синхронно) и через очередь задач (асинхронно).

---

## Архитектура

Система состоит из 5 контейнеров, поднимаемых одним `docker-compose.yml`:

```
                 ┌─────────────┐
   клиент  ─────▶│   app       │  главное FastAPI-приложение (порт 8000)
                 │ (FastAPI)   │
                 └──┬───────┬──┘
        HTTP /parse │       │ .delay()  (очередь)
                    ▼       ▼
              ┌─────────┐ ┌────────┐     ┌──────────┐
              │ parser  │ │ redis  │◀───▶│  worker  │ Celery-воркер
              │(FastAPI)│ │(брокер)│     │ (Celery) │
              └────┬────┘ └────────┘     └────┬─────┘
                   │                          │
                   └──────────┬───────────────┘
                              ▼
                        ┌──────────┐
                        │    db    │  PostgreSQL (как в ЛР1)
                        └──────────┘
```

| Сервис | Назначение | Порт (хост) |
|---|---|---|
| **db** | PostgreSQL (БД из ЛР1, таблица `parsed_pages`) | 5435 |
| **redis** | брокер очереди и хранилище результатов Celery | 6381 |
| **parser** | отдельный FastAPI-сервис парсера, эндпоинт `POST /parse` | 8100 |
| **app** | главное приложение: вызов парсера по HTTP + очередь | 8000 |
| **worker** | Celery-воркер, выполняет задачи парсинга в фоне | — |

Парсер (логика из ЛР2) и работа с БД вынесены в общий пакет `common/`, который
используется и сервисом-парсером, и Celery-воркером.

## Структура проекта

```
lab3/
├── docker-compose.yml      # оркестрация 5 сервисов
├── Dockerfile              # общий образ для app / parser / worker
├── requirements.txt
├── common/
│   ├── db.py               # подключение к БД + таблица parsed_pages
│   └── parser.py           # parse_and_save(url): загрузка, парсинг, сохранение
├── parser_service/
│   └── main.py             # FastAPI-парсер: POST /parse
└── main_app/
    ├── main.py             # эндпоинты /parse/sync, /parse/async, /parse/result
    ├── celery_app.py       # конфигурация Celery (брокер/бэкенд = Redis)
    └── tasks.py            # фоновая задача parse_url_task
```

---

## Выполнение подзадач

### Подзадача 1 — упаковка в Docker

- **FastAPI-приложение** (`main_app`), **БД** (сервис `db`, PostgreSQL как в ЛР1)
  и **парсер** (`parser_service`, логика из ЛР2) упакованы в контейнеры.
- **Dockerfile** — один общий образ: базовый `python:3.11-slim`, установка
  зависимостей, копирование кода. Команда запуска задаётся в compose для каждого
  сервиса.
- **docker-compose.yml** — описывает все сервисы, порты, переменные окружения и
  зависимости (`depends_on` с `healthcheck` у db и redis, чтобы приложения
  стартовали только после готовности инфраструктуры).
- **Вызов парсера по HTTP** — сервис `parser` предоставляет `POST /parse?url=...`.

### Подзадача 2 — вызов парсера из FastAPI (синхронно)

Эндпоинт **`POST /parse/sync?url=...`** главного приложения отправляет HTTP-запрос
сервису-парсеру (в отдельном контейнере) через `httpx` и возвращает результат
клиенту. См. `main_app/main.py::parse_sync`.

### Подзадача 3 — вызов парсера через очередь (асинхронно)

- **Celery + Redis** подключены: Redis — брокер и хранилище результатов
  (`main_app/celery_app.py`).
- **Задача** `parse_url_task` (`main_app/tasks.py`) выполняет парсинг в фоне на
  стороне воркера.
- Эндпоинт **`POST /parse/async?url=...`** ставит задачу в очередь (`.delay()`) и
  сразу возвращает `task_id`, не блокируя клиента.
- Эндпоинт **`GET /parse/result/{task_id}`** возвращает статус и результат задачи.
- В `docker-compose.yml` добавлены сервисы **redis** и **worker**.

---

## Запуск

```bash
cd lab3
docker compose up --build -d      # собрать и поднять все контейнеры
docker compose ps                 # проверить статусы
docker compose logs -f worker     # смотреть, как Celery выполняет задачи
docker compose down               # остановить (добавить -v чтобы удалить БД)
```

- Главное приложение (Swagger): <http://localhost:8000/docs>
- Сервис-парсер (Swagger): <http://localhost:8100/docs>

## Проверка (демонстрация)

```bash
# 1. Здоровье сервисов
curl http://localhost:8000/
curl http://localhost:8100/

# 2. Синхронный вызов парсера (подзадача 2)
curl -X POST "http://localhost:8000/parse/sync?url=https://example.com"

# 3. Асинхронный вызов через очередь (подзадача 3)
curl -X POST "http://localhost:8000/parse/async?url=https://www.python.org"
# -> {"message":"Task queued","task_id":"<ID>"}

# 4. Результат фоновой задачи
curl "http://localhost:8000/parse/result/<ID>"
# -> {"status":"SUCCESS","result":{"title":"Welcome to Python.org",...}}

# 5. Данные в БД
docker compose exec db psql -U postgres -d hackathon_fastapi \
  -c "SELECT id, title, approach FROM parsed_pages ORDER BY id;"
```

**Пример результата** (поле `approach` показывает путь вызова — `http` синхронно
через сервис-парсер, `celery` через очередь):

| id | title | approach |
|---|---|---|
| 1 | Example Domain | http |
| 2 | Welcome to Python.org | celery |

---

## Итог

Реализованы все три подзадачи: приложение, БД и парсер упакованы в Docker и
управляются через `docker-compose`; парсер вызывается из FastAPI синхронно по
HTTP (отдельный контейнер) и асинхронно через очередь Celery с брокером Redis и
отдельным воркером. Результаты парсинга сохраняются в БД из ЛР1.
