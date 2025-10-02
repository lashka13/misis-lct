import requests
import json
import time
import os

output_file = "sravni_reviews.json"

categories = {
    "refinanceMortgage": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&SqueezesVectorIds=&ReviewObjectType=banks&Tag=mortgageRefinancing&PageSize=50",
    "currency": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&ReviewObjectType=banks&Tag=currencyExchange&PageSize=50",
    "mobileApp": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&ReviewObjectType=banks&Tag=mobilnoyeprilozheniye&PageSize=50",
    "conditions": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&ReviewObjectType=banks&Tag=usloviya&PageSize=50",
    "transfers": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&ReviewObjectType=banks&Tag=moneyOrder&PageSize=50",
    "rko": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&ReviewObjectType=banks&Tag=businessRko&PageSize=50",
    "acquiring": "https://www.sravni.ru/proxy-reviews/reviews?ReviewObjectId=5bb4f768245bc22a520a6115&ReviewObjectType=banks&Tag=acquiring&PageSize=50"
}

FIELDS_TO_KEEP = [
    "commentsCount", "date", "title", "text", "reviewTag", "isLegal",
    "specificProductName", "rating", "ratingStatus", "problemSolved",
    "userDataStatus", "votes", "vote", "isRecommendedByUser",
    "positiveTags", "negativeTags", "hasCompanyResponse", "isAboutSravni"
]

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_category(category_name, base_url, all_reviews):
    print(f"\n=== Парсим категорию {category_name} ===")

    try:
        # Первый запрос — без PageIndex
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Ошибка при запросе первой страницы: {e}")
        return

    items = data.get("items", [])
    total = data.get("total", 0)

    if not items:
        print(f"⚠️ В категории {category_name} нет отзывов (total={total})")
        return

    for item in items:
        filtered_item = {k: item.get(k) for k in FIELDS_TO_KEEP}
        filtered_item["category"] = category_name
        all_reviews.append(filtered_item)

    save_json(all_reviews, output_file)
    print(f"Первая страница готова, всего собрано {len(all_reviews)} отзывов")

    # Если total > PageSize → продолжаем с PageIndex=2
    page_size = data.get("pageSize", 50)
    if total > page_size:
        page = 2
        while len(items) > 0:
            url = f"{base_url}&PageIndex={page}"
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
            except Exception as e:
                print(f"Ошибка на {page}-й странице: {e}")
                break

            if not items:
                print(f"✅ Отзывы в категории {category_name} закончились.")
                break

            for item in items:
                filtered_item = {k: item.get(k) for k in FIELDS_TO_KEEP}
                filtered_item["category"] = category_name
                all_reviews.append(filtered_item)

            save_json(all_reviews, output_file)
            print(f"Страница {page} готова, всего собрано {len(all_reviews)} отзывов")
            page += 1
            time.sleep(1)

def parse_all_categories():
    all_reviews = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            all_reviews = json.load(f)
        print(f"Загружено {len(all_reviews)} отзывов из файла {output_file}")

    for cat_name, url in categories.items():
        parse_category(cat_name, url, all_reviews)

    print(f"\n✅ Парсинг завершён. Всего собрано {len(all_reviews)} отзывов.")
    return all_reviews

if __name__ == "__main__":
    parse_all_categories()
