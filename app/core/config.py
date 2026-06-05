from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "BiblioTech"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./library.db"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str = "super-secret-key-change-it-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
