from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from api.core.models import Review, ReviewTopic, Sentiment, Topic


async def get_reviews_by_interval(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime | None = None,
) -> List[Review]:
    if end_date is None:
        end_date = start_date + timedelta(days=1)

    result = await session.execute(
        select(Review)
        .where(Review.date >= start_date, Review.date < end_date)
        .options(selectinload(Review.review_topics).selectinload(ReviewTopic.topic))
    )
    return result.scalars().all()


async def get_review_by_id(session: AsyncSession, review_id: int) -> Optional[Review]:
    result = await session.execute(select(Review).where(Review.id == review_id))
    return result.scalar_one_or_none()


async def create_review(
    session: AsyncSession,
    review_id: int,
    text: str,
    date: datetime,
    rating: int | None,
    sentiments: list[str],
    review_topics: list[str],
) -> Review:
    """
    Create a review with linked topics and sentiments.
    Commits immediately.
    """

    if len(sentiments) != len(review_topics):
        raise ValueError("Length of sentiments must match length of review_topics")

    # Create Review
    review = Review(id=review_id, text=text, date=date, rating=rating)
    session.add(review)

    # Pair topics and sentiments
    for topic_name, sentiment_value in zip(review_topics, sentiments):
        result = await session.execute(select(Topic).where(Topic.name == topic_name))
        topic = result.scalar_one_or_none()
        if not topic:
            topic = Topic(name=topic_name)
            session.add(topic)
            await session.flush()  # assign id

        review_topic = ReviewTopic(
            review=review,
            topic=topic,
            sentiment=Sentiment(sentiment_value),
        )
        session.add(review_topic)

    await session.commit()
    await session.refresh(review)
    return review


async def create_reviews_from_json_list(
    session: AsyncSession, reviews_data: List[Dict]
) -> None:
    """
    Bulk loader: insert reviews from JSON if they don't exist already.
    Uses create_review() for consistency.
    """
    for review_data in reviews_data:
        existing = await get_review_by_id(session, review_data["id"])
        if existing:
            continue

        await create_review(
            session=session,
            review_id=review_data["id"],
            text=review_data["text"],
            date=datetime.strptime(review_data["date"], "%Y-%m-%d %H:%M:%S"),
            rating=review_data.get("rating"),
            sentiments=review_data["sentiments"],
            review_topics=review_data["review_topics"],
        )


async def get_reviews_stats(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    mode: str,
) -> List[Dict[str, Any]]:
    """
    Возвращает количество отзывов по заданному временному интервалу
    и шкале деления.
    """

    # Нормализация временных зон
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    # Валидация
    if end_date <= start_date:
        raise ValueError("end_date должен быть больше start_date")

    # Построение запроса в зависимости от режима
    if mode == "all:month":
        trunc_func = func.date_trunc("month", Review.date)
    elif mode in ("month:day", "days:day"):
        trunc_func = func.date_trunc("day", Review.date)
    elif mode == "halfyear:week":
        trunc_func = func.date_trunc("week", Review.date)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    query = (
        select(
            trunc_func.label("period"),
            func.count(Review.id).label("count"),
        )
        .where(Review.date >= start_date, Review.date <= end_date)
        .group_by(trunc_func)
        .order_by("period")
    )

    result = await session.execute(query)
    rows = result.all()

    # Форматирование результата
    return format_stats_result(rows, mode)


def format_stats_result(rows: List, mode: str) -> List[Dict[str, Any]]:
    """Форматирует статистику в зависимости от режима"""
    formatted_data = []

    for row in rows:
        period = row.period
        count = row.count

        if mode == "all:month":
            period_str = period.strftime("%Y-%m")  # "2024-01"
        elif mode == "halfyear:week":
            # Показываем диапазон недели
            week_start = period
            week_end = period + timedelta(days=6)
            period_str = (
                f"{week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}"
            )
        else:  # day modes
            period_str = period.strftime("%Y-%m-%d")

        formatted_data.append(
            {
                "period": period_str,
                "count": count,
                "start_date": period.isoformat(),  # Для клиента, если нужна точная дата
            }
        )

    return formatted_data


async def get_dashboard_stats(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    mode: str,
) -> Dict[str, Any]:
    """
    Комплексная статистика для дашборда по интервалам
    """
    # Базовые метрики
    total_reviews = await session.scalar(
        select(func.count(Review.id)).where(
            Review.date.between(start_date, end_date)
        )
    )
    
    avg_rating = await session.scalar(
        select(func.avg(Review.rating)).where(
            Review.date.between(start_date, end_date),
            Review.rating.isnot(None)
        )
    )

    # Распределение рейтингов
    rating_dist = await session.execute(
        select(Review.rating, func.count(Review.id))
        .where(Review.date.between(start_date, end_date))
        .group_by(Review.rating)
        .order_by(Review.rating)
    )
    
    # Общая тональность
    sentiment_overall = await session.execute(
        select(
            ReviewTopic.sentiment,
            func.count(ReviewTopic.review_id)
        )
        .select_from(ReviewTopic)  # Явно указываем основную таблицу
        .join(Review, ReviewTopic.review_id == Review.id)  # Явное соединение
        .where(Review.date >= start_date, Review.date <= end_date)
        .group_by(ReviewTopic.sentiment)
    )
    
    # Топ тем
    popular_topics = await session.execute(
        select(Topic.name, func.count(ReviewTopic.review_id))
        .select_from(ReviewTopic)
        .join(Review)
        .join(Topic)
        .where(Review.date.between(start_date, end_date))
        .group_by(Topic.name)
        .order_by(func.count(ReviewTopic.review_id).desc())
    )
    
    # Проблемные темы (негативные)
    problem_topics = await session.execute(
        select(Topic.name, func.count(ReviewTopic.review_id))
        .select_from(ReviewTopic)
        .join(Review)
        .join(Topic)
        .where(
            Review.date.between(start_date, end_date),
            ReviewTopic.sentiment == Sentiment.NEGATIVE
        )
        .group_by(Topic.name)
        .order_by(func.count(ReviewTopic.review_id).desc())
    )
   
    
    sentiment_counts = {s: c for s, c in sentiment_overall}
    total_mentions = sum(sentiment_counts.values())
    nps_score = 0

    
    if total_mentions > 0:
        positive = sentiment_counts.get(Sentiment.POSITIVE, 0)
        negative = sentiment_counts.get(Sentiment.NEGATIVE, 0)
        nps_score = ((positive - negative) / total_mentions) * 100

    return {
        "total_reviews": total_reviews,
        "average_rating": float(avg_rating) if avg_rating else None,
        "rating_distribution": {str(r): c for r, c in rating_dist},
        "sentiment_distribution": {
            s.value: c for s, c in sentiment_overall
        },
        "popular_topics": [
            {"topic": topic, "count": count} 
            for topic, count in popular_topics
        ],
        "problem_topics": [
            {"topic": topic, "negative_count": count} 
            for topic, count in problem_topics
        ],
        "nps_score": round(nps_score, 2),
        "total_mentions": total_mentions,
    }

async def get_topic_trends(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    mode: str,
    topic_limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Динамика топ-тем по интервалам
    """
    if mode == "all:month":
        trunc_func = func.date_trunc("month", Review.date)
    elif mode in ("month:day", "days:day"):
        trunc_func = func.date_trunc("day", Review.date)
    elif mode == "halfyear:week":
        trunc_func = func.date_trunc("week", Review.date)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # Получаем топ тем за весь период
    top_topics_query = (
        select(Topic.name)
        .select_from(ReviewTopic)
        .join(Review)
        .join(Topic)
        .where(Review.date.between(start_date, end_date))
        .group_by(Topic.name)
        .order_by(func.count(ReviewTopic.review_id).desc())
        .limit(topic_limit)
    )
    
    top_topics_result = await session.execute(top_topics_query)
    top_topics = [name for name, in top_topics_result]

    # Динамика по топ-темам
    trends_query = (
        select(
            trunc_func.label("period"),
            Topic.name.label("topic"),
            func.count(ReviewTopic.review_id).label("count"),
            func.avg(
                case(
                    (ReviewTopic.sentiment == Sentiment.POSITIVE, 1),
                    (ReviewTopic.sentiment == Sentiment.NEGATIVE, -1),
                    else_=0
                )
            ).label("sentiment_score")
        )
        .select_from(ReviewTopic)
        .join(Review)
        .join(Topic)
        .where(
            Review.date.between(start_date, end_date),
            Topic.name.in_(top_topics)
        )
        .group_by(trunc_func, Topic.name)
        .order_by(trunc_func, Topic.name)
    )
    
    result = await session.execute(trends_query)
    rows = result.all()
    
    # Форматируем результат
    return [
        {
            "period": row.period.strftime("%Y-%m-%d"),
            "topic": row.topic,
            "count": row.count,
            "sentiment_score": float(row.sentiment_score) if row.sentiment_score else 0
        }
        for row in rows
    ]

async def get_sentiment_dynamics(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    mode: str,
) -> List[Dict[str, Any]]:
    """
    Динамика тональности по интервалам
    """
    if mode == "all:month":
        trunc_func = func.date_trunc("month", Review.date)
    elif mode in ("month:day", "days:day"):
        trunc_func = func.date_trunc("day", Review.date)
    elif mode == "halfyear:week":
        trunc_func = func.date_trunc("week", Review.date)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    query = (
        select(
            trunc_func.label("period"),
            ReviewTopic.sentiment,
            func.count(ReviewTopic.review_id).label("count")
        )
        .select_from(ReviewTopic)
        .join(Review)
        .where(Review.date.between(start_date, end_date))
        .group_by(trunc_func, ReviewTopic.sentiment)
        .order_by(trunc_func)
    )
    
    result = await session.execute(query)
    rows = result.all()
    
    # Группируем по периодам
    period_data = {}
    for period, sentiment, count in rows:
        period_str = period.strftime("%Y-%m-%d")
        if period_str not in period_data:
            period_data[period_str] = {
                "total": 0
            }
        
        period_data[period_str][sentiment.value] = count
        period_data[period_str]["total"] += count
    
    return [
        {
            "period": period,
            **data,
            
        }
        for period, data in period_data.items()
    ]
    
    
    
    
    
    
    
async def get_topics_statistics(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    mode: str,
    topic_names: List[str],
) -> List[Dict[str, Any]]:
    """
    Статистика по выбранным темам в интервалах
    """
    if not topic_names:
        return []

    # Определяем функцию для группировки по времени
    if mode == "all:month":
        trunc_func = func.date_trunc("month", Review.date)
    elif mode in ("month:day", "days:day"):
        trunc_func = func.date_trunc("day", Review.date)
    elif mode == "halfyear:week":
        trunc_func = func.date_trunc("week", Review.date)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # Основной запрос для статистики по темам
    query = (
        select(
            trunc_func.label("period"),
            Topic.name.label("topic_name"),
            ReviewTopic.sentiment,
            func.count(ReviewTopic.review_id).label("count"),
            func.avg(Review.rating).label("avg_rating")
        )
        .select_from(ReviewTopic)
        .join(Review, ReviewTopic.review_id == Review.id)
        .join(Topic, ReviewTopic.topic_id == Topic.id)
        .where(
            Review.date.between(start_date, end_date),
            Topic.name.in_(topic_names)
        )
        .group_by(trunc_func, Topic.name, ReviewTopic.sentiment)
        .order_by(trunc_func, Topic.name, ReviewTopic.sentiment)
    )

    result = await session.execute(query)
    rows = result.all()

    # Группируем результаты по периоду и теме
    stats_by_period_topic = {}
    
    for period, topic_name, sentiment, count, avg_rating in rows:
        period_str = period.strftime("%Y-%m-%d")
        key = (period_str, topic_name)
        
        if key not in stats_by_period_topic:
            stats_by_period_topic[key] = {
                "period": period_str,
                "topic": topic_name,
                "total_mentions": 0,
                "sentiment_breakdown": {
                    Sentiment.POSITIVE.value: 0,
                    Sentiment.NEGATIVE.value: 0,
                    Sentiment.NEUTRAL.value: 0
                },
                "avg_rating": 0,
                "rating_count": 0
            }
        
        stats_by_period_topic[key]["sentiment_breakdown"][sentiment.value] = count
        stats_by_period_topic[key]["total_mentions"] += count
        
        # Аккумулируем рейтинги для вычисления среднего
        if avg_rating is not None:
            current_avg = stats_by_period_topic[key]["avg_rating"]
            current_count = stats_by_period_topic[key]["rating_count"]
            total_count = current_count + count
            
            if total_count > 0:
                stats_by_period_topic[key]["avg_rating"] = (
                    (current_avg * current_count) + (avg_rating * count)
                ) / total_count
                stats_by_period_topic[key]["rating_count"] = total_count

    # Рассчитываем дополнительные метрики
    formatted_stats = []
    for stat in stats_by_period_topic.values():
        sentiment_data = stat["sentiment_breakdown"]
        total = stat["total_mentions"]
        
        # Рассчитываем проценты тональности
        sentiment_percentages = {
            sentiment: round((count / total) * 100, 2) if total > 0 else 0
            for sentiment, count in sentiment_data.items()
        }
        
        # Рассчитываем NPS-like показатель для темы
        positive = sentiment_data.get(Sentiment.POSITIVE.value, 0)
        negative = sentiment_data.get(Sentiment.NEGATIVE.value, 0)
        nps_score = round(((positive - negative) / total) * 100, 2) if total > 0 else 0
        
        formatted_stats.append({
            "period": stat["period"],
            "topic": stat["topic"],
            "total_mentions": total,
            "sentiment_breakdown": sentiment_data,
            "sentiment_percentages": sentiment_percentages,
            "nps_score": nps_score,
            "average_rating": round(stat["avg_rating"], 2) if stat["avg_rating"] else None,
            "dominant_sentiment": max(sentiment_data.items(), key=lambda x: x[1])[0] if total > 0 else None
        })

    return formatted_stats


async def get_topics_comparison(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    topic_names: List[str],
) -> List[Dict[str, Any]]:
    """
    Сравнительная статистика по темам за весь период (без разбивки по интервалам)
    """
    if not topic_names:
        return []

    query = (
        select(
            Topic.name.label("topic_name"),
            ReviewTopic.sentiment,
            func.count(ReviewTopic.review_id).label("count"),
            func.avg(Review.rating).label("avg_rating"),
            func.min(Review.date).label("first_mention"),
            func.max(Review.date).label("last_mention")
        )
        .select_from(ReviewTopic)
        .join(Review, ReviewTopic.review_id == Review.id)
        .join(Topic, ReviewTopic.topic_id == Topic.id)
        .where(
            Review.date.between(start_date, end_date),
            Topic.name.in_(topic_names)
        )
        .group_by(Topic.name, ReviewTopic.sentiment)
        .order_by(Topic.name, ReviewTopic.sentiment)
    )

    result = await session.execute(query)
    rows = result.all()

    # Группируем по теме
    stats_by_topic = {}
    
    for topic_name, sentiment, count, avg_rating, first_mention, last_mention in rows:
        if topic_name not in stats_by_topic:
            stats_by_topic[topic_name] = {
                "topic": topic_name,
                "total_mentions": 0,
                "sentiment_breakdown": {
                    Sentiment.POSITIVE.value: 0,
                    Sentiment.NEGATIVE.value: 0,
                    Sentiment.NEUTRAL.value: 0
                },
                "avg_rating": 0,
                "rating_count": 0,
                "first_mention": first_mention,
                "last_mention": last_mention
            }
        
        stats_by_topic[topic_name]["sentiment_breakdown"][sentiment.value] = count
        stats_by_topic[topic_name]["total_mentions"] += count
        
        # Аккумулируем рейтинги
        if avg_rating is not None:
            current_avg = stats_by_topic[topic_name]["avg_rating"]
            current_count = stats_by_topic[topic_name]["rating_count"]
            total_count = current_count + count
            
            if total_count > 0:
                stats_by_topic[topic_name]["avg_rating"] = (
                    (current_avg * current_count) + (avg_rating * count)
                ) / total_count
                stats_by_topic[topic_name]["rating_count"] = total_count

    # Форматируем результат
    formatted_stats = []
    for stat in stats_by_topic.values():
        sentiment_data = stat["sentiment_breakdown"]
        total = stat["total_mentions"]
        
        sentiment_percentages = {
            sentiment: round((count / total) * 100, 2) if total > 0 else 0
            for sentiment, count in sentiment_data.items()
        }
        
        positive = sentiment_data.get(Sentiment.POSITIVE.value, 0)
        negative = sentiment_data.get(Sentiment.NEGATIVE.value, 0)
        nps_score = round(((positive - negative) / total) * 100, 2) if total > 0 else 0
        
        formatted_stats.append({
            "topic": stat["topic"],
            "total_mentions": total,
            "sentiment_breakdown": sentiment_data,
            "sentiment_percentages": sentiment_percentages,
            "nps_score": nps_score,
            "average_rating": round(stat["avg_rating"], 2) if stat["avg_rating"] else None,
            "first_mention": stat["first_mention"].isoformat() if stat["first_mention"] else None,
            "last_mention": stat["last_mention"].isoformat() if stat["last_mention"] else None,
            "dominant_sentiment": max(sentiment_data.items(), key=lambda x: x[1])[0] if total > 0 else None
        })

    return sorted(formatted_stats, key=lambda x: x["total_mentions"], reverse=True)


async def get_all_available_topics(
    session: AsyncSession,
) -> List[str]:
    """
    Получить список всех доступных тем
    """
    try:
        result = await session.execute(
            select(Topic.name).order_by(Topic.name)
        )
        topics = [name for name, in result.all()]
        return topics
    except Exception as e:
        print(f"Error in get_all_available_topics: {e}")
        raise