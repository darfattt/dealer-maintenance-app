from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Date, Time, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Dealer(Base):
    __tablename__ = "dealers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), unique=True, nullable=False, index=True)
    dealer_name = Column(String(255), nullable=False)
    api_key = Column(String(255))
    api_token = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fetch_configurations = relationship("FetchConfiguration", back_populates="dealer")
    prospect_data = relationship("ProspectData", back_populates="dealer")
    fetch_logs = relationship("FetchLog", back_populates="dealer")

class FetchConfiguration(Base):
    __tablename__ = "fetch_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    schedule_type = Column(String(20), nullable=False)  # hourly, daily, custom
    cron_expression = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_fetch_at = Column(DateTime)
    next_fetch_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dealer = relationship("Dealer", back_populates="fetch_configurations")

class ProspectData(Base):
    __tablename__ = "prospect_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    id_prospect = Column(String(255))
    sumber_prospect = Column(String(10))
    tanggal_prospect = Column(Date)
    tagging_prospect = Column(String(10))
    nama_lengkap = Column(String(255))
    no_kontak = Column(String(50))
    no_ktp = Column(String(50))
    alamat = Column(Text)
    kode_propinsi = Column(String(10))
    kode_kota = Column(String(10))
    kode_kecamatan = Column(String(10))
    kode_kelurahan = Column(String(10))
    kode_pos = Column(String(10))
    latitude = Column(String(20))
    longitude = Column(String(20))
    alamat_kantor = Column(Text)
    kode_propinsi_kantor = Column(String(10))
    kode_kota_kantor = Column(String(10))
    kode_kecamatan_kantor = Column(String(10))
    kode_kelurahan_kantor = Column(String(10))
    kode_pos_kantor = Column(String(10))
    kode_pekerjaan = Column(String(10))
    no_kontak_kantor = Column(String(50))
    tanggal_appointment = Column(Date)
    waktu_appointment = Column(Time)
    metode_follow_up = Column(String(10))
    test_ride_preference = Column(String(10))
    status_follow_up_prospecting = Column(String(10))
    status_prospect = Column(String(10))
    id_sales_people = Column(String(50))
    id_event = Column(String(100))
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dealer = relationship("Dealer", back_populates="prospect_data")
    units = relationship("ProspectUnit", back_populates="prospect_data", cascade="all, delete-orphan")

class ProspectUnit(Base):
    __tablename__ = "prospect_units"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_data_id = Column(UUID(as_uuid=True), ForeignKey("prospect_data.id", ondelete="CASCADE"))
    kode_tipe_unit = Column(String(20))
    sales_program_id = Column(Text)
    created_time = Column(DateTime)
    modified_time = Column(DateTime)
    
    # Relationships
    prospect_data = relationship("ProspectData", back_populates="units")

class FetchLog(Base):
    __tablename__ = "fetch_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    fetch_type = Column(String(50))
    status = Column(String(20))  # success, failed, partial
    records_fetched = Column(Integer, default=0)
    error_message = Column(Text)
    fetch_duration_seconds = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dealer = relationship("Dealer", back_populates="fetch_logs")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
