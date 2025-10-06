"""
WhatsApp template audit logging model
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WhatsAppTemplateLogs(Base):
    """WhatsApp template audit log model"""

    __tablename__ = "whatsapp_template_logs"
    __table_args__ = (
        {"schema": "customer"}
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Template reference (nullable for delete operations)
    template_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Operation type
    operation = Column(String(20), nullable=False, index=True)  # CREATE, UPDATE, DELETE, COPY

    # Template data tracking
    old_data = Column(JSONB, nullable=True)  # Previous template data
    new_data = Column(JSONB, nullable=True)  # New template data

    # Operation context
    dealer_id = Column(String(50), nullable=True, index=True)  # Primary dealer involved
    user_email = Column(String(255), nullable=False, index=True)  # User who performed operation

    # Copy operation specific fields
    source_dealer_id = Column(String(50), nullable=True)  # Source dealer for copy operations
    target_dealer_id = Column(String(50), nullable=True)  # Target dealer for copy operations

    # Metadata
    operation_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    client_ip = Column(String(45), nullable=True)  # Client IP address
    user_agent = Column(Text, nullable=True)  # Browser/client user agent
    operation_notes = Column(Text, nullable=True)  # Optional operation notes

    # Audit timestamp
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<WhatsAppTemplateLogs(id={self.id}, operation={self.operation}, template_id={self.template_id}, user={self.user_email})>"

    def to_dict(self):
        """Convert log entry to dictionary"""
        return {
            "id": str(self.id),
            "template_id": str(self.template_id) if self.template_id else None,
            "operation": self.operation,
            "old_data": self.old_data,
            "new_data": self.new_data,
            "dealer_id": self.dealer_id,
            "user_email": self.user_email,
            "source_dealer_id": self.source_dealer_id,
            "target_dealer_id": self.target_dealer_id,
            "operation_timestamp": self.operation_timestamp.isoformat() if self.operation_timestamp else None,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "operation_notes": self.operation_notes,
            "created_date": self.created_date.isoformat() if self.created_date else None,
        }

    @classmethod
    def create_log_entry(
        cls,
        operation: str,
        user_email: str,
        template_id: Optional[str] = None,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        dealer_id: Optional[str] = None,
        source_dealer_id: Optional[str] = None,
        target_dealer_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        operation_notes: Optional[str] = None
    ) -> "WhatsAppTemplateLogs":
        """
        Create a new log entry

        Args:
            operation: Type of operation (CREATE, UPDATE, DELETE, COPY)
            user_email: Email of user performing operation
            template_id: ID of affected template
            old_data: Previous template data (for UPDATE/DELETE)
            new_data: New template data (for CREATE/UPDATE)
            dealer_id: Primary dealer ID involved
            source_dealer_id: Source dealer for copy operations
            target_dealer_id: Target dealer for copy operations
            client_ip: Client IP address
            user_agent: Client user agent
            operation_notes: Optional notes about operation

        Returns:
            WhatsAppTemplateLogs instance
        """
        return cls(
            template_id=template_id,
            operation=operation,
            old_data=old_data,
            new_data=new_data,
            dealer_id=dealer_id,
            user_email=user_email,
            source_dealer_id=source_dealer_id,
            target_dealer_id=target_dealer_id,
            operation_timestamp=datetime.utcnow(),
            client_ip=client_ip,
            user_agent=user_agent,
            operation_notes=operation_notes
        )

    def get_operation_summary(self) -> str:
        """Get human-readable operation summary"""
        operation_summaries = {
            "CREATE": f"Created template by {self.user_email}",
            "UPDATE": f"Updated template by {self.user_email}",
            "DELETE": f"Deleted template by {self.user_email}",
            "COPY": f"Copied templates from {self.source_dealer_id} to {self.target_dealer_id} by {self.user_email}"
        }

        base_summary = operation_summaries.get(self.operation, f"Unknown operation {self.operation}")

        if self.operation_notes:
            base_summary += f" - {self.operation_notes}"

        return base_summary

    def get_changed_fields(self) -> list:
        """Get list of fields that were changed (for UPDATE operations)"""
        if self.operation != "UPDATE" or not self.old_data or not self.new_data:
            return []

        changed_fields = []
        for key in self.new_data.keys():
            if key in self.old_data and self.old_data[key] != self.new_data[key]:
                changed_fields.append(key)

        return changed_fields