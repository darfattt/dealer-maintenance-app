"""
Configuration settings for the account service
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Information
    service_name: str = "account-service"
    service_version: str = "1.0.0"
    service_port: int = 8100
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard"
    db_schema: str = "account"
    
    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-jwt-key-here"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:5000,http://localhost:5173,http://localhost:5174,http://localhost:8501,http://localhost:8502"
    
    # API Gateway
    api_gateway_url: str = "http://localhost:8080"
    
    # Admin User (for initial setup)
    admin_email: str = "admin@dealer-dashboard.com"
    admin_password: str = "Admin123!"
    admin_full_name: str = "System Administrator"
    
    # Email Configuration (for password reset)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "noreply@dealer-dashboard.com"
    
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
