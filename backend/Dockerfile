# Базовый Образ на котором мы строимся
FROM python:3.13-slim

# Переменные
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.4.1 \
    POETRY_VIRTUALENVS_CREATE=false

# Рабочая директория внутри контейнера
WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# Установка Poetry
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

# Копируем Зависимости
COPY pyproject.toml poetry.lock* ./

# Установить зависимости
RUN poetry install --only main --no-root

# Копируем Код Приложения
COPY . .

RUN poetry install --only main

# порт который слушает наше приложения
EXPOSE 8000

# RUN  - выполняет команду при сборке
# CMD - команда которая запускается при старте контейнера

# uvicorn src.backend.main:app --host=0.0.0.0 --port=8000
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["make", "dev"]
