# К большому сожалению, после многочасового парсинга, я обнаржуил, что все отзывы заканчиваются на Читать далее

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os

save_file = "bankiros_reviews.json"

# Загружаем уже существующие отзывы
if os.path.exists(save_file):
    with open(save_file, "r", encoding="utf-8") as f:
        all_reviews = json.load(f)
    print(f"Загружено {len(all_reviews)} отзывов из существующего файла.")
else:
    all_reviews = []
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=4)

# Начальная страница
page = 691
has_next = True

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

while has_next:
    print(f"Парсим страницу {page}...")
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        url = f"https://bankiros.ru/review/show-more?bank_id=131&limit=10&sort=-date&page={page}"
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        # Проверяем, есть ли следующий блок
        has_next = data.get("issetNext", False)

        # Парсим HTML из 'reviews'
        soup = BeautifulSoup(data["reviews"], "html.parser")
        review_cards = soup.find_all("div", class_="xxx-reviews-card__body")

        for card in review_cards:
            # Рейтинг
            rating_span = card.find("div", class_="xxx-reviews-rating")
            rating_text = rating_span.find("span").text.strip() if rating_span else "0 из 5"
            rating = int(rating_text.split()[0])

            # Текст отзыва
            content = card.find("p", class_="xxx-reviews-card__content")
            review_text = content.get_text(separator=" ", strip=True) if content else ""

            all_reviews.append({"rating": rating, "review": review_text})

        print(f"Страница {page} спарсена, найдено {len(review_cards)} отзывов. Всего: {len(all_reviews)}")

        # Сохраняем прогресс
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=4)

        page += 1
        time.sleep(random.uniform(5, 10))  # рандомная пауза между запросами

    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            wait = random.uniform(20, 40)  # длинная пауза при 429
            print(f"Сайт заблокировал запрос (429). Ждём {int(wait)} секунд...")
            time.sleep(wait)
        else:
            print(f"HTTP ошибка на странице {page}: {e}. Пробуем снова через 10 секунд...")
            time.sleep(10)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса на странице {page}: {e}. Пробуем снова через 10 секунд...")
        time.sleep(10)

print(f"Готово! Всего отзывов сохранено: {len(all_reviews)}")
