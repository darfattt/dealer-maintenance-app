"""
Dealer schemas for API responses and requests
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DealerBase(BaseModel):
    """Base dealer schema"""
    dealer_id: str = Field(..., description="Unique dealer identifier")
    dealer_name: str = Field(..., description="Dealer name")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    api_token: Optional[str] = Field(None, description="API token for authentication")
    secret_key: Optional[str] = Field(None, description="Secret key for authentication")
    is_active: bool = Field(True, description="Active status")


class DealerResponse(BaseModel):
    """Single dealer response"""
    id: str
    dealer_id: str
    dealer_name: str
    api_key: Optional[str] = None
    api_token: Optional[str] = None
    secret_key: Optional[str] = None
    fonnte_api_key: Optional[str] = None
    fonnte_api_url: Optional[str] = None
    phone_number: Optional[str] = None
    google_location_url: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class DealerListItem(BaseModel):
    """Dealer list item (simplified for table display)"""
    id: str
    dealer_id: str
    dealer_name: str
    is_active: bool
    dgi_api_configured: bool = Field(..., description="DGI API configured (api_key & secret_key)")
    google_location_configured: bool = Field(..., description="Google location URL configured")
    whatsapp_api_configured: bool = Field(..., description="WhatsApp/Fonnte API configured")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class DealerListResponse(BaseModel):
    """Paginated dealer list response"""
    success: bool = True
    message: str = "Dealers retrieved successfully"
    data: List[DealerListItem]
    total_records: int
    page: int = 1
    page_size: int = 10
    total_pages: int = 1


class DealerUpdateRequest(BaseModel):
    """Request schema for updating dealer"""
    dealer_name: Optional[str] = Field(None, description="Dealer name")
    api_key: Optional[str] = Field(None, description="API key")
    api_token: Optional[str] = Field(None, description="API token")
    secret_key: Optional[str] = Field(None, description="Secret key")
    fonnte_api_key: Optional[str] = Field(None, description="Fonnte WhatsApp API key")
    fonnte_api_url: Optional[str] = Field(None, description="Fonnte API URL")
    phone_number: Optional[str] = Field(None, description="Phone number for WhatsApp")
    google_location_url: Optional[str] = Field(None, description="Google Maps location URL")
    is_active: Optional[bool] = Field(None, description="Active status")


class DealerStatusRequest(BaseModel):
    """Request schema for toggling dealer status"""
    is_active: bool = Field(..., description="Active status")


class DealerStatusResponse(BaseModel):
    """Response schema for dealer status update"""
    success: bool = True
    message: str
    data: Optional[DealerResponse] = None


class DealerUpdateResponse(BaseModel):
    """Response schema for dealer update"""
    success: bool = True
    message: str
    data: Optional[DealerResponse] = None
