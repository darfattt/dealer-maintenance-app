"""
Centralized logging configuration for microservices
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": os.getenv("SERVICE_NAME", "unknown-service"),
            "version": os.getenv("SERVICE_VERSION", "unknown"),
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    level: str = "INFO",
    use_json: bool = None
) -> logging.Logger:
    """
    Setup logger with appropriate formatter based on environment
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Force JSON format. If None, auto-detect based on environment
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Determine formatter based on environment
    if use_json is None:
        use_json = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def log_with_context(logger: logging.Logger, level: str, message: str, **context: Any) -> None:
    """
    Log message with additional context fields
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **context: Additional context fields
    """
    record = logging.LogRecord(
        name=logger.name,
        level=getattr(logging, level.upper()),
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    record.extra_fields = context
    logger.handle(record)


# Default logger for the utils module
logger = setup_logger(__name__)
