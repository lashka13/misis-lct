import json
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from api.core.settings import DATABASE_URL
from api.core.models import Base
from api.core.db.review_crud import create_reviews_from_json_list

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

JSON_PATH = Path(__file__).parent.parent / "transformed_reviews.json"

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if JSON_PATH.exists():
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            reviews_data = json.load(f)

        async with async_session_maker() as session:
            await create_reviews_from_json_list(session, reviews_data)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
