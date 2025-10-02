# Примеры использования API

## Запуск сервера

```bash
poetry run uvicorn lct_gazprombank.main:app --host 0.0.0.0 --port 8000
```

## Примеры запросов

### 1. Проверка работоспособности

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok",
  "service": "Review Analysis API"
}
```

### 2. Получение списка категорий

```bash
curl http://localhost:8000/categories
```

**Ответ:**
```json
[
  "Дебетовые карты",
  "Кредитные карты",
  "Ипотека",
  "Автокредиты",
  "Кредиты",
  "Реструктуризация",
  "Вклады",
  "Переводы",
  "Дистанционное обслуживание",
  "Мобильное приложение",
  "Обслуживание",
  "Прочее"
]
```

### 3. Классификация отзывов (основной эндпоинт по ТЗ)

**Согласно ТЗ раздел 2.4.1: принимает только id и text**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 1,
        "text": "Отличный банк! Быстро одобрили ипотеку, менеджеры профессиональные."
      },
      {
        "id": 2,
        "text": "Мобильное приложение постоянно виснет, невозможно пользоваться!"
      },
      {
        "id": 3,
        "text": "Кредитная карта с хорошими условиями, но обслуживание в отделении оставляет желать лучшего."
      }
    ]
  }'
```

**Ответ:**
```json
{
  "predictions": [
    {
      "id": 1,
      "text": "Отличный банк! Быстро одобрили ипотеку, менеджеры профессиональные.",
      "topics": ["Ипотека", "Обслуживание"],
      "sentiments": ["положительно", "положительно"],
      "date": null,
      "source": null
    },
    {
      "id": 2,
      "text": "Мобильное приложение постоянно виснет, невозможно пользоваться!",
      "topics": ["Мобильное Приложение"],
      "sentiments": ["отрицательно"],
      "date": null,
      "source": null
    },
    {
      "id": 3,
      "text": "Кредитная карта с хорошими условиями, но обслуживание в отделении оставляет желать лучшего.",
      "topics": ["Кредитные Карты", "Обслуживание"],
      "sentiments": ["положительно", "отрицательно"],
      "date": null,
      "source": null
    }
  ]
}
```

### 3.1. Загрузка исторических данных (для дашборда)

**Для наполнения базы данными с датами используйте /load-data**

```bash
curl -X POST http://localhost:8000/load-data \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 1,
        "text": "Отличный банк! Быстро одобрили ипотеку, менеджеры профессиональные.",
        "date": "2024-03-15T10:30:00",
        "source": "banki.ru"
      },
      {
        "id": 2,
        "text": "Мобильное приложение постоянно виснет, невозможно пользоваться!",
        "date": "2024-03-16T14:20:00",
        "source": "sravni.ru"
      },
      {
        "id": 3,
        "text": "Кредитная карта с хорошими условиями, но обслуживание в отделении оставляет желать лучшего.",
        "date": "2024-03-17T09:15:00",
        "source": "banki.ru"
      }
    ]
  }'
```

**Ответ:**
```json
{
  "loaded_count": 3,
  "predictions": [
    {
      "id": 1,
      "text": "Отличный банк! Быстро одобрили ипотеку, менеджеры профессиональные.",
      "topics": ["Ипотека", "Обслуживание"],
      "sentiments": ["положительно", "положительно"],
      "date": "2024-03-15T10:30:00",
      "source": "banki.ru"
    },
    {
      "id": 2,
      "text": "Мобильное приложение постоянно виснет, невозможно пользоваться!",
      "topics": ["Мобильное Приложение"],
      "sentiments": ["отрицательно"],
      "date": "2024-03-16T14:20:00",
      "source": "sravni.ru"
    },
    {
      "id": 3,
      "text": "Кредитная карта с хорошими условиями, но обслуживание в отделении оставляет желать лучшего.",
      "topics": ["Кредитные Карты", "Обслуживание"],
      "sentiments": ["положительно", "отрицательно"],
      "date": "2024-03-17T09:15:00",
      "source": "banki.ru"
    }
  ]
}
```

### 4. Получение всех отзывов

```bash
# Все отзывы
curl http://localhost:8000/reviews

# С фильтрацией по дате
curl "http://localhost:8000/reviews?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59"

# С фильтрацией по категориям
curl "http://localhost:8000/reviews?categories=Ипотека,Кредитные%20карты"

# С лимитом
curl "http://localhost:8000/reviews?limit=10"
```

### 5. Получение статистики

```bash
# Общая статистика
curl http://localhost:8000/statistics

# Статистика за период
curl "http://localhost:8000/statistics?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59"

# Статистика по конкретным категориям
curl "http://localhost:8000/statistics?categories=Ипотека,Кредитные%20карты"
```

**Пример ответа:**
```json
{
  "total_reviews": 150,
  "date_range": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-12-31T23:59:59"
  },
  "categories": [
    {
      "category": "Кредитные карты",
      "total_count": 45,
      "positive_count": 20,
      "neutral_count": 15,
      "negative_count": 10,
      "positive_percent": 44.44,
      "neutral_percent": 33.33,
      "negative_percent": 22.22
    },
    {
      "category": "Ипотека",
      "total_count": 30,
      "positive_count": 18,
      "neutral_count": 8,
      "negative_count": 4,
      "positive_percent": 60.0,
      "neutral_percent": 26.67,
      "negative_percent": 13.33
    }
  ]
}
```

### 6. Временная динамика

```bash
# По дням
curl "http://localhost:8000/statistics/timeline?granularity=day"

# По неделям
curl "http://localhost:8000/statistics/timeline?granularity=week"

# По месяцам с фильтром
curl "http://localhost:8000/statistics/timeline?granularity=month&categories=Ипотека"

# За период
curl "http://localhost:8000/statistics/timeline?start_date=2024-01-01T00:00:00&end_date=2024-06-30T23:59:59&granularity=month"
```

**Пример ответа:**
```json
{
  "categories": [
    {
      "category": "Кредитные карты",
      "timeline": [
        {
          "date": "2024-03-15",
          "positive": 5,
          "neutral": 3,
          "negative": 2,
          "total": 10
        },
        {
          "date": "2024-03-16",
          "positive": 3,
          "neutral": 4,
          "negative": 3,
          "total": 10
        }
      ]
    },
    {
      "category": "Ипотека",
      "timeline": [
        {
          "date": "2024-03-15",
          "positive": 8,
          "neutral": 2,
          "negative": 1,
          "total": 11
        }
      ]
    }
  ]
}
```

### 7. Удаление всех отзывов (для тестирования)

```bash
curl -X DELETE http://localhost:8000/reviews
```

## Тестирование с помощью Python скрипта

```bash
# Убедитесь, что сервер запущен
poetry run python test_api.py
```

## Swagger UI документация

После запуска сервера доступна интерактивная документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Примеры использования в Python

```python
import httpx
from datetime import datetime

async def classify_reviews():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/predict",
            json={
                "data": [
                    {
                        "id": 1,
                        "text": "Отличный банк!",
                        "date": datetime.now().isoformat(),
                        "source": "test"
                    }
                ]
            }
        )
        return response.json()

# Синхронный вариант
import requests

def get_statistics():
    response = requests.get("http://localhost:8000/statistics")
    return response.json()
```

## Формат даты

Все даты должны быть в формате ISO 8601:
- `2024-03-15T10:30:00` — с временем
- `2024-03-15T10:30:00+03:00` — с часовым поясом
- `2024-03-15T10:30:00Z` — UTC

## Коды ответов

- `200` — Успешный запрос
- `400` — Неверный формат данных
- `500` — Внутренняя ошибка сервера

## Лимиты

- Максимальное количество отзывов в одном запросе `/predict`: 250
- Максимальное время обработки: 3 минуты
- Батч размер: 10 отзывов (оптимизация под API лимиты)

