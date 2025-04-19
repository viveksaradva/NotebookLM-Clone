import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "DocuMind API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Knowledge Management API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # PostgreSQL settings (optional since we're using SQLite)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "documind")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "documind")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "documind")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000/api/v1")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # Changed from "forbid" to "ignore" to allow extra env vars
    }

    # API settings
    API_PREFIX: str = "/api/v1"

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    # Default to 7 days (60 * 24 * 7 = 10080 minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./documind.db")

    # Vector database settings
    VECTORDB_PATH: str = os.getenv("VECTORDB_PATH", "data/chroma_db")

    # LLM settings
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # File storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data")

settings = Settings()