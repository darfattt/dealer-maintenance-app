"""
Delivery process data models
"""

import os
import sys
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.database import Base


class DeliveryProcessData(Base):
    """Delivery process data from BAST API"""
    __tablename__ = "delivery_process_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), nullable=False, index=True)
    delivery_document_id = Column(String(100), nullable=True, index=True)
    tanggal_pengiriman = Column(String(50), nullable=True)
    id_driver = Column(String(100), nullable=True)
    status_delivery_document = Column(String(10), nullable=True, index=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    details = relationship("DeliveryProcessDetail", back_populates="delivery_process_data", cascade="all, delete-orphan")


class DeliveryProcessDetail(Base):
    """Individual delivery details for delivery process data"""
    __tablename__ = "delivery_process_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_process_data_id = Column(UUID(as_uuid=True), ForeignKey("delivery_process_data.id"), nullable=False)
    no_so = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True, index=True)
    no_mesin = Column(String(100), nullable=True, index=True)
    no_rangka = Column(String(100), nullable=True, index=True)
    id_customer = Column(String(100), nullable=True, index=True)
    waktu_pengiriman = Column(String(50), nullable=True)
    checklist_kelengkapan = Column(Text, nullable=True)
    lokasi_pengiriman = Column(Text, nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    nama_penerima = Column(String(200), nullable=True)
    no_kontak_penerima = Column(String(50), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    delivery_process_data = relationship("DeliveryProcessData", back_populates="details")
