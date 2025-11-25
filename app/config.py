from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Anthropic
    anthropic_api_key: str = ""
    model_name: str = "claude-3-5-haiku-20241022"

    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"

    # App
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
