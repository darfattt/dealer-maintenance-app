"""
Customer reminder request model for customer service
"""

import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, DateTime, Date, Time, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CustomerReminderRequest(Base):
    """Customer reminder request model"""
    
    __tablename__ = "customer_reminder_request"
    __table_args__ = {"schema": "customer"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Dealer reference
    dealer_id = Column(String(10), nullable=False, index=True)
    
    # Request timing
    request_date = Column(Date, nullable=False)
    request_time = Column(Time, nullable=False)
    
    # Customer data  
    nomor_telepon_pelanggan = Column(String(20), nullable=False)  # Customer primary phone number
    
    # Additional customer/vehicle data
    nama_pemilik = Column(String(255), nullable=False)  # Primary customer/owner name field
    nama_pembawa = Column(String(255), nullable=True)
    no_telepon_pembawa = Column(String(20), nullable=True)
    nomor_mesin = Column(String(50), nullable=True)
    nomor_polisi = Column(String(20), nullable=True)
    tipe_unit = Column(String(100), nullable=True)
    tanggal_beli = Column(Date, nullable=True)
    tanggal_expired_kpb = Column(Date, nullable=True)
    
    # AHASS data
    kode_ahass = Column(String(10), nullable=True)
    nama_ahass = Column(String(255), nullable=True)
    alamat_ahass = Column(Text, nullable=True)
    
    # Status tracking
    request_status = Column(String(20), nullable=False, default='PENDING')
    whatsapp_status = Column(String(20), nullable=False, default='NOT_SENT')
    
    # Reminder categorization
    reminder_target = Column(String(50), nullable=False)  # maps to filter_target
    reminder_type = Column(String(100), nullable=False)  # maps to filter_data
    
    # WhatsApp message content
    whatsapp_message = Column(Text, nullable=True)
    
    # Fonnte API response
    fonnte_response = Column(JSON, nullable=True)
    
    # Transaction tracking
    transaction_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_by = Column(String(100), nullable=True)
    last_modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CustomerReminderRequest(id={self.id}, dealer_id={self.dealer_id}, nama_pemilik={self.nama_pemilik})>"
    
    def to_dict(self):
        """Convert customer reminder request to dictionary"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "request_date": self.request_date.isoformat() if self.request_date else None,
            "request_time": self.request_time.isoformat() if self.request_time else None,
            "nomor_telepon_pelanggan": self.nomor_telepon_pelanggan,
            "nama_pemilik": self.nama_pemilik,
            "nama_pembawa": self.nama_pembawa,
            "no_telepon_pembawa": self.no_telepon_pembawa,
            "nomor_mesin": self.nomor_mesin,
            "nomor_polisi": self.nomor_polisi,
            "tipe_unit": self.tipe_unit,
            "tanggal_beli": self.tanggal_beli.isoformat() if self.tanggal_beli else None,
            "tanggal_expired_kpb": self.tanggal_expired_kpb.isoformat() if self.tanggal_expired_kpb else None,
            "kode_ahass": self.kode_ahass,
            "nama_ahass": self.nama_ahass,
            "alamat_ahass": self.alamat_ahass,
            "request_status": self.request_status,
            "whatsapp_status": self.whatsapp_status,
            "reminder_target": self.reminder_target,
            "reminder_type": self.reminder_type,
            "whatsapp_message": self.whatsapp_message,
            "fonnte_response": self.fonnte_response,
            "transaction_id": str(self.transaction_id) if self.transaction_id else None,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_by": self.last_modified_by,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
        }