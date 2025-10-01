"""API роуты для классификации отзывов."""

from fastapi import APIRouter, HTTPException

from lct_gazprombank.schemas import PredictRequest, PredictResponse, ReviewInput, ReviewOutput
from lct_gazprombank.services import get_classification_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Список отзывов не может быть пустым")

        reviews = [ReviewInput(id=item.id, text=item.text) for item in request.data]

        service = get_classification_service(batch_size=10)
        result = await service.predict(reviews)

        predictions = [
            ReviewOutput(
                id=review.id,
                topics=review.topics,
                sentiments=review.sentiments,
            )
            for review in result
        ]

        return PredictResponse(predictions=predictions)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}") from e


@router.get("/health")
async def health():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "service": "Review Analysis API"}


@router.get("/")
async def root():
    """Корневой endpoint с информацией об API"""
    return {
        "service": "Review Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "POST /predict - Классификация отзывов",
            "health": "GET /health - Проверка работоспособности сервиса",
        },
    }
