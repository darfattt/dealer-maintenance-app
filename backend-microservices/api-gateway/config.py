"""
Configuration settings for the API Gateway
"""

import os
from typing import List, Dict
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
    account_service_url: str = "http://localhost:8100"
    dealer_dashboard_service_url: str = "http://localhost:8000"
    
    # JWT Configuration (should match account service)
    jwt_secret_key: str = "your-super-secret-jwt-key-here"
    jwt_algorithm: str = "HS256"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8501,http://localhost:8502"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Timeout Configuration
    request_timeout: int = 30  # seconds
    
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
            "/api/v1/auth": self.account_service_url,
            "/api/v1/users": self.account_service_url,
            "/api/v1/health": self.account_service_url,
            "/api/v1/dealers": self.dealer_dashboard_service_url,
            "/api/v1/dashboard": self.dealer_dashboard_service_url,
            "/api/v1/jobs": self.dealer_dashboard_service_url,
        }


# Global settings instance
settings = Settings()
