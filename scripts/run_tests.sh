#!/bin/bash

set -e  # Exit on any error

echo "=========================================="
echo "Smart Contract Audit Bot - Test Runner"
echo "=========================================="

# Adjust path to app/config.py
if [ ! -f "app/config.py" ]; then
    echo "Error: Please run this script from the project root and ensure app/config.py exists"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please create one with your API keys:"
    echo "1. cp .env.template .env"
    echo "2. Edit .env and fill in your keys"
    exit 1
fi

echo "Loading environment variables from .env..."
export $(grep -v '^#' .env | xargs)

# Warn about fake API keys
echo "Checking API key configuration..."
if [[ "$PINECONE_API_KEY" == "your_pinecone_api_key_here" ]] || [[ "$PINECONE_API_KEY" == "pc-1234"* ]]; then
    echo "⚠ Warning: Template Pinecone API key detected"
else
    echo "✓ Pinecone API key is set"
fi

if [[ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]] || [[ "$OPENAI_API_KEY" == "sk-1234"* ]]; then
    echo "⚠ Warning: Template OpenAI API key detected"
else
    echo "✓ OpenAI API key is set"
fi

echo ""
echo "Installing Python dependencies..."
pip install -q pytest numpy

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
fi

echo "Dependencies installed successfully"
echo ""

# Run tests
echo "Running test_pinecone_connection.py..."
python tests/test_pinecone_connection.py

echo ""
echo "Quick configuration validation..."
python -c "
try:
    from app.config import get_settings
    settings = get_settings()
    print('✓ Config loaded')
    print(f'  Index name: {settings.pinecone_index_name}')
    print(f'  Dimension: {settings.embedding_dimension}')
    print(f'  Environment: {settings.pinecone_environment}')
except Exception as e:
    print(f'✗ Config load failed: {e}')
    exit(1)
"

echo ""
echo "=========================================="
echo "✅ All tests completed successfully!"
echo "=========================================="
