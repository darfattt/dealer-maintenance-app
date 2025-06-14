from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Date, Time, Integer, Text, ForeignKey, Float, JSON, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")

# Create engine with connection pooling and better error handling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "options": "-csearch_path=dealer_integration,public"
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Dealer(Base):
    __tablename__ = "dealers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), unique=True, nullable=False, index=True)
    dealer_name = Column(String(255), nullable=False)
    api_key = Column(String(255))
    api_token = Column(String(255))
    secret_key = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fetch_configurations = relationship("FetchConfiguration", back_populates="dealer")
    prospect_data = relationship("ProspectData", back_populates="dealer")
    fetch_logs = relationship("FetchLog", back_populates="dealer")
    pkb_data = relationship("PKBData", back_populates="dealer")
    parts_inbound_data = relationship("PartsInboundData", back_populates="dealer")
    leasing_data = relationship("LeasingData", back_populates="dealer")
    document_handling_data = relationship("DocumentHandlingData", back_populates="dealer")
    unit_inbound_data = relationship("UnitInboundData", back_populates="dealer")
    delivery_process_data = relationship("DeliveryProcessData", back_populates="dealer")
    billing_process_data = relationship("BillingProcessData", back_populates="dealer")
    unit_invoice_data = relationship("UnitInvoiceData", back_populates="dealer")
    parts_sales_data = relationship("PartsSalesData", back_populates="dealer")
    dp_hlo_data = relationship("DPHLOData", back_populates="dealer")
    workshop_invoice_data = relationship("WorkshopInvoiceData", back_populates="dealer")
    unpaid_hlo_data = relationship("UnpaidHLOData", back_populates="dealer")
    parts_invoice_data = relationship("PartsInvoiceData", back_populates="dealer")

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

class PKBData(Base):
    __tablename__ = "pkb_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
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

    # Relationships
    dealer = relationship("Dealer", back_populates="pkb_data")
    services = relationship("PKBService", back_populates="pkb_data", cascade="all, delete-orphan")
    parts = relationship("PKBPart", back_populates="pkb_data", cascade="all, delete-orphan")

class PKBService(Base):
    __tablename__ = "pkb_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pkb_data_id = Column(UUID(as_uuid=True), ForeignKey("pkb_data.id", ondelete="CASCADE"))
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

    # Relationships
    pkb_data = relationship("PKBData", back_populates="services")

class PKBPart(Base):
    __tablename__ = "pkb_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pkb_data_id = Column(UUID(as_uuid=True), ForeignKey("pkb_data.id", ondelete="CASCADE"))
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

    # Relationships
    pkb_data = relationship("PKBData", back_populates="parts")

class PartsInboundData(Base):
    __tablename__ = "parts_inbound_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_penerimaan = Column(String(100), nullable=False, index=True)
    tgl_penerimaan = Column(String(20))
    no_shipping_list = Column(String(100))
    created_time = Column(String(50))
    modified_time = Column(String(50))
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="parts_inbound_data")
    po_items = relationship("PartsInboundPO", back_populates="parts_inbound_data", cascade="all, delete-orphan")

class PartsInboundPO(Base):
    __tablename__ = "parts_inbound_po"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parts_inbound_data_id = Column(UUID(as_uuid=True), ForeignKey("parts_inbound_data.id", ondelete="CASCADE"))
    no_po = Column(String(100))
    jenis_order = Column(String(10))
    id_warehouse = Column(String(50))
    parts_number = Column(String(100))
    kuantitas = Column(Integer)
    uom = Column(String(20))
    created_time = Column(String(50))
    modified_time = Column(String(50))

    # Relationships
    parts_inbound_data = relationship("PartsInboundData", back_populates="po_items")

class LeasingData(Base):
    __tablename__ = "leasing_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    id_dokumen_pengajuan = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True, index=True)
    jumlah_dp = Column(Numeric(15, 2), nullable=True)
    tenor = Column(Integer, nullable=True)
    jumlah_cicilan = Column(Numeric(15, 2), nullable=True)
    tanggal_pengajuan = Column(String(50), nullable=True)
    id_finance_company = Column(String(100), nullable=True)
    nama_finance_company = Column(String(255), nullable=True)
    id_po_finance_company = Column(String(100), nullable=True)
    tanggal_pembuatan_po = Column(String(50), nullable=True)
    tanggal_pengiriman_po_finance_company = Column(String(50), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="leasing_data")


class DocumentHandlingData(Base):
    __tablename__ = "document_handling_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    id_so = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True, index=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="document_handling_data")
    units = relationship("DocumentHandlingUnit", back_populates="document_handling_data", cascade="all, delete-orphan")


class DocumentHandlingUnit(Base):
    __tablename__ = "document_handling_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_handling_data_id = Column(UUID(as_uuid=True), ForeignKey("document_handling_data.id"), nullable=False)
    nomor_rangka = Column(String(100), nullable=True, index=True)
    nomor_faktur_stnk = Column(String(100), nullable=True)
    tanggal_pengajuan_stnk_ke_biro = Column(String(50), nullable=True)
    status_faktur_stnk = Column(String(10), nullable=True)
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


class UnitInboundData(Base):
    """Unit Inbound data from Purchase Order"""
    __tablename__ = "unit_inbound_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_shipping_list = Column(String(100), nullable=True, index=True)
    tanggal_terima = Column(String(50), nullable=True)
    main_dealer_id = Column(String(10), nullable=True)
    no_invoice = Column(String(100), nullable=True, index=True)
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


class DeliveryProcessData(Base):
    """Delivery process data from BAST API"""
    __tablename__ = "delivery_process_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    delivery_document_id = Column(String(100), nullable=True, index=True)
    tanggal_pengiriman = Column(String(50), nullable=True)
    id_driver = Column(String(100), nullable=True)
    status_delivery_document = Column(String(10), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="delivery_process_data")
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


class BillingProcessData(Base):
    """Billing process data from INV1 API"""
    __tablename__ = "billing_process_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    id_invoice = Column(String(100), nullable=True, index=True)
    id_spk = Column(String(100), nullable=True, index=True)
    id_customer = Column(String(100), nullable=True, index=True)
    amount = Column(Numeric(15, 2), nullable=True)
    tipe_pembayaran = Column(String(10), nullable=True)
    cara_bayar = Column(String(10), nullable=True)
    status = Column(String(10), nullable=True)
    note = Column(Text, nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="billing_process_data")


class UnitInvoiceData(Base):
    """Unit invoice data from MDINVH1 API"""
    __tablename__ = "unit_invoice_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_invoice = Column(String(100), nullable=True, index=True)
    tanggal_invoice = Column(String(50), nullable=True)
    tanggal_jatuh_tempo = Column(String(50), nullable=True)
    main_dealer_id = Column(String(10), nullable=True)
    total_harga_sebelum_diskon = Column(Numeric(15, 2), nullable=True)
    total_diskon_per_unit = Column(Numeric(15, 2), nullable=True)
    potongan_per_invoice = Column(Numeric(15, 2), nullable=True)
    total_ppn = Column(Numeric(15, 2), nullable=True)
    total_harga = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="unit_invoice_data")
    units = relationship("UnitInvoiceUnit", back_populates="unit_invoice_data", cascade="all, delete-orphan")


class UnitInvoiceUnit(Base):
    """Individual units for unit invoice data"""
    __tablename__ = "unit_invoice_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_invoice_data_id = Column(UUID(as_uuid=True), ForeignKey("unit_invoice_data.id"), nullable=False)
    kode_tipe_unit = Column(String(50), nullable=True)
    kode_warna = Column(String(10), nullable=True)
    kuantitas = Column(Integer, nullable=True)
    no_mesin = Column(String(100), nullable=True)
    no_rangka = Column(String(100), nullable=True)
    harga_satuan_sebelum_diskon = Column(Numeric(15, 2), nullable=True)
    diskon_per_unit = Column(Numeric(15, 2), nullable=True)
    po_id = Column(String(100), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    unit_invoice_data = relationship("UnitInvoiceData", back_populates="units")


class PartsSalesData(Base):
    """Parts sales data from PRSL API"""
    __tablename__ = "parts_sales_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_so = Column(String(100), nullable=True, index=True)
    tgl_so = Column(String(50), nullable=True)
    id_customer = Column(String(100), nullable=True, index=True)
    nama_customer = Column(String(200), nullable=True)
    disc_so = Column(Numeric(15, 2), nullable=True)
    total_harga_so = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="parts_sales_data")
    parts = relationship("PartsSalesPart", back_populates="parts_sales_data", cascade="all, delete-orphan")


class PartsSalesPart(Base):
    """Individual parts for parts sales data"""
    __tablename__ = "parts_sales_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parts_sales_data_id = Column(UUID(as_uuid=True), ForeignKey("parts_sales_data.id"), nullable=False)
    parts_number = Column(String(100), nullable=True, index=True)
    kuantitas = Column(Integer, nullable=True)
    harga_parts = Column(Numeric(15, 2), nullable=True)
    promo_id_parts = Column(String(100), nullable=True)
    disc_amount = Column(Numeric(15, 2), nullable=True)
    disc_percentage = Column(String(20), nullable=True)
    ppn = Column(Numeric(15, 2), nullable=True)
    total_harga_parts = Column(Numeric(15, 2), nullable=True)
    uang_muka = Column(Numeric(15, 2), nullable=True)
    booking_id_reference = Column(String(100), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    parts_sales_data = relationship("PartsSalesData", back_populates="parts")


class DPHLOData(Base):
    """DP HLO data from DPHLO API"""
    __tablename__ = "dp_hlo_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_invoice_uang_jaminan = Column(String(100), nullable=True, index=True)
    id_hlo_document = Column(String(100), nullable=True, index=True)
    tanggal_pemesanan_hlo = Column(String(50), nullable=True)
    no_work_order = Column(String(100), nullable=True, index=True)
    id_customer = Column(String(100), nullable=True, index=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="dp_hlo_data")
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


class WorkshopInvoiceData(Base):
    """Workshop Invoice data from INV2 API (NJB & NSC)"""
    __tablename__ = "workshop_invoice_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
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

    # Relationships
    dealer = relationship("Dealer", back_populates="workshop_invoice_data")
    njb_services = relationship("WorkshopInvoiceNJB", back_populates="workshop_invoice_data", cascade="all, delete-orphan")
    nsc_parts = relationship("WorkshopInvoiceNSC", back_populates="workshop_invoice_data", cascade="all, delete-orphan")


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
    workshop_invoice_data = relationship("WorkshopInvoiceData", back_populates="njb_services")


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
    workshop_invoice_data = relationship("WorkshopInvoiceData", back_populates="nsc_parts")


class UnpaidHLOData(Base):
    """Unpaid HLO data from UNPAIDHLO API"""
    __tablename__ = "unpaid_hlo_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    id_hlo_document = Column(String(100), nullable=True, index=True)
    tanggal_pemesanan_hlo = Column(String(50), nullable=True)
    no_work_order = Column(String(100), nullable=True, index=True)
    no_buku_claim_c2 = Column(String(100), nullable=True)
    no_ktp = Column(String(100), nullable=True, index=True)
    nama_customer = Column(String(200), nullable=True)
    alamat = Column(Text, nullable=True)
    kode_propinsi = Column(String(10), nullable=True)
    kode_kota = Column(String(10), nullable=True)
    kode_kecamatan = Column(String(20), nullable=True)
    kode_kelurahan = Column(String(20), nullable=True)
    kode_pos = Column(String(10), nullable=True)
    no_kontak = Column(String(50), nullable=True)
    kode_tipe_unit = Column(String(50), nullable=True)
    tahun_motor = Column(String(10), nullable=True)
    no_mesin = Column(String(100), nullable=True, index=True)
    no_rangka = Column(String(100), nullable=True, index=True)
    flag_numbering = Column(String(10), nullable=True)
    vehicle_off_road = Column(String(10), nullable=True)
    job_return = Column(String(10), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="unpaid_hlo_data")
    parts = relationship("UnpaidHLOPart", back_populates="unpaid_hlo_data", cascade="all, delete-orphan")


class UnpaidHLOPart(Base):
    """Parts for unpaid HLO data"""
    __tablename__ = "unpaid_hlo_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unpaid_hlo_data_id = Column(UUID(as_uuid=True), ForeignKey("unpaid_hlo_data.id"), nullable=False)
    parts_number = Column(String(100), nullable=True, index=True)
    kuantitas = Column(Integer, nullable=True)
    harga_parts = Column(Numeric(15, 2), nullable=True)
    total_harga_parts = Column(Numeric(15, 2), nullable=True)
    uang_muka = Column(Numeric(15, 2), nullable=True)
    sisa_bayar = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    unpaid_hlo_data = relationship("UnpaidHLOData", back_populates="parts")


class PartsInvoiceData(Base):
    """Parts Invoice data from MDINVH3 API"""
    __tablename__ = "parts_invoice_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    no_invoice = Column(String(100), nullable=True, index=True)
    tgl_invoice = Column(String(50), nullable=True)
    tgl_jatuh_tempo = Column(String(50), nullable=True)
    main_dealer_id = Column(String(10), nullable=True)
    total_harga_sebelum_diskon = Column(Numeric(15, 2), nullable=True)
    total_diskon_per_parts_number = Column(Numeric(15, 2), nullable=True)
    potongan_per_invoice = Column(Numeric(15, 2), nullable=True)
    total_ppn = Column(Numeric(15, 2), nullable=True)
    total_harga = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dealer = relationship("Dealer", back_populates="parts_invoice_data")
    parts = relationship("PartsInvoicePart", back_populates="parts_invoice_data", cascade="all, delete-orphan")


class PartsInvoicePart(Base):
    """Parts for parts invoice data"""
    __tablename__ = "parts_invoice_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parts_invoice_data_id = Column(UUID(as_uuid=True), ForeignKey("parts_invoice_data.id"), nullable=False)
    no_po = Column(String(100), nullable=True, index=True)
    jenis_order = Column(String(10), nullable=True)
    parts_number = Column(String(100), nullable=True, index=True)
    kuantitas = Column(Integer, nullable=True)
    uom = Column(String(20), nullable=True)
    harga_satuan_sebelum_diskon = Column(Numeric(15, 2), nullable=True)
    diskon_per_parts_number = Column(Numeric(15, 2), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)

    # Relationships
    parts_invoice_data = relationship("PartsInvoiceData", back_populates="parts")


class APIConfiguration(Base):
    __tablename__ = "api_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_name = Column(String(100), unique=True, nullable=False, index=True)
    base_url = Column(String(500), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    timeout_seconds = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
