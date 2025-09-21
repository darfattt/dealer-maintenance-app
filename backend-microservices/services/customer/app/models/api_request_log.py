"""
API request log model for tracking API calls
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ApiRequestLog(Base):
    """API request log model for tracking requests and responses"""

    __tablename__ = "api_request_log"
    __table_args__ = (
        {"schema": "customer"}
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Request identification
    request_name = Column(String(100), nullable=False, index=True)  # e.g., 'add_bulk_reminders', 'validate_customer'
    dealer_id = Column(String(50), nullable=True, index=True)       # Dealer ID from request
    request_method = Column(String(10), nullable=False)             # HTTP method: GET, POST, etc.
    endpoint = Column(String(200), nullable=False)                  # API endpoint path

    # Request data
    request_payload = Column(JSONB, nullable=True)                  # Full request body as JSON
    request_headers = Column(JSONB, nullable=True)                  # Important request headers
    request_ip = Column(String(45), nullable=True)                  # Client IP address (IPv4/IPv6)
    user_email = Column(String(255), nullable=True, index=True)     # User email from JWT token

    # Response data
    response_status = Column(String(20), nullable=True, index=True) # 'success', 'error', 'partial_success'
    response_code = Column(Integer, nullable=True)                  # HTTP status code
    response_data = Column(JSONB, nullable=True)                    # Response payload (optional)
    error_message = Column(Text, nullable=True)                     # Error details if any

    # Performance metrics
    processing_time_ms = Column(Integer, nullable=True)             # Processing duration in milliseconds

    # Timestamps
    request_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_timestamp = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ApiRequestLog(id={self.id}, request_name={self.request_name}, dealer_id={self.dealer_id}, status={self.response_status})>"

    def to_dict(self):
        """Convert API request log to dictionary"""
        return {
            "id": str(self.id),
            "request_name": self.request_name,
            "dealer_id": self.dealer_id,
            "request_method": self.request_method,
            "endpoint": self.endpoint,
            "request_payload": self.request_payload,
            "request_headers": self.request_headers,
            "request_ip": self.request_ip,
            "user_email": self.user_email,
            "response_status": self.response_status,
            "response_code": self.response_code,
            "response_data": self.response_data,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "request_timestamp": self.request_timestamp.isoformat() if self.request_timestamp else None,
            "response_timestamp": self.response_timestamp.isoformat() if self.response_timestamp else None,
            "created_date": self.created_date.isoformat() if self.created_date else None,
        }

    def update_response(
        self,
        response_status: str,
        response_code: int,
        processing_time_ms: int,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update log entry with response information"""
        self.response_status = response_status
        self.response_code = response_code
        self.processing_time_ms = processing_time_ms
        self.response_timestamp = datetime.utcnow()

        if response_data:
            self.response_data = response_data

        if error_message:
            self.error_message = error_message