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


class DealerRegistrationRequest(BaseModel):
    """Request schema for registering a new dealer with admin user"""
    # Step 1: Dealer Info
    dealer_id: str = Field(..., description="Unique dealer ID (1-10 chars)")
    dealer_name: str = Field(..., description="Dealer name")
    # Step 2: DGI API Configuration
    api_key: Optional[str] = Field(None, description="DGI API key")
    secret_key: Optional[str] = Field(None, description="DGI secret key")
    # Step 3: WhatsApp Configuration
    fonnte_api_key: Optional[str] = Field(None, description="Fonnte API key")
    fonnte_api_url: Optional[str] = Field('https://api.fonnte.com/send', description="Fonnte API URL")
    phone_number: Optional[str] = Field(None, description="WhatsApp phone number")
    # Step 4: Google Maps Configuration
    google_location_url: Optional[str] = Field(None, description="Google Maps URL")
    # Step 5: Admin User Info
    admin_email: str = Field(..., description="Admin user email")
    admin_full_name: str = Field(..., description="Admin user full name")
    admin_password: str = Field(..., min_length=8, description="Admin user password")


class TemplateCopyResult(BaseModel):
    """Result of WhatsApp template copy operation"""
    success: bool = Field(..., description="Whether template copy succeeded")
    templates_found: int = Field(..., description="Number of templates found in source")
    templates_copied: int = Field(..., description="Number of templates copied")
    templates_skipped: int = Field(..., description="Number of templates skipped (already exist)")
    errors: List[str] = Field(default_factory=list, description="List of error messages if any")


class DealerRegistrationResponse(BaseModel):
    """Response schema for dealer registration"""
    success: bool = True
    message: str
    dealer: Optional[DealerResponse] = None
    admin_user: Optional[dict] = None
    template_copy_result: Optional[TemplateCopyResult] = Field(None, description="WhatsApp template copy results (if WhatsApp configured)")


class BulkDealerRegistrationItem(BaseModel):
    """Single dealer registration result in bulk operation"""
    dealer_id: str = Field(..., description="Dealer ID that was processed")
    success: bool = Field(..., description="Whether registration succeeded")
    message: str = Field(..., description="Success or error message")
    dealer: Optional[DealerResponse] = Field(None, description="Dealer data if successful")
    admin_user: Optional[dict] = Field(None, description="Admin user data if successful")
    template_copy_result: Optional[TemplateCopyResult] = Field(None, description="WhatsApp template copy results (if WhatsApp configured)")


class BulkDealerRegistrationResponse(BaseModel):
    """Response schema for bulk dealer registration from Excel"""
    success: bool = Field(True, description="Overall operation status")
    message: str = Field(..., description="Summary message")
    total_processed: int = Field(..., description="Total number of dealers processed")
    total_success: int = Field(..., description="Number of successful registrations")
    total_failed: int = Field(..., description="Number of failed registrations")
    results: List[BulkDealerRegistrationItem] = Field(..., description="Detailed results for each dealer")
