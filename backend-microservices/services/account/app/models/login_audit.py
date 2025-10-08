"""
Login audit model for account service
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.user import Base


class AuditAction(enum.Enum):
    """Audit action types enumeration"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"


class LoginAudit(Base):
    """Login audit model for tracking authentication activities"""

    __tablename__ = "login_audit"
    __table_args__ = (
        Index('ix_login_audit_user_id', 'user_id'),
        Index('ix_login_audit_email', 'email'),
        Index('ix_login_audit_action', 'action'),
        Index('ix_login_audit_created_at', 'created_at'),
        Index('ix_login_audit_user_created', 'user_id', 'created_at'),
        Index('ix_login_audit_ip_address', 'ip_address'),
        {"schema": "account"}
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # User reference (nullable for failed login attempts with unknown user)
    user_id = Column(UUID(as_uuid=True), ForeignKey("account.users.id", ondelete="SET NULL"), nullable=True)

    # Audit information
    action = Column(Enum(AuditAction), nullable=False)
    email = Column(String(255), nullable=False)  # Store email for failed attempts

    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv4: 15 chars, IPv6: 45 chars
    user_agent = Column(Text, nullable=True)

    # Result
    success = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(Text, nullable=True)  # Store reason for failed attempts

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to user (optional, since user_id can be null)
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<LoginAudit(id={self.id}, action={self.action.value}, email={self.email}, success={self.success})>"

    def to_dict(self):
        """Convert login audit to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "action": self.action.value,
            "email": self.email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
