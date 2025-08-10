"""
Dealer Access Key model for external API authentication
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DealerAccessKey(Base):
    """Dealer Access Key model for API authentication"""
    
    __tablename__ = "dealer_access_key"
    __table_args__ = {"schema": "dealer_integration"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to dealers table
    dealer_id = Column(String(10), nullable=False, index=True)
    
    # Access key (should be unique across all dealers)
    access_key = Column(String(64), unique=True, nullable=False, index=True)
    
    # Key metadata
    name = Column(String(255), nullable=True)  # Description/name for the key
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DealerAccessKey(id={self.id}, dealer_id={self.dealer_id}, name={self.name}, is_active={self.is_active})>"
    
    def is_valid(self) -> bool:
        """Check if access key is valid (active and not expired)"""
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def is_expired(self) -> bool:
        """Check if access key is expired"""
        if not self.expires_at:
            return False
        return self.expires_at < datetime.utcnow()
    
    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert access key to dictionary"""
        data = {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "name": self.name,
            "is_active": self.is_active,
            "is_expired": self.is_expired(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Only include sensitive data if explicitly requested
        if include_sensitive:
            data["access_key"] = self.access_key
        else:
            # Show only first 6 characters for security
            data["access_key_preview"] = self.access_key[:6] + "..." if self.access_key else None
        
        return data
    
    @staticmethod
    def generate_access_key(dealer_id: str, prefix: str = "ak") -> str:
        """Generate a new access key"""
        import secrets
        import string
        
        # Generate random string
        alphabet = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Create access key with format: prefix_dealerId_randomString
        return f"{prefix}_{dealer_id}_{random_part}"