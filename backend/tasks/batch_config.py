"""
Batch Processing Configuration
Centralized configuration for batch job processing performance settings
"""

import os
from typing import Dict, Any

class BatchProcessingConfig:
    """Configuration class for batch processing settings"""
    
    # Database Connection Settings
    DB_POOL_SIZE = int(os.getenv("BATCH_DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW = int(os.getenv("BATCH_DB_MAX_OVERFLOW", "50"))
    DB_POOL_TIMEOUT = int(os.getenv("BATCH_DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("BATCH_DB_POOL_RECYCLE", "1800"))  # 30 minutes
    
    # Batch Processing Settings
    DEFAULT_BATCH_SIZE = int(os.getenv("BATCH_DEFAULT_SIZE", "1000"))
    CHUNK_SIZE = int(os.getenv("BATCH_CHUNK_SIZE", "100"))
    MAX_RECORDS_PER_JOB = int(os.getenv("BATCH_MAX_RECORDS", "50000"))
    
    # API Client Settings
    API_CONNECT_TIMEOUT = int(os.getenv("API_CONNECT_TIMEOUT", "10"))
    API_READ_TIMEOUT = int(os.getenv("API_READ_TIMEOUT", "35"))
    API_WRITE_TIMEOUT = int(os.getenv("API_WRITE_TIMEOUT", "10"))
    API_POOL_TIMEOUT = int(os.getenv("API_POOL_TIMEOUT", "5"))
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv("BATCH_MAX_RETRIES", "3"))
    RETRY_BASE_DELAY = float(os.getenv("BATCH_RETRY_BASE_DELAY", "1.0"))
    RETRY_MAX_DELAY = float(os.getenv("BATCH_RETRY_MAX_DELAY", "30.0"))
    RETRY_BACKOFF_FACTOR = float(os.getenv("BATCH_RETRY_BACKOFF", "2.0"))
    
    # Circuit Breaker Settings
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    CIRCUIT_BREAKER_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "300"))  # 5 minutes
    
    # Job Queue Settings
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
    MAX_JOBS_PER_DEALER = int(os.getenv("MAX_JOBS_PER_DEALER", "1"))
    JOB_TIMEOUT_SECONDS = int(os.getenv("JOB_TIMEOUT_SECONDS", "3600"))  # 1 hour
    
    # Resource Monitoring
    MEMORY_THRESHOLD_PERCENT = int(os.getenv("MEMORY_THRESHOLD_PERCENT", "80"))
    CPU_THRESHOLD_PERCENT = int(os.getenv("CPU_THRESHOLD_PERCENT", "90"))
    
    # Logging Settings
    LOG_LEVEL = os.getenv("BATCH_LOG_LEVEL", "INFO")
    LOG_BATCH_PROGRESS = os.getenv("LOG_BATCH_PROGRESS", "true").lower() == "true"
    LOG_PERFORMANCE_METRICS = os.getenv("LOG_PERFORMANCE_METRICS", "true").lower() == "true"
    
    # Performance Optimization Settings
    ENABLE_BULK_OPERATIONS = os.getenv("ENABLE_BULK_OPERATIONS", "true").lower() == "true"
    ENABLE_PARALLEL_PROCESSING = os.getenv("ENABLE_PARALLEL_PROCESSING", "true").lower() == "true"
    ENABLE_MEMORY_OPTIMIZATION = os.getenv("ENABLE_MEMORY_OPTIMIZATION", "true").lower() == "true"
    
    @classmethod
    def get_api_client_config(cls) -> Dict[str, Any]:
        """Get API client configuration"""
        return {
            "connect_timeout": cls.API_CONNECT_TIMEOUT,
            "read_timeout": cls.API_READ_TIMEOUT,
            "write_timeout": cls.API_WRITE_TIMEOUT,
            "pool_timeout": cls.API_POOL_TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "retry_base_delay": cls.RETRY_BASE_DELAY,
            "retry_max_delay": cls.RETRY_MAX_DELAY,
            "circuit_breaker_threshold": cls.CIRCUIT_BREAKER_THRESHOLD,
            "circuit_breaker_timeout": cls.CIRCUIT_BREAKER_TIMEOUT
        }
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "pool_size": cls.DB_POOL_SIZE,
            "max_overflow": cls.DB_MAX_OVERFLOW,
            "pool_timeout": cls.DB_POOL_TIMEOUT,
            "pool_recycle": cls.DB_POOL_RECYCLE
        }
    
    @classmethod
    def get_batch_config(cls) -> Dict[str, Any]:
        """Get batch processing configuration"""
        return {
            "default_batch_size": cls.DEFAULT_BATCH_SIZE,
            "chunk_size": cls.CHUNK_SIZE,
            "max_records_per_job": cls.MAX_RECORDS_PER_JOB,
            "enable_bulk_operations": cls.ENABLE_BULK_OPERATIONS,
            "enable_parallel_processing": cls.ENABLE_PARALLEL_PROCESSING,
            "enable_memory_optimization": cls.ENABLE_MEMORY_OPTIMIZATION
        }
    
    @classmethod
    def get_job_queue_config(cls) -> Dict[str, Any]:
        """Get job queue configuration"""
        return {
            "max_concurrent_jobs": cls.MAX_CONCURRENT_JOBS,
            "max_jobs_per_dealer": cls.MAX_JOBS_PER_DEALER,
            "job_timeout_seconds": cls.JOB_TIMEOUT_SECONDS,
            "memory_threshold_percent": cls.MEMORY_THRESHOLD_PERCENT,
            "cpu_threshold_percent": cls.CPU_THRESHOLD_PERCENT
        }
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration settings"""
        return {
            "api_client": cls.get_api_client_config(),
            "database": cls.get_database_config(),
            "batch_processing": cls.get_batch_config(),
            "job_queue": cls.get_job_queue_config(),
            "logging": {
                "level": cls.LOG_LEVEL,
                "log_batch_progress": cls.LOG_BATCH_PROGRESS,
                "log_performance_metrics": cls.LOG_PERFORMANCE_METRICS
            }
        }

# Processor-specific configurations
PROCESSOR_CONFIGS = {
    "prospect": {
        "batch_size": 500,
        "estimated_duration": 300,  # 5 minutes
        "priority": "normal"
    },
    "pkb": {
        "batch_size": 1000,
        "estimated_duration": 600,  # 10 minutes
        "priority": "normal"
    },
    "parts_inbound": {
        "batch_size": 2000,
        "estimated_duration": 900,  # 15 minutes
        "priority": "normal"
    },
    "leasing": {
        "batch_size": 300,
        "estimated_duration": 450,  # 7.5 minutes
        "priority": "high"
    },
    "document_handling": {
        "batch_size": 800,
        "estimated_duration": 720,  # 12 minutes
        "priority": "high"
    },
    "unit_inbound": {
        "batch_size": 1500,
        "estimated_duration": 800,  # 13 minutes
        "priority": "normal"
    },
    "delivery_process": {
        "batch_size": 1200,
        "estimated_duration": 600,  # 10 minutes
        "priority": "high"
    },
    "billing_process": {
        "batch_size": 1000,
        "estimated_duration": 540,  # 9 minutes
        "priority": "high"
    },
    "unit_invoice": {
        "batch_size": 800,
        "estimated_duration": 480,  # 8 minutes
        "priority": "normal"
    },
    "parts_sales": {
        "batch_size": 1500,
        "estimated_duration": 720,  # 12 minutes
        "priority": "normal"
    },
    "dp_hlo": {
        "batch_size": 600,
        "estimated_duration": 420,  # 7 minutes
        "priority": "normal"
    },
    "workshop_invoice": {
        "batch_size": 1000,
        "estimated_duration": 600,  # 10 minutes
        "priority": "normal"
    },
    "unpaid_hlo": {
        "batch_size": 400,
        "estimated_duration": 300,  # 5 minutes
        "priority": "low"
    },
    "parts_invoice": {
        "batch_size": 1200,
        "estimated_duration": 660,  # 11 minutes
        "priority": "normal"
    }
}

def get_processor_config(processor_type: str) -> Dict[str, Any]:
    """Get configuration for a specific processor type"""
    return PROCESSOR_CONFIGS.get(processor_type, {
        "batch_size": BatchProcessingConfig.DEFAULT_BATCH_SIZE,
        "estimated_duration": 600,  # 10 minutes default
        "priority": "normal"
    })

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    # Production optimizations
    BatchProcessingConfig.MAX_CONCURRENT_JOBS = 2  # More conservative in production
    BatchProcessingConfig.MEMORY_THRESHOLD_PERCENT = 70  # Lower threshold
    BatchProcessingConfig.CPU_THRESHOLD_PERCENT = 80
elif os.getenv("ENVIRONMENT") == "development":
    # Development settings
    BatchProcessingConfig.LOG_LEVEL = "DEBUG"
    BatchProcessingConfig.LOG_BATCH_PROGRESS = True
    BatchProcessingConfig.LOG_PERFORMANCE_METRICS = True
