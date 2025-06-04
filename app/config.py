
"""
Configuration module for Smart Contract Audit Bot
Handles environment variables and application settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    pinecone_api_key: str = ""
    
    # Pinecone Configuration
    pinecone_environment: str = "aws"
    pinecone_index_name: str = "solidity-analyzer-v1"
    pinecone_region: str = "us-east-1"
    
    # Application Settings
    app_name: str = "Smart Contract Audit Bot"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    debug_mode: bool = True
    
    # Security Settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_extensions: list = [".sol", ".txt"]
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # LLM Settings
    openai_model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.1
    
    # Chunking Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Vector Database Settings
    embedding_dimension: int = 1536
    index_dimension: int = 1536
    index_metric: str = "cosine"
    top_k_results: int = 5
    top_k: int = 10
    min_score: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment

# Global settings instance (lazy loading)
_settings = None

def validate_configuration(settings_instance: Settings) -> bool:
    """Validate that all required configuration is present"""
    required_keys = ["openai_api_key", "pinecone_api_key"]
    missing_keys = []
    
    for key in required_keys:
        if not getattr(settings_instance, key):
            missing_keys.append(key.upper())
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True

def get_settings() -> Settings:
    """Get validated settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
        validate_configuration(_settings)
    return _settings
