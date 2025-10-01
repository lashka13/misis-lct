"""Схемы для работы с отзывами."""

from pydantic import BaseModel, Field


class ReviewInput(BaseModel):
    """Входные данные отзыва для предсказания"""

    id: int = Field(description="Уникальный идентификатор отзыва")
    text: str = Field(description="Текст отзыва")


class ClassificationRequest(BaseModel):
    """Запрос на классификацию"""

    reviews: list[ReviewInput] = Field(description="Список отзывов для анализа")


class ClassificationPrediction(BaseModel):
    """Классификация для одного отзыва"""

    id: int = Field(description="Идентификатор отзыва")
    topics: list[str] = Field(description="Список тем отзыва")
    sentiments: list[str] = Field(description="Список тональностей для каждой темы")


class ClassificationResponse(BaseModel):
    """Ответ с предсказаниями"""

    predictions: list[ClassificationPrediction] = Field(description="Список предсказаний")