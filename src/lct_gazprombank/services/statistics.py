"""Сервис для расчета статистики по отзывам."""

from collections import defaultdict
from datetime import datetime

from lct_gazprombank.schemas import (
    CategoryStatistics,
    CategoryTimeline,
    StatisticsResponse,
    TimelineDataPoint,
    TimelineResponse,
)
from lct_gazprombank.storage import get_storage


class StatisticsService:
    """Сервис для расчета статистики и аналитики по отзывам"""

    def __init__(self):
        """Инициализация сервиса"""
        self.storage = get_storage()

    def get_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        categories: list[str] | None = None,
    ) -> StatisticsResponse:
        """Получить общую статистику по отзывам

        Args:
            start_date (Optional[datetime]): Начальная дата
            end_date (Optional[datetime]): Конечная дата
            categories (Optional[list[str]]): Фильтр по категориям

        Returns:
            StatisticsResponse: Статистика по отзывам
        """
        reviews = self.storage.get_all_reviews(
            start_date=start_date,
            end_date=end_date,
            categories=categories,
        )

        category_data = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0, "total": 0})

        min_date = None
        max_date = None

        for review in reviews:
            if review.date:
                if min_date is None or review.date < min_date:
                    min_date = review.date
                if max_date is None or review.date > max_date:
                    max_date = review.date

            for topic, sentiment in zip(review.topics, review.sentiments, strict=False):
                category_data[topic]["total"] += 1
                if sentiment == "положительно":
                    category_data[topic]["positive"] += 1
                elif sentiment == "нейтрально":
                    category_data[topic]["neutral"] += 1
                elif sentiment == "отрицательно":
                    category_data[topic]["negative"] += 1

        category_stats = []
        for category, data in sorted(category_data.items()):
            total = data["total"]
            if total > 0:
                category_stats.append(
                    CategoryStatistics(
                        category=category,
                        total_count=total,
                        positive_count=data["positive"],
                        neutral_count=data["neutral"],
                        negative_count=data["negative"],
                        positive_percent=round(data["positive"] / total * 100, 2),
                        neutral_percent=round(data["neutral"] / total * 100, 2),
                        negative_percent=round(data["negative"] / total * 100, 2),
                    )
                )

        return StatisticsResponse(
            total_reviews=len(reviews),
            date_range={
                "start": min_date.isoformat() if min_date else None,
                "end": max_date.isoformat() if max_date else None,
            },
            categories=category_stats,
        )

    def get_timeline(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        categories: list[str] | None = None,
        granularity: str = "day",
    ) -> TimelineResponse:
        """Получить временную динамику отзывов

        Args:
            start_date (Optional[datetime]): Начальная дата
            end_date (Optional[datetime]): Конечная дата
            categories (Optional[list[str]]): Фильтр по категориям
            granularity (str): Гранулярность ("day", "week", "month")

        Returns:
            TimelineResponse: Временная динамика
        """
        reviews = self.storage.get_all_reviews(
            start_date=start_date,
            end_date=end_date,
            categories=categories,
        )

        reviews_with_dates = [r for r in reviews if r.date]

        category_timeline_data = defaultdict(lambda: defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0}))

        for review in reviews_with_dates:
            date_key = self._format_date_by_granularity(review.date, granularity)

            for topic, sentiment in zip(review.topics, review.sentiments, strict=False):
                if sentiment == "положительно":
                    category_timeline_data[topic][date_key]["positive"] += 1
                elif sentiment == "нейтрально":
                    category_timeline_data[topic][date_key]["neutral"] += 1
                elif sentiment == "отрицательно":
                    category_timeline_data[topic][date_key]["negative"] += 1

        category_timelines = []
        for category, timeline_data in sorted(category_timeline_data.items()):
            timeline_points = []
            for date_key, sentiments in sorted(timeline_data.items()):
                total = sentiments["positive"] + sentiments["neutral"] + sentiments["negative"]
                timeline_points.append(
                    TimelineDataPoint(
                        date=date_key,
                        positive=sentiments["positive"],
                        neutral=sentiments["neutral"],
                        negative=sentiments["negative"],
                        total=total,
                    )
                )

            category_timelines.append(CategoryTimeline(category=category, timeline=timeline_points))

        return TimelineResponse(categories=category_timelines)

    def _format_date_by_granularity(self, date: datetime, granularity: str) -> str:
        """Форматировать дату в зависимости от гранулярности

        Args:
            date (datetime): Дата
            granularity (str): Гранулярность

        Returns:
            str: Отформатированная дата
        """
        if granularity == "month":
            return date.strftime("%Y-%m")
        elif granularity == "week":
            return date.strftime("%Y-W%U")
        else:
            return date.strftime("%Y-%m-%d")


def get_statistics_service() -> StatisticsService:
    """Получить экземпляр сервиса статистики

    Returns:
        StatisticsService: Сервис статистики
    """
    return StatisticsService()
