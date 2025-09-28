"""
Configuration settings for the customer service
"""

import os
from typing import List
from pydantic import Field
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
    
    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-jwt-key-here-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: str = "http://autology.id:5000,http://localhost:3000,http://localhost:3001,http://localhost:5000,http://localhost:5173,http://localhost:5174,http://localhost:8501,http://localhost:8502,http://localhost:8080"
    
    # Fonnte API Configuration
    fonnte_default_api_url: str = "https://api.fonnte.com/send"
    fonnte_timeout: int = 30
    
    # Sentiment Analysis API Configuration - Environment Configurable
    sentiment_api_url: str = Field(
        default="https://ai.daya-group.co.id:8090/api/v1/prediction/f482750b-b270-4515-8e91-c36d1c215e0b",
        env="SENTIMENT_API_URL"
    )
    sentiment_api_token: str = Field(
        default="VQF6fIutCf5Md2s7MR5qiJmvAoGJe6jynNGWydXHxyI",
        env="SENTIMENT_API_TOKEN"
    )
    sentiment_api_timeout: int = Field(default=120, env="SENTIMENT_API_TIMEOUT")  # Reduced from 120s to 60s
    sentiment_api_max_retries: int = Field(default=5, env="SENTIMENT_API_MAX_RETRIES")
    sentiment_api_retry_delay: float = Field(default=2.0, env="SENTIMENT_API_RETRY_DELAY")
    sentiment_api_connect_timeout: int = Field(default=10, env="SENTIMENT_API_CONNECT_TIMEOUT")
    sentiment_api_read_timeout: int = Field(default=60, env="SENTIMENT_API_READ_TIMEOUT")
    
    # Circuit Breaker Configuration for Sentiment Analysis
    sentiment_circuit_breaker_failure_threshold: int = Field(default=5, env="SENTIMENT_CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    sentiment_circuit_breaker_timeout: int = Field(default=300, env="SENTIMENT_CIRCUIT_BREAKER_TIMEOUT")  # 5 minutes
    sentiment_circuit_breaker_expected_exception: bool = Field(default=True, env="SENTIMENT_CIRCUIT_BREAKER_EXPECTED_EXCEPTION")

    # Apify API Configuration - Google Maps Scraper
    apify_api_url: str = Field(
        default="https://api.apify.com/v2/actor-tasks/operational_tangent~google-maps-scraper-task/run-sync-get-dataset-items",
        env="APIFY_API_URL"
    )
    apify_api_token: str = Field(
        default="",
        env="APIFY_API_TOKEN"
    )
    apify_timeout: int = Field(default=120, env="APIFY_TIMEOUT")

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