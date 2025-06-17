"""
Main FastAPI application for the account service
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
from app.routes import auth_router, users_router, user_dealers_router, health_router
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from utils.database import DatabaseManager
from utils.logger import setup_logger

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
        from app.models.user import User, UserDealer, Base

        # Create schema and tables
        db_manager.create_schema_tables(Base.metadata)
        logger.info("Database tables created successfully")

        # Create default admin user if not exists
        await create_default_admin()

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.service_name}")


async def create_default_admin():
    """Create default admin user if not exists"""
    try:
        db = next(db_manager.get_session())
        user_repo = UserRepository(db)
        
        # Check if admin user already exists
        admin_user = user_repo.get_user_by_email(settings.admin_email)
        if admin_user:
            logger.info("Default admin user already exists")
            return
        
        # Create admin user
        from app.schemas.user import UserCreate
        admin_data = UserCreate(
            email=settings.admin_email,
            password=settings.admin_password,
            full_name=settings.admin_full_name,
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        
        admin_user = user_repo.create_user(admin_data)
        logger.info(f"Default admin user created: {admin_user.email}")
        
    except Exception as e:
        logger.error(f"Failed to create default admin user: {str(e)}")
    finally:
        db.close()


# Create FastAPI application
app = FastAPI(
    title="Account Service",
    description="User authentication and authorization microservice for Dealer Dashboard",
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
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(user_dealers_router, prefix="/api/v1")
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
        "database_schema": settings.db_schema
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
