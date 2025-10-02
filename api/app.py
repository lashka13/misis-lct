from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routes import reviews
from .core import database
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    yield

app = FastAPI(lifespan=lifespan)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(shop.router, tags=['shop'])
app.include_router(reviews.router, tags=['reviews'])