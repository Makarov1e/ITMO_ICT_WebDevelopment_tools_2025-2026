# Базовый образ для всех Python-сервисов ЛР3 (app, parser, worker)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

# Сначала зависимости — слой кешируется, пока requirements.txt не меняется
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Исходный код сервисов
COPY common ./common
COPY parser_service ./parser_service
COPY main_app ./main_app

# Команда запуска переопределяется в docker-compose для каждого сервиса
CMD ["uvicorn", "main_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
