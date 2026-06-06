# Установка и соединение с БД

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Создание БД (PostgreSQL)

```sql
CREATE ROLE hackathon_user LOGIN PASSWORD 'hackathon_password';
CREATE DATABASE hackathon_fastapi OWNER hackathon_user;
```

## Переменные окружения (`.env`)

```ini
DATABASE_URL=postgresql+psycopg2://hackathon_user:hackathon_password@localhost:5432/hackathon_fastapi
JWT_SECRET=dev-super-secret-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Конфигурация

Настройки читаются из `.env` через `pydantic-settings`.
Файл [`app/core/config.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/core/config.py):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://hackathon_user:hackathon_password@localhost:5432/hackathon_fastapi"
    jwt_secret: str = "dev-super-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
```

## Код соединения с БД

Файл [`app/core/database.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/core/database.py):

```python
from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

# echo=False — без подробного лога SQL; pool_pre_ping — проверка живости соединения
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    """FastAPI-зависимость: выдаёт сессию БД и гарантированно закрывает её."""
    with Session(engine) as session:
        yield session
```

## Миграции (Alembic)

`alembic/env.py` подключает метаданные SQLModel и берёт URL из настроек приложения:

```python
from sqlmodel import SQLModel
from app.core.config import settings
import app.models  # noqa: F401  — регистрирует таблицы в SQLModel.metadata

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = SQLModel.metadata
```

Команды:

```bash
# применить миграции
alembic upgrade head

# сгенерировать новую миграцию после изменения моделей
alembic revision --autogenerate -m "описание"
```

## Запуск и наполнение данными

```bash
uvicorn app.main:app --reload --port 8001   # сервер + Swagger на /docs
python seed.py                              # демо-данные (идемпотентно)
```

- Swagger UI: <http://127.0.0.1:8001/docs>
- OpenAPI JSON: <http://127.0.0.1:8001/openapi.json>
