"""
Configuration settings for the customer service
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Information
    service_name: str = "customer-service"
    service_version: str = "1.0.0"
    service_port: int = 8300
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard"
    db_schema: str = "customer"
    dealer_integration_schema: str = "dealer_integration"
    
    # CORS
    allowed_origins: str = "http://autology.id:5000,http://localhost:3000,http://localhost:3001,http://localhost:5000,http://localhost:5173,http://localhost:5174,http://localhost:8501,http://localhost:8502,http://localhost:8080"
    
    # Fonnte API Configuration
    fonnte_default_api_url: str = "https://api.fonnte.com/send"
    fonnte_timeout: int = 30
    
    # Rate limiting
    request_timeout: int = 30
    max_requests_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        # Environment variable mapping
        env_prefix = ""
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()