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
    customer_name = Column(String(255), nullable=False)
    no_telp = Column(String(20), nullable=False)
    
    # Status tracking
    request_status = Column(String(20), nullable=False, default='PENDING')
    whatsapp_status = Column(String(20), nullable=False, default='NOT_SENT')
    
    # Reminder type (e.g., 'SERVICE_REMINDER', 'PAYMENT_REMINDER', 'APPOINTMENT_REMINDER')
    reminder_type = Column(String(50), nullable=False)
    
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
        return f"<CustomerReminderRequest(id={self.id}, dealer_id={self.dealer_id}, customer_name={self.customer_name})>"
    
    def to_dict(self):
        """Convert customer reminder request to dictionary"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "request_date": self.request_date.isoformat() if self.request_date else None,
            "request_time": self.request_time.isoformat() if self.request_time else None,
            "customer_name": self.customer_name,
            "no_telp": self.no_telp,
            "request_status": self.request_status,
            "whatsapp_status": self.whatsapp_status,
            "reminder_type": self.reminder_type,
            "whatsapp_message": self.whatsapp_message,
            "fonnte_response": self.fonnte_response,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_by": self.last_modified_by,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
        }