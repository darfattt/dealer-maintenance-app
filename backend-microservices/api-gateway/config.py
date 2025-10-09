"""
Configuration settings for the API Gateway
"""

import os
from typing import List, Dict
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API Gateway settings"""
    
    # Gateway Configuration
    gateway_port: int = 8080
    gateway_host: str = "0.0.0.0"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Service URLs
    account_service_url: str = "http://account_service:8100"
    customer_service_url: str = "http://customer_service:8300"
    dealer_dashboard_service_url: str = "http://backend:8000"
    dashboard_dealer_service_url: str = "http://dashboard_dealer_service:8200"
    
    # JWT Configuration (should match account service)
    jwt_secret_key: str = "your-super-secret-jwt-key-here-change-this-in-production"
    jwt_algorithm: str = "HS256"
    
    # CORS
    allowed_origins: str = Field(
        default="http://autology.id:5000,http://localhost:3000,http://localhost:3001,http://localhost:5000,http://localhost:5173,http://localhost:5174,http://localhost:8501,http://localhost:8502,http://127.0.0.1:5173,http://127.0.0.1:5000",
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Timeout Configuration - Environment Configurable
    request_timeout: int = Field(default=120, env="API_GATEWAY_REQUEST_TIMEOUT")  # Increased for file uploads
    file_upload_timeout: int = Field(default=300, env="API_GATEWAY_FILE_UPLOAD_TIMEOUT")  # 5 minutes for large files
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def get_service_routes(self) -> Dict[str, str]:
        """Get service routing configuration"""
        return {
            # Primary routes with /api prefix
            "/api/v1/auth": self.account_service_url,
            "/api/v1/users": self.account_service_url,
            "/api/v1/health": self.account_service_url,
            "/api/v1/customer": self.customer_service_url,
            "/api/v1/reminder": self.customer_service_url,
            "/api/v1/whatsapp-templates": self.customer_service_url,
            "/api/v1/google-reviews": self.customer_service_url,
            "/api/v1/dealers": self.dealer_dashboard_service_url,
            "/api/v1/h23-dashboard": self.dashboard_dealer_service_url,
            "/api/v1/dashboard": self.dashboard_dealer_service_url,
            "/api/v1/admin": self.dashboard_dealer_service_url,
            "/api/v1/jobs": self.dealer_dashboard_service_url,
            "/api/v1/audit": self.account_service_url,
            "/api/v1/api-logs": self.customer_service_url,
            "/api/v1/trackers": self.customer_service_url,
            "/api/v1/google-scrape-anomalies": self.customer_service_url,
             "/api/v1/whatsapp-anomalies": self.customer_service_url,
            # Google Reviews routes
            "/google-reviews": self.customer_service_url,
            "/api/google-reviews": self.customer_service_url,
            # Fallback routes without /api prefix (for debugging/compatibility)
            "/v1/auth": self.account_service_url,
            "/v1/users": self.account_service_url,
            "/v1/customer": self.customer_service_url,
            "/v1/reminder": self.customer_service_url,
            "/v1/whatsapp-templates": self.customer_service_url,
            "/v1/google-reviews": self.customer_service_url,
            "/v1/dealers": self.dealer_dashboard_service_url,
            "/v1/h23-dashboard": self.dashboard_dealer_service_url,
            "/v1/dashboard": self.dashboard_dealer_service_url,
            "/v1/admin": self.dashboard_dealer_service_url,
            "/v1/jobs": self.dealer_dashboard_service_url,
        }


# Global settings instance
settings = Settings()
