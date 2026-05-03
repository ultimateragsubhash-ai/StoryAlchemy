from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM API
    meshapi_api_key: str = ""
    meshapi_base_url: str = "https://api.meshapi.ai/v1"
    openai_api_key: str = ""
    
    # Vector Database
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "story_patterns"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017/storyalchemy"
    
    # Application
    env: str = "development"
    port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:8501"
    
    # Feature Flags
    enable_semantic_cache: bool = True
    max_iterations: int = 1
    cache_ttl_seconds: int = 604800
    max_requests_per_hour: int = 100
    
    # Models (OpenRouter/MeshAPI format: provider/model)
    default_embedding_model: str = "all-MiniLM-L6-v2"
    # Try different model formats - common OpenRouter models
    default_generation_model: str = "openai/gpt-4o-mini"  # Cheaper option for generation
    cheap_model: str = "google/gemini-flash-1.5"  # Fast, cheap model for extraction/critique
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"  # Standard naming
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
