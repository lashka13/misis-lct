FROM python:3.11-slim

WORKDIR /app

# Копирование и установка зависимостей
COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Копирование кода и данных
COPY src/ ./src/
COPY data/ ./data/

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["poetry", "run", "uvicorn", "lct_gazprombank.main:app", "--host", "0.0.0.0", "--port", "8000"]
