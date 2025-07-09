"""
Billing Process Data Model

This module defines the SQLAlchemy model for billing process data
from the dealer_integration schema.
"""

import os
import sys
from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.database import Base

class BillingProcessData(Base):
    """Billing process data from INV1 API"""
    __tablename__ = "billing_process_data"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealer_integration.dealers.dealer_id"), nullable=False)
    id_invoice = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True)
    id_customer = Column(String(100), nullable=True)
    amount = Column(DECIMAL(15, 2), nullable=True)
    tipe_pembayaran = Column(String(10), nullable=True)
    cara_bayar = Column(String(10), nullable=True)
    status = Column(String(10), nullable=True)
    note = Column(String, nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BillingProcessData(id={self.id}, dealer_id={self.dealer_id}, id_invoice={self.id_invoice})>"
