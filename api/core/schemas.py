from datetime import datetime
from pydantic import BaseModel, field_serializer, field_validator, Field
from typing import List, Literal, Dict, Any, Optional
from api.core.models import Review


class ReviewSchema(BaseModel):
    id: int
    text: str
    date: datetime
    rating: int | None
    topics: List[str]
    sentiments: List[str]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_relationships(cls, obj: Review):
        """Custom method to create schema from ORM with relationships"""
        topics = [rt.topic.name for rt in obj.review_topics]
        sentiments = [rt.sentiment.value for rt in obj.review_topics]
        
        return cls(
            id=obj.id,
            text=obj.text,
            date=obj.date,
            rating=obj.rating,
            topics=topics,
            sentiments=sentiments
        )


class PredictSchema(BaseModel):
    id: int
    text: str


class PredictResponseSchema(BaseModel):
    id: int
    topics: List[str]
    sentiments: List[str]

    model_config = {"from_attributes": True}

    @field_serializer("topics", when_used="always")
    def serialize_topics(self, review):
        return [rt.topic.name for rt in review.review_topics]

    @field_serializer("sentiments", when_used="always")
    def serialize_sentiments(self, review):
        return [rt.sentiment.value for rt in review.review_topics]


class IntervalRequestSchema(BaseModel):
    start_date: datetime
    end_date: datetime
    mode: Literal["all:month", "month:day", "halfyear:week", "days:day"]

    @field_validator("end_date")
    def validate_days_limit(cls, v, info):
        mode = info.data.get("mode")
        start = info.data.get("start_date")
        if mode == "days:day" and (v - start).days > 30:
            raise ValueError("Интервал в режиме 'days:day' не может превышать 30 дней")
        return v









class DashboardOverviewResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    meta: Dict[str, Any]

class TopicTrendsResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
    meta: Dict[str, Any]

class ComprehensiveDashboardResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    meta: Dict[str, Any]
    
    
    
    
    
class TopicsStatisticsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    mode: Literal["all:month", "month:day", "halfyear:week", "days:day"]
    topics: List[str]

class TopicStatisticResponse(BaseModel):
    period: str
    topic: str
    total_mentions: int
    sentiment_breakdown: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    nps_score: float
    average_rating: Optional[float]
    dominant_sentiment: Optional[str]

class TopicsComparisonResponse(BaseModel):
    topic: str
    total_mentions: int
    sentiment_breakdown: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    nps_score: float
    average_rating: Optional[float]
    first_mention: Optional[str]
    last_mention: Optional[str]
    dominant_sentiment: Optional[str]

class TopicsStatisticsResponse(BaseModel):
    status: str
    data: List[TopicStatisticResponse]
    meta: Dict[str, Any]

class TopicsComparisonResponseSchema(BaseModel):
    status: str
    data: List[TopicsComparisonResponse]
    meta: Dict[str, Any]

class AvailableTopicsResponse(BaseModel):
    status: str
    data: List[str]
    count: int
    

class TopicsComparisonRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    topics: List[str]
    
    


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
    topics: list[str] = Field(description="Список тем отзыва")
    sentiments: list[str] = Field(description="Список тональностей для каждой темы")
    
    
class PredictRequest(BaseModel):
    """Запрос на предсказание"""

    data: list[ReviewInput] = Field(description="Список отзывов для анализа")
    
    
class PredictResponse(BaseModel):
    """Ответ с предсказаниями"""

    predictions: list[ReviewOutput] = Field(description="Список предсказаний")