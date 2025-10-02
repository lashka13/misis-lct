# Мне показалось, что парсер vbr.ru работает направильно потому, что на сайте было написано, что отзывов 10000, а у меня уже
# >20000 набралось, поэтому я сделал этот скрипт для проверки уникальности и количества отзывов
# Скрипт показал, что все есть 4 уникальные и их количество действительно >20000 -> парсер работает исправно

import json
from collections import defaultdict

# Файл с отзывами
file_path = "vbr_reviews.json"

# Загружаем данные
with open(file_path, "r", encoding="utf-8") as f:
    reviews = json.load(f)

print(f"Всего отзывов: {len(reviews)}")

# Считаем повторения
text_counts = defaultdict(int)

for review in reviews:
    text = review.get("text", "").strip()
    text_counts[text] += 1

duplicates = [(text, count) for text, count in text_counts.items() if count > 1]

# Сортируем по убыванию количества повторений
duplicates_sorted = sorted(duplicates, key=lambda x: x[1], reverse=True)

if duplicates_sorted:
    print(f"Найдено повторяющихся отзывов: {len(duplicates_sorted)}")
    # for i, (dup, count) in enumerate(duplicates_sorted, 1):
    #     print(f"{i}: {dup[:100]}... (встречается {count} раз)")
else:
    print("Повторяющихся отзывов не найдено.")
