"""
User model for account service
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserRole(enum.Enum):
    """User roles enumeration"""
    SUPER_ADMIN = "SUPER_ADMIN"
    DEALER_ADMIN = "DEALER_ADMIN"
    DEALER_USER = "DEALER_USER"


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    __table_args__ = {"schema": "account"}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User identification
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Authorization
    role = Column(Enum(UserRole), nullable=False, default=UserRole.DEALER_ADMIN)
    
    # Dealer association (for DEALER_ADMIN users)
    dealer_id = Column(String(10), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)

    # Relationships
    user_dealers = relationship("UserDealer", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role.value,
            "dealer_id": self.dealer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.DEALER_USER: 1,
            UserRole.DEALER_ADMIN: 2,
            UserRole.SUPER_ADMIN: 3,
        }

        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level
    
    def can_access_dealer(self, dealer_id: str) -> bool:
        """Check if user can access specific dealer data"""
        if self.role == UserRole.SUPER_ADMIN:
            return True

        if self.role == UserRole.DEALER_ADMIN:
            return self.dealer_id == dealer_id

        if self.role == UserRole.DEALER_USER:
            # For DEALER_USER, check through users_dealer relationship
            return any(ud.dealer_id == dealer_id for ud in self.user_dealers)

        return False

    def get_accessible_dealer_ids(self) -> list[str]:
        """Get list of dealer IDs that user can access"""
        if self.role == UserRole.SUPER_ADMIN:
            # SUPER_ADMIN can access all dealers - return empty list to indicate "all"
            return []

        if self.role == UserRole.DEALER_ADMIN:
            return [self.dealer_id] if self.dealer_id else []

        if self.role == UserRole.DEALER_USER:
            return [ud.dealer_id for ud in self.user_dealers]

        return []


class UserDealer(Base):
    """User-Dealer relationship model for DEALER_USER role"""

    __tablename__ = "users_dealer"
    __table_args__ = {"schema": "account"}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("account.users.id"), nullable=False, index=True)

    # Dealer ID (stored as string, not a foreign key to maintain loose coupling)
    dealer_id = Column(String(10), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship back to user
    user = relationship("User", back_populates="user_dealers")

    def __repr__(self):
        return f"<UserDealer(id={self.id}, user_id={self.user_id}, dealer_id={self.dealer_id})>"

    def to_dict(self):
        """Convert user dealer to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "dealer_id": self.dealer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
