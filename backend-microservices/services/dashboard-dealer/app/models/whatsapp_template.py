"""
WhatsApp Template Model for Dashboard Dealer Service
Mirrors the customer.whatsapp_template table for template copying operations
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WhatsAppTemplate(Base):
    """
    WhatsApp message template model

    This model mirrors the customer.whatsapp_template table.
    Used by dashboard-dealer service to copy templates when registering new dealers.
    """

    __tablename__ = "whatsapp_template"
    __table_args__ = (
        {"schema": "customer"}
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Template categorization
    reminder_target = Column(String(50), nullable=False, index=True)
    reminder_type = Column(String(100), nullable=False, index=True)

    # Dealer-specific templates (NULL for global templates)
    dealer_id = Column(String(50), nullable=True, index=True)

    # Template content
    template = Column(Text, nullable=False)

    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_by = Column(String(100), nullable=True)
    last_modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<WhatsAppTemplate("
            f"id={self.id}, "
            f"reminder_target={self.reminder_target}, "
            f"reminder_type={self.reminder_type}, "
            f"dealer_id={self.dealer_id})>"
        )
