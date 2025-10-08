"""
Pydantic schemas for API request log operations
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class ApiRequestLogResponse(BaseModel):
    """Schema for API request log response"""
    id: str
    request_name: str
    dealer_id: Optional[str]
    request_method: str
    endpoint: str
    request_payload: Optional[Dict]
    request_headers: Optional[Dict]
    request_ip: Optional[str]
    user_email: Optional[str]
    response_status: Optional[str]
    response_code: Optional[int]
    response_data: Optional[Dict]
    error_message: Optional[str]
    processing_time_ms: Optional[int]
    request_timestamp: datetime
    response_timestamp: Optional[datetime]
    created_date: datetime

    class Config:
        from_attributes = True


class ApiRequestLogListResponse(BaseModel):
    """Schema for API request log list response"""
    date: str
    total: int
    logs: list[ApiRequestLogResponse]


class DealerSummaryResponse(BaseModel):
    """Schema for dealer summary response"""
    dealer_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_processing_time_ms: float
    request_count_by_type: Dict[str, int]


class DealerSummaryListResponse(BaseModel):
    """Schema for dealer summary list response"""
    date: str
    total_dealers: int
    summaries: list[DealerSummaryResponse]
