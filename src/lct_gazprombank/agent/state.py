from typing import Any, TypedDict


class ClassificationState(TypedDict):
    """Состояние агента для классификации отзывов"""

    available_categories: list[str]
    reviews: list[str]
    categories: list[list[str]]
    sentiments: list[dict[str, str]]
    rate_limiter: Any
