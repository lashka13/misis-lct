#50634 уникальных отзыва
import json

# Файл с отзывами
file_path = "reviews_full.json"

# Загружаем данные (словарь, где ключ — id, значение — словарь отзыва)
with open(file_path, "r", encoding="utf-8") as f:
    reviews_dict = json.load(f)

print(f"Всего отзывов: {len(reviews_dict)}")

# Считаем повторения
seen_texts = set()
duplicates = []

for review_id, review in reviews_dict.items():
    text = review.get("text", "").strip()
    if text in seen_texts:
        duplicates.append((review_id, text))
    else:
        seen_texts.add(text)

print(f"Уникальных отзывов (без повторов): {len(seen_texts)}")

if duplicates:
    print(f"Найдено повторяющихся отзывов: {len(duplicates)}")
    for i, (dup_id, dup_text) in enumerate(duplicates, 1):
        print(f"{i}: id={dup_id}, {dup_text[:100]}...")  # показываем id и первые 100 символов дубликата
else:
    print("Повторяющихся отзывов не найдено.")
