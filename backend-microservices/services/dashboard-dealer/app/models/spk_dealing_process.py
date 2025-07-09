"""
SPK Dealing Process Data Model

This module defines the SQLAlchemy model for SPK dealing process data
from the dealer_integration schema.
"""

import os
import sys
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Numeric
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

class SPKDealingProcessData(Base):
    """SPK dealing process data from SPKD1 API"""
    __tablename__ = "spk_dealing_process_data"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealer_integration.dealers.dealer_id"), nullable=False)
    id_spk = Column(String(100), nullable=True, index=True)
    id_prospect = Column(String(100), nullable=True, index=True)
    nama_customer = Column(String(200), nullable=True)
    no_ktp = Column(String(50), nullable=True, index=True)
    alamat = Column(Text, nullable=True)
    kode_propinsi = Column(String(10), nullable=True)
    kode_kota = Column(String(10), nullable=True)
    kode_kecamatan = Column(String(20), nullable=True)
    kode_kelurahan = Column(String(20), nullable=True)
    kode_pos = Column(String(10), nullable=True)
    no_kontak = Column(String(50), nullable=True)
    nama_bpkb = Column(String(200), nullable=True)
    no_ktp_bpkb = Column(String(50), nullable=True)
    alamat_bpkb = Column(Text, nullable=True)
    kode_propinsi_bpkb = Column(String(10), nullable=True)
    kode_kota_bpkb = Column(String(10), nullable=True)
    kode_kecamatan_bpkb = Column(String(20), nullable=True)
    kode_kelurahan_bpkb = Column(String(20), nullable=True)
    kode_pos_bpkb = Column(String(10), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    npwp = Column(String(50), nullable=True)
    no_kk = Column(String(50), nullable=True)
    alamat_kk = Column(Text, nullable=True)
    kode_propinsi_kk = Column(String(10), nullable=True)
    kode_kota_kk = Column(String(10), nullable=True)
    kode_kecamatan_kk = Column(String(20), nullable=True)
    kode_kelurahan_kk = Column(String(20), nullable=True)
    kode_pos_kk = Column(String(10), nullable=True)
    fax = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    id_sales_people = Column(String(50), nullable=True)
    id_event = Column(String(100), nullable=True)
    tanggal_pesanan = Column(String(50), nullable=True, index=True)
    status_spk = Column(String(10), nullable=True, index=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    units = relationship("SPKDealingProcessUnit", back_populates="spk_dealing_process_data", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SPKDealingProcessData(id={self.id}, dealer_id={self.dealer_id}, id_spk={self.id_spk})>"


class SPKDealingProcessUnit(Base):
    """Unit data for SPK dealing process"""
    __tablename__ = "spk_dealing_process_units"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spk_dealing_process_data_id = Column(UUID(as_uuid=True), ForeignKey("dealer_integration.spk_dealing_process_data.id"), nullable=False)
    kode_tipe_unit = Column(String(50), nullable=True, index=True)
    kode_warna = Column(String(10), nullable=True)
    quantity = Column(Integer, nullable=True)
    harga_jual = Column(Numeric(15, 2), nullable=True)
    diskon = Column(Numeric(15, 2), nullable=True)
    amount_ppn = Column(Numeric(15, 2), nullable=True)
    faktur_pajak = Column(String(100), nullable=True)
    tipe_pembayaran = Column(String(10), nullable=True)
    jumlah_tanda_jadi = Column(Numeric(15, 2), nullable=True)
    tanggal_pengiriman = Column(String(50), nullable=True, index=True)
    id_sales_program = Column(Text, nullable=True)
    id_apparel = Column(Text, nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    spk_dealing_process_data = relationship("SPKDealingProcessData", back_populates="units")

    def __repr__(self):
        return f"<SPKDealingProcessUnit(id={self.id}, kode_tipe_unit={self.kode_tipe_unit}, quantity={self.quantity})>"