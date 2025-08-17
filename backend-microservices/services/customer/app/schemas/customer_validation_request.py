"""
Pydantic schemas for customer validation request
"""

from typing import Optional, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field, field_validator


class CustomerValidationRequestCreate(BaseModel):
    """Schema for creating a customer validation request"""
    
    nama_pembawa: str = Field(..., min_length=1, max_length=255, description="Customer name")
    nomor_telepon_pembawa: str = Field(..., min_length=8, max_length=20, description="Phone number")
    tipe_unit: str = Field(..., min_length=1, max_length=100, description="Unit type")
    nomor_polisi: str = Field(..., min_length=1, max_length=20, description="License plate number")
    kode_ahass: str = Field(..., min_length=1, max_length=10, description="AHASS code")
    nama_ahass: str = Field(..., min_length=1, max_length=255, description="AHASS name")
    alamat_ahass: str = Field(..., min_length=1, description="AHASS address")
    nomor_mesin: str = Field(..., min_length=1, max_length=50, description="Engine number")
    created_time: Optional[str] = Field(None, description="Created time in format 'DD/MM/YYYY HH:mm:ss' (optional, defaults to now)")
    modified_time: Optional[str] = Field(None, description="Modified time in format 'DD/MM/YYYY HH:mm:ss' (optional, defaults to now)")
    
    @field_validator('nomor_telepon_pembawa')
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
    
    @field_validator('created_time', 'modified_time')
    @classmethod
    def validate_datetime_format(cls, v):
        """Validate datetime format DD/MM/YYYY HH:mm:ss (optional fields)"""
        if v is None:
            return v
        
        try:
            datetime.strptime(v, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            raise ValueError('Invalid datetime format. Expected DD/MM/YYYY HH:mm:ss')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "kode_ahass": "00999",
                "nama_ahass": "Daya Adicipta Motora",
                "alamat_ahass": "Jl Cibereum no 26",
                "nama_pembawa": "Budi",
                "nomor_telepon_pembawa": "628561111111",
                "nomor_mesin": "JB22E1572318",
                "nomor_polisi": "D1234XY",
                "tipe_unit": "VARIO 125 CBS ISS"
            }
        }


class CustomerValidationResponseData(BaseModel):
    """Schema for customer validation response data"""
    
    request_id: str = Field(..., description="Request UUID")
    dealer_id: str = Field(..., description="Dealer ID")
    request_status: str = Field(..., description="Request processing status")
    whatsapp_status: str = Field(..., description="WhatsApp message status")
    whatsapp_message: str = Field(..., description="WhatsApp message content")
    created_at: str = Field(..., description="Request creation timestamp")
    fonnte_response: Optional[Dict[str, Any]] = Field(None, description="Fonnte API response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "request_status": "PROCESSED",
                "whatsapp_status": "SENT",
                "whatsapp_message": "Halo John,\n\nTerima kasih telah melakukan validasi customer untuk unit Motor dengan nomor polisi B1234ABC...",
                "created_at": "2025-01-10T10:30:00.000Z",
                "fonnte_response": {
                    "detail": "success! message in queue",
                    "id": ["80367170"],
                    "process": "pending",
                    "requestid": 2937124,
                    "status": True,
                    "target": ["6282227097005"]
                }
            }
        }


class CustomerValidationResponse(BaseModel):
    """Schema for customer validation response"""
    
    status: int = Field(..., description="Status code (1 for success)")
    message: Dict[str, str] = Field(..., description="Response message")
    data: Optional[CustomerValidationResponseData] = Field(None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 1,
                "message": {
                    "confirmation": "Data berhasil diproses"
                },
                "data": {
                    "request_id": "123e4567-e89b-12d3-a456-426614174000",
                    "request_status": "PROCESSED",
                    "whatsapp_status": "SENT",
                    "whatsapp_message": "Halo John,\n\nTerima kasih telah melakukan validasi customer...",
                    "created_at": "2025-01-10T10:30:00.000Z",
                    "fonnte_response": {
                        "status": True,
                        "id": ["80367170"],
                        "requestid": 2937124
                    }
                }
            }
        }


class CustomerValidationRequestResponse(BaseModel):
    """Schema for detailed customer validation request response"""
    
    id: str
    dealer_id: str
    request_date: str
    request_time: str
    nama_pembawa: str
    nomor_telepon_pembawa: str
    tipe_unit: str
    nomor_polisi: str
    kode_ahass: Optional[str]
    nama_ahass: Optional[str]
    alamat_ahass: Optional[str]
    nomor_mesin: Optional[str]
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