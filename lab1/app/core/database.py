"""Подключение к БД: движок SQLAlchemy и фабрика сессий для SQLModel."""
from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

# echo=False — отключаем подробный лог SQL; pool_pre_ping — проверка живости соединения
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    """FastAPI-зависимость: выдаёт сессию БД и гарантированно закрывает её."""
    with Session(engine) as session:
        yield session
