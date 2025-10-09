"""
Pydantic schemas for WhatsApp integration anomaly logging
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field
from enum import Enum


class RequestType(str, Enum):
    """Enum for request types"""
    VALIDATION = "VALIDATION"
    REMINDER = "REMINDER"
    ALL = "ALL"


class WhatsAppAnomalyRecord(BaseModel):
    """Schema for individual WhatsApp integration failure record"""

    id: str = Field(..., description="Record UUID")
    dealer_id: str = Field(..., description="Dealer ID")
    request_type: str = Field(..., description="Type of request (VALIDATION/REMINDER)")
    request_date: str = Field(..., description="Request date (YYYY-MM-DD)")
    request_time: str = Field(..., description="Request time (HH:mm:ss)")
    customer_name: Optional[str] = Field(None, description="Customer name")
    phone_number: Optional[str] = Field(None, description="Phone number (masked)")
    whatsapp_status: str = Field(..., description="WhatsApp message status")
    whatsapp_message: Optional[str] = Field(None, description="WhatsApp message content")
    fonnte_response: Optional[Dict[str, Any]] = Field(None, description="Fonnte API response")
    error_details: Optional[str] = Field(None, description="Error details extracted from response")
    created_date: str = Field(..., description="Record creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "dealer_id": "00999",
                "request_type": "VALIDATION",
                "request_date": "2025-01-10",
                "request_time": "10:30:00",
                "customer_name": "John Doe",
                "phone_number": "0821****3421",
                "whatsapp_status": "FAILED",
                "whatsapp_message": "Halo John, terima kasih...",
                "fonnte_response": {
                    "status": False,
                    "reason": "invalid number"
                },
                "error_details": "invalid number",
                "created_date": "2025-01-10T10:30:00+07:00"
            }
        }


class PaginationMetadata(BaseModel):
    """Schema for pagination metadata"""

    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_records: int = Field(..., description="Total number of records")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 10,
                "total_records": 150,
                "total_pages": 15
            }
        }


class WhatsAppAnomalyListResponse(BaseModel):
    """Schema for paginated WhatsApp anomaly list response"""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: List[WhatsAppAnomalyRecord] = Field(..., description="List of anomaly records")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "WhatsApp anomalies retrieved successfully",
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "dealer_id": "00999",
                        "request_type": "VALIDATION",
                        "request_date": "2025-01-10",
                        "request_time": "10:30:00",
                        "customer_name": "John Doe",
                        "phone_number": "0821****3421",
                        "whatsapp_status": "FAILED",
                        "whatsapp_message": "Halo John...",
                        "fonnte_response": {"status": False},
                        "error_details": "invalid number",
                        "created_date": "2025-01-10T10:30:00+07:00"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_records": 150,
                    "total_pages": 15
                }
            }
        }


class WhatsAppStatusBreakdown(BaseModel):
    """Schema for WhatsApp status breakdown"""

    status: str = Field(..., description="Status name")
    count: int = Field(..., description="Number of occurrences")
    percentage: float = Field(..., description="Percentage of total")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "FAILED",
                "count": 45,
                "percentage": 75.0
            }
        }


class WhatsAppAnomalySummary(BaseModel):
    """Schema for WhatsApp anomaly summary statistics"""

    total_failed: int = Field(..., description="Total failed integrations")
    daily_failed: int = Field(..., description="Failed integrations today")
    weekly_failed: int = Field(..., description="Failed integrations in past 7 days")
    total_requests: int = Field(..., description="Total requests in period")
    failure_rate: float = Field(..., description="Failure rate percentage")
    daily_failure_rate: float = Field(..., description="Daily failure rate percentage")
    weekly_failure_rate: float = Field(..., description="Weekly failure rate percentage")
    breakdown_by_status: List[WhatsAppStatusBreakdown] = Field(..., description="Breakdown by status")
    breakdown_by_type: Dict[str, int] = Field(..., description="Breakdown by request type")

    class Config:
        json_schema_extra = {
            "example": {
                "total_failed": 150,
                "daily_failed": 12,
                "weekly_failed": 85,
                "total_requests": 500,
                "failure_rate": 30.0,
                "daily_failure_rate": 25.0,
                "weekly_failure_rate": 28.0,
                "breakdown_by_status": [
                    {"status": "FAILED", "count": 90, "percentage": 60.0},
                    {"status": "ERROR", "count": 45, "percentage": 30.0},
                    {"status": "REJECTED", "count": 15, "percentage": 10.0}
                ],
                "breakdown_by_type": {
                    "VALIDATION": 80,
                    "REMINDER": 70
                }
            }
        }


class WhatsAppAnomalySummaryResponse(BaseModel):
    """Schema for WhatsApp anomaly summary response"""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: WhatsAppAnomalySummary = Field(..., description="Summary statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "WhatsApp anomaly summary retrieved successfully",
                "data": {
                    "total_failed": 150,
                    "daily_failed": 12,
                    "weekly_failed": 85,
                    "total_requests": 500,
                    "failure_rate": 30.0,
                    "daily_failure_rate": 25.0,
                    "weekly_failure_rate": 28.0,
                    "breakdown_by_status": [
                        {"status": "FAILED", "count": 90, "percentage": 60.0}
                    ],
                    "breakdown_by_type": {
                        "VALIDATION": 80,
                        "REMINDER": 70
                    }
                }
            }
        }
