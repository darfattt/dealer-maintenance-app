"""
Dealer model for dashboard-dealer service
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Dealer(Base):
    """Dealer configuration model"""
    __tablename__ = "dealers"
    __table_args__ = {"schema": "dealer_integration"}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Dealer identification
    dealer_id = Column(String(10), unique=True, nullable=False, index=True)
    dealer_name = Column(String(255), nullable=False)

    # DGI API configuration
    api_key = Column(String(255), nullable=True)
    api_token = Column(String(255), nullable=True)
    secret_key = Column(String(255), nullable=True)

    # Fonnte WhatsApp configuration
    fonnte_api_key = Column(String(255), nullable=True)
    fonnte_api_url = Column(String(255), nullable=True, default='https://api.fonnte.com/send')

    # Contact information
    phone_number = Column(String(255), nullable=True)
    google_location_url = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Dealer(id={self.id}, dealer_id={self.dealer_id}, dealer_name={self.dealer_name})>"

    def to_dict(self):
        """Convert dealer to dictionary"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "dealer_name": self.dealer_name,
            "api_key": self.api_key,
            "api_token": self.api_token,
            "secret_key": self.secret_key,
            "fonnte_api_key": self.fonnte_api_key,
            "fonnte_api_url": self.fonnte_api_url,
            "phone_number": self.phone_number,
            "google_location_url": self.google_location_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
