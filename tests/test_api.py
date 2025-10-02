"""Скрипт для тестирования API."""

import asyncio

import httpx


async def test_api():
    """Тестирование всех эндпоинтов API"""

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(timeout=180.0) as client:
        print("🔍 Тестирование API Review Analysis\n")

        # 1. Проверка работоспособности
        print("1️⃣ GET /health")
        response = await client.get(f"{base_url}/health")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}\n")

        # 2. Получение категорий
        print("2️⃣ GET /categories")
        response = await client.get(f"{base_url}/categories")
        print(f"   Статус: {response.status_code}")
        categories = response.json()
        print(f"   Количество категорий: {len(categories)}")
        print(f"   Категории: {', '.join(categories[:5])}...\n")

        # 3. Классификация тестовых отзывов (только id и text по ТЗ)
        print("3️⃣ POST /predict (основной эндпоинт по ТЗ)")
        test_reviews = {
            "data": [
                {"id": 1, "text": "Отличное обслуживание в отделении, все быстро и вежливо!"},
                {"id": 2, "text": "Мобильное приложение постоянно зависает, очень неудобно."},
                {"id": 3, "text": "Кредитную карту одобрили быстро, но проценты высокие."},
            ]
        }

        response = await client.post(f"{base_url}/predict", json=test_reviews)
        print(f"   Статус: {response.status_code}")

        if response.status_code == 200:
            predictions = response.json()["predictions"]
            print(f"   Обработано отзывов: {len(predictions)}")
            for pred in predictions:
                print(f"\n   Отзыв #{pred['id']}:")
                print(f"   Текст: {pred['text'][:50]}...")
                print(f"   Темы: {', '.join(pred['topics'])}")
                print(f"   Тональность: {', '.join(pred['sentiments'])}")
        else:
            print(f"   Ошибка: {response.text}")

        print("\n" + "=" * 80 + "\n")

        # 3.1 Загрузка данных с датами (для дашборда)
        print("3️⃣.1 POST /load-data (загрузка исторических данных)")
        load_data_reviews = {
            "data": [
                {
                    "id": 101,
                    "text": "Отличный банк! Быстро одобрили ипотеку.",
                    "date": "2024-03-15T10:30:00",
                    "source": "banki.ru",
                },
                {
                    "id": 102,
                    "text": "Мобильное приложение виснет постоянно!",
                    "date": "2024-03-16T14:20:00",
                    "source": "sravni.ru",
                },
                {
                    "id": 103,
                    "text": "Кредитная карта с хорошими условиями.",
                    "date": "2024-03-17T09:15:00",
                    "source": "banki.ru",
                },
            ]
        }

        response = await client.post(f"{base_url}/load-data", json=load_data_reviews)
        print(f"   Статус: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   Загружено отзывов: {result['loaded_count']}")
        else:
            print(f"   Ошибка: {response.text}")

        print("\n" + "=" * 80 + "\n")

        # 4. Получение всех отзывов
        print("4️⃣ GET /reviews")
        response = await client.get(f"{base_url}/reviews")
        print(f"   Статус: {response.status_code}")

        if response.status_code == 200:
            reviews = response.json()
            print(f"   Всего отзывов в базе: {len(reviews)}\n")

        # 5. Статистика
        print("5️⃣ GET /statistics")
        response = await client.get(f"{base_url}/statistics")
        print(f"   Статус: {response.status_code}")

        if response.status_code == 200:
            stats = response.json()
            print(f"   Всего отзывов: {stats['total_reviews']}")
            if stats["date_range"]["start"]:
                print(f"   Диапазон дат: {stats['date_range']['start']} — {stats['date_range']['end']}")
            print("\n   Статистика по категориям:")
            for cat_stat in stats["categories"][:5]:
                print(f"   • {cat_stat['category']}: {cat_stat['total_count']} отзывов")
                print(
                    f"     ↳ ✅ {cat_stat['positive_percent']}% | "
                    f"➖ {cat_stat['neutral_percent']}% | "
                    f"❌ {cat_stat['negative_percent']}%"
                )

        print("\n" + "=" * 80 + "\n")

        # 6. Временная динамика
        print("6️⃣ GET /statistics/timeline")
        response = await client.get(f"{base_url}/statistics/timeline?granularity=day")
        print(f"   Статус: {response.status_code}")

        if response.status_code == 200:
            timeline = response.json()
            print(f"   Категорий с динамикой: {len(timeline['categories'])}")
            if timeline["categories"]:
                cat = timeline["categories"][0]
                print(f"\n   Пример (категория '{cat['category']}'):")
                for point in cat["timeline"][:3]:
                    print(
                        f"   {point['date']}: ✅ {point['positive']} | ➖ {point['neutral']} | ❌ {point['negative']}"
                    )

        print("\n✨ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_api())
