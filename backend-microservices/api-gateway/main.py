"""
API Gateway for microservices
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from config import settings
from middleware import RateLimitMiddleware, AuthMiddleware, ProxyMiddleware, LoggingMiddleware
from utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Initialize middleware
rate_limiter = RateLimitMiddleware(
    requests_per_window=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window
)

auth_middleware = AuthMiddleware(
    jwt_secret=settings.jwt_secret_key,
    jwt_algorithm=settings.jwt_algorithm
)

proxy_middleware = ProxyMiddleware(
    service_routes=settings.get_service_routes(),
    timeout=settings.request_timeout
)

logging_middleware = LoggingMiddleware()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting API Gateway")
    logger.info(f"Service routes: {settings.get_service_routes()}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway")
    await proxy_middleware.close()


# Create FastAPI application
app = FastAPI(
    title="API Gateway",
    description="API Gateway for Dealer Dashboard Microservices",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly in production
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "InternalServerError"
            }
        }
    )


# Middleware processing
@app.middleware("http")
async def process_request(request: Request, call_next):
    """Process all HTTP requests through middleware"""
    start_time = time.time()
    
    try:
        # Rate limiting
        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": 429,
                        "message": "Rate limit exceeded",
                        "type": "RateLimitExceeded"
                    }
                }
            )
        
        # Authentication (for non-public paths)
        if not auth_middleware.is_public_path(request.url.path):
            user = auth_middleware.extract_user_from_token(request)
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "code": 401,
                            "message": "Authentication required",
                            "type": "Unauthorized"
                        }
                    }
                )
            # Store user in request state
            request.state.user = user
        
        # Proxy request to appropriate service
        response = await proxy_middleware.proxy_request(request)
        
        # Log request
        process_time = time.time() - start_time
        await logging_middleware.log_request(request, response, process_time)
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "type": "InternalServerError"
                }
            }
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
        "services": list(settings.get_service_routes().keys())
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "services": settings.get_service_routes()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
