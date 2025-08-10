"""
Pydantic schemas for customer validation request
"""

from typing import Optional, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field, field_validator


class CustomerValidationRequestCreate(BaseModel):
    """Schema for creating a customer validation request"""
    
    namaPembawa: str = Field(..., min_length=1, max_length=255, description="Customer name")
    noTelp: str = Field(..., min_length=8, max_length=20, description="Phone number")
    tipeUnit: str = Field(..., min_length=1, max_length=100, description="Unit type")
    noPol: str = Field(..., min_length=1, max_length=20, description="License plate number")
    createdTime: str = Field(..., description="Created time in format 'DD/MM/YYYY HH:mm:ss'")
    modifiedTime: str = Field(..., description="Modified time in format 'DD/MM/YYYY HH:mm:ss'")
    dealerId: str = Field(..., min_length=4, max_length=10, description="Dealer ID")
    
    @field_validator('noTelp')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove common phone number prefixes and spaces
        cleaned = v.replace('+62', '0').replace(' ', '').replace('-', '')
        if not cleaned.startswith('0'):
            cleaned = '0' + cleaned
        
        # Check if it's a valid Indonesian phone number
        if not (cleaned.startswith('08') and len(cleaned) >= 10 and len(cleaned) <= 13):
            raise ValueError('Invalid Indonesian phone number format')
        
        return cleaned
    
    @field_validator('createdTime', 'modifiedTime')
    @classmethod
    def validate_datetime_format(cls, v):
        """Validate datetime format DD/MM/YYYY HH:mm:ss"""
        try:
            datetime.strptime(v, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            raise ValueError('Invalid datetime format. Expected DD/MM/YYYY HH:mm:ss')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "namaPembawa": "Adit",
                "noTelp": "082148523421",
                "tipeUnit": "BeAT Street",
                "noPol": "D 123 AD",
                "createdTime": "31/12/2019 15:40:50",
                "modifiedTime": "31/12/2019 15:40:50",
                "dealerId": "0009999"
            }
        }


class CustomerValidationResponse(BaseModel):
    """Schema for customer validation response"""
    
    status: int = Field(..., description="Status code (1 for success)")
    message: Dict[str, str] = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 1,
                "message": {
                    "confirmation": "Data berhasil disimpan"
                },
                "data": None
            }
        }


class CustomerValidationRequestResponse(BaseModel):
    """Schema for detailed customer validation request response"""
    
    id: str
    dealer_id: str
    request_date: str
    request_time: str
    nama_pembawa: str
    no_telp: str
    tipe_unit: str
    no_pol: str
    request_status: str
    whatsapp_status: str
    fonnte_response: Optional[Dict[str, Any]]
    created_by: Optional[str]
    created_date: str
    last_modified_by: Optional[str]
    last_modified_date: str
    
    class Config:
        from_attributes = True


class WhatsAppMessageRequest(BaseModel):
    """Schema for WhatsApp message request"""
    
    dealer_id: str
    phone_number: str
    customer_name: str
    unit_type: str
    license_plate: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "dealer_id": "0009999",
                "phone_number": "082148523421",
                "customer_name": "Adit",
                "unit_type": "BeAT Street",
                "license_plate": "D 123 AD"
            }
        }


class WhatsAppMessageResponse(BaseModel):
    """Schema for WhatsApp message response"""
    
    success: bool
    message: str
    response_data: Optional[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "WhatsApp message sent successfully",
                "response_data": {
                    "status": "sent",
                    "id": "message_id_123"
                }
            }
        }