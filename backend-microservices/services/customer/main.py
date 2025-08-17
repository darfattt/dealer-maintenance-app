"""
Main FastAPI application for the customer service
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from app.config import settings
from app.routes.customer import router as customer_router
from app.routes.customer_reminder import router as customer_reminder_router
from app.routes.health import router as health_router
from utils.database import DatabaseManager
from utils.logger import setup_logger
from sqlalchemy import text

# Setup logger
logger = setup_logger(__name__)

# Database manager
db_manager = DatabaseManager(settings.db_schema)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    
    # Create database schema and tables
    try:
        # Import models to register them with Base
        from app.models.customer_validation_request import CustomerValidationRequest, Base
        from app.models.customer_reminder_request import CustomerReminderRequest
        
        # Create schema and tables with checkfirst=True to avoid conflicts
        logger.info("Creating database schema and tables...")
        db_manager.create_schema_tables_safe(Base.metadata)
        logger.info("Database tables created successfully")
        
        # Create customer schema if not exists
        for session in db_manager.get_session():
            session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.db_schema}"))
            session.commit()
            logger.info(f"Schema {settings.db_schema} ensured")
            break
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.service_name}")


# Create FastAPI application
app = FastAPI(
    title="Customer Service",
    description="Customer validation and reminder WhatsApp notification microservice for Dealer Dashboard",
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
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


# Include routers
app.include_router(customer_router, prefix="/api/v1")
app.include_router(customer_reminder_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled"
    }


# Service info endpoint
@app.get("/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_schema": settings.db_schema,
        "fonnte_api_url": settings.fonnte_default_api_url
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )