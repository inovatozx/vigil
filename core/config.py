from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    APP_NAME: str = "Vigil AI Workspace"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = "sqlite:///./data/app.db"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "super-secret-key-vigil-ai-replace-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TOTP_ISSUER: str = "VigilAI"
    CORS_ORIGINS: list[str] = ["*"] # Adjust in production
    RATE_LIMIT_PER_MINUTE: int = 1000
    SEARCH_ENGINE_URL: str = os.environ.get("SEARCH_ENGINE_URL", "http://localhost:8080") # SearXNG
    CHROMA_DB_PATH: str = "./data/chroma_db"
    EMBEDDING_MODEL_PATH: str = "./data/models/onnx_embedding_model"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
