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
    # Sentiment analysis fields
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_reasons: Optional[str] = None
    sentiment_suggestion: Optional[str] = None
    sentiment_themes: Optional[str] = None
    sentiment_analyzed_at: Optional[str] = None
    sentiment_batch_id: Optional[str] = None
    # Audit fields
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
    date_from: Optional[str] = Field(None, description="Filter by date from (YYYY-MM-DD format)")
    date_to: Optional[str] = Field(None, description="Filter by date to (YYYY-MM-DD format)")
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


class SentimentAnalysisRecord(BaseModel):
    """Individual sentiment analysis record for API requests"""
    id: str
    no_tiket: str
    review: str

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "no_tiket": "#421491",
                "review": "Tidak dapat potongan Voucher"
            }
        }


class SentimentAnalysisRequest(BaseModel):
    """Request schema for sentiment analysis"""
    question: str  # JSON string of sentiment analysis records
    
    class Config:
        schema_extra = {
            "example": {
                "question": "[{'id': '26947de5-41d8-4b7c-8708-d20330ed07d6','no_tiket': '#421491','review': 'Tidak dapat potongan Voucher'},{'id': '36947de5-41d8-4b7c-8708-d20330ed07d6','no_tiket': '#421492','review': 'staff nya ramah'}]"
            }
        }


class SentimentAnalysisResult(BaseModel):
    """Individual sentiment analysis result"""
    id: str
    no_tiket: str
    review: str
    sentiment: str
    score: float
    reasons: str
    themes: List[str]
    suggestion: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "26947de5-41d8-4b7c-8708-d20330ed07d6",
                "no_tiket": "#421491",
                "review": "Tidak dapat potongan Voucher",
                "sentiment": "Negative",
                "score": -1.5,
                "reasons": "Tidak mendapatkan manfaat dari promosi yang diharapkan",
                "themes": ["Promosi"],
                "suggestion": "Memastikan informasi promosi diberikan secara jelas"
            }
        }


class SentimentAnalysisResponse(BaseModel):
    """Response for single record sentiment analysis"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Sentiment analysis completed successfully",
                "data": {
                    "record_id": "123e4567-e89b-12d3-a456-426614174000",
                    "sentiment": "Positive",
                    "sentiment_score": 1.5,
                    "analyzed_at": "2025-08-31T10:30:00.000Z"
                }
            }
        }


class BulkSentimentAnalysisResponse(BaseModel):
    """Response for bulk sentiment analysis"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Bulk sentiment analysis completed",
                "data": {
                    "batch_id": "456e7890-e89b-12d3-a456-426614174000",
                    "total_records": 100,
                    "analyzed_records": 95,
                    "failed_records": 5,
                    "started_at": "2025-08-31T10:00:00.000Z",
                    "completed_at": "2025-08-31T10:30:00.000Z"
                }
            }
        }


class SentimentAnalysisFilters(BaseModel):
    """Filters for sentiment analysis queries"""
    sentiment: Optional[str] = Field(None, description="Filter by sentiment (Positive/Negative/Neutral)")
    min_score: Optional[float] = Field(None, description="Minimum sentiment score")
    max_score: Optional[float] = Field(None, description="Maximum sentiment score")
    analyzed_from: Optional[str] = Field(None, description="Filter by analysis date from (YYYY-MM-DD)")
    analyzed_to: Optional[str] = Field(None, description="Filter by analysis date to (YYYY-MM-DD)")
    has_themes: Optional[str] = Field(None, description="Filter by specific theme")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of records per page")

    @validator('analyzed_from', 'analyzed_to')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @validator('sentiment')
    def validate_sentiment(cls, v):
        if v is not None and v not in ['Positive', 'Negative', 'Neutral']:
            raise ValueError('Sentiment must be Positive, Negative, or Neutral')
        return v

    @validator('min_score', 'max_score')
    def validate_score_range(cls, v):
        if v is not None and not (-5.0 <= v <= 5.0):
            raise ValueError('Score must be between -5.0 and 5.0')
        return v