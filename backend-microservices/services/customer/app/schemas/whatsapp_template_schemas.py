"""
Pydantic schemas for WhatsApp template management operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class TemplateOperation(str, Enum):
    """Enum for template audit operations"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    COPY = "COPY"


class WhatsAppTemplateResponse(BaseModel):
    """Schema for WhatsApp template response"""

    id: str = Field(..., description="Template UUID")
    reminder_target: str = Field(..., description="Reminder target category")
    reminder_type: str = Field(..., description="Reminder type")
    dealer_id: Optional[str] = Field(None, description="Dealer ID (null for global templates)")
    template: str = Field(..., description="Template content")
    created_by: Optional[str] = Field(None, description="User who created the template")
    created_date: str = Field(..., description="Creation timestamp")
    last_modified_by: Optional[str] = Field(None, description="User who last modified")
    last_modified_date: str = Field(..., description="Last modification timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "reminder_target": "KPB-1",
                "reminder_type": "H+30 tanggal beli (by WA)",
                "dealer_id": "AHASS001",
                "template": "Halo {nama_pelanggan}, saatnya servis KPB-1 untuk kendaraan Anda.",
                "created_by": "admin@dealer.com",
                "created_date": "2024-01-15T10:30:00.000Z",
                "last_modified_by": "admin@dealer.com",
                "last_modified_date": "2024-01-15T10:30:00.000Z"
            }
        }


class WhatsAppTemplateListRequest(BaseModel):
    """Schema for template list request parameters"""

    dealer_id: Optional[str] = Field(None, description="Filter by dealer ID (empty for global templates)")
    reminder_target: Optional[str] = Field(None, description="Filter by reminder target")
    template: Optional[str] = Field(None, description="Search in template content (contains)")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(10, ge=1, le=100, description="Page size (max 100)")

    class Config:
        json_schema_extra = {
            "example": {
                "dealer_id": "AHASS001",
                "reminder_target": "KPB-1",
                "template": "servis",
                "page": 1,
                "size": 10
            }
        }


class WhatsAppTemplateListResponse(BaseModel):
    """Schema for paginated template list response"""

    success: bool = Field(..., description="Request success status")
    data: List[WhatsAppTemplateResponse] = Field(..., description="List of templates")
    pagination: Dict[str, Any] = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "reminder_target": "KPB-1",
                        "reminder_type": "H+30 tanggal beli (by WA)",
                        "dealer_id": "AHASS001",
                        "template": "Halo {nama_pelanggan}, saatnya servis KPB-1.",
                        "created_by": "admin@dealer.com",
                        "created_date": "2024-01-15T10:30:00.000Z",
                        "last_modified_by": "admin@dealer.com",
                        "last_modified_date": "2024-01-15T10:30:00.000Z"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "size": 10,
                    "total": 25,
                    "total_pages": 3,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }


class WhatsAppTemplateUpdateRequest(BaseModel):
    """Schema for template update request"""

    template: str = Field(..., min_length=1, max_length=2000, description="Template content")
    reminder_target: str = Field(..., min_length=1, max_length=50, description="Reminder target category")
    reminder_type: str = Field(..., min_length=1, max_length=100, description="Reminder type")

    @validator('template')
    def validate_template_content(cls, v):
        """Validate template content for basic security"""
        if not v or not v.strip():
            raise ValueError('Template content cannot be empty')

        # Basic XSS prevention
        dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f'Template content contains potentially dangerous pattern: {pattern}')

        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "template": "Halo {nama_pelanggan}, saatnya melakukan servis KPB-1 untuk kendaraan Honda Anda.",
                "reminder_target": "KPB-1",
                "reminder_type": "H+30 tanggal beli (by WA)"
            }
        }


class WhatsAppTemplateUpdateResponse(BaseModel):
    """Schema for template update response"""

    success: bool = Field(..., description="Update success status")
    message: str = Field(..., description="Response message")
    data: Optional[WhatsAppTemplateResponse] = Field(None, description="Updated template data")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Template updated successfully",
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "reminder_target": "KPB-1",
                    "reminder_type": "H+30 tanggal beli (by WA)",
                    "dealer_id": "AHASS001",
                    "template": "Updated template content",
                    "created_by": "admin@dealer.com",
                    "created_date": "2024-01-15T10:30:00.000Z",
                    "last_modified_by": "user@dealer.com",
                    "last_modified_date": "2024-01-16T14:30:00.000Z"
                }
            }
        }


class WhatsAppTemplateDeleteResponse(BaseModel):
    """Schema for template delete response"""

    success: bool = Field(..., description="Delete success status")
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Template deleted successfully"
            }
        }


class WhatsAppTemplateCopyRequest(BaseModel):
    """Schema for template copy request"""

    source_dealer_id: str = Field(..., min_length=1, max_length=50, description="Source dealer ID")
    target_dealer_id: str = Field(..., min_length=1, max_length=50, description="Target dealer ID")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing templates")

    @validator('target_dealer_id')
    def validate_different_dealers(cls, v, values):
        """Ensure source and target dealers are different"""
        if 'source_dealer_id' in values and v == values['source_dealer_id']:
            raise ValueError('Source and target dealer IDs must be different')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "source_dealer_id": "AHASS001",
                "target_dealer_id": "AHASS002",
                "overwrite_existing": False
            }
        }


class WhatsAppTemplateCopyResponse(BaseModel):
    """Schema for template copy response"""

    success: bool = Field(..., description="Copy operation success status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Copy operation statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Templates copied successfully",
                "data": {
                    "source_dealer_id": "AHASS001",
                    "target_dealer_id": "AHASS002",
                    "templates_found": 15,
                    "templates_copied": 12,
                    "templates_skipped": 3,
                    "overwrite_existing": False,
                    "copy_timestamp": "2024-01-16T14:30:00.000Z"
                }
            }
        }


class WhatsAppTemplateLogResponse(BaseModel):
    """Schema for template audit log response"""

    id: str = Field(..., description="Log entry UUID")
    template_id: Optional[str] = Field(None, description="Template UUID")
    operation: str = Field(..., description="Operation type")
    old_data: Optional[Dict[str, Any]] = Field(None, description="Previous template data")
    new_data: Optional[Dict[str, Any]] = Field(None, description="New template data")
    dealer_id: Optional[str] = Field(None, description="Primary dealer ID")
    user_email: str = Field(..., description="User who performed operation")
    source_dealer_id: Optional[str] = Field(None, description="Source dealer for copy operations")
    target_dealer_id: Optional[str] = Field(None, description="Target dealer for copy operations")
    operation_timestamp: str = Field(..., description="Operation timestamp")
    operation_notes: Optional[str] = Field(None, description="Operation notes")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174000",
                "template_id": "123e4567-e89b-12d3-a456-426614174000",
                "operation": "UPDATE",
                "old_data": {"template": "Old template content"},
                "new_data": {"template": "New template content"},
                "dealer_id": "AHASS001",
                "user_email": "admin@dealer.com",
                "source_dealer_id": None,
                "target_dealer_id": None,
                "operation_timestamp": "2024-01-16T14:30:00.000Z",
                "operation_notes": "Updated template for better clarity"
            }
        }


class WhatsAppTemplateLogsResponse(BaseModel):
    """Schema for template logs list response"""

    success: bool = Field(..., description="Request success status")
    data: List[WhatsAppTemplateLogResponse] = Field(..., description="List of log entries")
    pagination: Optional[Dict[str, Any]] = Field(None, description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "456e7890-e89b-12d3-a456-426614174000",
                        "template_id": "123e4567-e89b-12d3-a456-426614174000",
                        "operation": "UPDATE",
                        "old_data": {"template": "Old content"},
                        "new_data": {"template": "New content"},
                        "dealer_id": "AHASS001",
                        "user_email": "admin@dealer.com",
                        "source_dealer_id": None,
                        "target_dealer_id": None,
                        "operation_timestamp": "2024-01-16T14:30:00.000Z",
                        "operation_notes": None
                    }
                ],
                "pagination": {
                    "page": 1,
                    "size": 10,
                    "total": 5,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
        }