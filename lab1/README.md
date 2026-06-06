# Лабораторная работа 1 — FastAPI + SQLModel + PostgreSQL

Серверное приложение системы проведения хакатона на **FastAPI** с ORM **SQLModel**,
БД **PostgreSQL**, миграциями **Alembic** и **ручной JWT-аутентификацией**.

## Соответствие заданию

### Задание на 9 баллов
- ✅ ORM-таблицы (SQLModel) + PostgreSQL — `app/models/`
- ✅ CRUD-API для всех сущностей — `app/api/routers/`
- ✅ GET с вложенными объектами:
  - **many-to-many**: задача ↔ теги (`Task.tags`)
  - **one-to-many**: команда → участники, решение → оценки, задача → ресурсные ссылки
- ✅ Миграции Alembic — `alembic/`
- ✅ Аннотации типов во всех методах API (схемы `app/schemas/`)
- ✅ Разделение по слоям: `models / schemas / crud / api / core`
- ✅ Комментарии к нетривиальным частям

### Задание на 15 баллов
- ✅ Регистрация и авторизация — `app/api/routers/auth.py`
- ✅ Генерация JWT — `app/core/security.py::create_access_token`
- ✅ **Аутентификация по JWT реализована вручную** (без сторонних библиотек):
  декодирование/проверка подписи — `app/core/security.py::decode_access_token`,
  зависимость аутентификации — `app/api/deps.py::get_current_user`
- ✅ Хэширование паролей — `app/core/security.py` (PBKDF2-HMAC-SHA256, стандартная библиотека)
- ✅ Доп. методы: `GET /users/me`, `GET /users`, `GET /users/{id}`, `POST /users/me/change-password`

> JWT (создание + проверка) и хэширование реализованы на стандартной библиотеке Python
> (`hmac`, `hashlib`, `base64`, `secrets`) — без сторонних JWT/security-пакетов.

## Структура проекта

```
lab1/
├── alembic/                 # миграции
│   ├── env.py
│   └── versions/
├── alembic.ini
├── app/
│   ├── main.py              # точка входа FastAPI
│   ├── core/
│   │   ├── config.py        # настройки из .env
│   │   ├── database.py      # движок и сессии
│   │   └── security.py      # хэширование + JWT (вручную)
│   ├── models/              # ORM-модели SQLModel
│   ├── schemas/             # Pydantic-схемы (вход/выход API)
│   ├── crud/                # бизнес-логика работы с БД
│   └── api/
│       ├── deps.py          # зависимости: сессия, аутентификация, RBAC
│       └── routers/         # auth, users, tasks, teams, solutions
├── requirements.txt
└── .env.example
```

## Запуск

### 1. Зависимости
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. PostgreSQL
```sql
CREATE ROLE hackathon_user LOGIN PASSWORD 'hackathon_password';
CREATE DATABASE hackathon_fastapi OWNER hackathon_user;
```

### 3. Окружение
```bash
cp .env.example .env   # при необходимости поправить DATABASE_URL / JWT_SECRET
```

### 4. Миграции
```bash
alembic upgrade head
# при изменении моделей:
# alembic revision --autogenerate -m "описание"
```

### 5. Запуск сервера
```bash
uvicorn app.main:app --reload --port 8001
```

- Swagger UI: http://127.0.0.1:8001/docs
- OpenAPI: http://127.0.0.1:8001/openapi.json

## Примеры запросов

```bash
# Регистрация
curl -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345","role":"ADMIN"}'

# Логин -> JWT
curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}'

# Запрос с токеном
curl http://127.0.0.1:8001/users/me -H "Authorization: Bearer <TOKEN>"
```

## Роли и доступ
- `ADMIN` — создание/изменение задач и тегов, смена ролей пользователей
- `JURY` — выставление оценок решениям
- `CURATOR` — куратор задачи
- `CAPTAIN` — капитан команды
