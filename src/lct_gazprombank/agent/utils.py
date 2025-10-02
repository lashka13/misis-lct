"""Утилиты для агента."""

import asyncio
import json
import re
import time
from collections import deque

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from lct_gazprombank.core import settings


class RateLimiter:
    """Rate limiter для ограничения количества запросов в минуту"""

    def __init__(self, max_requests_per_minute: int):
        """Инициализация rate limiter

        Args:
            max_requests_per_minute (int): Максимальное количество запросов в минуту
        """
        self.max_requests = max_requests_per_minute
        self.requests = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Ожидание возможности сделать запрос с учетом rate limit"""
        async with self._lock:
            now = time.time()

            while self.requests and self.requests[0] < now - 60:
                self.requests.popleft()

            if len(self.requests) >= self.max_requests:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    now = time.time()
                    while self.requests and self.requests[0] < now - 60:
                        self.requests.popleft()

            self.requests.append(time.time())


def format_reviews(reviews: list[str]) -> str:
    """Форматирование списка отзывов в читаемый текст

    Args:
        reviews (list[str]): Список текстов отзывов

    Returns:
        str: Отформатированная строка с пронумерованными отзывами
    """
    formatted_reviews = ""
    for i, review in enumerate(reviews, 1):
        formatted_reviews += f"\n{i}. Отзыв (ID={i}):\n{review}\n"
        formatted_reviews += "-" * 100 + "\n"
    return formatted_reviews


def format_reviews_with_categories(reviews: list[str], categories: list[list[str]]) -> str:
    """Форматирование списка отзывов с категориями в читаемый текст

    Args:
        reviews (list[str]): Список текстов отзывов
        categories (list[list[str]]): Список категорий для каждого отзыва

    Returns:
        str: Отформатированная строка с отзывами и их категориями
    """
    formatted_reviews = ""
    for i, (review, cats) in enumerate(zip(reviews, categories, strict=True), 1):
        formatted_reviews += f"\n{i}. Отзыв (ID={i}):\n"
        formatted_reviews += f"Категории: {', '.join(cats)}\n"
        formatted_reviews += f"Текст: {review}\n"
        formatted_reviews += "-" * 100 + "\n"
    return formatted_reviews


def clean_json_response(response: AIMessage) -> str:
    """Очистить ответ от markdown форматирования и извлечь JSON

    Args:
        response (AIMessage): Ответ модели

    Returns:
        str: Чистый JSON текст
    """
    content = response.content
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content)
    content = content.strip()

    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if json_match:
        content = json_match.group(0)

    return content


def parse_review_categories(response: AIMessage) -> list[list[str]]:
    """Парсинг ответа модели в список категорий для каждого отзыва

    Args:
        response (AIMessage): Ответ модели

    Returns:
        list[list[str]]: Список категорий для каждого отзыва

    Raises:
        ValueError: Код 400 - Если не удалось распарсить ответ
    """
    try:
        content = clean_json_response(response)
        data = json.loads(content)
        reviews = data["reviews"]
        reviews.sort(key=lambda x: x["review_id"])

        reviews_categories = []
        for review in reviews:
            categories = review["categories"]
            categories_normalized = [category.title().strip() for category in categories]
            reviews_categories.append(categories_normalized)
        return reviews_categories

    except Exception as e:
        raise ValueError(f"Ошибка парсинга ответа модели в категории: {e}") from e


def parse_review_sentiments(response: AIMessage) -> list[dict[str, str]]:
    """Парсинг ответа модели в список тональностей для каждого отзыва

    Args:
        response (AIMessage): Ответ модели

    Returns:
        list[dict[str, str]]: Список словарей {категория: тональность} для каждого отзыва

    Raises:
        ValueError: Код 400 - Если не удалось распарсить ответ
    """
    try:
        content = clean_json_response(response)
        data = json.loads(content)
        reviews = data["reviews"]
        reviews.sort(key=lambda x: x["review_id"])

        reviews_sentiments = []
        for review in reviews:
            sentiments = review["sentiments"]

            normalized_sentiments = {}
            for category, sentiment in sentiments.items():
                sentiment_normalized = sentiment.lower().strip()

                if sentiment_normalized not in ["положительно", "нейтрально", "отрицательно"]:
                    sentiment_normalized = "нейтрально"

                normalized_sentiments[category] = sentiment_normalized

            reviews_sentiments.append(normalized_sentiments)

        return reviews_sentiments

    except Exception as e:
        raise ValueError(f"Ошибка парсинга ответа модели в тональности: {e}") from e


def setup_llm() -> None:
    llm = ChatOpenAI(
        model=settings.LLM_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,
    )

    return llm


# Синглтон
llm = setup_llm()
