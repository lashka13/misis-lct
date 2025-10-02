# Парсер https://www.vbr.ru/banki/otzivy/
# >20000 отзывов

import requests
from bs4 import BeautifulSoup
import html
import json
import os
import time
import random

save_file = "vbr_reviews.json"
all_reviews = []

# Загружаем уже собранные отзывы, если файл существует
if os.path.exists(save_file):
    with open(save_file, "r", encoding="utf-8") as f:
        all_reviews = json.load(f)
    print(f"Загружено {len(all_reviews)} отзывов из {save_file}")
else:
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)

# фиксируем стартовую страницу (2255)
page = 2255

while True:
    url = f"https://www.vbr.ru/api/reviews/?sorttype=date&companytype=bank&reviewtype=0&iscompanyrecommended=false&sortdirection=desc&pagesize=20&page={page}&append=false"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        if not resp.text.strip():
            raise ValueError("Пустой ответ от сервера")

        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"Ошибка на странице {page}: {e}. Ждём 10 секунд и пробуем снова...")
        time.sleep(10)
        continue

    review_cards = soup.find_all("div", class_="reviews-card")
    if not review_cards:
        print("Отзывы закончились.")
        break

    for card in review_cards:
        # оценка
        grade_tag = card.find("div", class_="rating-star-simple")
        grade = int(grade_tag.text.strip()) if grade_tag else None

        # дата
        date_tag = card.find("span", class_="avatar-title-date")
        date = date_tag.text.strip() if date_tag else None

        # текст
        text_tag = card.find("div", class_="reviews-text")
        raw_text = text_tag.get_text(separator=" ", strip=True) if text_tag else ""
        clean_text = html.unescape(raw_text)

        all_reviews.append({
            "grade": grade,
            "date": date,
            "text": clean_text
        })

    # сохраняем прогресс после каждой страницы
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)

    print(f"Страница {page} обработана, собрано {len(review_cards)} отзывов. Всего: {len(all_reviews)}")

    page += 1
    time.sleep(random.uniform(2, 5))  # пауза, чтобы не забанили
