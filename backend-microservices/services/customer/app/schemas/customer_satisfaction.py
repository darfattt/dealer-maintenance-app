"""
Customer satisfaction schemas for API requests and responses
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CustomerSatisfactionRecordResponse(BaseModel):
    """Individual customer satisfaction record response"""
    id: str
    no_tiket: Optional[str] = None
    no_booking_no_order_pemesanan: Optional[str] = None
    nama_konsumen: Optional[str] = None
    no_hp: Optional[str] = None
    alamat_email: Optional[str] = None
    source: Optional[str] = None
    kota: Optional[str] = None
    fu_by_se: Optional[str] = None
    fu_by_sda: Optional[str] = None
    no_ahass: Optional[str] = None
    status: Optional[str] = None
    nama_ahass: Optional[str] = None
    tanggal_service: Optional[str] = None
    periode_service: Optional[str] = None
    tanggal_rating: Optional[str] = None
    jenis_hari: Optional[str] = None
    periode_utk_suspend: Optional[str] = None
    submit_review_date_first_fu_cs: Optional[str] = None
    lt_tgl_rating_submit: Optional[str] = None
    sesuai_lt: Optional[str] = None
    periode_fu: Optional[str] = None
    inbox: Optional[str] = None
    indikasi_keluhan: Optional[str] = None
    rating: Optional[str] = None
    departemen: Optional[str] = None
    no_ahass_duplicate: Optional[str] = None
    status_duplicate: Optional[str] = None
    nama_ahass_duplicate: Optional[str] = None
    upload_batch_id: Optional[str] = None
    created_by: Optional[str] = None
    created_date: Optional[str] = None
    last_modified_by: Optional[str] = None
    last_modified_date: Optional[str] = None

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_prev: bool


class CustomerSatisfactionListResponse(BaseModel):
    """Paginated list of customer satisfaction records"""
    success: bool
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Customer satisfaction records retrieved successfully",
                "data": {
                    "records": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "no_tiket": "#350549",
                            "nama_konsumen": "Rendra Akbar Kurnia",
                            "no_ahass": "8783",
                            "periode_utk_suspend": "6 Januari - 12 Januari 2025",
                            "submit_review_date_first_fu_cs": "2 Januari 2025",
                            "rating": "3"
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "page_size": 10,
                        "total_count": 100,
                        "total_pages": 10,
                        "has_next": True,
                        "has_prev": False
                    }
                }
            }
        }


class UploadTrackerResponse(BaseModel):
    """Upload tracker response"""
    id: str
    file_name: str
    file_size: Optional[int] = None
    total_records: int
    successful_records: int
    failed_records: int
    upload_status: str
    error_message: Optional[str] = None
    uploaded_by: Optional[str] = None
    upload_date: Optional[str] = None
    completed_date: Optional[str] = None

    class Config:
        from_attributes = True


class UploadTrackersListResponse(BaseModel):
    """Paginated list of upload trackers"""
    success: bool
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


class CustomerSatisfactionUploadResponse(BaseModel):
    """Response for file upload"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "File uploaded successfully",
                "data": {
                    "upload_tracker_id": "123e4567-e89b-12d3-a456-426614174000",
                    "file_name": "customer_satisfaction.xlsx",
                    "total_records": 1000,
                    "successful_records": 995,
                    "failed_records": 5,
                    "upload_status": "COMPLETED"
                }
            }
        }


class CustomerSatisfactionStatisticsResponse(BaseModel):
    """Statistics response for customer satisfaction data"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Statistics retrieved successfully",
                "data": {
                    "total_records": 1000,
                    "rating_distribution": [
                        {"rating": "5", "count": 400},
                        {"rating": "4", "count": 300},
                        {"rating": "3", "count": 200},
                        {"rating": "2", "count": 80},
                        {"rating": "1", "count": 20}
                    ],
                    "top_ahass": [
                        {"no_ahass": "8783", "nama_ahass": "BENJOYO MOTOR", "count": 150},
                        {"no_ahass": "15895", "nama_ahass": "MARKONI MANDIRIPERKASA", "count": 120}
                    ]
                }
            }
        }


class CustomerSatisfactionFilters(BaseModel):
    """Query filters for customer satisfaction data"""
    periode_utk_suspend: Optional[str] = Field(None, description="Filter by periode untuk suspend")
    submit_review_date: Optional[str] = Field(None, description="Filter by submit review date (partial match)")
    no_ahass: Optional[str] = Field(None, description="Filter by No AHASS")
    date_from: Optional[str] = Field(None, description="Filter by created date from (YYYY-MM-DD format)")
    date_to: Optional[str] = Field(None, description="Filter by created date to (YYYY-MM-DD format)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of records per page")

    @validator('date_from', 'date_to')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    message: str
    data: Optional[Any] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "File format not supported. Please upload .xlsx or .csv files only.",
                "data": None
            }
        }