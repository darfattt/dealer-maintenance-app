"""
Document Handling Data Models

This module defines the SQLAlchemy models for document handling data
from the dealer_integration schema.
"""

import os
import sys
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric
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

class DocumentHandlingData(Base):
    """Document handling data from DOC1 API"""
    __tablename__ = "document_handling_data"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealer_integration.dealers.dealer_id"), nullable=False)
    id_so = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True, index=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    units = relationship("DocumentHandlingUnit", back_populates="document_handling_data", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DocumentHandlingData(id={self.id}, dealer_id={self.dealer_id}, id_spk={self.id_spk})>"


class DocumentHandlingUnit(Base):
    """Document handling unit data from DOC1 API"""
    __tablename__ = "document_handling_units"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_handling_data_id = Column(UUID(as_uuid=True), ForeignKey("dealer_integration.document_handling_data.id"), nullable=False)
    nomor_rangka = Column(String(100), nullable=True, index=True)
    nomor_faktur_stnk = Column(String(100), nullable=True)
    tanggal_pengajuan_stnk_ke_biro = Column(String(50), nullable=True, index=True)
    status_faktur_stnk = Column(String(10), nullable=True, index=True)
    nomor_stnk = Column(String(100), nullable=True)
    tanggal_penerimaan_stnk_dari_biro = Column(String(50), nullable=True)
    plat_nomor = Column(String(50), nullable=True)
    nomor_bpkb = Column(String(100), nullable=True)
    tanggal_penerimaan_bpkb_dari_biro = Column(String(50), nullable=True)
    tanggal_terima_stnk_oleh_konsumen = Column(String(50), nullable=True)
    tanggal_terima_bpkb_oleh_konsumen = Column(String(50), nullable=True)
    nama_penerima_bpkb = Column(String(255), nullable=True)
    nama_penerima_stnk = Column(String(255), nullable=True)
    jenis_id_penerima_bpkb = Column(String(10), nullable=True)
    jenis_id_penerima_stnk = Column(String(10), nullable=True)
    no_id_penerima_bpkb = Column(String(100), nullable=True)
    no_id_penerima_stnk = Column(String(100), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    document_handling_data = relationship("DocumentHandlingData", back_populates="units")

    def __repr__(self):
        return f"<DocumentHandlingUnit(id={self.id}, nomor_rangka={self.nomor_rangka}, status_faktur_stnk={self.status_faktur_stnk})>"