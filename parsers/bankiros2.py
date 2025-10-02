import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os

save_file = "bankiros_reviews2.json"

# Загружаем уже собранные отзывы
if os.path.exists(save_file):
    with open(save_file, "r", encoding="utf-8") as f:
        all_reviews = json.load(f)
    print(f"Загружено {len(all_reviews)} отзывов из существующего файла.")
else:
    all_reviews = []
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=4)

# Стартовая страница (можно указать вручную)
start_page = len(all_reviews) // 10 + 1
page = start_page
has_next = True

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def get_full_review(full_url):
    """Получаем полный текст отзыва по ссылке"""
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        resp = requests.get(full_url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        content_div = soup.find("div", class_="xxx-review__content")
        if content_div:
            return content_div.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Ошибка при загрузке полного отзыва {full_url}: {e}")
    return None

while has_next:
    print(f"📄 Парсим список, страница {page}...")
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        url = f"https://bankiros.ru/review/show-more?bank_id=131&limit=10&sort=-date&page={page}"
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        has_next = data.get("issetNext", False)
        soup = BeautifulSoup(data["reviews"], "html.parser")
        review_cards = soup.find_all("div", class_="xxx-reviews-card__body")

        for card in review_cards:
            # рейтинг
            rating_span = card.find("div", class_="xxx-reviews-rating")
            rating_text = rating_span.find("span").text.strip() if rating_span else "0 из 5"
            rating = int(rating_text.split()[0])

            # текст
            content = card.find("p", class_="xxx-reviews-card__content")
            review_text = content.get_text(separator=" ", strip=True) if content else ""

            # Смотрим, есть ли "Читать далее"
            full_link_tag = content.find("a", href=True) if content else None
            if full_link_tag and "otzyv" in full_link_tag["href"]:
                full_url = full_link_tag["href"]
                if full_url.startswith("/"):
                    full_url = "https://bankiros.ru" + full_url
                full_text = get_full_review(full_url)
                if full_text:
                    review_text = full_text
                time.sleep(random.uniform(2, 5))  # пауза после запроса полного отзыва

            all_reviews.append({
                "rating": rating,
                "review": review_text
            })

        # Сохраняем после каждой страницы
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=4)

        print(f"✅ Страница {page} готова. Найдено {len(review_cards)} отзывов. Всего сохранено: {len(all_reviews)}")

        page += 1
        time.sleep(random.uniform(5, 10))  # пауза между страницами

    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            wait = random.uniform(30, 60)
            print(f"Сайт заблокировал запрос (429). Ждём {int(wait)} секунд...")
            time.sleep(wait)
        else:
            print(f"HTTP ошибка на странице {page}: {e}. Ждём 10 секунд...")
            time.sleep(10)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса на странице {page}: {e}. Ждём 10 секунд...")
        time.sleep(10)

print(f"Готово! Всего отзывов сохранено: {len(all_reviews)}")
