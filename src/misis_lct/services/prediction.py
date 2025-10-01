"""Сервис для предсказаний."""

from misis_lct.agent.graph import classification_agent
from misis_lct.schemas import PredictResponse, ReviewInput, ReviewPrediction


class ClassificationService:
    """Сервис для классификации отзывов и определения тональности"""

    def __init__(self, available_categories: list[str]):
        """Инициализация сервиса

        Args:
            available_categories (list[str]): Список доступных категорий
        """
        self.available_categories = available_categories

    async def classify(self, reviews: list[ReviewInput]) -> PredictResponse:
        """Классификация тем и тональности для отзывов

        Args:
            reviews (list[ReviewInput]): Список отзывов для анализа

        Returns:
            PredictResponse: Результаты классификации
        """
        reviews_texts = [review.text for review in reviews]
        reviews_ids = [review.id for review in reviews]

        result = await classification_agent.ainvoke(
            {
                "reviews": reviews_texts,
                "available_categories": self.available_categories,
            }
        )

        predictions = []
        categories_list = result.get("categories", [])
        sentiments_list = result.get("sentiments", [])

        for i, review_id in enumerate(reviews_ids):
            topics = categories_list[i] if i < len(categories_list) else []
            sentiment_dict = sentiments_list[i] if i < len(sentiments_list) else {}

            sentiments = [sentiment_dict.get(topic, "нейтрально") for topic in topics]

            predictions.append(
                ReviewPrediction(
                    id=review_id,
                    topics=topics,
                    sentiments=sentiments,
                )
            )

        return PredictResponse(predictions=predictions)


with open("data/categories.txt") as file:
    categories = file.read().splitlines()

classification_service = ClassificationService(categories)
