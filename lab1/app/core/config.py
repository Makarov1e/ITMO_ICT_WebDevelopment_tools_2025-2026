"""Конфигурация приложения, читаемая из переменных окружения (.env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Подключение к PostgreSQL (SQLAlchemy URL)
    database_url: str = "postgresql+psycopg2://hackathon_user:hackathon_password@localhost:5432/hackathon_fastapi"

    # Параметры JWT
    jwt_secret: str = "dev-super-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Единый экземпляр настроек на всё приложение
settings = Settings()
