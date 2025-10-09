"""
User model for dashboard-dealer service (read from account schema)
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserRole(enum.Enum):
    """User roles enumeration"""
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    DEALER_ADMIN = "DEALER_ADMIN"
    DEALER_USER = "DEALER_USER"


class User(Base):
    """User model for authentication and authorization (account schema)"""

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


class UserDealer(Base):
    """User-Dealer relationship model for DEALER_USER role (account schema)"""

    __tablename__ = "users_dealer"
    __table_args__ = (
        Index('ix_users_dealer_id', 'id'),
        Index('ix_users_dealer_user_id', 'user_id'),
        Index('ix_users_dealer_dealer_id', 'dealer_id'),
        {"schema": "account"}
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("account.users.id"), nullable=False)

    # Dealer ID (stored as string, not a foreign key to maintain loose coupling)
    dealer_id = Column(String(10), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserDealer(id={self.id}, user_id={self.user_id}, dealer_id={self.dealer_id})>"
