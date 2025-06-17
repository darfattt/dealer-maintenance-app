"""
Unit Inbound Data models for dashboard-dealer service
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Dealer(Base):
    """Dealer model for reference"""
    __tablename__ = "dealers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), unique=True, nullable=False, index=True)
    dealer_name = Column(String(255), nullable=False)
    api_key = Column(String(255))
    api_token = Column(String(255))
    secret_key = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    unit_inbound_data = relationship("UnitInboundData", back_populates="dealer")


class UnitInboundData(Base):
    """Unit Inbound data from Purchase Order"""
    __tablename__ = "unit_inbound_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_shipping_list = Column(String(100), nullable=True)
    tanggal_terima = Column(String(50), nullable=True)
    main_dealer_id = Column(String(10), nullable=True)
    no_invoice = Column(String(100), nullable=True)
    status_shipping_list = Column(String(10), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="unit_inbound_data")
    units = relationship("UnitInboundUnit", back_populates="unit_inbound_data", cascade="all, delete-orphan")


class UnitInboundUnit(Base):
    """Individual unit details for unit inbound data"""
    __tablename__ = "unit_inbound_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_inbound_data_id = Column(UUID(as_uuid=True), ForeignKey("unit_inbound_data.id"), nullable=False)
    kode_tipe_unit = Column(String(50), nullable=True, index=True)
    kode_warna = Column(String(10), nullable=True)
    kuantitas_terkirim = Column(Integer, nullable=True)
    kuantitas_diterima = Column(Integer, nullable=True)
    no_mesin = Column(String(100), nullable=True, index=True)
    no_rangka = Column(String(100), nullable=True, index=True)
    status_rfs = Column(String(10), nullable=True)
    po_id = Column(String(100), nullable=True, index=True)
    kelengkapan_unit = Column(Text, nullable=True)
    no_goods_receipt = Column(String(100), nullable=True)
    doc_nrfs_id = Column(String(100), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    unit_inbound_data = relationship("UnitInboundData", back_populates="units")
