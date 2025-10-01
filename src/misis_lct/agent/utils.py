"""Утилиты для агента."""

import asyncio
import json
import re
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from misis_lct.core.config import GOOGLE_API_KEY, LLM_NAME

model_exception_message = """Ошибка при инициализации языковой модели (LLM):
Убедитесь, что указан верный API ключ в .env файле.
Gemini модель из Google AI Studio не поддерживается на территории Российской Федерации.
Для корректной работы модели необходимо использовать VPN.
Не все VPN сервисы работают корректно: бывают случаи некорректного обхода блокировок или длительных задержек при вызове модели.
Стабильно работает бесплатный VPN Proxy Master (доступен в AppStore). Может потребоваться множественное переподключение VPN."""


class LLM:
    """Обертка над моделью для вызова с повторением при превышении квоты/лимита запросов."""

    def __init__(self) -> None:
        """
        Получить Gemini модель из Google AI Studio.

        Raises:
            RuntimeError: Ошибка при инициализации языковой модели
        """
        try:
            llm = ChatGoogleGenerativeAI(
                model=LLM_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.0,
            )

            _ = llm.invoke("Hello!")

            self.llm = llm

        except Exception:
            raise RuntimeError(model_exception_message) from None

    async def _arun_with_retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Выполнить функцию с повторными попытками при ошибках"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_text = str(e)
                is_quota = "429" in error_text or "ResourceExhausted" in error_text or "quota" in error_text.lower()

                if not is_quota or attempt == max_retries - 1:
                    raise

                print("Превышен лимит API, ожидание 60 секунд...")
                await asyncio.sleep(60)

        raise RuntimeError(f"Не удалось выполнить запрос после {max_retries} попыток")

    def _wrap_runnable(self, runnable: Any) -> Any:
        """Обёртка runnable: синхронные и асинхронные вызовы через ретраи"""

        async def ainvoke(*args: Any, **kwargs: Any) -> Any:
            return await self._arun_with_retry(runnable.ainvoke, *args, **kwargs)

        async def astream(*args: Any, **kwargs: Any) -> Any:
            return await self._arun_with_retry(runnable.astream, *args, **kwargs)

        return SimpleNamespace(
            ainvoke=ainvoke,
            astream=astream,
        )

    def bind_tools(self, *args: Any, **kwargs: Any) -> Any:
        """Привязать инструменты к модели"""
        return self._wrap_runnable(self.llm.bind_tools(*args, **kwargs))

    def with_structured_output(self, *args: Any, **kwargs: Any) -> Any:
        """Получить структурированный вывод"""
        return self._wrap_runnable(self.llm.with_structured_output(*args, **kwargs))

    async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
        """Асинхронный вызов модели"""
        return await self._arun_with_retry(self.llm.ainvoke, *args, **kwargs)

    async def astream(self, *args: Any, **kwargs: Any) -> Any:
        """Асинхронный стрим модели"""
        return await self._arun_with_retry(self.llm.astream, *args, **kwargs)


def format_reviews(reviews: list[str]) -> str:
    """Форматирование списка отзывов в читаемый текст.

    Args:
        reviews: Список текстов отзывов

    Returns:
        Отформатированная строка с пронумерованными отзывами
    """
    formatted_reviews = ""
    for i, review in enumerate(reviews, 1):
        formatted_reviews += f"\n{i}. Отзыв (ID={i}):\n{review}\n"
        formatted_reviews += "-" * 100 + "\n"
    return formatted_reviews


def format_reviews_with_categories(reviews: list[str], categories: list[list[str]]) -> str:
    """Форматирование списка отзывов с категориями в читаемый текст

    Args:
        reviews: Список текстов отзывов
        categories: Список категорий для каждого отзыва

    Returns:
        Отформатированная строка с отзывами и их категориями
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
    """Парсинг ответа модели в список категорий для каждого отзыва.

    Args:
        response: Ответ модели

    Returns:
        Список категорий для каждого отзыва

    Raises:
        ValueError: Если не удалось распарсить ответ
    """
    try:
        content = response.content
        content = clean_json_response(content)

        data = json.loads(content)
        reviews_data = data.get("reviews", [])

        if not reviews_data:
            raise ValueError("Ответ не содержит данных о отзывах")

        reviews_data.sort(key=lambda x: x.get("review_id", 0))
        reviews_categories = []
        for review in reviews_data:
            categories = review.get("categories", ["other"])
            if not categories:
                categories = ["other"]
            reviews_categories.append(categories)

        return reviews_categories

    except Exception as e:
        raise ValueError(f"Ошибка парсинга ответа модели в категории: {e}") from e


def parse_review_sentiments(response: AIMessage) -> list[dict[str, str]]:
    """
    Парсинг ответа модели в список тональностей для каждого отзыва

    Args:
        response: Ответ модели

    Returns:
        Список словарей {категория: тональность} для каждого отзыва

    Raises:
        ValueError: Если не удалось распарсить ответ
    """
    try:
        content = response.content
        content = clean_json_response(content)

        data = json.loads(content)
        reviews_data = data.get("reviews", [])

        if not reviews_data:
            raise ValueError("Ответ не содержит данных о отзывах")

        reviews_data.sort(key=lambda x: x.get("review_id", 0))

        reviews_sentiments = []
        for review in reviews_data:
            sentiments = review.get("sentiments", {})

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


# Синглтон
llm = LLM()
