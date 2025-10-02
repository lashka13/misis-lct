import requests
import time
import json
import os
import random
import re
import html

# категории продуктов
CATEGORIES = {
    "debitcards": "debitcards",
    "creditcards": "creditcards",
    "hypothec": "hypothec",
    "autocredits": "autocredits",
    "credits": "credits",
    "restructing": "restructing",
    "deposits": "deposits",
    "transfers": "transfers",
    "remote": "remote",
    "other": "other",
    "mobile_app": "mobile_app",
    "individual": "individual"
}

# типы отзывов
TYPES = {
    "all": {"param": {"type": "all"}},
    "with_answer": {"param": {"type": "is_with_agent_answer"}},
    "resolved": {"param": {"type": "resolution_is_approved"}},
    "countable": {"param": {"is_countable": "on"}},
}

BASE_URL = "https://www.banki.ru/services/responses/list/ajax/"
SAVE_FILE = "reviews_full.json"

# Загружаем уже собранные отзывы
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        all_reviews = json.load(f)
    print(f"Найден файл {SAVE_FILE}, загружено {len(all_reviews)} отзывов")
else:
    all_reviews = {}

# очистка html-тегов
def clean_html(raw_text):
    raw_text = html.unescape(raw_text or "")
    clean_text = re.sub(r"<.*?>", "", raw_text)
    return clean_text.strip()

# нужные поля
FIELDS = [
    "id", "title", "text", "grade", "commentCount", "isCountable",
    "dateCreate", "resolutionIsApproved", "agentAnswerText", "hasDocuments"
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

# обходим все категории и типы
for category, product in CATEGORIES.items():
    for type_name, type_params in TYPES.items():
        print(f"\n==== Парсим категорию: {category}, тип: {type_name} ====")
        page = 1

        while True:
            params = {"bank": "gazprombank", "product": product, "page": page}
            params.update(type_params["param"])

            try:
                resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"Ошибка на странице {page} ({category}, {type_name}): {e}")
                print("Ждём 10 секунд и пробуем снова...")
                time.sleep(10)
                continue

            reviews = data.get("data", [])
            if not reviews:
                print(f"Отзывы закончились для {category}, {type_name}")
                break

            for item in reviews:
                review_id = str(item.get("id"))
                if not review_id:
                    continue

                if review_id not in all_reviews:
                    cleaned = {k: item.get(k) for k in FIELDS}
                    cleaned["text"] = clean_html(cleaned.get("text"))
                    cleaned["categories"] = [category]
                    cleaned["types"] = [type_name]
                    all_reviews[review_id] = cleaned
                else:
                    # обновляем категории и типы
                    if category not in all_reviews[review_id]["categories"]:
                        all_reviews[review_id]["categories"].append(category)
                    if type_name not in all_reviews[review_id]["types"]:
                        all_reviews[review_id]["types"].append(type_name)

            # сохраняем прогресс после каждой страницы
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(all_reviews, f, ensure_ascii=False, indent=2)

            print(f"Категория {category}, тип {type_name}, стр. {page}: {len(reviews)} отзывов. Всего: {len(all_reviews)}")

            page += 1
            time.sleep(random.uniform(2, 5))  # пауза

print(f"\nПарсинг завершён. Всего сохранено {len(all_reviews)} уникальных отзывов в {SAVE_FILE}")
