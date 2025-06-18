"""
Dashboard schemas for API responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


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


class PaymentTypeItem(BaseModel):
    """Individual payment type item for billing process data"""
    tipe_pembayaran: Optional[str] = Field(None, description="Payment type (CASH, CREDIT, etc.)")
    count: int = Field(..., description="Number of records with this payment type")
    total_amount: Optional[Decimal] = Field(None, description="Total amount for this payment type")

    class Config:
        from_attributes = True


class PaymentTypeResponse(BaseModel):
    """Response schema for payment type statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[PaymentTypeItem] = Field(..., description="List of payment type counts and amounts")
    total_records: int = Field(..., description="Total number of records")
    total_amount: Optional[Decimal] = Field(None, description="Grand total amount across all payment types")

    class Config:
        from_attributes = True
