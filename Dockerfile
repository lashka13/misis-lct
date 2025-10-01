FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && poetry install

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "misis_lct.main:app", "--host", "0.0.0.0", "--port", "8000"]

