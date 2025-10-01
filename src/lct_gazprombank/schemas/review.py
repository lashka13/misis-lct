from pydantic import BaseModel, Field


class ReviewInput(BaseModel):
    """Входной отзыв для классификации"""

    id: int = Field(description="Уникальный идентификатор отзыва")
    text: str = Field(description="Текст отзыва")


class ReviewOutput(BaseModel):
    """Выходной классифицированный отзыв"""

    id: int = Field(description="Идентификатор отзыва")
    topics: list[str] = Field(description="Список тем отзыва")
    sentiments: list[str] = Field(description="Список тональностей для каждой темы")


class PredictRequest(BaseModel):
    """Запрос на предсказание"""

    data: list[ReviewInput] = Field(description="Список отзывов для анализа")


class PredictResponse(BaseModel):
    """Ответ с предсказаниями"""

    predictions: list[ReviewOutput] = Field(description="Список предсказаний")
