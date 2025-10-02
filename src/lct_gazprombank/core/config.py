from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    PROJECT_NAME: str = "Review Analysis API"

    LLM_NAME: str = "openai/gpt-oss-20b:free"
    OPENROUTER_API_KEY: str

    BATCH_SIZE: int = 15
    MAX_CONCURRENT_REQUESTS: int = 10
    RATE_LIMIT_PER_MINUTE: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
