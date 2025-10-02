FROM python:3.13-slim
WORKDIR /app

# только pyproject.toml
COPY pyproject.toml /app/

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# исходники backend
COPY api /app/api

EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]