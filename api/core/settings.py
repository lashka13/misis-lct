from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT')


class Settings(BaseSettings):
    """Настройки приложения"""

    PROJECT_NAME: str = "Review Analysis API"

    LLM_NAME: str = "models/gemma-3-27b-it"
    GOOGLE_API_KEY: str

    BATCH_SIZE: int = 15
    MAX_CONCURRENT_REQUESTS: int = 10
    RATE_LIMIT_PER_MINUTE: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
ALEBMIC_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
DATE_FORMAT = '%m/%d/%Y %H:%M UTC' #%m/%d/%Y - 
# '6/29/2011 4:52:48 AM UTC'