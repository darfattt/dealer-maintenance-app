"""
Customer satisfaction raw data model for customer service
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import Indonesian timezone utility function
def _get_indonesia_timezone_utc():
    """Get current Indonesian time as UTC for database storage"""
    try:
        from app.utils.timezone_utils import get_indonesia_utc_now
        return get_indonesia_utc_now()
    except ImportError:
        # Fallback to standard UTC if timezone utils not available
        return datetime.utcnow()


class CustomerSatisfactionRaw(Base):
    """Customer satisfaction raw data model - stores CSV data as-is"""
    
    __tablename__ = "customer_satisfaction_raw"
    __table_args__ = {"schema": "customer"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # CSV columns as-is (keeping Indonesian field names)
    no_tiket = Column(String(50), nullable=True)
    no_booking_no_order_pemesanan = Column(String(100), nullable=True)
    nama_konsumen = Column(String(255), nullable=True)
    no_hp = Column(String(20), nullable=True)
    alamat_email = Column(String(255), nullable=True)
    source = Column(String(100), nullable=True)
    kota = Column(String(100), nullable=True)
    fu_by_se = Column(String(100), nullable=True)
    fu_by_sda = Column(String(100), nullable=True)
    no_ahass = Column(String(10), nullable=True, index=True)  # Indexed for filtering
    status = Column(String(50), nullable=True)
    nama_ahass = Column(String(255), nullable=True)
    tanggal_service = Column(String(50), nullable=True)
    periode_service = Column(String(10), nullable=True)
    tanggal_rating = Column(String(50), nullable=True)
    jenis_hari = Column(String(50), nullable=True)
    periode_utk_suspend = Column(String(100), nullable=True, index=True)  # Indexed for filtering
    submit_review_date_first_fu_cs = Column(String(50), nullable=True, index=True)  # Indexed for filtering
    lt_tgl_rating_submit = Column(String(10), nullable=True)
    sesuai_lt = Column(String(50), nullable=True)
    periode_fu = Column(String(10), nullable=True)
    inbox = Column(Text, nullable=True)
    indikasi_keluhan = Column(String(100), nullable=True)
    rating = Column(String(10), nullable=True)
    departemen = Column(String(100), nullable=True)
    no_ahass_duplicate = Column(String(10), nullable=True)  # Second No AHASS column
    status_duplicate = Column(String(50), nullable=True)    # Second Status column  
    nama_ahass_duplicate = Column(String(255), nullable=True)  # Second Nama AHASS column
    
    # Upload tracking
    upload_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Sentiment analysis fields
    sentiment = Column(String(20), nullable=True)  # Positive, Negative, Neutral
    sentiment_score = Column(Numeric(4, 2), nullable=True)  # -5.00 to 5.00
    sentiment_reasons = Column(Text, nullable=True)
    sentiment_suggestion = Column(Text, nullable=True)
    sentiment_themes = Column(Text, nullable=True)  # JSON array as string
    sentiment_analyzed_at = Column(DateTime, nullable=True)
    sentiment_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Audit fields - using Indonesian timezone
    created_by = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=_get_indonesia_timezone_utc, nullable=False)
    last_modified_by = Column(String(100), nullable=True)
    last_modified_date = Column(DateTime, default=_get_indonesia_timezone_utc, onupdate=_get_indonesia_timezone_utc, nullable=False)
    
    def __repr__(self):
        return f"<CustomerSatisfactionRaw(id={self.id}, no_tiket={self.no_tiket}, nama_konsumen={self.nama_konsumen})>"
    
    def to_dict(self):
        """Convert customer satisfaction raw data to dictionary"""
        return {
            "id": str(self.id),
            "no_tiket": self.no_tiket,
            "no_booking_no_order_pemesanan": self.no_booking_no_order_pemesanan,
            "nama_konsumen": self.nama_konsumen,
            "no_hp": self.no_hp,
            "alamat_email": self.alamat_email,
            "source": self.source,
            "kota": self.kota,
            "fu_by_se": self.fu_by_se,
            "fu_by_sda": self.fu_by_sda,
            "no_ahass": self.no_ahass,
            "status": self.status,
            "nama_ahass": self.nama_ahass,
            "tanggal_service": self.tanggal_service,
            "periode_service": self.periode_service,
            "tanggal_rating": self.tanggal_rating,
            "jenis_hari": self.jenis_hari,
            "periode_utk_suspend": self.periode_utk_suspend,
            "submit_review_date_first_fu_cs": self.submit_review_date_first_fu_cs,
            "lt_tgl_rating_submit": self.lt_tgl_rating_submit,
            "sesuai_lt": self.sesuai_lt,
            "periode_fu": self.periode_fu,
            "inbox": self.inbox,
            "indikasi_keluhan": self.indikasi_keluhan,
            "rating": self.rating,
            "departemen": self.departemen,
            "no_ahass_duplicate": self.no_ahass_duplicate,
            "status_duplicate": self.status_duplicate,
            "nama_ahass_duplicate": self.nama_ahass_duplicate,
            "upload_batch_id": str(self.upload_batch_id) if self.upload_batch_id else None,
            # Sentiment analysis fields
            "sentiment": self.sentiment,
            "sentiment_score": float(self.sentiment_score) if self.sentiment_score is not None else None,
            "sentiment_reasons": self.sentiment_reasons,
            "sentiment_suggestion": self.sentiment_suggestion,
            "sentiment_themes": self.sentiment_themes,
            "sentiment_analyzed_at": self.sentiment_analyzed_at.isoformat() if self.sentiment_analyzed_at else None,
            "sentiment_batch_id": str(self.sentiment_batch_id) if self.sentiment_batch_id else None,
            # Audit fields
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_by": self.last_modified_by,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
        }


class CustomerSatisfactionUploadTracker(Base):
    """Upload tracker for customer satisfaction files"""
    
    __tablename__ = "customer_satisfaction_upload_tracker"
    __table_args__ = {"schema": "customer"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    
    # Upload summary
    total_records = Column(Integer, nullable=False, default=0)
    successful_records = Column(Integer, nullable=False, default=0)
    failed_records = Column(Integer, nullable=False, default=0)
    
    # Processing status
    upload_status = Column(String(20), nullable=False, default='PROCESSING')  # PROCESSING, COMPLETED, FAILED
    
    # Error details
    error_message = Column(Text, nullable=True)
    
    # Audit fields - using Indonesian timezone
    uploaded_by = Column(String(100), nullable=True)
    upload_date = Column(DateTime, default=_get_indonesia_timezone_utc, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<CustomerSatisfactionUploadTracker(id={self.id}, file_name={self.file_name}, status={self.upload_status})>"
    
    def to_dict(self):
        """Convert upload tracker to dictionary"""
        return {
            "id": str(self.id),
            "file_name": self.file_name,
            "file_size": self.file_size,
            "total_records": self.total_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "upload_status": self.upload_status,
            "error_message": self.error_message,
            "uploaded_by": self.uploaded_by,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
        }