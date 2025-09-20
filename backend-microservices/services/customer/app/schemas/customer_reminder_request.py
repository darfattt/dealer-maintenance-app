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
    BOOKING_SERVICE = "Booking Servis"
    ULTAH_KONSUMEN = "Ultah Konsumen"
    SELESAI_SERVICE = "Selesai Servis"


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
    
    nama_pelanggan: str = Field(..., min_length=1, max_length=255, description="Customer name")
    nomor_telepon_pelanggan: str = Field(..., min_length=8, max_length=20, description="Customer phone number")
    nomor_mesin: str = Field(..., min_length=1, max_length=50, description="Engine number")
    nomor_polisi: str = Field(..., min_length=1, max_length=20, description="License plate number")
    tipe_unit: str = Field(..., min_length=1, max_length=100, description="Unit type")
    tanggal_beli: str = Field(..., description="Purchase date in YYYY-MM-DD format")
    tanggal_expired_kpb: str = Field(..., description="KPB expiry date in YYYY-MM-DD format")
    
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
                        "nama_pelanggan": "Firman",
                        "nomor_telepon_pelanggan": "628561111112",
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
    
    nama_pelanggan: str = Field(..., min_length=1, max_length=255, description="Customer name")
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
                "nama_pelanggan": "John Doe",
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
    nama_pelanggan: str
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
    nama_pelanggan: str
    reminder_type: ReminderType
    custom_message: Optional[str] = Field(None, description="Custom message content (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dealer_id": "0009999",
                "phone_number": "082148523421",
                "nama_pelanggan": "John Doe",
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


# Utility functions for category classification
def get_target_only_categories() -> set:
    """
    Get set of reminder targets that use target-only query strategy
    (without specific reminder_type matching)

    Returns:
        set: Reminder target values that use target-only queries
    """
    return {
        ReminderTarget.NON_KPB.value,
        ReminderTarget.BOOKING_SERVICE.value,
        ReminderTarget.ULTAH_KONSUMEN.value,
        ReminderTarget.SELESAI_SERVICE.value
    }


def get_kpb_categories() -> set:
    """
    Get set of KPB reminder targets that use full query strategy
    (with specific reminder_type matching and fallback to N/A)

    Returns:
        set: KPB reminder target values
    """
    return {
        ReminderTarget.KPB_1.value,
        ReminderTarget.KPB_2.value,
        ReminderTarget.KPB_3.value,
        ReminderTarget.KPB_4.value
    }


class ReminderTargetOption(BaseModel):
    """Schema for reminder target dropdown option"""

    label: str = Field(..., description="Display label for the option")
    value: str = Field(..., description="Value for the option")

    class Config:
        json_schema_extra = {
            "example": {
                "label": "KPB 1",
                "value": "KPB-1"
            }
        }


class ReminderTargetResponse(BaseModel):
    """Schema for reminder target options response"""

    success: bool = Field(..., description="Success status")
    data: List[ReminderTargetOption] = Field(..., description="List of reminder target options")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {"label": "All Targets", "value": ""},
                    {"label": "KPB 1", "value": "KPB-1"},
                    {"label": "KPB 2", "value": "KPB-2"}
                ]
            }
        }


def get_reminder_target_options() -> List[ReminderTargetOption]:
    """
    Get reminder target options for frontend dropdown

    Returns:
        List[ReminderTargetOption]: List of reminder target options including "All Targets"
    """
    options = [
        ReminderTargetOption(label="All Targets", value="")
    ]

    # Add options from enum with user-friendly labels
    target_labels = {
        ReminderTarget.KPB_1.value: "KPB 1",
        ReminderTarget.KPB_2.value: "KPB 2",
        ReminderTarget.KPB_3.value: "KPB 3",
        ReminderTarget.KPB_4.value: "KPB 4",
        ReminderTarget.NON_KPB.value: "Non KPB",
        ReminderTarget.BOOKING_SERVICE.value: "Booking Servis",
        ReminderTarget.ULTAH_KONSUMEN.value: "Ultah Konsumen",
        ReminderTarget.SELESAI_SERVICE.value: "Selesai Servis"
    }

    for target_value, target_label in target_labels.items():
        options.append(ReminderTargetOption(label=target_label, value=target_value))

    return options