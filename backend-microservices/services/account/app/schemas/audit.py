"""
Pydantic schemas for audit-related operations
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.login_audit import AuditAction


class AuditLogBase(BaseModel):
    """Base audit log schema"""
    action: AuditAction
    email: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log"""
    user_id: Optional[str] = None
    success: bool = True
    failure_reason: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: str
    user_id: Optional[str]
    action: AuditAction
    email: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    failure_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for audit log list response"""
    logs: list[AuditLogResponse]
    total: int
    page: int
    per_page: int
    pages: int


class AuditStatsResponse(BaseModel):
    """Schema for audit statistics response"""
    total_attempts: int
    successful_logins: int
    failed_logins: int
    logouts: int
    success_rate: float
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
