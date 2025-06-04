
"""
FastAPI Main Application
Smart Contract Audit Bot API Server
"""
import os
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from app.config import get_settings, Settings
from app.ingestion_sol import ingestion_service
from app.chatbot_sol import audit_bot
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

# Initialize FastAPI app
app = FastAPI(
    title="Smart Contract Audit Bot",
    description="AI-powered smart contract security analysis and auditing system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.mount("/", StaticFiles(directory="app/frontend", html=True), name="static")



# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    include_context: bool = True

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    context_used: bool = False
    timestamp: str
    error: Optional[str] = None

class ContractAnalysisRequest(BaseModel):
    contract_content: str = Field(..., min_length=10)

class VulnerabilityExplanationRequest(BaseModel):
    vulnerability_type: str = Field(..., min_length=1, max_length=100)

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_hash: Optional[str] = None
    chunks_added: Optional[int] = None
    action: Optional[str] = None
    error: Optional[str] = None

# Dependency injection
def get_settings_dependency() -> Settings:
    return get_settings()

# Rate limiting (simplified - in production use Redis)
request_counts = {}

def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting check"""
    current_time = datetime.now().timestamp()
    hour_ago = current_time - 3600
    
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if req_time > hour_ago
    ]
    
    # Check limit
    if len(request_counts[client_ip]) >= 100:  # 100 requests per hour
        return False
    
    request_counts[client_ip].append(current_time)
    return True

# Utility functions
async def validate_file(file: UploadFile, settings: Settings) -> None:
    """Validate uploaded file"""
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB"
        )
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.allowed_file_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_file_extensions)}"
        )

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):  # ❗ You missed the `request` parameter
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        stats = await ingestion_service.get_contract_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if "error" not in stats else "error",
            "services": {
                "ingestion": "active",
                "chatbot": "active",
                "vector_db": "connected" if "error" not in stats else "error"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/upload", response_model=UploadResponse)
async def upload_contract(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    settings: Settings = Depends(get_settings_dependency)
):
    """Upload and ingest a smart contract file"""
    try:
        # Validate file
        await validate_file(file, settings)
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Ingest contract
        result = await ingestion_service.ingest_contract(file.filename, content_str)
        
        if result["success"]:
            return UploadResponse(
                success=True,
                message=result["message"],
                file_hash=result.get("file_hash"),
                chunks_added=result.get("chunks_added"),
                action=result.get("action")
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    settings: Settings = Depends(get_settings_dependency)
):
    """Chat with the audit bot"""
    try:
        result = await audit_bot.chat(
            user_message=request.message,
            include_context=request.include_context
        )
        
        if result["success"]:
            return ChatResponse(
                success=True,
                response=result["response"],
                context_used=result["context_used"],
                timestamp=result["timestamp"]
            )
        else:
            return ChatResponse(
                success=False,
                error=result["error"],
                context_used=False,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/analyze")
async def analyze_contract(
    request: ContractAnalysisRequest,
    settings: Settings = Depends(get_settings_dependency)
):
    """Perform comprehensive security analysis of a contract"""
    try:
        result = await audit_bot.analyze_contract_security(request.contract_content)
        
        if result["success"]:
            return {
                "success": True,
                "analysis": result["analysis"],
                "timestamp": result["timestamp"],
                "contract_hash": result["contract_hash"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/improvements")
async def suggest_improvements(
    request: ContractAnalysisRequest,
    settings: Settings = Depends(get_settings_dependency)
):
    """Suggest improvements for a contract"""
    try:
        result = await audit_bot.suggest_improvements(request.contract_content)
        
        if result["success"]:
            return {
                "success": True,
                "improvements": result["improvements"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improvement analysis failed: {str(e)}")

@app.post("/explain-vulnerability")
async def explain_vulnerability(
    request: VulnerabilityExplanationRequest,
    settings: Settings = Depends(get_settings_dependency)
):
    """Explain a specific vulnerability type"""
    try:
        result = await audit_bot.explain_vulnerability(request.vulnerability_type)
        
        if result["success"]:
            return {
                "success": True,
                "explanation": result["explanation"],
                "vulnerability_type": result["vulnerability_type"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        db_stats = await ingestion_service.get_contract_stats()
        conversation_stats = audit_bot.get_conversation_summary()
        
        return {
            "database": db_stats,
            "conversation": conversation_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.post("/clear-conversation")
async def clear_conversation():
    """Clear the current conversation history"""
    try:
        audit_bot.clear_conversation()
        return {
            "success": True,
            "message": "Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear conversation failed: {str(e)}")

@app.get("/search")
async def search_contracts(
    query: str,
    k: int = 5
):
    """Search for relevant contract chunks"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = await ingestion_service.search_contracts(query, k)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await ingestion_service.initialize_vector_store()
        print("✅ Smart Contract Audit Bot API started successfully")
        print("📚 Vector database initialized")
        print("🤖 Chatbot ready")
        print("🔍 Ingestion service active")
    except Exception as e:
        print(f"❌ Startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0
        port=8001,
        reload=True,
        log_level="info"
    )
