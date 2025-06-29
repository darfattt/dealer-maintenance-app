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


class DeliveryProcessStatusItem(BaseModel):
    """Individual status item for delivery process data"""
    status_delivery_document: Optional[str] = Field(None, description="Original status of delivery document")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class DeliveryProcessStatusResponse(BaseModel):
    """Response schema for delivery process status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[DeliveryProcessStatusItem] = Field(..., description="List of delivery status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class ProspectFollowUpItem(BaseModel):
    """Individual follow-up status item for prospect data"""
    status_follow_up_prospecting: Optional[str] = Field(None, description="Original status follow up prospecting code")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class ProspectFollowUpResponse(BaseModel):
    """Response schema for prospect follow-up status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[ProspectFollowUpItem] = Field(..., description="List of prospect follow-up status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class SPKStatusItem(BaseModel):
    """Individual status item for SPK dealing process data"""
    status_spk: Optional[str] = Field(None, description="Original SPK status code")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class SPKStatusResponse(BaseModel):
    """Response schema for SPK status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[SPKStatusItem] = Field(..., description="List of SPK status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class TopLeasingItem(BaseModel):
    """Individual leasing company item for top leasing data"""
    nama_finance_company: Optional[str] = Field(None, description="Finance company name")
    count: int = Field(..., description="Number of PO records for this finance company")

    class Config:
        from_attributes = True


class TopLeasingResponse(BaseModel):
    """Response schema for top leasing company statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[TopLeasingItem] = Field(..., description="List of top leasing companies")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class DocumentHandlingCountResponse(BaseModel):
    """Response schema for document handling count statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    count: int = Field(..., description="Count of SPK records matching criteria")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class StatusProspectItem(BaseModel):
    """Individual status item for prospect data grouped by status_prospect"""
    status_prospect: Optional[str] = Field(None, description="Original status prospect code")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class StatusProspectResponse(BaseModel):
    """Response schema for status prospect statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[StatusProspectItem] = Field(..., description="List of status prospect counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class MetodeFollowUpItem(BaseModel):
    """Individual metode item for prospect data grouped by metode_follow_up"""
    metode_follow_up: Optional[str] = Field(None, description="Original metode follow up code")
    metode_label: Optional[str] = Field(None, description="Human-readable metode label")
    count: int = Field(..., description="Number of records with this metode")

    class Config:
        from_attributes = True


class MetodeFollowUpResponse(BaseModel):
    """Response schema for metode follow up statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[MetodeFollowUpItem] = Field(..., description="List of metode follow up counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class SumberProspectItem(BaseModel):
    """Individual sumber item for prospect data grouped by sumber_prospect"""
    sumber_prospect: Optional[str] = Field(None, description="Original sumber prospect code")
    sumber_label: Optional[str] = Field(None, description="Human-readable sumber label")
    count: int = Field(..., description="Number of records with this sumber")

    class Config:
        from_attributes = True


class SumberProspectResponse(BaseModel):
    """Response schema for top sumber prospect statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[SumberProspectItem] = Field(..., description="List of top 5 sumber prospect counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True
