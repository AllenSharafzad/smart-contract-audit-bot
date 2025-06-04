
#!/usr/bin/env python3
"""
Comprehensive test suite for Pinecone connection and basic functionality
Tests the fixed configuration and validates core operations
"""

import pytest
import sys
import os
import time
import numpy as np
from unittest.mock import patch, MagicMock

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

class TestPineconeConnection:
    """Test suite for Pinecone connection and basic operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.config = None
        self.index = None
    
    def teardown_method(self):
        """Cleanup after each test method"""
        if self.index and hasattr(self.index, 'delete'):
            try:
                # Clean up test vectors
                self.index.delete(delete_all=True)
            except:
                pass
    
    def test_config_initialization(self):
        """Test that configuration loads and validates properly"""
        try:
            self.config = Config()
            
            # Test that all required fields are present
            assert self.config.pinecone_api_key is not None, "Pinecone API key not loaded"
            assert self.config.pinecone_environment is not None, "Pinecone environment not loaded"
            assert self.config.pinecone_cloud is not None, "Pinecone cloud not loaded"
            assert self.config.pinecone_region is not None, "Pinecone region not loaded"
            assert self.config.openai_api_key is not None, "OpenAI API key not loaded"
            assert self.config.index_name is not None, "Index name not loaded"
            assert self.config.dimension == 1536, "Dimension not set correctly"
            
            print("✓ Configuration loaded successfully")
            print(f"  - Environment: {self.config.pinecone_environment}")
            print(f"  - Cloud: {self.config.pinecone_cloud}")
            print(f"  - Region: {self.config.pinecone_region}")
            print(f"  - Index: {self.config.index_name}")
            print(f"  - Dimension: {self.config.dimension}")
            
        except Exception as e:
            pytest.fail(f"Configuration initialization failed: {e}")
    
    def test_env_value_cleaning(self):
        """Test that environment value cleaning works properly"""
        config = Config()
        
        # Test cleaning various formats
        test_cases = [
            ('"quoted_value"', 'quoted_value'),
            ("'single_quoted'", 'single_quoted'),
            ('value_with_comment # this is a comment', 'value_with_comment'),
            ('  spaced_value  ', 'spaced_value'),
            ('"quoted_with_comment" # comment', 'quoted_with_comment'),
            ('  "  spaced_quoted  "  # comment  ', 'spaced_quoted'),
        ]
        
        for input_val, expected in test_cases:
            cleaned = config._clean_env_value(input_val)
            assert cleaned == expected, f"Failed to clean '{input_val}' -> expected '{expected}', got '{cleaned}'"
        
        print("✓ Environment value cleaning works correctly")
    
    @pytest.mark.skipif(
        os.getenv('PINECONE_API_KEY', '').startswith('your_') or 
        os.getenv('PINECONE_API_KEY', '') == 'pc-1234567890abcdef1234567890abcdef12345678',
        reason="Real Pinecone API key required for integration tests"
    )
    def test_pinecone_initialization(self):
        """Test Pinecone initialization with real API keys"""
        try:
            self.config = Config()
            self.index = self.config.initialize_pinecone()
            
            assert self.index is not None, "Failed to get index object"
            
            # Test basic index operations
            stats = self.index.describe_index_stats()
            assert 'dimension' in stats, "Index stats should contain dimension"
            
            print("✓ Pinecone initialization successful")
            print(f"  - Index stats: {stats}")
            
        except Exception as e:
            pytest.fail(f"Pinecone initialization failed: {e}")
    
    @pytest.mark.skipif(
        os.getenv('PINECONE_API_KEY', '').startswith('your_') or 
        os.getenv('PINECONE_API_KEY', '') == 'pc-1234567890abcdef1234567890abcdef12345678',
        reason="Real Pinecone API key required for integration tests"
    )
    def test_basic_ingestion_and_retrieval(self):
        """Test basic document ingestion and retrieval"""
        try:
            self.config = Config()
            self.index = self.config.initialize_pinecone()
            
            # Create test vectors
            test_vectors = [
                {
                    'id': 'test-doc-1',
                    'values': np.random.rand(1536).tolist(),
                    'metadata': {
                        'content': 'This is a test smart contract audit document',
                        'type': 'audit',
                        'severity': 'medium'
                    }
                },
                {
                    'id': 'test-doc-2', 
                    'values': np.random.rand(1536).tolist(),
                    'metadata': {
                        'content': 'Another test document about security vulnerabilities',
                        'type': 'vulnerability',
                        'severity': 'high'
                    }
                }
            ]
            
            # Upsert test vectors
            upsert_response = self.index.upsert(vectors=test_vectors)
            assert upsert_response['upserted_count'] == 2, "Failed to upsert test vectors"
            
            print("✓ Test vectors upserted successfully")
            
            # Wait for indexing
            time.sleep(2)
            
            # Test query
            query_vector = np.random.rand(1536).tolist()
            query_response = self.index.query(
                vector=query_vector,
                top_k=2,
                include_metadata=True
            )
            
            assert 'matches' in query_response, "Query response should contain matches"
            assert len(query_response['matches']) <= 2, "Should return at most 2 matches"
            
            print("✓ Query executed successfully")
            print(f"  - Found {len(query_response['matches'])} matches")
            
            # Test fetch
            fetch_response = self.index.fetch(ids=['test-doc-1'])
            assert 'vectors' in fetch_response, "Fetch response should contain vectors"
            assert 'test-doc-1' in fetch_response['vectors'], "Should fetch the requested document"
            
            print("✓ Fetch executed successfully")
            
            # Cleanup
            self.index.delete(ids=['test-doc-1', 'test-doc-2'])
            print("✓ Test vectors cleaned up")
            
        except Exception as e:
            pytest.fail(f"Ingestion and retrieval test failed: {e}")
    
    def test_mock_pinecone_operations(self):
        """Test Pinecone operations with mocked responses (works without real API keys)"""
        with patch('pinecone.init') as mock_init, \
             patch('pinecone.list_indexes') as mock_list, \
             patch('pinecone.Index') as mock_index_class, \
             patch('pinecone.create_index') as mock_create:
            
            # Setup mocks
            mock_list.return_value = []
            mock_index = MagicMock()
            mock_index.describe_index_stats.return_value = {'dimension': 1536, 'total_vector_count': 0}
            mock_index.upsert.return_value = {'upserted_count': 1}
            mock_index.query.return_value = {'matches': []}
            mock_index_class.return_value = mock_index
            mock_create.return_value = None
            
            # Test with mock
            self.config = Config()
            
            # Override API keys for mock test
            self.config.pinecone_api_key = 'mock-key'
            self.config.openai_api_key = 'mock-key'
            
            index = self.config.initialize_pinecone()
            
            # Verify mocks were called
            mock_init.assert_called_once()
            mock_index_class.assert_called_once()
            
            # Test operations
            stats = index.describe_index_stats()
            assert stats['dimension'] == 1536
            
            upsert_result = index.upsert(vectors=[{'id': 'test', 'values': [0.1] * 1536}])
            assert upsert_result['upserted_count'] == 1
            
            query_result = index.query(vector=[0.1] * 1536, top_k=1)
            assert 'matches' in query_result
            
            print("✓ Mock Pinecone operations work correctly")

def run_tests():
    """Run all tests and return results"""
    print("=" * 60)
    print("SMART CONTRACT AUDIT BOT - PINECONE FUNCTIONALITY TESTS")
    print("=" * 60)
    
    # Check if real API keys are available
    real_keys = (
        os.getenv('PINECONE_API_KEY', '').startswith('pc-') and 
        not os.getenv('PINECONE_API_KEY', '').startswith('pc-1234') and
        os.getenv('OPENAI_API_KEY', '').startswith('sk-') and
        not os.getenv('OPENAI_API_KEY', '').startswith('sk-1234')
    )
    
    if real_keys:
        print("✓ Real API keys detected - running full integration tests")
    else:
        print("⚠ Template/mock API keys detected - running configuration and mock tests only")
        print("  To run full tests, update .env with real API keys")
    
    print()
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--no-header'
    ])
    
    return exit_code == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
