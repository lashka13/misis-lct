"""API роуты для классификации отзывов."""

from fastapi import APIRouter, HTTPException

from lct_gazprombank.schemas import PredictRequest, PredictResponse
from lct_gazprombank.services import get_classification_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """Классификация отзывов

    Args:
        request (PredictRequest): Запрос на классификацию отзывов

    Raises:
        HTTPException: Ошибка валидации/обработки данных

    Returns:
        PredictResponse: Ответ с предсказаниями
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Список отзывов не может быть пустым")

        service = get_classification_service(batch_size=10)
        result = await service.predict(request.data)

        return PredictResponse(predictions=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}") from e



