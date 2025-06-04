#!/usr/bin/env python3
"""
Test configuration loading
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    print("Testing configuration loading...")
    
    # Test loading environment variables directly
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Environment variables loaded:")
    env_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY", 
        "PINECONE_INDEX_NAME",
        "PINECONE_ENVIRONMENT",
        "PINECONE_REGION",
        "INDEX_DIMENSION",
        "INDEX_METRIC",
        "TOP_K",
        "MIN_SCORE",
        "DEBUG_MODE"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive keys
            if "KEY" in var:
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value
            print(f"  {var}: {display_value}")
        else:
            print(f"  {var}: NOT SET")
    
    print("\nTesting app.config import...")
    from app.config import Settings
    
    print("Creating Settings instance...")
    settings = Settings()
    
    print("✅ Configuration loaded successfully!")
    print(f"OpenAI API Key: {'✓' if settings.openai_api_key else '✗'}")
    print(f"Pinecone API Key: {'✓' if settings.pinecone_api_key else '✗'}")
    print(f"Pinecone Index: {settings.pinecone_index_name}")
    print(f"Pinecone Environment: {settings.pinecone_environment}")
    print(f"Debug Mode: {settings.debug_mode}")
    
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()