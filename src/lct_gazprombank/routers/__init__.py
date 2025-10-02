from .predict import router as predict_router
from .root import router as root_router
from .statistics import router as statistics_router

__all__ = ["predict_router", "root_router", "statistics_router"]
