"""
FastAPI main application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from loguru import logger
import sys

from backend.core.config import get_settings
from backend.models.schemas import HealthResponse
from backend.api.routes import chat, predictions, data

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/sephira_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="INFO"
)

# Initialize settings
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Sephira Orion API",
    description="RAG-based sentiment analysis system with predictive capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
# Allow localhost for development and Vercel domain for production
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.vercel.app",  # Allow all Vercel preview deployments
    "https://sephiraorion.vercel.app",  # Production domain (update with your actual domain)
]

# In production, be more restrictive
if settings.environment == "production":
    # Only allow production domains
    allowed_origins = [
        "https://*.vercel.app",
        "https://sephiraorion.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app" if settings.environment == "production" else None,
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s - "
        f"Client: {request.client.host}"
    )
    
    return response


# Include routers
app.include_router(chat.router)
app.include_router(predictions.router)
app.include_router(data.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Sephira Orion API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns system status and service availability.
    """
    try:
        # Check services
        services = {
            "api": True,
            "rag_engine": False,
            "predictor": False,
            "database": False
        }
        
        # Try to check RAG engine
        try:
            from backend.core.rag_engine import RAGEngine
            engine = RAGEngine()
            stats = engine.get_stats()
            services["rag_engine"] = stats['status'] == 'operational'
            services["database"] = True
        except:
            pass
        
        # Try to check predictor
        try:
            from backend.models.predictor import SentimentPredictor
            predictor = SentimentPredictor()
            services["predictor"] = True
        except:
            pass
        
        return HealthResponse(
            status="healthy" if all(services.values()) else "degraded",
            version="1.0.0",
            timestamp=datetime.now(),
            services=services
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            timestamp=datetime.now(),
            services={"api": True}
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
