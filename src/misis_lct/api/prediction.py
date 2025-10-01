"""API для предсказаний."""

from fastapi import APIRouter, HTTPException

from misis_lct.schemas import PredictRequest, PredictResponse
from misis_lct.services import get_prediction_service

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Предсказание тем и тональности для отзывов.

    Args:
        request: Запрос с отзывами

    Returns:
        Результаты предсказания

    Raises:
        HTTPException: Если произошла ошибка при обработке
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Список отзывов не может быть пустым")

        if len(request.data) > 250:
            raise HTTPException(status_code=400, detail="Максимальное количество отзывов за один запрос: 250")

        service = get_prediction_service()
        result = await service.predict(request.data)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}") from e
