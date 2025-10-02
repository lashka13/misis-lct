import json
from datetime import datetime
from pathlib import Path

from lct_gazprombank.schemas import ReviewOutput


class ReviewStorage:
    """Хранилище результатов классификации отзывов"""

    def __init__(self, storage_path: str | None = None):
        """Инициализация хранилища

        Args:
            storage_path (Optional[str]): Путь к файлу хранилища (по умолчанию data/reviews.json)
        """
        if storage_path is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            storage_path = str(project_root / "data" / "reviews.json")

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.storage_path.exists():
            self._save_reviews([])

    def _save_reviews(self, reviews: list[dict]) -> None:
        """Сохранить отзывы в файл

        Args:
            reviews (list[dict]): Список отзывов для сохранения
        """
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2, default=str)

    def _load_reviews(self) -> list[dict]:
        """Загрузить отзывы из файла

        Returns:
            list[dict]: Список отзывов
        """
        try:
            with open(self.storage_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def add_reviews(self, reviews: list[ReviewOutput]) -> None:
        """Добавить отзывы в хранилище

        Args:
            reviews (list[ReviewOutput]): Список классифицированных отзывов
        """
        existing_reviews = self._load_reviews()
        existing_ids = {r["id"] for r in existing_reviews}

        new_reviews = []
        for review in reviews:
            if review.id not in existing_ids:
                review_dict = review.model_dump()
                # Конвертируем datetime в строку
                if review_dict.get("date"):
                    review_dict["date"] = review_dict["date"].isoformat()
                new_reviews.append(review_dict)

        if new_reviews:
            all_reviews = existing_reviews + new_reviews
            self._save_reviews(all_reviews)

    def get_all_reviews(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        categories: list[str] | None = None,
        sources: list[str] | None = None,
    ) -> list[ReviewOutput]:
        """Получить все отзывы с фильтрацией

        Args:
            start_date (Optional[datetime]): Начальная дата фильтра
            end_date (Optional[datetime]): Конечная дата фильтра
            categories (Optional[list[str]]): Список категорий для фильтрации
            sources (Optional[list[str]]): Список источников для фильтрации

        Returns:
            list[ReviewOutput]: Отфильтрованный список отзывов
        """
        reviews = self._load_reviews()
        result = []

        for review_dict in reviews:
            # Конвертируем строку даты обратно в datetime
            if review_dict.get("date"):
                try:
                    review_dict["date"] = datetime.fromisoformat(review_dict["date"])
                except (ValueError, TypeError):
                    review_dict["date"] = None

            # Фильтрация по дате
            if start_date and review_dict.get("date"):
                if review_dict["date"] < start_date:
                    continue

            if end_date and review_dict.get("date"):
                if review_dict["date"] > end_date:
                    continue

            # Фильтрация по категориям
            if categories:
                review_categories = review_dict.get("topics", [])
                if not any(cat in review_categories for cat in categories):
                    continue

            # Фильтрация по источникам
            if sources and review_dict.get("source"):
                if review_dict["source"] not in sources:
                    continue

            result.append(ReviewOutput(**review_dict))

        return result

    def get_review_by_id(self, review_id: int) -> ReviewOutput | None:
        """Получить отзыв по ID

        Args:
            review_id (int): ID отзыва

        Returns:
            Optional[ReviewOutput]: Отзыв или None
        """
        reviews = self._load_reviews()
        for review_dict in reviews:
            if review_dict["id"] == review_id:
                if review_dict.get("date"):
                    try:
                        review_dict["date"] = datetime.fromisoformat(review_dict["date"])
                    except (ValueError, TypeError):
                        review_dict["date"] = None
                return ReviewOutput(**review_dict)
        return None

    def clear_all(self) -> None:
        """Очистить все отзывы из хранилища"""
        self._save_reviews([])


# Синглтон хранилища
_storage_instance: ReviewStorage | None = None


def get_storage() -> ReviewStorage:
    """Получить синглтон хранилища

    Returns:
        ReviewStorage: Экземпляр хранилища
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ReviewStorage()
    return _storage_instance
