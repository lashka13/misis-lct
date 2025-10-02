from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Проверка работоспособности сервиса

    Returns:
        dict[str, str]: Статус и название сервиса
    """
    return {"status": "ok", "service": "Review Analysis API"}


@router.get("/")
async def root() -> dict[str, str | dict[str, str]]:
    """Корневой endpoint с информацией об API

    Returns:
        dict: Информация об API и список эндпоинтов
    """
    return {
        "service": "Review Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "POST /predict - Классификация отзывов (без даты и источника)",
            "load_data": "POST /load-data - Загрузка исторических данных с датами",
            "health": "GET /health - Проверка работоспособности сервиса",
            "categories": "GET /categories - Список доступных категорий",
            "reviews": "GET /reviews - Получить отзывы с фильтрацией",
            "statistics": "GET /statistics - Общая статистика по категориям",
            "timeline": "GET /statistics/timeline - Временная динамика",
        },
        "docs": "/docs - Swagger UI документация",
    }
