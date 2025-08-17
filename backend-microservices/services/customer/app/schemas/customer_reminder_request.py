"""
Pydantic schemas for customer reminder request
"""

from typing import Optional, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ReminderType(str, Enum):
    """Enum for reminder types"""
    SERVICE_REMINDER = "SERVICE_REMINDER"
    PAYMENT_REMINDER = "PAYMENT_REMINDER"
    APPOINTMENT_REMINDER = "APPOINTMENT_REMINDER"
    MAINTENANCE_REMINDER = "MAINTENANCE_REMINDER"
    FOLLOW_UP_REMINDER = "FOLLOW_UP_REMINDER"
    CUSTOM_REMINDER = "CUSTOM_REMINDER"


class CustomerReminderRequestCreate(BaseModel):
    """Schema for creating a customer reminder request"""
    
    customerName: str = Field(..., min_length=1, max_length=255, description="Customer name")
    noTelp: str = Field(..., min_length=8, max_length=20, description="Phone number")
    reminderType: ReminderType = Field(..., description="Type of reminder")
    createdTime: Optional[str] = Field(None, description="Created time in format 'DD/MM/YYYY HH:mm:ss' (optional, defaults to now)")
    modifiedTime: Optional[str] = Field(None, description="Modified time in format 'DD/MM/YYYY HH:mm:ss' (optional, defaults to now)")
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
                "customerName": "John Doe",
                "noTelp": "082148523421",
                "reminderType": "SERVICE_REMINDER",
                "dealerId": "0009999"
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
    customer_name: str
    no_telp: str
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
    customer_name: str
    reminder_type: ReminderType
    custom_message: Optional[str] = Field(None, description="Custom message content (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dealer_id": "0009999",
                "phone_number": "082148523421",
                "customer_name": "John Doe",
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