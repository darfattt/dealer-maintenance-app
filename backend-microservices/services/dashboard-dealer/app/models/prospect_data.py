"""
Prospect Data Model

This module defines the SQLAlchemy model for prospect data
from the dealer_integration schema.
"""

import os
import sys
from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Time, Text
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

class ProspectData(Base):
    """Prospect data from PROS1 API"""
    __tablename__ = "prospect_data"
    __table_args__ = {'schema': 'dealer_integration'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealer_integration.dealers.dealer_id"), nullable=False)
    id_prospect = Column(String(255), nullable=True)
    sumber_prospect = Column(String(10), nullable=True)
    tanggal_prospect = Column(Date, nullable=True)
    tagging_prospect = Column(String(10), nullable=True)
    nama_lengkap = Column(String(255), nullable=True)
    no_kontak = Column(String(50), nullable=True)
    no_ktp = Column(String(50), nullable=True)
    alamat = Column(Text, nullable=True)
    kode_propinsi = Column(String(10), nullable=True)
    kode_kota = Column(String(10), nullable=True)
    kode_kecamatan = Column(String(10), nullable=True)
    kode_kelurahan = Column(String(10), nullable=True)
    kode_pos = Column(String(10), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    alamat_kantor = Column(Text, nullable=True)
    kode_propinsi_kantor = Column(String(10), nullable=True)
    kode_kota_kantor = Column(String(10), nullable=True)
    kode_kecamatan_kantor = Column(String(10), nullable=True)
    kode_kelurahan_kantor = Column(String(10), nullable=True)
    kode_pos_kantor = Column(String(10), nullable=True)
    kode_pekerjaan = Column(String(10), nullable=True)
    no_kontak_kantor = Column(String(50), nullable=True)
    tanggal_appointment = Column(Date, nullable=True, index=True)
    waktu_appointment = Column(Time, nullable=True)
    metode_follow_up = Column(String(10), nullable=True)
    test_ride_preference = Column(String(10), nullable=True)
    status_follow_up_prospecting = Column(String(10), nullable=True, index=True)
    status_prospect = Column(String(10), nullable=True)
    id_sales_people = Column(String(50), nullable=True)
    id_event = Column(String(100), nullable=True)
    created_time = Column(DateTime, nullable=True)
    modified_time = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProspectData(id={self.id}, dealer_id={self.dealer_id}, id_prospect={self.id_prospect})>"