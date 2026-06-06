# Лабораторная работа 1 — FastAPI Hackathon API

Серверное приложение системы проведения **хакатона** на **FastAPI** с ORM **SQLModel**,
БД **PostgreSQL**, миграциями **Alembic** и **ручной JWT-аутентификацией**.

## Ссылки на GitHub

- **Репозиторий:** <https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026>
- **Папка лабораторной (ветка `main`):** <https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1>
- **Исходный код приложения:** [`lab1/app/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/app)
- **Миграции Alembic:** [`lab1/alembic/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/alembic)

## Соответствие заданию

### Задание на 9 баллов

| Требование | Реализация |
|---|---|
| ORM-таблицы (SQLAlchemy/SQLModel) + PostgreSQL | [`app/models/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/app/models) — см. [Модели](models.md) |
| CRUD-API | [`app/api/routers/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/app/api/routers) — см. [Эндпоинты](endpoints.md) |
| GET с вложенными объектами (M2M, 1-M) | задача↔теги (M2M); команда→участники, решение→оценки, задача→ссылки (1-M) |
| Миграции Alembic | [`alembic/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/alembic) |
| Аннотации типов в API | [`app/schemas/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/app/schemas) |
| Разделение кода по слоям | `models / schemas / crud / api / core` |

### Задание на 15 баллов

| Требование | Реализация |
|---|---|
| Авторизация и регистрация | [`app/api/routers/auth.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/routers/auth.py) |
| Генерация JWT-токенов | `create_access_token` в [`app/core/security.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/core/security.py) |
| **Аутентификация по JWT — вручную** | `decode_access_token` + `get_current_user` ([deps.py](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/deps.py)) |
| Хэширование паролей | PBKDF2-HMAC-SHA256 (стандартная библиотека) |
| Доп. методы пользователя | `GET /users/me`, `GET /users`, `GET /users/{id}`, `POST /users/me/change-password` |

> **Важно (п.3):** JWT (кодирование, декодирование, проверка подписи) и хэширование паролей
> реализованы только на стандартной библиотеке Python (`hmac`, `hashlib`, `base64`, `secrets`),
> без сторонних JWT/security-библиотек. См. [Безопасность](security.md).

## Архитектура

```
lab1/
├── alembic/                 # миграции БД
├── app/
│   ├── main.py              # точка входа FastAPI
│   ├── core/                # config, database, security
│   ├── models/              # ORM-модели SQLModel
│   ├── schemas/             # Pydantic-схемы (вход/выход API)
│   ├── crud/                # бизнес-логика работы с БД
│   └── api/                 # deps + routers
├── requirements.txt
└── seed.py                  # наполнение демо-данными
```

## Предметная область

Система хакатона: **пользователи с ролями** (ADMIN / JURY / CURATOR / CAPTAIN),
**задачи** (с тегами и ресурсами), **команды** (с участниками), **решения** и **оценки жюри**.
