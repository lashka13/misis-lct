from datetime import datetime

from pydantic import BaseModel, Field


class ReviewInput(BaseModel):
    """Входной отзыв для классификации"""

    id: int = Field(description="Уникальный идентификатор отзыва")
    text: str = Field(description="Текст отзыва")


class ReviewInputWithMetadata(BaseModel):
    """Входной отзыв с дополнительными метаданными (для загрузки исторических данных)"""

    id: int = Field(description="Уникальный идентификатор отзыва")
    text: str = Field(description="Текст отзыва")
    date: datetime = Field(description="Дата отзыва")
    source: str | None = Field(default=None, description="Источник отзыва (banki.ru, sravni.ru и др.)")


class ReviewOutput(BaseModel):
    """Выходной классифицированный отзыв"""

    id: int = Field(description="Идентификатор отзыва")
    text: str = Field(description="Текст отзыва")
    topics: list[str] = Field(description="Список тем отзыва")
    sentiments: list[str] = Field(description="Список тональностей для каждой темы")
    date: datetime | None = Field(default=None, description="Дата отзыва")
    source: str | None = Field(default=None, description="Источник отзыва")


class PredictRequest(BaseModel):
    """Запрос на предсказание"""

    data: list[ReviewInput] = Field(description="Список отзывов для анализа")


class PredictResponse(BaseModel):
    """Ответ с предсказаниями"""

    predictions: list[ReviewOutput] = Field(description="Список предсказаний")


class LoadDataRequest(BaseModel):
    """Запрос на загрузку исторических данных с метаданными"""

    data: list[ReviewInputWithMetadata] = Field(description="Список отзывов с датами для загрузки")


class LoadDataResponse(BaseModel):
    """Ответ на загрузку данных"""

    loaded_count: int = Field(description="Количество загруженных отзывов")
    predictions: list[ReviewOutput] = Field(description="Список обработанных отзывов")


class CategoryStatistics(BaseModel):
    """Статистика по категории"""

    category: str = Field(description="Название категории")
    total_count: int = Field(description="Общее количество отзывов")
    positive_count: int = Field(description="Количество положительных отзывов")
    neutral_count: int = Field(description="Количество нейтральных отзывов")
    negative_count: int = Field(description="Количество отрицательных отзывов")
    positive_percent: float = Field(description="Процент положительных отзывов")
    neutral_percent: float = Field(description="Процент нейтральных отзывов")
    negative_percent: float = Field(description="Процент отрицательных отзывов")


class TimelineDataPoint(BaseModel):
    """Точка данных для временной линии"""

    date: str = Field(description="Дата в формате YYYY-MM-DD")
    positive: int = Field(description="Количество положительных")
    neutral: int = Field(description="Количество нейтральных")
    negative: int = Field(description="Количество отрицательных")
    total: int = Field(description="Общее количество")


class CategoryTimeline(BaseModel):
    """Временная динамика категории"""

    category: str = Field(description="Название категории")
    timeline: list[TimelineDataPoint] = Field(description="Данные по времени")


class StatisticsResponse(BaseModel):
    """Общая статистика"""

    total_reviews: int = Field(description="Общее количество отзывов")
    date_range: dict[str, str | None] = Field(description="Диапазон дат (start, end)")
    categories: list[CategoryStatistics] = Field(description="Статистика по категориям")


class TimelineResponse(BaseModel):
    """Ответ с данными временной динамики"""

    categories: list[CategoryTimeline] = Field(description="Динамика по категориям")
