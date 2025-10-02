from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lct_gazprombank.core.config import settings
from lct_gazprombank.routers import predict_router, root_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для анализа отзывов клиентов Газпромбанка",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router, tags=["root"])
app.include_router(predict_router, tags=["prediction"])
