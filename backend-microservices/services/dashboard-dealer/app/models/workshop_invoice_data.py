"""
Workshop Invoice Data Models for H23 Dashboard
"""

import os
import sys
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Add utils to path for database connection
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if parent_path not in sys.path:
    sys.path.append(parent_path)

from utils.database import Base

class WorkshopInvoiceData(Base):
    """Workshop Invoice data from INV2 API (NJB & NSC)"""
    __tablename__ = "workshop_invoice_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), nullable=False, index=True)
    no_work_order = Column(String(100), nullable=True, index=True)
    no_njb = Column(String(100), nullable=True, index=True)
    tanggal_njb = Column(String(50), nullable=True)
    total_harga_njb = Column(Numeric(15, 2), nullable=True)
    no_nsc = Column(String(100), nullable=True, index=True)
    tanggal_nsc = Column(String(50), nullable=True)
    total_harga_nsc = Column(Numeric(15, 2), nullable=True)
    honda_id_sa = Column(String(100), nullable=True)
    honda_id_mekanik = Column(String(100), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (these would be defined if we had the related models)
    # njb_services = relationship("WorkshopInvoiceNJB", back_populates="workshop_invoice_data", cascade="all, delete-orphan")
    # nsc_parts = relationship("WorkshopInvoiceNSC", back_populates="workshop_invoice_data", cascade="all, delete-orphan")

class WorkshopInvoiceNJB(Base):
    """NJB (Nota Jasa Bengkel) services for workshop invoice"""
    __tablename__ = "workshop_invoice_njb"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workshop_invoice_data_id = Column(UUID(as_uuid=True), ForeignKey("workshop_invoice_data.id"), nullable=False)
    id_job = Column(String(100), nullable=True, index=True)
    harga_servis = Column(Numeric(15, 2), nullable=True)
    promo_id_jasa = Column(String(100), nullable=True)
    disc_service_amount = Column(Numeric(15, 2), nullable=True)
    disc_service_percentage = Column(String(20), nullable=True)
    total_harga_servis = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    workshop_invoice_data = relationship("WorkshopInvoiceData")

class WorkshopInvoiceNSC(Base):
    """NSC (Nota Suku Cadang) parts for workshop invoice"""
    __tablename__ = "workshop_invoice_nsc"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workshop_invoice_data_id = Column(UUID(as_uuid=True), ForeignKey("workshop_invoice_data.id"), nullable=False)
    id_job = Column(String(100), nullable=True, index=True)
    parts_number = Column(String(100), nullable=True, index=True)
    kuantitas = Column(Integer, nullable=True)
    harga_parts = Column(Numeric(15, 2), nullable=True)
    promo_id_parts = Column(String(100), nullable=True)
    disc_parts_amount = Column(Numeric(15, 2), nullable=True)
    disc_parts_percentage = Column(String(20), nullable=True)
    ppn = Column(Numeric(15, 2), nullable=True)
    total_harga_parts = Column(Numeric(15, 2), nullable=True)
    uang_muka = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    workshop_invoice_data = relationship("WorkshopInvoiceData")