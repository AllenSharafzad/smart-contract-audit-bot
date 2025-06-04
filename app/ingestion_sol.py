
"""
Solidity Contract Ingestion Module
Handles parsing, chunking, and embedding of Solidity smart contracts
"""
import os
import re
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.config import get_settings

class SolidityParser:
    """Parse and extract information from Solidity contracts"""
    
    def __init__(self):
        self.contract_pattern = re.compile(r'contract\s+(\w+).*?\{', re.DOTALL)
        self.function_pattern = re.compile(r'function\s+(\w+)\s*\([^)]*\)\s*(?:public|private|internal|external)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?\s*\{', re.DOTALL)
        self.modifier_pattern = re.compile(r'modifier\s+(\w+)\s*\([^)]*\)\s*\{', re.DOTALL)
        self.event_pattern = re.compile(r'event\s+(\w+)\s*\([^)]*\);')
        
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from Solidity contract"""
        metadata = {
            "contracts": [],
            "functions": [],
            "modifiers": [],
            "events": [],
            "imports": [],
            "pragma": None
        }
        
        # Extract pragma
        pragma_match = re.search(r'pragma\s+solidity\s+([^;]+);', content)
        if pragma_match:
            metadata["pragma"] = pragma_match.group(1).strip()
        
        # Extract imports
        import_matches = re.findall(r'import\s+[^;]+;', content)
        metadata["imports"] = [imp.strip() for imp in import_matches]
        
        # Extract contracts
        contract_matches = self.contract_pattern.findall(content)
        metadata["contracts"] = contract_matches
        
        # Extract functions
        function_matches = self.function_pattern.findall(content)
        metadata["functions"] = function_matches
        
        # Extract modifiers
        modifier_matches = self.modifier_pattern.findall(content)
        metadata["modifiers"] = modifier_matches
        
        # Extract events
        event_matches = self.event_pattern.findall(content)
        metadata["events"] = event_matches
        
        return metadata
    
    def identify_security_patterns(self, content: str) -> List[str]:
        """Identify potential security-related patterns in the contract"""
        security_patterns = []
        
        # Check for common security patterns
        patterns = {
            "reentrancy_guard": r'nonReentrant|ReentrancyGuard',
            "access_control": r'onlyOwner|onlyAdmin|require\s*\(\s*msg\.sender',
            "safe_math": r'SafeMath|\.add\(|\.sub\(|\.mul\(|\.div\(',
            "external_calls": r'\.call\(|\.delegatecall\(|\.staticcall\(',
            "time_dependency": r'block\.timestamp|now\s',
            "randomness": r'block\.difficulty|blockhash\(',
            "overflow_checks": r'require\s*\([^)]*\+|require\s*\([^)]*\-'
        }
        
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                security_patterns.append(pattern_name)
        
        return security_patterns

class ContractIngestionService:
    """Service for ingesting and processing Solidity contracts"""
    
    def __init__(self):
        self.settings = get_settings()
        self.parser = SolidityParser()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.settings.openai_api_key,
            model="text-embedding-ada-002"
        )
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
        self.vector_store = None
        
    async def initialize_vector_store(self):
        """Initialize Pinecone vector store"""
        try:
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.settings.pinecone_index_name not in existing_indexes:
                self.pc.create_index(
                    name=self.settings.pinecone_index_name,
                    dimension=self.settings.embedding_dimension,
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
            
            self.vector_store = PineconeVectorStore(
                index_name=self.settings.pinecone_index_name,
                embedding=self.embeddings
            )
            
        except Exception as e:
            raise Exception(f"Failed to initialize vector store: {str(e)}")
    
    def generate_file_hash(self, content: str) -> str:
        """Generate hash for file content to avoid duplicates"""
        return hashlib.md5(content.encode()).hexdigest()
    
    async def process_contract_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Process a single Solidity contract file"""
        try:
            # Extract metadata
            metadata = self.parser.extract_metadata(content)
            security_patterns = self.parser.identify_security_patterns(content)
            
            # Generate file hash
            file_hash = self.generate_file_hash(content)
            
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Prepare documents for vector store
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "contracts": metadata["contracts"],
                    "functions": metadata["functions"][:10],  # Limit to avoid metadata size issues
                    "security_patterns": security_patterns,
                    "pragma": metadata["pragma"],
                    "content_type": "solidity_contract"
                }
                documents.append({
                    "content": chunk,
                    "metadata": doc_metadata
                })
            
            return {
                "success": True,
                "file_path": file_path,
                "file_hash": file_hash,
                "chunks_count": len(chunks),
                "metadata": metadata,
                "security_patterns": security_patterns,
                "documents": documents
            }
            
        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    async def ingest_contract(self, file_path: str, content: str) -> Dict[str, Any]:
        """Ingest a single contract into the vector database"""
        if not self.vector_store:
            await self.initialize_vector_store()
        
        # Process the contract
        result = await self.process_contract_file(file_path, content)
        
        if not result["success"]:
            return result
        
        try:
            # Check if file already exists
            existing_docs = self.vector_store.similarity_search(
                query=f"file_hash:{result['file_hash']}",
                k=1,
                filter={"file_hash": result["file_hash"]}
            )
            
            if existing_docs:
                return {
                    "success": True,
                    "message": "Contract already exists in database",
                    "file_hash": result["file_hash"],
                    "action": "skipped"
                }
            
            # Add documents to vector store
            texts = [doc["content"] for doc in result["documents"]]
            metadatas = [doc["metadata"] for doc in result["documents"]]
            
            self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            
            return {
                "success": True,
                "message": "Contract successfully ingested",
                "file_path": file_path,
                "file_hash": result["file_hash"],
                "chunks_added": len(texts),
                "metadata": result["metadata"],
                "security_patterns": result["security_patterns"],
                "action": "ingested"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to ingest contract: {str(e)}"
            }
    
    async def ingest_multiple_contracts(self, contracts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Ingest multiple contracts"""
        results = []
        
        for contract in contracts:
            result = await self.ingest_contract(
                contract["file_path"],
                contract["content"]
            )
            results.append(result)
        
        return results
    
    async def search_contracts(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant contract chunks"""
        if not self.vector_store:
            await self.initialize_vector_store()
        
        k = k or self.settings.top_k_results
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": getattr(doc, 'score', None)
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    async def get_contract_stats(self) -> Dict[str, Any]:
        """Get statistics about ingested contracts"""
        if not self.vector_store:
            await self.initialize_vector_store()
        
        try:
            # This is a simplified version - in production you'd want more detailed stats
            index = self.pc.Index(self.settings.pinecone_index_name)
            stats = index.describe_index_stats()
            
            return {
                "total_vectors": stats.total_vector_count,
                "index_fullness": stats.index_fullness,
                "dimension": stats.dimension
            }
            
        except Exception as e:
            return {"error": f"Failed to get stats: {str(e)}"}

# Global service instance
ingestion_service = ContractIngestionService()
