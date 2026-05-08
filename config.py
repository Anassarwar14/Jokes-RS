"""Configuration for the API backend."""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables or defaults."""
    
    # Database
    database_url: str = "postgresql://jokes_user:jokes_password@localhost:5433/jokes_db"
    
    # API
    api_title: str = "Jokes Recommendation API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # Model paths
    models_dir: Path = Path(__file__).parent / "models"
    processed_data_dir: Path = Path(__file__).parent / "data" / "processed"
    
    # Model defaults
    default_model: str = "pmf"
    default_seed: int = 42
    
    # Recommendation defaults
    default_top_k: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
