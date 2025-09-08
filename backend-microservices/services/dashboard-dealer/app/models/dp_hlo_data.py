"""
DP HLO Data models for H23 dashboard
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class DPHLOData(Base):
    """DP HLO data from DPHLO API"""
    __tablename__ = "dp_hlo_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), nullable=False)
    no_invoice_uang_jaminan = Column(String(100), nullable=True, index=True)
    id_hlo_document = Column(String(100), nullable=True, index=True)
    tanggal_pemesanan_hlo = Column(String(50), nullable=True)
    no_work_order = Column(String(100), nullable=True, index=True)
    id_customer = Column(String(100), nullable=True, index=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parts = relationship("DPHLOPart", back_populates="dp_hlo_data", cascade="all, delete-orphan")


class DPHLOPart(Base):
    """Individual parts for DP HLO data"""
    __tablename__ = "dp_hlo_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dp_hlo_data_id = Column(UUID(as_uuid=True), ForeignKey("dp_hlo_data.id"), nullable=False)
    parts_number = Column(String(100), nullable=True, index=True)
    kuantitas = Column(Integer, nullable=True)
    harga_parts = Column(Numeric(15, 2), nullable=True)
    total_harga_parts = Column(Numeric(15, 2), nullable=True)
    uang_muka = Column(Numeric(15, 2), nullable=True)
    sisa_bayar = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    dp_hlo_data = relationship("DPHLOData", back_populates="parts")