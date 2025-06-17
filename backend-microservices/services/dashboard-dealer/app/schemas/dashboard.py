"""
Dashboard schemas for API responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class UnitInboundStatusItem(BaseModel):
    """Individual status item for unit inbound data"""
    status_shipping_list: Optional[str] = Field(None, description="Original status of shipping list")
    status_label: Optional[str] = Field(None, description="Human-readable status label in Indonesian")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class UnitInboundStatusResponse(BaseModel):
    """Response schema for unit inbound status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[UnitInboundStatusItem] = Field(..., description="List of status counts")
    total_records: int = Field(..., description="Total number of records")
    
    class Config:
        from_attributes = True
