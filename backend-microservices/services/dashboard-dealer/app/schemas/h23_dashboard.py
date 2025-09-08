"""
H23 Dashboard schemas for API responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


# Work Order Section Schemas

class TotalUnitEntryResponse(BaseModel):
    """Response schema for total unit entry statistics with trend"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    count: int = Field(..., description="Current period count of work orders")
    previous_count: int = Field(..., description="Previous period count of work orders")
    trend: str = Field(..., description="Trend direction: up, down, or stable")
    percentage: float = Field(..., description="Percentage change from previous period")

    class Config:
        from_attributes = True


class WorkOrderRevenueResponse(BaseModel):
    """Response schema for work order revenue statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    total_revenue: float = Field(..., description="Total revenue from work orders")
    total_records: int = Field(..., description="Total number of work order records")

    class Config:
        from_attributes = True


class WorkOrderStatusItem(BaseModel):
    """Individual work order status item"""
    status_work_order: Optional[str] = Field(None, description="Work order status code")
    status_label: str = Field(..., description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class WorkOrderStatusResponse(BaseModel):
    """Response schema for work order status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[WorkOrderStatusItem] = Field(..., description="List of work order status counts")
    total_records: int = Field(..., description="Total number of work order records")

    class Config:
        from_attributes = True


# Pembayaran Section Schemas

class NJBStatisticsResponse(BaseModel):
    """Response schema for NJB (Nota Jasa Bengkel) statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    total_amount: float = Field(..., description="Total amount from NJB records")
    total_records: int = Field(..., description="Total number of NJB records")
    
    class Config:
        from_attributes = True


class NSCStatisticsResponse(BaseModel):
    """Response schema for NSC (Nota Suku Cadang) statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    total_amount: float = Field(..., description="Total combined amount from NJB + NSC records")
    total_records: int = Field(..., description="Total number of NSC records")
    
    class Config:
        from_attributes = True


class HLOStatisticsResponse(BaseModel):
    """Response schema for HLO (Honda Layanan Otomotif) statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    total_hlo_documents: int = Field(..., description="Total number of distinct HLO documents")
    total_parts: int = Field(..., description="Total number of parts from dp_hlo_parts")
    total_records: int = Field(..., description="Total number of HLO records")
    
    class Config:
        from_attributes = True


# Base response for errors
class H23DashboardErrorResponse(BaseModel):
    """Error response schema for H23 Dashboard APIs"""
    success: bool = Field(False, description="Request failed")
    message: str = Field(..., description="Error message")
    error_detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        from_attributes = True