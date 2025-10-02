import asyncio

from lct_gazprombank.agent import classification_agent
from lct_gazprombank.agent.utils import RateLimiter
from lct_gazprombank.core import settings
from lct_gazprombank.schemas import ReviewInput, ReviewInputWithMetadata, ReviewOutput
from lct_gazprombank.utils import load_categories_from_file


class ClassificationService:
    """Сервис для классификации отзывов и определения тональности."""

    def __init__(self, available_categories: list[str]):
        """Инициализация сервиса классификации

        Args:
            available_categories (list[str]): Список доступных категорий
        """
        self.available_categories = available_categories
        self._semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
        self._rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)

    async def predict(self, reviews: list[ReviewInput] | list[ReviewInputWithMetadata]) -> list[ReviewOutput]:
        """Предсказание тем и тональности для отзывов с параллельной обработкой

        Args:
            reviews: Список отзывов для анализа

        Returns:
            list[ReviewOutput]: Список классифицированных отзывов
        """
        batches = [reviews[i : i + settings.BATCH_SIZE] for i in range(0, len(reviews), settings.BATCH_SIZE)]
        responses = await asyncio.gather(*[self._predict_batch(batch) for batch in batches])
        return [item for response in responses for item in response]

    async def _predict_batch(self, reviews: list[ReviewInput] | list[ReviewInputWithMetadata]) -> list[ReviewOutput]:
        """Предсказание для одного батча отзывов

        Args:
            reviews: Батч отзывов (с метаданными или без)

        Returns:
            list[ReviewOutput]: Список классифицированных отзывов
        """
        async with self._semaphore:
            review_texts = [review.text for review in reviews]

            result = await classification_agent.ainvoke(
                {
                    "reviews": review_texts,
                    "available_categories": self.available_categories,
                    "rate_limiter": self._rate_limiter,
                }
            )

            categories_list = result.get("categories", [])
            sentiments_list = result.get("sentiments", [])

            classifications = []
            for idx, review in enumerate(reviews):
                topics = categories_list[idx] if idx < len(categories_list) else ["Прочее"]
                sentiments_dict = sentiments_list[idx] if idx < len(sentiments_list) else {}
                sentiments = [sentiments_dict.get(topic, "нейтрально") for topic in topics]

                classifications.append(
                    ReviewOutput(
                        id=review.id,
                        text=review.text,
                        topics=topics,
                        sentiments=sentiments,
                        date=getattr(review, "date", None),
                        source=getattr(review, "source", None),
                    )
                )

            return classifications


def get_classification_service() -> ClassificationService:
    """Получить экземпляр сервиса классификации

    Returns:
        ClassificationService: Сервис классификации
    """
    available_categories = load_categories_from_file()
    return ClassificationService(available_categories=available_categories)
