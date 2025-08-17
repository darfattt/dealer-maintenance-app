"""
Customer validation request model for customer service
"""

import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, DateTime, Date, Time, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CustomerValidationRequest(Base):
    """Customer validation request model"""
    
    __tablename__ = "customer_validation_request"
    __table_args__ = {"schema": "customer"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Dealer reference
    dealer_id = Column(String(10), nullable=False, index=True)
    
    # Request timing
    request_date = Column(Date, nullable=False)
    request_time = Column(Time, nullable=False)
    
    # Customer data
    nama_pembawa = Column(String(255), nullable=False)
    nomor_telepon_pembawa = Column(String(20), nullable=False)
    tipe_unit = Column(String(100), nullable=False)
    nomor_polisi = Column(String(20), nullable=False)
    
    # AHASS data
    kode_ahass = Column(String(10), nullable=True)
    nama_ahass = Column(String(255), nullable=True)
    alamat_ahass = Column(Text, nullable=True)
    nomor_mesin = Column(String(50), nullable=True)
    
    # Status tracking
    request_status = Column(String(20), nullable=False, default='PENDING')
    whatsapp_status = Column(String(20), nullable=False, default='NOT_SENT')
    
    # WhatsApp message content
    whatsapp_message = Column(Text, nullable=True)
    
    # Fonnte API response
    fonnte_response = Column(JSON, nullable=True)
    
    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_by = Column(String(100), nullable=True)
    last_modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CustomerValidationRequest(id={self.id}, dealer_id={self.dealer_id}, nama_pembawa={self.nama_pembawa})>"
    
    def to_dict(self):
        """Convert customer validation request to dictionary"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "request_date": self.request_date.isoformat() if self.request_date else None,
            "request_time": self.request_time.isoformat() if self.request_time else None,
            "nama_pembawa": self.nama_pembawa,
            "nomor_telepon_pembawa": self.nomor_telepon_pembawa,
            "tipe_unit": self.tipe_unit,
            "nomor_polisi": self.nomor_polisi,
            "kode_ahass": self.kode_ahass,
            "nama_ahass": self.nama_ahass,
            "alamat_ahass": self.alamat_ahass,
            "nomor_mesin": self.nomor_mesin,
            "request_status": self.request_status,
            "whatsapp_status": self.whatsapp_status,
            "whatsapp_message": self.whatsapp_message,
            "fonnte_response": self.fonnte_response,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_by": self.last_modified_by,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
        }