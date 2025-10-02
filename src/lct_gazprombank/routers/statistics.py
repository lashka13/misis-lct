"""API роуты для статистики и работы с отзывами."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from lct_gazprombank.schemas import (
    LoadDataRequest,
    LoadDataResponse,
    ReviewOutput,
    StatisticsResponse,
    TimelineResponse,
)
from lct_gazprombank.services import get_classification_service, get_statistics_service
from lct_gazprombank.storage import get_storage
from lct_gazprombank.utils import load_categories_from_file

router = APIRouter()


@router.post("/load-data", response_model=LoadDataResponse)
async def load_data(request: LoadDataRequest) -> LoadDataResponse:
    """Загрузить исторические данные с метаданными (дата, источник)

    Args:
        request (LoadDataRequest): Отзывы с обязательными датами и опциональными источниками

    Raises:
        HTTPException: Ошибка валидации, обработки, загрузки данных

    Returns:
        LoadDataResponse: Количество загруженных отзывов и результаты классификации
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Список отзывов не может быть пустым")

        service = get_classification_service()
        result = await service.predict(request.data)

        storage = get_storage()
        storage.add_reviews(result)

        return LoadDataResponse(loaded_count=len(result), predictions=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки данных: {str(e)}") from e


@router.get("/categories", response_model=list[str])
async def get_categories() -> list[str]:
    """Получить список всех доступных категорий

    Returns:
        list[str]: Список всех доступных категорий
    """
    try:
        categories = load_categories_from_file()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения категорий: {str(e)}") from e


@router.get("/reviews", response_model=list[ReviewOutput])
async def get_reviews(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    categories: str | None = Query(default=None),
    sources: str | None = Query(default=None),
    limit: int | None = Query(default=None),
) -> list[ReviewOutput]:
    """Получить отзывы с фильтрацией

    Args:
        start_date: Начальная дата в формате ISO (например: 2024-01-01T00:00:00)
        end_date: Конечная дата в формате ISO (например: 2025-05-31T23:59:59)
        categories: Список категорий через запятую
        sources: Список источников через запятую
        limit: Максимальное количество отзывов

    Returns:
        list[ReviewOutput]: Список отфильтрованных отзывов

    Raises:
        HTTPException: Ошибка получения отзывов
    """
    try:
        storage = get_storage()

        category_list = [c.strip() for c in categories.split(",")] if categories else None
        source_list = [s.strip() for s in sources.split(",")] if sources else None

        reviews = storage.get_all_reviews(
            start_date=start_date,
            end_date=end_date,
            categories=category_list,
            sources=source_list,
        )

        if limit and limit > 0:
            reviews = reviews[:limit]

        return reviews

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения отзывов: {str(e)}") from e


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    categories: str | None = Query(default=None),
) -> StatisticsResponse:
    """Получить общую статистику по отзывам

    Args:
        start_date: Начальная дата фильтра
        end_date: Конечная дата фильтра
        categories: Список категорий через запятую

    Returns:
        StatisticsResponse: Статистика по категориям с процентным распределением тональностей
    """
    try:
        service = get_statistics_service()

        category_list = [c.strip() for c in categories.split(",")] if categories else None

        stats = service.get_statistics(
            start_date=start_date,
            end_date=end_date,
            categories=category_list,
        )

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}") from e


@router.get("/statistics/timeline", response_model=TimelineResponse)
async def get_timeline(
    start_date: datetime | None = Query(default=None, description="Начальная дата фильтра"),
    end_date: datetime | None = Query(default=None, description="Конечная дата фильтра"),
    categories: str | None = Query(default=None, description="Категории через запятую"),
    granularity: str = Query(default="day", description="Гранулярность: day, week, month"),
) -> TimelineResponse:
    """Получить временную динамику отзывов

    Args:
        start_date: Начальная дата фильтра
        end_date: Конечная дата фильтра
        categories: Список категорий через запятую
        granularity: Гранулярность агрегации (day, week, month)

    Returns:
        TimelineResponse: Динамика тональностей и количества отзывов по времени для каждой категории
    """
    try:
        if granularity not in ["day", "week", "month"]:
            raise HTTPException(status_code=400, detail="granularity должна быть: day, week или month")

        service = get_statistics_service()

        category_list = [c.strip() for c in categories.split(",")] if categories else None

        timeline = service.get_timeline(
            start_date=start_date,
            end_date=end_date,
            categories=category_list,
            granularity=granularity,
        )

        return timeline

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения временной динамики: {str(e)}") from e


@router.delete("/reviews")
async def clear_all_reviews() -> dict[str, str]:
    """Удалить все отзывы из хранилища (для тестирования)"""
    try:
        storage = get_storage()
        storage.clear_all()
        return {"message": "Все отзывы успешно удалены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления отзывов: {str(e)}") from e
