"""
Pydantic schemas for customer reminder request
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date, time
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ReminderTarget(str, Enum):
    """Enum for reminder targets"""
    KPB_1 = "KPB-1"
    KPB_2 = "KPB-2"
    KPB_3 = "KPB-3"
    KPB_4 = "KPB-4"
    NON_KPB = "Non KPB"
    BOOKING_SERVICE = "Booking Service"
    ULTAH_KONSUMEN = "Ultah Konsumen"


class ReminderType(str, Enum):
    """Enum for reminder types"""
    # KPB-1 Types
    KPB_1_H_PLUS_30 = "H+30 tanggal beli (by WA)"
    KPB_1_H_MINUS_7 = "H-7 dari expired KPB-1 (by WA)"
    
    # KPB-2 Types
    KPB_2_H_MINUS_60 = "H-60 dari expired KPB-2 (by WA)"
    KPB_2_H_MINUS_30 = "H-30 dari expired KPB-2 (by WA)"
    KPB_2_H_MINUS_7 = "H-7 dari expired KPB-2 (by WA)"
    
    # KPB-3 Types
    KPB_3_H_MINUS_60 = "H-60 dari expired KPB-3 (by WA)"
    KPB_3_H_MINUS_30 = "H-30 dari expired KPB-3 (by WA)"
    KPB_3_H_MINUS_7 = "H-7 dari expired KPB-3 (by WA)"
    
    # KPB-4 Types
    KPB_4_H_MINUS_60 = "H-60 dari expired KPB-4 (by WA)"
    KPB_4_H_MINUS_30 = "H-30 dari expired KPB-4 (by WA)"
    KPB_4_H_MINUS_7 = "H-7 dari expired KPB-4 (by WA)"
    
    # Other Types
    NON_KPB = "N/A"
    BOOKING_SERVICE = "N/A"
    ULTAH_KONSUMEN = "N/A"


class BulkReminderCustomerData(BaseModel):
    """Schema for individual customer data in bulk reminder"""
    
    nama_pemilik: str = Field(..., min_length=1, max_length=255, description="Vehicle owner name")
    nama_pelanggan: str = Field(..., min_length=1, max_length=255, description="Customer name")
    nomor_telepon_pelanggan: str = Field(..., min_length=8, max_length=20, description="Customer phone number")
    nama_pembawa: str = Field(..., min_length=1, max_length=255, description="Person bringing vehicle")
    no_telepon_pembawa: str = Field(..., min_length=8, max_length=20, description="Person phone number")
    nomor_mesin: str = Field(..., min_length=1, max_length=50, description="Engine number")
    nomor_polisi: str = Field(..., min_length=1, max_length=20, description="License plate number")
    tipe_unit: str = Field(..., min_length=1, max_length=100, description="Unit type")
    tanggal_beli: str = Field(..., description="Purchase date in YYYY-MM-DD format")
    tanggal_expired_kpb: str = Field(..., description="KPB expiry date in YYYY-MM-DD format")
    
    @field_validator('nomor_telepon_pelanggan', 'no_telepon_pembawa')
    @classmethod
    def validate_phone_numbers(cls, v):
        """Validate phone number format"""
        # Remove common phone number prefixes and spaces
        cleaned = v.replace('+62', '0').replace(' ', '').replace('-', '')
        if not cleaned.startswith('0'):
            cleaned = '0' + cleaned
        
        # Check if it's a valid Indonesian phone number
        if not (cleaned.startswith('08') and len(cleaned) >= 10 and len(cleaned) <= 13):
            raise ValueError('Invalid Indonesian phone number format')
        
        return cleaned


class BulkReminderRequest(BaseModel):
    """Schema for bulk reminder request"""
    
    kode_ahass: str = Field(..., min_length=1, max_length=10, description="AHASS code")
    nama_ahass: str = Field(..., min_length=1, max_length=255, description="AHASS name")
    alamat_ahass: str = Field(..., min_length=1, description="AHASS address")
    filter_target: str = Field(..., description="Filter target (maps to reminder_target)")
    filter_data: str = Field(..., description="Filter data (maps to reminder_type)")
    data: List[BulkReminderCustomerData] = Field(..., min_items=1, description="List of customer data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "kode_ahass": "00999",
                "nama_ahass": "Daya Adicipta Motora",
                "alamat_ahass": "Jl Cibereum no 26",
                "filter_target": "KPB-1",
                "filter_data": "H-7 dari expired KPB",
                "data": [
                    {
                        "nama_pemilik": "Firman",
                        "nama_pelanggan": "Firman",
                        "nomor_telepon_pelanggan": "628561111112",
                        "nama_pembawa": "Budi",
                        "no_telepon_pembawa": "628561111112",
                        "nomor_mesin": "JB22E1572318",
                        "nomor_polisi": "D1234XY",
                        "tipe_unit": "VARIO 125 CBS ISS",
                        "tanggal_beli": "2025-06-25",
                        "tanggal_expired_kpb": "2025-08-25"
                    }
                ]
            }
        }


class CustomerReminderRequestCreate(BaseModel):
    """Schema for creating a customer reminder request"""
    
    nama_pemilik: str = Field(..., min_length=1, max_length=255, description="Owner name")
    nomor_telepon_pelanggan: str = Field(..., min_length=8, max_length=20, description="Customer phone number")
    reminder_type: ReminderType = Field(..., description="Type of reminder")
    created_time: Optional[str] = Field(None, description="Created time in format 'DD/MM/YYYY HH:mm:ss' (optional, defaults to now)")
    modified_time: Optional[str] = Field(None, description="Modified time in format 'DD/MM/YYYY HH:mm:ss' (optional, defaults to now)")
    dealer_id: str = Field(..., min_length=4, max_length=10, description="Dealer ID")
    
    @field_validator('nomor_telepon_pelanggan')
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
                "nama_pemilik": "John Doe",
                "nomor_telepon_pelanggan": "082148523421",
                "reminder_type": "SERVICE_REMINDER",
                "dealer_id": "0009999"
            }
        }


class CustomerReminderResponseData(BaseModel):
    """Schema for customer reminder response data"""
    
    request_id: str = Field(..., description="Request UUID")
    dealer_id: str = Field(..., description="Dealer ID")
    request_status: str = Field(..., description="Request processing status")
    whatsapp_status: str = Field(..., description="WhatsApp message status")
    whatsapp_message: str = Field(..., description="WhatsApp message content")
    reminder_type: str = Field(..., description="Type of reminder")
    created_at: str = Field(..., description="Request creation timestamp")
    fonnte_response: Optional[Dict[str, Any]] = Field(None, description="Fonnte API response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "dealer_id": "12284",
                "request_status": "PROCESSED",
                "whatsapp_status": "SENT",
                "whatsapp_message": "Halo John Doe,\n\nIni adalah pengingat untuk servis kendaraan Anda...",
                "reminder_type": "SERVICE_REMINDER",
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


class CustomerReminderResponse(BaseModel):
    """Schema for customer reminder response"""
    
    status: int = Field(..., description="Status code (1 for success)")
    message: Dict[str, str] = Field(..., description="Response message")
    data: Optional[CustomerReminderResponseData] = Field(None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 1,
                "message": {
                    "confirmation": "Reminder berhasil dibuat"
                },
                "data": {
                    "request_id": "123e4567-e89b-12d3-a456-426614174000",
                    "dealer_id": "12284",
                    "request_status": "PROCESSED",
                    "whatsapp_status": "SENT",
                    "whatsapp_message": "Halo John Doe,\n\nIni adalah pengingat untuk servis kendaraan Anda...",
                    "reminder_type": "SERVICE_REMINDER",
                    "created_at": "2025-01-10T10:30:00.000Z",
                    "fonnte_response": {
                        "status": True,
                        "id": ["80367170"],
                        "requestid": 2937124
                    }
                }
            }
        }


class CustomerReminderRequestResponse(BaseModel):
    """Schema for detailed customer reminder request response"""
    
    id: str
    dealer_id: str
    request_date: str
    request_time: str
    nama_pemilik: str
    nomor_telepon_pelanggan: str
    request_status: str
    whatsapp_status: str
    reminder_type: str
    whatsapp_message: Optional[str]
    fonnte_response: Optional[Dict[str, Any]]
    created_by: Optional[str]
    created_date: str
    last_modified_by: Optional[str]
    last_modified_date: str
    
    class Config:
        from_attributes = True


class WhatsAppReminderRequest(BaseModel):
    """Schema for WhatsApp reminder message request"""
    
    dealer_id: str
    phone_number: str
    nama_pemilik: str
    reminder_type: ReminderType
    custom_message: Optional[str] = Field(None, description="Custom message content (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dealer_id": "0009999",
                "phone_number": "082148523421",
                "nama_pemilik": "John Doe",
                "reminder_type": "SERVICE_REMINDER",
                "custom_message": "Jangan lupa service rutin kendaraan Anda minggu ini"
            }
        }


class WhatsAppReminderResponse(BaseModel):
    """Schema for WhatsApp reminder message response"""
    
    success: bool
    message: str
    response_data: Optional[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "WhatsApp reminder sent successfully",
                "response_data": {
                    "status": "sent",
                    "id": "message_id_123"
                }
            }
        }


class BulkReminderResponse(BaseModel):
    """Schema for bulk reminder response"""
    
    status: int = Field(..., description="Status code (1 for success)")
    message: Dict[str, str] = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data with processing results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 1,
                "message": {
                    "confirmation": "Bulk reminders berhasil diproses"
                },
                "data": {
                    "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                    "total_customers": 10,
                    "successful_reminders": 8,
                    "failed_reminders": 2,
                    "success_rate": 80.0,
                    "processing_status": "completed",
                    "kode_ahass": "00999",
                    "filter_target": "KPB-1",
                    "filter_data": "H-7 dari expired KPB"
                }
            }
        }


class CustomerReminderStatsResponse(BaseModel):
    """Schema for customer reminder statistics response"""
    
    total_reminders: int
    pending_reminders: int
    sent_reminders: int
    failed_reminders: int
    delivery_percentage: float
    reminder_type_breakdown: Dict[str, int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_reminders": 150,
                "pending_reminders": 10,
                "sent_reminders": 130,
                "failed_reminders": 10,
                "delivery_percentage": 86.67,
                "reminder_type_breakdown": {
                    "SERVICE_REMINDER": 80,
                    "PAYMENT_REMINDER": 40,
                    "APPOINTMENT_REMINDER": 30
                }
            }
        }