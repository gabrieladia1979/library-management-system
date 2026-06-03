from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "BiblioTech"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./library.db"
    API_V1_STR: str = "/api/v1"

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
