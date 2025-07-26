"""
Pizza Shack REST API Backend
FastAPI application with modular structure following best practices
"""
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from dotenv import load_dotenv
import time

from .routes import main_router, api_router
from .database import init_database
from .schemas import ErrorResponse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Pizza Shack API",
    description="Pizza ordering API with IETF Agent Authentication support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS Configuration
def get_cors_origins():
    """Get CORS origins from environment variable"""
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000')
    return [origin.strip() for origin in cors_origins.split(',')]


def get_cors_methods():
    """Get CORS methods from environment variable"""
    cors_methods = os.getenv('CORS_METHODS', '*')
    if cors_methods == '*':
        return ["*"]
    return [method.strip() for method in cors_methods.split(',')]


def get_cors_headers():
    """Get CORS headers from environment variable"""
    cors_headers = os.getenv('CORS_HEADERS', '*')
    if cors_headers == '*':
        return ["*"]
    return [header.strip() for header in cors_headers.split(',')]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=os.getenv('CORS_CREDENTIALS', 'true').lower() == 'true',
    allow_methods=get_cors_methods(),
    allow_headers=get_cors_headers(),
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with detailed information"""
    start_time = time.time()
    
    # Log request details
    logger.info(f"🚀 [PIZZA-API] Incoming Request:")
    logger.info(f"  ├─ Method: {request.method}")
    logger.info(f"  ├─ URL: {request.url}")
    logger.info(f"  ├─ Path: {request.url.path}")
    logger.info(f"  ├─ Query Params: {dict(request.query_params)}")
    logger.info(f"  └─ Client: {request.client.host if request.client else 'N/A'}")
    
    # Process the request
    response = await call_next(request)
    
    # Log response details
    process_time = time.time() - start_time
    logger.info(f"✅ [PIZZA-API] Response: {response.status_code} | {process_time:.3f}s")
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error response format"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
            timestamp=datetime.now(timezone.utc).isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            status_code=500,
            timestamp=datetime.now(timezone.utc).isoformat()
        ).dict()
    )


# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Pizza Shack API...")
    init_database()
    logger.info("Pizza Shack API started successfully")


# Include routers
app.include_router(main_router)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )