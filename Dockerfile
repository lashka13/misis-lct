FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY src/ ./src/
COPY data/ ./data/

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "lct_gazprombank.main:app", "--host", "0.0.0.0", "--port", "8000"]
