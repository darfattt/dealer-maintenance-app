"""
Dealer configuration model for customer service (references existing dealers table)
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DealerConfig(Base):
    """Dealer configuration model - references existing dealers table"""
    
    __tablename__ = "dealers"
    __table_args__ = {"schema": "dealer_integration"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dealer identification
    dealer_id = Column(String(10), unique=True, nullable=False, index=True)
    dealer_name = Column(String(255), nullable=False)
    
    # API configuration
    api_key = Column(String(255))
    api_token = Column(String(255))
    secret_key = Column(String(255))
    
    # Fonnte WhatsApp configuration
    fonnte_api_key = Column(String(255), nullable=True)
    fonnte_api_url = Column(String(255), nullable=True, default='https://api.fonnte.com/send')
    
    # Contact information
    phone_number = Column(String(255), nullable=True)
    
    # Autology integration
    autology_access_key = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DealerConfig(id={self.id}, dealer_id={self.dealer_id}, dealer_name={self.dealer_name})>"
    
    def to_dict(self):
        """Convert dealer config to dictionary (excluding sensitive data)"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "dealer_name": self.dealer_name,
            "has_fonnte_config": bool(self.fonnte_api_key),
            "fonnte_api_url": self.fonnte_api_url,
            "phone_number": self.phone_number,
            "has_autology_config": bool(self.autology_access_key),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def has_fonnte_configuration(self) -> bool:
        """Check if dealer has Fonnte configuration"""
        return bool(self.fonnte_api_key and self.fonnte_api_url)