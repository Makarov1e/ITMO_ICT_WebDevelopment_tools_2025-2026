# Эндпоинты API

Интерактивная документация (Swagger UI) доступна на `/docs`, схема OpenAPI — на `/openapi.json`.
Исходники роутеров: [`app/api/routers/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/app/api/routers).

Обозначения: 🔑 — требуется JWT, 👑 — только `ADMIN`, ⚖️ — только `JURY`.

## Аутентификация — [`auth.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/routers/auth.py)

| Метод | Путь | Описание | Доступ |
|---|---|---|---|
| POST | `/auth/register` | Регистрация пользователя | публичный |
| POST | `/auth/login` | Авторизация, выдача JWT | публичный |

## Пользователи — [`users.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/routers/users.py)

| Метод | Путь | Описание | Доступ |
|---|---|---|---|
| GET | `/users/me` | Текущий пользователь (по JWT) | 🔑 |
| POST | `/users/me/change-password` | Смена пароля | 🔑 |
| GET | `/users` | Список пользователей | 🔑 |
| GET | `/users/{user_id}` | Пользователь по id | 🔑 |
| PATCH | `/users/{user_id}` | Обновление профиля (себя или 👑) | 🔑 |

## Задачи и теги — [`tasks.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/routers/tasks.py)

| Метод | Путь | Описание | Доступ |
|---|---|---|---|
| GET | `/tasks` | Список задач (с вложенными тегами/куратором/ссылками) | 🔑 |
| GET | `/tasks/{task_id}` | Задача по id (вложенные объекты) | 🔑 |
| POST | `/tasks` | Создать задачу | 👑 |
| PATCH | `/tasks/{task_id}` | Обновить задачу | 👑 |
| DELETE | `/tasks/{task_id}` | Удалить задачу | 👑 |
| GET | `/tasks/tags/all` | Список тегов | 🔑 |
| POST | `/tasks/tags` | Создать тег | 👑 |

## Команды — [`teams.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/routers/teams.py)

| Метод | Путь | Описание | Доступ |
|---|---|---|---|
| GET | `/teams` | Список команд (с вложенными участниками) | 🔑 |
| GET | `/teams/{team_id}` | Команда по id (вложенные объекты) | 🔑 |
| POST | `/teams` | Создать команду (с участниками) | 🔑 |
| PATCH | `/teams/{team_id}` | Обновить команду | 🔑 |
| DELETE | `/teams/{team_id}` | Удалить команду | 🔑 |
| POST | `/teams/{team_id}/members` | Добавить участника | 🔑 |

## Решения и оценки — [`solutions.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/routers/solutions.py)

| Метод | Путь | Описание | Доступ |
|---|---|---|---|
| GET | `/solutions` | Список решений (вложенные оценки + средний балл) | 🔑 |
| GET | `/solutions/{solution_id}` | Решение по id | 🔑 |
| POST | `/solutions` | Создать решение | 🔑 |
| PATCH | `/solutions/{solution_id}` | Обновить решение | 🔑 |
| DELETE | `/solutions/{solution_id}` | Удалить решение | 🔑 |
| POST | `/solutions/{solution_id}/evaluations` | Оценить решение | ⚖️ |

## Примеры запросов

### Регистрация и логин

```bash
curl -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345","role":"ADMIN"}'

curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}'
# -> {"access_token":"<JWT>","token_type":"bearer"}
```

### Запрос с токеном

```bash
curl http://127.0.0.1:8001/users/me \
  -H "Authorization: Bearer <JWT>"
```

### Создание задачи с тегами и ресурсами (👑)

```bash
curl -X POST http://127.0.0.1:8001/tasks \
  -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
  -d '{"title":"Рекомендательная система","description":"ML","curator_id":4,
       "tag_ids":[1,2],"resource_links":[{"title":"Датасет","url":"https://x/ds"}]}'
```

### GET решения с вложенными оценками и средним баллом

```json
{
  "id": 1, "title": "RecoEngine", "status": "SUBMITTED",
  "team": {"id": 1, "name": "CodeStorm"},
  "task": {"id": 1, "title": "Рекомендательная система"},
  "evaluations": [
    {"id": 1, "score": 9, "comment": "Отлично",
     "jury_member": {"id": 2, "username": "jury1", "role": "JURY"}}
  ],
  "avg_score": 9.0
}
```
