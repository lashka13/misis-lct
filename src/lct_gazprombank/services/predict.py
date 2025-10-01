"""Сервис для предсказаний."""

from lct_gazprombank.agent import classification_agent
from lct_gazprombank.schemas import ReviewInput, ReviewOutput
from lct_gazprombank.utils import load_categories_from_file


class ClassificationService:
    """Сервис для классификации отзывов и определения тональности."""

    def __init__(self, available_categories: list[str], batch_size: int = 10):
        """Инициализация сервиса

        Args:
            available_categories (list[str]): Список доступных категорий
            batch_size (int, optional): Размер батча для обработки (по умолчанию 10 для оптимизации API лимитов)
        """
        self.available_categories = available_categories
        self.batch_size = batch_size

    async def predict(self, reviews: list[ReviewInput]) -> list[ReviewOutput]:
        """Предсказание тем и тональности для отзывов с батчингом

        Args:
            reviews (list[ReviewInput]): Список отзывов для анализа

        Returns:
            list[ReviewOutput]: Список классифицированных отзывов
        """
        results = []

        for i in range(0, len(reviews), self.batch_size):
            batch = reviews[i : i + self.batch_size]
            batch_results = await self._predict_batch(batch)
            results.extend(batch_results)

        return results

    async def _predict_batch(self, reviews: list[ReviewInput]) -> list[ReviewOutput]:
        """Предсказание для одного батча отзывов

        Args:
            reviews (list[ReviewInput]): Батч отзывов

        Returns:
            list[ReviewOutput]: Список классифицированных отзывов
        """
        review_texts = [review.text for review in reviews]

        result = await classification_agent.ainvoke(
            {
                "reviews": review_texts,
                "available_categories": self.available_categories,
            }
        )

        classifications = []
        categories_list = result.get("categories", [])
        sentiments_list = result.get("sentiments", [])

        for idx, review in enumerate(reviews):
            review_topics = categories_list[idx] if idx < len(categories_list) else ["прочее"]
            sentiment_dict = sentiments_list[idx] if idx < len(sentiments_list) else {}
            sentiments = [sentiment_dict.get(topic, "нейтрально") for topic in review_topics]

            classifications.append(
                ReviewOutput(
                    id=review.id,
                    topics=review_topics,
                    sentiments=sentiments,
                )
            )

        return classifications


def get_classification_service(batch_size: int = 10) -> ClassificationService:
    """
    Получить синглтон сервиса классификации

    Args:
        batch_size (int, optional): Размер батча для обработки (по умолчанию 10 для оптимизации API лимитов)

    Returns:
        ClassificationService: Сервис классификации
    """
    categories = load_categories_from_file()
    classification_service = ClassificationService(
        available_categories=categories,
        batch_size=batch_size,
    )
    return classification_service
