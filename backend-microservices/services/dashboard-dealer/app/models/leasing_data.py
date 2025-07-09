"""
Leasing Data Model

This module defines the SQLAlchemy model for leasing data
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

class LeasingData(Base):
    """Leasing data from LEAS1 API"""
    __tablename__ = "leasing_data"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealer_integration.dealers.dealer_id"), nullable=False)
    id_dokumen_pengajuan = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True, index=True)
    jumlah_dp = Column(Numeric(15, 2), nullable=True)
    tenor = Column(Integer, nullable=True)
    jumlah_cicilan = Column(Numeric(15, 2), nullable=True)
    tanggal_pengajuan = Column(String(50), nullable=True, index=True)
    id_finance_company = Column(String(100), nullable=True)
    nama_finance_company = Column(String(255), nullable=True, index=True)
    id_po_finance_company = Column(String(100), nullable=True, index=True)
    tanggal_pembuatan_po = Column(String(50), nullable=True)
    tanggal_pengiriman_po_finance_company = Column(String(50), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LeasingData(id={self.id}, dealer_id={self.dealer_id}, nama_finance_company={self.nama_finance_company})>"