"""
PKB (Perintah Kerja Bengkel) Data Models for H23 Dashboard
"""

import os
import sys
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, UniqueConstraint
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

class PKBData(Base):
    """PKB (Perintah Kerja Bengkel) Data Model"""
    __tablename__ = "pkb_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), nullable=False, index=True)
    no_work_order = Column(String(100), nullable=False, index=True)
    no_sa_form = Column(String(100))
    tanggal_servis = Column(String(20))
    waktu_pkb = Column(String(50))
    no_polisi = Column(String(20))
    no_rangka = Column(String(50))
    no_mesin = Column(String(50))
    kode_tipe_unit = Column(String(20))
    tahun_motor = Column(String(10))
    informasi_bensin = Column(String(10))
    km_terakhir = Column(Integer)
    tipe_coming_customer = Column(String(10))
    nama_pemilik = Column(String(255))
    alamat_pemilik = Column(Text)
    kode_propinsi_pemilik = Column(String(10))
    kode_kota_pemilik = Column(String(10))
    kode_kecamatan_pemilik = Column(String(10))
    kode_kelurahan_pemilik = Column(String(20))
    kode_pos_pemilik = Column(String(10))
    alamat_pembawa = Column(Text)
    kode_propinsi_pembawa = Column(String(10))
    kode_kota_pembawa = Column(String(10))
    kode_kecamatan_pembawa = Column(String(10))
    kode_kelurahan_pembawa = Column(String(20))
    kode_pos_pembawa = Column(String(10))
    nama_pembawa = Column(String(255))
    no_telp_pembawa = Column(String(50))
    hubungan_dengan_pemilik = Column(String(10))
    keluhan_konsumen = Column(Text)
    rekomendasi_sa = Column(Text)
    honda_id_sa = Column(String(50))
    honda_id_mekanik = Column(String(50))
    saran_mekanik = Column(Text)
    asal_unit_entry = Column(String(10))
    id_pit = Column(String(20))
    jenis_pit = Column(String(10))
    waktu_pendaftaran = Column(String(50))
    waktu_selesai = Column(String(50))
    total_frt = Column(String(20))
    set_up_pembayaran = Column(String(10))
    catatan_tambahan = Column(Text)
    konfirmasi_pekerjaan_tambahan = Column(String(10))
    no_buku_claim_c2 = Column(String(50))
    no_work_order_job_return = Column(String(100))
    total_biaya_service = Column(Float)
    waktu_pekerjaan = Column(String(20))
    status_work_order = Column(String(10))
    created_time = Column(String(50))
    modified_time = Column(String(50))
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraints for bulk upsert operations
    __table_args__ = (
        UniqueConstraint('dealer_id', 'no_work_order', name='uq_pkb_dealer_work_order'),
    )

class PKBService(Base):
    """PKB Services related to PKB Data"""
    __tablename__ = "pkb_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pkb_data_id = Column(UUID(as_uuid=True), nullable=False)
    id_job = Column(String(50))
    nama_pekerjaan = Column(String(255))
    jenis_pekerjaan = Column(String(100))
    biaya_service = Column(Float)
    promo_id_jasa = Column(String(50))
    disc_service_amount = Column(Float)
    disc_service_percentage = Column(Float)
    total_harga_servis = Column(Float)
    created_time = Column(String(50))
    modified_time = Column(String(50))

    # Unique constraints for bulk upsert operations
    __table_args__ = (
        UniqueConstraint('pkb_data_id', 'id_job', name='uq_pkb_service_data_id_job'),
    )

class PKBPart(Base):
    """PKB Parts related to PKB Data"""
    __tablename__ = "pkb_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pkb_data_id = Column(UUID(as_uuid=True), nullable=False)
    id_job = Column(String(50))
    parts_number = Column(String(100))
    harga_parts = Column(Float)
    promo_id_parts = Column(String(50))
    disc_parts_amount = Column(Float)
    disc_parts_percentage = Column(Float)
    ppn = Column(Float)
    total_harga_parts = Column(Float)
    uang_muka = Column(Float)
    kuantitas = Column(Integer)
    created_time = Column(String(50))
    modified_time = Column(String(50))

    # Unique constraints for bulk upsert operations
    __table_args__ = (
        UniqueConstraint('pkb_data_id', 'id_job', 'parts_number', name='uq_pkb_part_data_id_job_parts_number'),
    )