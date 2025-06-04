#!/usr/bin/env python3
"""
Standalone test for configuration - run this first
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variables Test ===")
env_vars = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "PINECONE_INDEX_NAME": os.getenv("PINECONE_INDEX_NAME"),
    "PINECONE_ENVIRONMENT": os.getenv("PINECONE_ENVIRONMENT"),
    "PINECONE_REGION": os.getenv("PINECONE_REGION"),
    "INDEX_DIMENSION": os.getenv("INDEX_DIMENSION"),
    "INDEX_METRIC": os.getenv("INDEX_METRIC"),
    "TOP_K": os.getenv("TOP_K"),
    "MIN_SCORE": os.getenv("MIN_SCORE"),
    "DEBUG_MODE": os.getenv("DEBUG_MODE")
}

for key, value in env_vars.items():
    if value:
        if "KEY" in key:
            display_value = value[:10] + "..." if len(value) > 10 else value
        else:
            display_value = value
        print(f"✓ {key}: {display_value}")
    else:
        print(f"✗ {key}: NOT SET")

print("\n=== Testing Pydantic Settings ===")
try:
    # Test creating Settings directly
    from pydantic_settings import BaseSettings
    
    class TestSettings(BaseSettings):
        openai_api_key: str = ""
        pinecone_api_key: str = ""
        pinecone_environment: str = "aws"
        pinecone_index_name: str = "solidity-analyzer-v1"
        pinecone_region: str = "us-east-1"
        debug_mode: bool = True
        index_dimension: int = 1536
        index_metric: str = "cosine"
        top_k: int = 10
        min_score: float = 0.5
        
        class Config:
            env_file = ".env"
            case_sensitive = False
            extra = "allow"
    
    test_settings = TestSettings()
    print("✓ Pydantic Settings creation successful!")
    print(f"  OpenAI Key: {'✓' if test_settings.openai_api_key else '✗'}")
    print(f"  Pinecone Key: {'✓' if test_settings.pinecone_api_key else '✗'}")
    print(f"  Index Name: {test_settings.pinecone_index_name}")
    print(f"  Environment: {test_settings.pinecone_environment}")
    
except Exception as e:
    print(f"✗ Pydantic Settings failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing App Config Import ===")
try:
    sys.path.insert(0, os.getcwd())
    from app.config import get_settings
    
    settings = get_settings()
    print("✓ App config import successful!")
    print(f"  OpenAI Key: {'✓' if settings.openai_api_key else '✗'}")
    print(f"  Pinecone Key: {'✓' if settings.pinecone_api_key else '✗'}")
    
except Exception as e:
    print(f"✗ App config import failed: {e}")
    import traceback
    traceback.print_exc()