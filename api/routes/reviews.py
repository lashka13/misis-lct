from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime
from api.core.db.review_crud import (
    get_reviews_by_interval,
    get_reviews_stats,
    get_dashboard_stats,
    get_topic_trends,
    get_sentiment_dynamics,
    get_all_available_topics,
    get_topics_statistics,
    get_topics_comparison,
)
from api.core.schemas import (
    ReviewSchema,
    PredictRequest,
    PredictResponse,
    IntervalRequestSchema,
    TopicsStatisticsResponse,
    TopicsStatisticsRequest,
    TopicsComparisonResponseSchema,
    AvailableTopicsResponse,
)
from api.core.database import get_async_session
from api.core.services.predict import get_classification_service

router = APIRouter(prefix="/api")


@router.get("/reviews", response_model=List[ReviewSchema])
async def read_reviews(
    start_date: datetime = Query(..., description="Начало интервала (YYYY-MM-DD)"),
    end_date: datetime | None = Query(None, description="Конец интервала (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить список уже предсказанных отзывов за указанный интервал времени.
    Если end_date не указан, будет выбран ровно один день.
    """
    reviews = await get_reviews_by_interval(session, start_date, end_date)
    return [ReviewSchema.from_orm_with_relationships(review) for review in reviews]


@router.post("/reviews/stats")
async def read_reviews_stats(
    request: IntervalRequestSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить отзывы по времени с разными шкалами деления
    """
    try:
        data = await get_reviews_stats(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )
        return {
            "status": "success",
            "data": data,
            "meta": {
                "mode": request.mode,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "total_periods": len(data),
                "total_reviews": sum(item["count"] for item in data),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/predict", response_model=PredictResponse)
async def predict(
    data: PredictRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить список предсказаний для определённых отзывов.
    """
    if not data.data:
        raise HTTPException(
            status_code=400, detail="Список отзывов не должен быть пустым"
        )
    try:
        service = get_classification_service()
        result = await service.predict(data.data)

        return PredictResponse(predictions=result)

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Неверный формат данных: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка обработки: {str(e)}"
        ) from e


@router.post("/dashboard/overview")
async def get_dashboard_overview(
    request: IntervalRequestSchema,
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Общая статистика дашборда за интервал
    """
    try:
        stats = await get_dashboard_stats(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )
        return {
            "status": "success",
            "data": stats,
            "meta": {
                "mode": request.mode,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dashboard/topic-trends")
async def get_dashboard_topic_trends(
    request: IntervalRequestSchema,
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Динамика топ-тем за интервал
    """
    try:
        trends = await get_topic_trends(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )
        return {
            "status": "success",
            "data": trends,
            "meta": {
                "mode": request.mode,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dashboard/sentiment-dynamics")
async def get_dashboard_sentiment_dynamics(
    request: IntervalRequestSchema,
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Динамика тональности за интервал
    """
    try:
        dynamics = await get_sentiment_dynamics(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )
        return {
            "status": "success",
            "data": dynamics,
            "meta": {
                "mode": request.mode,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dashboard/comprehensive")
async def get_comprehensive_dashboard(
    request: IntervalRequestSchema,
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Все данные дашборда в одном запросе
    """
    try:
        overview = await get_dashboard_stats(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )

        trends = await get_topic_trends(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )

        dynamics = await get_sentiment_dynamics(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )

        reviews_timeline = await get_reviews_stats(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
        )

        return {
            "status": "success",
            "data": {
                "overview": overview,
                "topic_trends": trends,
                "sentiment_dynamics": dynamics,
                "reviews_timeline": reviews_timeline,
            },
            "meta": {
                "mode": request.mode,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/topics/statistics", response_model=TopicsStatisticsResponse)
async def get_topics_statistics_endpoint(  # Изменили имя функции
    request: TopicsStatisticsRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить статистику по выбранным темам в интервалах времени
    """
    try:
        stats = await get_topics_statistics(  # Это вызов CRUD функции
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            mode=request.mode,
            topic_names=request.topics,
        )

        return {
            "status": "success",
            "data": stats,
            "meta": {
                "mode": request.mode,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "topics_analyzed": request.topics,
                "topics_found": list(set([item["topic"] for item in stats])),
                "total_periods": len(set([item["period"] for item in stats])),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/topics/comparison", response_model=TopicsComparisonResponseSchema)
async def get_topics_comparison_endpoint(
    request: TopicsStatisticsRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Сравнительная статистика по темам за весь период (без разбивки по интервалам)
    """
    try:
        comparison = await get_topics_comparison(
            session=session,
            start_date=request.start_date,
            end_date=request.end_date,
            topic_names=request.topics,
            # Убрали mode, так как он не используется в get_topics_comparison
        )

        return {
            "status": "success",
            "data": comparison,
            "meta": {
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "topics_analyzed": request.topics,
                "topics_found": [item["topic"] for item in comparison],
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/topics/available", response_model=AvailableTopicsResponse)
async def get_available_topics_endpoint(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получить список всех доступных тем для выбора
    """
    try:
        # Важно: вызываем CRUD функцию, а не эту же функцию рекурсивно
        topics = await get_all_available_topics(session)

        return {"status": "success", "data": topics, "count": len(topics)}
    except Exception as e:
        print(f"Error in /topics/available endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
