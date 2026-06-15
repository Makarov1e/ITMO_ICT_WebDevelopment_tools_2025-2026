# Лабораторная работа 1. Реализация серверного приложения на FastAPI

**Студент:** Макаров Егор
**Тема:** Система организации и проведения хакатонов
**Стек:** FastAPI · SQLModel · PostgreSQL · Alembic · ручная JWT-аутентификация

---

## 1. Цель работы

Разработать полноценное серверное приложение на фреймворке **FastAPI** с применением
ORM, реляционной БД, миграций и аутентификации. Работа объединяет три практики курса,
которые засчитываются как одна лабораторная:

- **Практика 1.1** — базовое приложение FastAPI и CRUD-API;
- **Практика 1.2** — ORM SQLModel, PostgreSQL и связи между сущностями;
- **Практика 1.3** — миграции Alembic, переменные окружения, структура проекта.

## 2. Предметная область

Система для организации хакатонов. По заданию реализован следующий функционал:

- **Регистрация участников** — пользователи регистрируются и авторизуются в системе;
- **Формирование команд** — создание команд, добавление участников с разными ролями;
- **Публикация задач** — организаторы публикуют задачи с описанием, тегами и ресурсами;
- **Оценка работ** — команды загружают решения, жюри выставляет оценки.

Роли пользователей: `ADMIN` (организатор), `JURY` (жюри), `CURATOR` (куратор задачи),
`CAPTAIN` (капитан команды). Доступ к операциям разграничен по ролям (RBAC).

## 3. Используемые технологии

| Технология | Назначение |
|---|---|
| FastAPI | Веб-фреймворк, маршрутизация, валидация, Swagger UI |
| SQLModel | ORM поверх SQLAlchemy + Pydantic |
| PostgreSQL | Реляционная база данных |
| Alembic | Версионирование схемы БД (миграции) |
| Pydantic / pydantic-settings | Схемы ввода-вывода, чтение настроек из `.env` |
| Uvicorn | ASGI-сервер |
| Стандартная библиотека (`hmac`, `hashlib`, `base64`, `secrets`) | Ручная реализация JWT и хэширования паролей |

## 4. Структура проекта

```
lab1/
├── app/
│   ├── main.py              # точка входа: создание FastAPI, подключение роутеров
│   ├── core/
│   │   ├── config.py        # настройки из .env (URL БД, JWT-секрет)
│   │   ├── database.py      # движок SQLAlchemy и фабрика сессий
│   │   └── security.py      # хэширование паролей (PBKDF2) + JWT (вручную)
│   ├── models/              # ORM-таблицы SQLModel (user, team, task, solution)
│   ├── schemas/             # Pydantic-схемы запросов/ответов (Create/Update/Read)
│   ├── crud/                # операции с БД для каждой сущности
│   └── api/
│       ├── deps.py          # зависимости: сессия, аутентификация, проверка ролей
│       └── routers/         # эндпоинты: auth, users, tasks, teams, solutions
├── alembic/                 # миграции (env.py, versions/)
├── alembic.ini
├── seed.py                  # наполнение БД демо-данными
├── requirements.txt
├── .env.example
└── README.md
```

Приложение построено по слоистой архитектуре: запрос проходит
`router → deps → crud → models/schemas → core`. Каждый слой отвечает только за свою
задачу, что упрощает поддержку и тестирование.

## 5. Ход работы

### 5.1. Практика 1.1 — базовое приложение и CRUD

- Создано приложение FastAPI ([app/main.py](app/main.py)) с корневым эндпоинтом
  `GET /`, возвращающим статус сервиса.
- Запуск через `uvicorn app.main:app --reload`, автодокументация на `/docs`.
- Для всех сущностей реализован полный CRUD (создание, чтение списка, чтение одного
  объекта, обновление, удаление) в роутерах [app/api/routers/](app/api/routers/).
- Данные типизированы Pydantic-схемами ([app/schemas/](app/schemas/)): отдельные модели
  для входа (`...Create`, `...Update`) и выхода (`...Read`).
- Применены перечисления (`Enum`): `UserRole`, `SolutionStatus`.

### 5.2. Практика 1.2 — SQLModel, PostgreSQL и связи

- Подключение к PostgreSQL вынесено в [app/core/database.py](app/core/database.py)
  (движок + зависимость `get_session`).
- Описаны ORM-модели ([app/models/](app/models/)) и связи между ними:

| Тип связи | Пример |
|---|---|
| **many-to-many** | `Task.tags` ↔ `Tag.tasks` через таблицу `TaskTagLink` |
| **one-to-many** | `Team.members`, `Solution.evaluations`, `Task.resource_links` |
| **many-to-one** | `Team.selected_task`, `Solution.team`, `Solution.task` |
| **one-to-one** | `Task.curator` (FK с `unique=True`), `Team.captain` |

- Реализовано **вложенное отображение** связанных объектов: например, `GET /tasks/{id}`
  возвращает задачу вместе с куратором, тегами и ресурсными ссылками (схема `TaskRead`).
- Обновление выполнено через `model_dump(exclude_unset=True)` — изменяются только
  переданные поля.

### 5.3. Практика 1.3 — миграции, переменные окружения, структура

- Настроен **Alembic** ([alembic/env.py](alembic/env.py)): импортируются модели,
  `target_metadata = SQLModel.metadata`, URL базы берётся из настроек приложения
  (то есть из `.env`). В шаблон миграций добавлен `import sqlmodel`.
- Схема БД создаётся и изменяется **только миграциями** (`alembic upgrade head`),
  а не автосозданием таблиц на старте — это корректный продакшен-подход.
- Чувствительные данные (URL БД, JWT-секрет) вынесены в `.env`
  ([app/core/config.py](app/core/config.py)); файл `.env` добавлен в `.gitignore`,
  а в репозитории хранится только шаблон `.env.example`.

### 5.4. Дополнительно — регистрация и JWT-аутентификация

- Регистрация и логин — роутер [app/api/routers/auth.py](app/api/routers/auth.py).
- **JWT реализован вручную**, без сторонних библиотек
  ([app/core/security.py](app/core/security.py)): сборка и подпись токена
  (`create_access_token`) и проверка подписи и срока действия (`decode_access_token`)
  на `hmac` + `hashlib` + `base64`.
- Пароли хэшируются алгоритмом **PBKDF2-HMAC-SHA256** (формат как в Django).
- Проверка токена и разграничение доступа по ролям — [app/api/deps.py](app/api/deps.py)
  (`get_current_user`, `require_roles`).

## 6. Описание API

Полная интерактивная документация — Swagger UI на `/docs`.

### Аутентификация
| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | Регистрация пользователя |
| POST | `/auth/login` | Авторизация, выдача JWT |

### Пользователи
| Метод | Путь | Описание |
|---|---|---|
| GET | `/users/me` | Текущий пользователь |
| POST | `/users/me/change-password` | Смена пароля |
| GET | `/users` · `/users/{id}` | Список / один пользователь |
| PATCH | `/users/{id}` | Изменение (роль и т.п.) |

### Задачи и теги
| Метод | Путь | Описание |
|---|---|---|
| GET | `/tasks` · `/tasks/{id}` | Список / задача с вложенными объектами |
| POST · PATCH · DELETE | `/tasks` · `/tasks/{id}` | CRUD задачи (только ADMIN) |
| GET | `/tasks/tags/all` | Список тегов |
| POST | `/tasks/tags` | Создание тега |

### Команды
| Метод | Путь | Описание |
|---|---|---|
| GET | `/teams` · `/teams/{id}` | Список / команда с участниками |
| POST · PATCH · DELETE | `/teams` · `/teams/{id}` | CRUD команды |
| POST | `/teams/{id}/members` | Добавление участника |

### Решения и оценки
| Метод | Путь | Описание |
|---|---|---|
| GET | `/solutions` · `/solutions/{id}` | Список / решение с оценками |
| POST · PATCH · DELETE | `/solutions` · `/solutions/{id}` | CRUD решения |
| POST | `/solutions/{id}/evaluations` | Оценка решения (только JURY) |

## 7. Запуск проекта

```bash
cd lab1
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Создать БД в PostgreSQL:

```sql
CREATE ROLE hackathon_user LOGIN PASSWORD 'hackathon_password';
CREATE DATABASE hackathon_fastapi OWNER hackathon_user;
```

Настроить окружение, применить миграции, наполнить демо-данными и запустить:

```bash
cp .env.example .env          # при необходимости поправить DATABASE_URL / JWT_SECRET
alembic upgrade head          # создание схемы БД
python seed.py                # демо-данные (идемпотентно)
uvicorn app.main:app --reload --port 8001
```

- Swagger UI: http://127.0.0.1:8001/docs
- OpenAPI: http://127.0.0.1:8001/openapi.json

### Работа с миграциями

```bash
alembic revision --autogenerate -m "описание"   # создать миграцию по изменениям моделей
alembic upgrade head                             # применить
alembic downgrade -1                             # откатить на шаг назад
```

## 8. Проверка работы (сценарий демонстрации)

В Swagger UI (`/docs`):

1. `POST /auth/login` с `admin / admin12345` → скопировать `access_token`.
2. Нажать **Authorize** 🔒 и вставить токен (без слова `Bearer`).
3. `GET /tasks/{task_id}` (id 1–5) → ответ с вложенными `curator`, `tags`, `resource_links`.
4. `POST /tasks`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}` — демонстрация CRUD.
5. Войти как `captain1 / captain12345` и попробовать `POST /tasks` → **403** (RBAC).
6. Войти как `jury1 / jury12345` и выставить оценку через `POST /solutions/{id}/evaluations`.

**Демо-учётные записи** (создаются `seed.py`):

| Логин | Пароль | Роль |
|---|---|---|
| `admin` | `admin12345` | ADMIN |
| `jury1` | `jury12345` | JURY |
| `curator1` | `curator12345` | CURATOR |
| `captain1` | `captain12345` | CAPTAIN |

## 9. Вывод

В ходе работы разработано серверное приложение на FastAPI для системы проведения
хакатонов. Освоены: построение REST API и CRUD-операций, работа с ORM SQLModel и
PostgreSQL, проектирование связей между таблицами (one-to-one, one-to-many,
many-to-many) с вложенным отображением данных, версионирование схемы БД с помощью
Alembic, вынос настроек в переменные окружения и разделение проекта на слои.
Дополнительно реализованы регистрация, авторизация и аутентификация по JWT с
разграничением доступа по ролям — без использования сторонних библиотек безопасности.
Все требования трёх практик выполнены.
