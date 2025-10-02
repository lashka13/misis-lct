#4198 уникальных отзыва
# Проверка уникальности отзывов в файле sravni_reviews.json (массив словарей)
import json

# Файл с отзывами
file_path = "sravni_reviews.json"

# Загружаем данные (список словарей)
with open(file_path, "r", encoding="utf-8") as f:
    reviews_list = json.load(f)

print(f"Всего отзывов: {len(reviews_list)}")

# Считаем повторения
seen_texts = set()
duplicates = []

for idx, review in enumerate(reviews_list):
    text = review.get("text", "").strip()
    if text in seen_texts:
        duplicates.append((idx, text))
    else:
        seen_texts.add(text)

print(f"Уникальных отзывов (без повторов): {len(seen_texts)}")

if duplicates:
    print(f"Найдено повторяющихся отзывов: {len(duplicates)}")
    for i, (dup_idx, dup_text) in enumerate(duplicates, 1):
        print(f"{i}: индекс={dup_idx}, {dup_text[:100]}...")  # показываем индекс и первые 100 символов дубликата
else:
    print("Повторяющихся отзывов не найдено.")
