import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, and_, or_, extract
from sqlalchemy.orm import sessionmaker, Session
from database import Dealer, ProspectData, ProspectUnit, FetchLog, PKBData, PKBService, PKBPart, PartsInboundData, PartsInboundPO, LeasingData, DocumentHandlingData, DocumentHandlingUnit, UnitInboundData, UnitInboundUnit, DeliveryProcessData, DeliveryProcessDetail, BillingProcessData, UnitInvoiceData, UnitInvoiceUnit, PartsSalesData, PartsSalesPart, DPHLOData, DPHLOPart, WorkshopInvoiceData, WorkshopInvoiceNJB, WorkshopInvoiceNSC, UnpaidHLOData, UnpaidHLOPart, PartsInvoiceData, PartsInvoicePart

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")

# Create database connection
@st.cache_resource
def get_database_connection():
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "options": "-csearch_path=dealer_integration,public"
        },
        pool_pre_ping=True,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

# Page configuration
st.set_page_config(
    page_title="Dealer Dashboard Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .chart-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_dealers_from_db():
    """Fetch dealers directly from database"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        dealers = db.query(Dealer).filter(Dealer.is_active == True).all()
        return [{"dealer_id": d.dealer_id, "dealer_name": d.dealer_name} for d in dealers]
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_prospect_analytics(dealer_id):
    """Get prospect analytics directly from database"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Daily counts
        daily_counts = db.query(
            ProspectData.tanggal_prospect,
            func.count(ProspectData.id).label('count')
        ).filter(
            ProspectData.dealer_id == dealer_id,
            ProspectData.tanggal_prospect.isnot(None)
        ).group_by(
            ProspectData.tanggal_prospect
        ).order_by(
            ProspectData.tanggal_prospect
        ).all()
        
        # Status distribution
        status_counts = db.query(
            ProspectData.status_prospect,
            func.count(ProspectData.id).label('count')
        ).filter(
            ProspectData.dealer_id == dealer_id,
            ProspectData.status_prospect.isnot(None)
        ).group_by(
            ProspectData.status_prospect
        ).all()
        
        # Unit type distribution
        unit_counts = db.query(
            ProspectUnit.kode_tipe_unit,
            func.count(ProspectUnit.id).label('count')
        ).join(
            ProspectData, ProspectUnit.prospect_data_id == ProspectData.id
        ).filter(
            ProspectData.dealer_id == dealer_id,
            ProspectUnit.kode_tipe_unit.isnot(None)
        ).group_by(
            ProspectUnit.kode_tipe_unit
        ).all()
        
        # Total counts
        total_prospects = db.query(func.count(ProspectData.id)).filter(
            ProspectData.dealer_id == dealer_id
        ).scalar()
        
        # Recent prospects (last 7 days)
        recent_date = date.today() - timedelta(days=7)
        recent_prospects = db.query(func.count(ProspectData.id)).filter(
            ProspectData.dealer_id == dealer_id,
            ProspectData.tanggal_prospect >= recent_date
        ).scalar()
        
        # Active prospects (status 1 and 2)
        active_prospects = db.query(func.count(ProspectData.id)).filter(
            ProspectData.dealer_id == dealer_id,
            ProspectData.status_prospect.in_(['1', '2'])
        ).scalar()
        
        return {
            "total_prospects": total_prospects or 0,
            "recent_prospects": recent_prospects or 0,
            "active_prospects": active_prospects or 0,
            "daily_counts": [{"date": str(row.tanggal_prospect), "count": row.count} for row in daily_counts],
            "status_distribution": [{"status": row.status_prospect, "count": row.count} for row in status_counts],
            "unit_distribution": [{"unit": row.kode_tipe_unit, "count": row.count} for row in unit_counts]
        }
    finally:
        db.close()

def format_status_display(status):
    """Format status for display with appropriate icons"""
    if not status:
        return "❓ Unknown"

    status_lower = status.lower()
    if status_lower == "success":
        return "✅ Success"
    elif status_lower == "failed":
        return "❌ Failed"
    elif status_lower == "partial":
        return "⚠️ Partial"
    elif status_lower == "completed":
        return "✅ Completed"
    elif status_lower == "error":
        return "❌ Error"
    elif status_lower == "running":
        return "🔄 Running"
    elif status_lower == "pending":
        return "⏳ Pending"
    else:
        return f"❓ {status.title()}"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_recent_fetch_logs(dealer_id, limit=10):
    """Get recent fetch logs from database"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        logs = db.query(FetchLog).filter(
            FetchLog.dealer_id == dealer_id
        ).order_by(
            FetchLog.completed_at.desc()
        ).limit(limit).all()

        return [{
            "status": log.status,
            "records_fetched": log.records_fetched,
            "duration": log.fetch_duration_seconds,
            "completed_at": log.completed_at.strftime('%Y-%m-%d %H:%M:%S') if log.completed_at else None
        } for log in logs]
    finally:
        db.close()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_dashboard_analytics(from_date, to_date):
    """Get dashboard analytics data for charts"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Convert dates to datetime for comparison
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        # Get fetch logs within date range
        logs = db.query(FetchLog).filter(
            FetchLog.completed_at >= from_datetime,
            FetchLog.completed_at <= to_datetime
        ).all()

        # Prepare data for charts
        chart_data = []
        for log in logs:
            if log.completed_at:
                # Calculate week start date
                week_start = log.completed_at.date() - timedelta(days=log.completed_at.weekday())

                chart_data.append({
                    "dealer_id": log.dealer_id,
                    "dealer_name": log.dealer.dealer_name if log.dealer else "Unknown",
                    "fetch_type": log.fetch_type,
                    "status": log.status,
                    "records_fetched": log.records_fetched or 0,
                    "duration": log.fetch_duration_seconds or 0,
                    "completed_at": log.completed_at,
                    "date": log.completed_at.date(),
                    "week_start": week_start,
                    "week_label": f"Week of {week_start.strftime('%Y-%m-%d')}"
                })

        return chart_data
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_prospect_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get prospect data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(ProspectData).filter(ProspectData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            search_filter = or_(
                ProspectData.nama_lengkap.ilike(f"%{search_term}%"),
                ProspectData.no_kontak.ilike(f"%{search_term}%"),
                ProspectData.id_prospect.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        prospects = query.order_by(ProspectData.tanggal_prospect.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries
        data = []
        for prospect in prospects:
            data.append({
                "ID Prospect": prospect.id_prospect,
                "Nama Lengkap": prospect.nama_lengkap,
                "No Kontak": prospect.no_kontak,
                "Tanggal Prospect": prospect.tanggal_prospect.strftime('%Y-%m-%d') if prospect.tanggal_prospect else None,
                "Status": prospect.status_prospect,
                "Sumber": prospect.sumber_prospect,
                "Alamat": prospect.alamat[:50] + "..." if prospect.alamat and len(prospect.alamat) > 50 else prospect.alamat,
                "Sales People": prospect.id_sales_people,
                "Created": prospect.created_time.strftime('%Y-%m-%d %H:%M') if prospect.created_time else None
            })

        return data, total_count
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_pkb_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get PKB data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(PKBData).filter(PKBData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            search_filter = or_(
                PKBData.no_work_order.ilike(f"%{search_term}%"),
                PKBData.nama_pemilik.ilike(f"%{search_term}%"),
                PKBData.no_polisi.ilike(f"%{search_term}%"),
                PKBData.no_rangka.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        pkb_records = query.order_by(PKBData.tanggal_servis.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries
        data = []
        for pkb in pkb_records:
            data.append({
                "No Work Order": pkb.no_work_order,
                "Tanggal Servis": pkb.tanggal_servis,
                "Nama Pemilik": pkb.nama_pemilik,
                "No Polisi": pkb.no_polisi,
                "No Rangka": pkb.no_rangka,
                "Tipe Unit": pkb.kode_tipe_unit,
                "KM Terakhir": pkb.km_terakhir,
                "Total Biaya": f"Rp {pkb.total_biaya_service:,.0f}" if pkb.total_biaya_service else "N/A",
                "Status": pkb.status_work_order,
                "Created": pkb.created_time
            })

        return data, total_count
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_parts_inbound_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Parts Inbound data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(PartsInboundData).filter(PartsInboundData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            search_filter = or_(
                PartsInboundData.no_penerimaan.ilike(f"%{search_term}%"),
                PartsInboundData.no_shipping_list.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        parts_inbound_records = query.order_by(PartsInboundData.tgl_penerimaan.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with PO details
        data = []
        for parts_inbound in parts_inbound_records:
            # Get PO items count
            po_count = len(parts_inbound.po_items) if parts_inbound.po_items else 0

            # Get sample PO numbers (first 3)
            po_numbers = []
            if parts_inbound.po_items:
                po_numbers = [po.no_po for po in parts_inbound.po_items[:3]]

            po_display = ", ".join(po_numbers)
            if po_count > 3:
                po_display += f" (+{po_count - 3} more)"

            data.append({
                "No Penerimaan": parts_inbound.no_penerimaan,
                "Tanggal Penerimaan": parts_inbound.tgl_penerimaan,
                "No Shipping List": parts_inbound.no_shipping_list,
                "PO Numbers": po_display if po_display else "No PO",
                "PO Count": po_count,
                "Created": parts_inbound.created_time,
                "Fetched": parts_inbound.fetched_at.strftime('%Y-%m-%d %H:%M') if parts_inbound.fetched_at else None
            })

        return data, total_count
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_leasing_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Leasing data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(LeasingData).filter(LeasingData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            search_filter = or_(
                LeasingData.id_dokumen_pengajuan.ilike(f"%{search_term}%"),
                LeasingData.id_spk.ilike(f"%{search_term}%"),
                LeasingData.nama_finance_company.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        leasing_records = query.order_by(LeasingData.tanggal_pengajuan.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries
        data = []
        for leasing in leasing_records:
            data.append({
                "ID Dokumen": leasing.id_dokumen_pengajuan,
                "ID SPK": leasing.id_spk,
                "Finance Company": leasing.nama_finance_company,
                "Jumlah DP": f"Rp {leasing.jumlah_dp:,.0f}" if leasing.jumlah_dp else "N/A",
                "Tenor": f"{leasing.tenor} bulan" if leasing.tenor else "N/A",
                "Cicilan": f"Rp {leasing.jumlah_cicilan:,.0f}" if leasing.jumlah_cicilan else "N/A",
                "Tanggal Pengajuan": leasing.tanggal_pengajuan,
                "ID PO Finance": leasing.id_po_finance_company,
                "Tanggal PO": leasing.tanggal_pembuatan_po,
                "Created": leasing.created_time,
                "Fetched": leasing.fetched_at.strftime('%Y-%m-%d %H:%M') if leasing.fetched_at else None
            })

        return data, total_count
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_document_handling_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Document Handling data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(DocumentHandlingData).filter(DocumentHandlingData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            # Join with units to search in chassis numbers
            query = query.join(DocumentHandlingUnit, DocumentHandlingData.id == DocumentHandlingUnit.document_handling_data_id, isouter=True)
            search_filter = or_(
                DocumentHandlingData.id_so.ilike(f"%{search_term}%"),
                DocumentHandlingData.id_spk.ilike(f"%{search_term}%"),
                DocumentHandlingUnit.nomor_rangka.ilike(f"%{search_term}%"),
                DocumentHandlingUnit.plat_nomor.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter).distinct()

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        document_records = query.order_by(DocumentHandlingData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with unit details
        data = []
        for doc in document_records:
            # Get units for this document
            units = db.query(DocumentHandlingUnit).filter(
                DocumentHandlingUnit.document_handling_data_id == doc.id
            ).all()

            # Get first unit for main display
            first_unit = units[0] if units else None

            data.append({
                "id": str(doc.id),
                "dealer_id": doc.dealer_id,
                "dealer_name": doc.dealer.dealer_name if doc.dealer else "Unknown",
                "id_so": doc.id_so,
                "id_spk": doc.id_spk,
                "created_time": doc.created_time,
                "modified_time": doc.modified_time,
                "fetched_at": doc.fetched_at.isoformat() if doc.fetched_at else None,
                "unit_count": len(units),
                "units": [
                    {
                        "id": str(unit.id),
                        "nomor_rangka": unit.nomor_rangka,
                        "nomor_faktur_stnk": unit.nomor_faktur_stnk,
                        "status_faktur_stnk": unit.status_faktur_stnk,
                        "nomor_stnk": unit.nomor_stnk,
                        "plat_nomor": unit.plat_nomor,
                        "nomor_bpkb": unit.nomor_bpkb,
                        "nama_penerima_bpkb": unit.nama_penerima_bpkb,
                        "nama_penerima_stnk": unit.nama_penerima_stnk,
                        "tanggal_terima_stnk_oleh_konsumen": unit.tanggal_terima_stnk_oleh_konsumen,
                        "tanggal_terima_bpkb_oleh_konsumen": unit.tanggal_terima_bpkb_oleh_konsumen
                    } for unit in units
                ]
            })

        return data, total_count
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_unit_inbound_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Unit Inbound data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(UnitInboundData).filter(UnitInboundData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            # Join with units to search in chassis numbers and engine numbers
            query = query.join(UnitInboundUnit, UnitInboundData.id == UnitInboundUnit.unit_inbound_data_id, isouter=True)
            search_filter = or_(
                UnitInboundData.no_shipping_list.ilike(f"%{search_term}%"),
                UnitInboundData.no_invoice.ilike(f"%{search_term}%"),
                UnitInboundUnit.no_rangka.ilike(f"%{search_term}%"),
                UnitInboundUnit.no_mesin.ilike(f"%{search_term}%"),
                UnitInboundUnit.po_id.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter).distinct()

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        shipment_records = query.order_by(UnitInboundData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with unit details
        data = []
        for shipment in shipment_records:
            # Get units for this shipment
            units = db.query(UnitInboundUnit).filter(
                UnitInboundUnit.unit_inbound_data_id == shipment.id
            ).all()

            # Get first unit for main display
            first_unit = units[0] if units else None

            data.append({
                "id": str(shipment.id),
                "dealer_id": shipment.dealer_id,
                "dealer_name": shipment.dealer.dealer_name if shipment.dealer else "Unknown",
                "no_shipping_list": shipment.no_shipping_list,
                "tanggal_terima": shipment.tanggal_terima,
                "main_dealer_id": shipment.main_dealer_id,
                "no_invoice": shipment.no_invoice,
                "status_shipping_list": shipment.status_shipping_list,
                "created_time": shipment.created_time,
                "modified_time": shipment.modified_time,
                "fetched_at": shipment.fetched_at.isoformat() if shipment.fetched_at else None,
                "unit_count": len(units),
                "units": [
                    {
                        "id": str(unit.id),
                        "kode_tipe_unit": unit.kode_tipe_unit,
                        "kode_warna": unit.kode_warna,
                        "kuantitas_terkirim": unit.kuantitas_terkirim,
                        "kuantitas_diterima": unit.kuantitas_diterima,
                        "no_mesin": unit.no_mesin,
                        "no_rangka": unit.no_rangka,
                        "status_rfs": unit.status_rfs,
                        "po_id": unit.po_id,
                        "kelengkapan_unit": unit.kelengkapan_unit,
                        "no_goods_receipt": unit.no_goods_receipt,
                        "doc_nrfs_id": unit.doc_nrfs_id
                    } for unit in units
                ]
            })

        return data, total_count
    finally:
        db.close()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_delivery_process_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Delivery Process data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(DeliveryProcessData).filter(DeliveryProcessData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            # Join with details to search in SO, SPK, customer, etc.
            query = query.join(DeliveryProcessDetail, DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id, isouter=True)
            search_filter = or_(
                DeliveryProcessData.delivery_document_id.ilike(f"%{search_term}%"),
                DeliveryProcessData.id_driver.ilike(f"%{search_term}%"),
                DeliveryProcessDetail.no_so.ilike(f"%{search_term}%"),
                DeliveryProcessDetail.id_spk.ilike(f"%{search_term}%"),
                DeliveryProcessDetail.id_customer.ilike(f"%{search_term}%"),
                DeliveryProcessDetail.nama_penerima.ilike(f"%{search_term}%"),
                DeliveryProcessDetail.no_rangka.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter).distinct()

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        delivery_records = query.order_by(DeliveryProcessData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with delivery details
        data = []
        for delivery in delivery_records:
            # Get details for this delivery
            details = db.query(DeliveryProcessDetail).filter(
                DeliveryProcessDetail.delivery_process_data_id == delivery.id
            ).all()

            # Get first detail for main display
            first_detail = details[0] if details else None

            data.append({
                "id": str(delivery.id),
                "dealer_id": delivery.dealer_id,
                "dealer_name": delivery.dealer.dealer_name if delivery.dealer else "Unknown",
                "delivery_document_id": delivery.delivery_document_id,
                "tanggal_pengiriman": delivery.tanggal_pengiriman,
                "id_driver": delivery.id_driver,
                "status_delivery_document": delivery.status_delivery_document,
                "created_time": delivery.created_time,
                "modified_time": delivery.modified_time,
                "fetched_at": delivery.fetched_at.isoformat() if delivery.fetched_at else None,
                "detail_count": len(details),
                "details": [
                    {
                        "id": str(detail.id),
                        "no_so": detail.no_so,
                        "id_spk": detail.id_spk,
                        "no_mesin": detail.no_mesin,
                        "no_rangka": detail.no_rangka,
                        "id_customer": detail.id_customer,
                        "waktu_pengiriman": detail.waktu_pengiriman,
                        "checklist_kelengkapan": detail.checklist_kelengkapan,
                        "lokasi_pengiriman": detail.lokasi_pengiriman,
                        "latitude": detail.latitude,
                        "longitude": detail.longitude,
                        "nama_penerima": detail.nama_penerima,
                        "no_kontak_penerima": detail.no_kontak_penerima
                    } for detail in details
                ]
            })

        return data, total_count
    finally:
        db.close()

# Main app
st.markdown('<div class="main-header">📊 Dealer Analytics Dashboard</div>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("📊 Analytics Dashboard")
st.sidebar.markdown("---")

# Menu navigation
menu_options = {
    "🏠 Home": "home",
    "📋 Fetch Logs": "fetch_logs",
    "👥 Prospect Data": "prospect",
    "🔧 PKB Data": "pkb",
    "📦 Parts Inbound": "parts_inbound",
    "💰 Leasing Data": "leasing",
    "📄 Document Handling": "doch_read",
    "🚚 Unit Inbound": "uinb_read",
    "🚛 Delivery Process": "bast_read",
    "💳 Billing Process": "inv1_read",
    "📋 Unit Invoice": "mdinvh1_read",
    "🛒 Parts Sales": "prsl_read",
    "🔧 DP HLO": "dphlo_read",
    "🔨 Workshop Invoice": "inv2_read",
    "📋 Unpaid HLO": "unpaidhlo_read",
    "📄 Parts Invoice": "mdinvh3_read",
    "📋 SPK Dealing Process": "spk_read"
}

selected_menu = st.sidebar.selectbox(
    "Navigation",
    options=list(menu_options.keys()),
    index=0
)

current_page = menu_options[selected_menu]

st.sidebar.markdown("---")

# Get dealers
dealers = get_dealers_from_db()

if not dealers:
    st.error("❌ No active dealers found. Please add dealers in the Admin Panel.")
    st.info("🔗 Access Admin Panel: http://localhost:8502")
    st.stop()

# Dealer selection
selected_dealer_id = st.sidebar.selectbox(
    "Select Dealer",
    options=[d['dealer_id'] for d in dealers],
    format_func=lambda x: f"{x} - {next(d['dealer_name'] for d in dealers if d['dealer_id'] == x)}"
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("🔗 **Admin Panel**: http://localhost:8502")

def render_home_page():
    """Render the new home page with dashboard charts and date filters"""
    st.title("🏠 Dashboard Analytics")
    st.markdown("**System-wide analytics and insights**")

    # Date filter controls (independent of dealer filter)
    st.subheader("📅 Date Range Filter")
    col1, col2 = st.columns(2)

    with col1:
        from_date = st.date_input(
            "From Date",
            value=date.today() - timedelta(days=30),
            key="home_from_date"
        )

    with col2:
        to_date = st.date_input(
            "To Date",
            value=date.today(),
            key="home_to_date"
        )

    # Validate date range
    if from_date > to_date:
        st.error("From date cannot be later than to date.")
        return

    # Get dashboard analytics data
    try:
        chart_data = get_dashboard_analytics(from_date, to_date)

        if not chart_data:
            st.warning(f"No data found for the selected date range ({from_date} to {to_date}).")
            return

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(chart_data)

        # Overview metrics
        st.subheader("📊 Overview Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_jobs = len(df)
            st.metric("Total Jobs", total_jobs)

        with col2:
            # Count successful jobs (success or completed status)
            successful_jobs = len(df[df['status'].isin(['success', 'completed'])])
            st.metric("Successful Jobs", successful_jobs)

        with col3:
            total_records = df['records_fetched'].sum()
            st.metric("Total Records", f"{total_records:,}")

        with col4:
            unique_dealers = df['dealer_id'].nunique()
            st.metric("Active Dealers", unique_dealers)

        # Charts section
        st.subheader("📈 Analytics Charts")

        # Chart 1: Jobs by API Name (Fetch Type)
        st.subheader("🔧 Jobs by API Type")
        api_counts = df.groupby('fetch_type').size().reset_index(name='count')
        api_counts = api_counts.sort_values('count', ascending=False)

        fig_api = px.bar(
            api_counts,
            x='fetch_type',
            y='count',
            title='Number of Jobs by API Type',
            labels={'fetch_type': 'API Type', 'count': 'Number of Jobs'}
        )
        fig_api.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_api, use_container_width=True)

        # Chart 2: Jobs by Dealer (Pie Charts)
        st.subheader("🏢 Jobs by Dealer")

        # Aggregate data by dealer
        dealer_stats = df.groupby(['dealer_id', 'dealer_name']).agg({
            'dealer_id': 'count',  # Count of jobs
            'records_fetched': 'sum'  # Sum of records
        }).rename(columns={
            'dealer_id': 'total_jobs',
            'records_fetched': 'total_records'
        }).reset_index()

        # Sort by total jobs and get top 10 dealers
        dealer_stats = dealer_stats.sort_values('total_jobs', ascending=False).head(10)

        # Create two columns for side-by-side pie charts
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart for total jobs
            fig_jobs = px.pie(
                dealer_stats,
                values='total_jobs',
                names='dealer_name',
                title='Distribution of Jobs by Dealer (Top 10)',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_jobs.update_traces(textposition='inside', textinfo='percent+label')
            fig_jobs.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_jobs, use_container_width=True)

        with col2:
            # Pie chart for total records
            fig_records = px.pie(
                dealer_stats,
                values='total_records',
                names='dealer_name',
                title='Distribution of Records by Dealer (Top 10)',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_records.update_traces(textposition='inside', textinfo='percent+label')
            fig_records.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_records, use_container_width=True)

        # Summary table for dealer statistics
        st.subheader("📊 Dealer Statistics Summary")
        dealer_display = dealer_stats.copy()
        dealer_display['total_records'] = dealer_display['total_records'].apply(lambda x: f"{x:,}")
        dealer_display = dealer_display.rename(columns={
            'dealer_name': 'Dealer Name',
            'total_jobs': 'Total Jobs',
            'total_records': 'Total Records'
        })[['Dealer Name', 'Total Jobs', 'Total Records']]

        st.dataframe(dealer_display, use_container_width=True, hide_index=True)

        # Chart 3: Jobs by Week
        st.subheader("📅 Jobs by Week")
        weekly_counts = df.groupby('week_label').size().reset_index(name='count')
        weekly_counts = weekly_counts.sort_values('week_label')

        fig_weekly = px.line(
            weekly_counts,
            x='week_label',
            y='count',
            title='Number of Jobs by Week',
            labels={'week_label': 'Week', 'count': 'Number of Jobs'},
            markers=True
        )
        fig_weekly.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_weekly, use_container_width=True)

        # Chart 4: Success Rate by API Type
        st.subheader("✅ Success Rate by API Type")
        success_rate = df.groupby('fetch_type').agg({
            'status': lambda x: x.isin(['success', 'completed']).sum(),
            'fetch_type': 'count'
        }).rename(columns={'status': 'successful', 'fetch_type': 'total'})
        success_rate['success_rate'] = (success_rate['successful'] / success_rate['total'] * 100).round(2)
        success_rate = success_rate.reset_index()

        fig_success = px.bar(
            success_rate,
            x='fetch_type',
            y='success_rate',
            title='Success Rate by API Type (%)',
            labels={'fetch_type': 'API Type', 'success_rate': 'Success Rate (%)'}
        )
        fig_success.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_success, use_container_width=True)

        # Chart 5: Records Fetched by API Type
        st.subheader("📊 Records Fetched by API Type")
        records_by_api = df.groupby('fetch_type')['records_fetched'].sum().reset_index()
        records_by_api = records_by_api.sort_values('records_fetched', ascending=False)

        fig_records = px.bar(
            records_by_api,
            x='fetch_type',
            y='records_fetched',
            title='Total Records Fetched by API Type',
            labels={'fetch_type': 'API Type', 'records_fetched': 'Records Fetched'}
        )
        fig_records.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_records, use_container_width=True)

        # Summary table
        st.subheader("📋 Summary by API Type")
        summary_table = df.groupby('fetch_type').agg({
            'status': lambda x: x.isin(['success', 'completed']).sum(),
            'fetch_type': 'count',
            'records_fetched': 'sum',
            'duration': 'mean'
        }).rename(columns={
            'status': 'Successful Jobs',
            'fetch_type': 'Total Jobs',
            'records_fetched': 'Total Records',
            'duration': 'Avg Duration (s)'
        })
        summary_table['Success Rate (%)'] = (summary_table['Successful Jobs'] / summary_table['Total Jobs'] * 100).round(2)
        summary_table['Avg Duration (s)'] = summary_table['Avg Duration (s)'].round(2)
        summary_table = summary_table.reset_index()

        st.dataframe(summary_table, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")


def render_fetch_logs_page(dealer_id):
    """Render the fetch logs page (previously home page)"""
    st.title("📋 Fetch Logs")
    st.markdown(f"**Selected Dealer:** {dealer_id}")

    # Get database connection
    SessionLocal = get_database_connection()
    db = SessionLocal()

    try:
        # Get dealer information
        if dealer_id != "All":
            dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
            if dealer:
                st.info(f"**Dealer Name:** {dealer.dealer_name}")

        # Overview metrics
        st.subheader("📊 Overview Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Count prospect data
            prospect_count = db.query(ProspectData).filter(
                ProspectData.dealer_id == dealer_id if dealer_id != "All" else True
            ).count()
            st.metric("Prospect Records", prospect_count)

        with col2:
            # Count PKB data
            pkb_count = db.query(PKBData).filter(
                PKBData.dealer_id == dealer_id if dealer_id != "All" else True
            ).count()
            st.metric("PKB Records", pkb_count)

        with col3:
            # Count parts inbound data
            parts_count = db.query(PartsInboundData).filter(
                PartsInboundData.dealer_id == dealer_id if dealer_id != "All" else True
            ).count()
            st.metric("Parts Inbound", parts_count)

        with col4:
            # Count fetch logs
            logs_count = db.query(FetchLog).filter(
                FetchLog.dealer_id == dealer_id if dealer_id != "All" else True
            ).count()
            st.metric("Total Fetch Logs", logs_count)

        # Recent activity
        st.subheader("🕒 Recent Activity")

        # Debug: Show status distribution
        if st.checkbox("🔍 Show Status Debug Info", key="status_debug"):
            status_counts = db.query(
                FetchLog.status,
                func.count(FetchLog.id).label('count')
            ).filter(
                FetchLog.dealer_id == dealer_id if dealer_id != "All" else True
            ).group_by(FetchLog.status).all()

            if status_counts:
                st.write("**Status Distribution in Database:**")
                for status, count in status_counts:
                    st.write(f"- {status}: {count} records")
            else:
                st.write("No fetch logs found")

        # Get recent fetch logs
        recent_logs = get_recent_fetch_logs(dealer_id, limit=10)

        if recent_logs:
            st.subheader("📋 Recent Fetch Logs")

            # Format the data for display
            display_data = []
            for log in recent_logs:
                display_data.append({
                    "Status": format_status_display(log["status"]),
                    "Records": log["records_fetched"] or 0,
                    "Duration (s)": f"{log['duration']:.2f}" if log["duration"] else "N/A",
                    "Completed At": log["completed_at"] or "N/A"
                })

            if display_data:
                df_display = pd.DataFrame(display_data)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No recent fetch logs found.")

        

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
    finally:
        db.close()

def render_prospect_data_page(dealer_id):
    """Render the prospect data table page"""
    st.subheader("👥 Prospect Data")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search by name, phone, or prospect ID...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'prospect_page' not in st.session_state:
        st.session_state.prospect_page = 1

    # Get data
    data, total_count = get_prospect_data_table(dealer_id, st.session_state.prospect_page, page_size, search_term)

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.prospect_page}")

    if data:
        # Display data table
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Pagination controls
        total_pages = (total_count + page_size - 1) // page_size

        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First") and st.session_state.prospect_page > 1:
                    st.session_state.prospect_page = 1
                    st.rerun()

            with col2:
                if st.button("⏪ Previous") and st.session_state.prospect_page > 1:
                    st.session_state.prospect_page -= 1
                    st.rerun()

            with col3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.prospect_page} of {total_pages}</div>", unsafe_allow_html=True)

            with col4:
                if st.button("Next ⏩") and st.session_state.prospect_page < total_pages:
                    st.session_state.prospect_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️") and st.session_state.prospect_page < total_pages:
                    st.session_state.prospect_page = total_pages
                    st.rerun()
    else:
        st.warning("No prospect data found for the selected dealer.")

def render_pkb_data_page(dealer_id):
    """Render the PKB data table page"""
    st.subheader("🔧 PKB (Service Record) Data")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search by work order, owner name, or plate number...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'pkb_page' not in st.session_state:
        st.session_state.pkb_page = 1

    # Get data
    data, total_count = get_pkb_data_table(dealer_id, st.session_state.pkb_page, page_size, search_term)

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.pkb_page}")

    if data:
        # Display data table
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Pagination controls
        total_pages = (total_count + page_size - 1) // page_size

        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First") and st.session_state.pkb_page > 1:
                    st.session_state.pkb_page = 1
                    st.rerun()

            with col2:
                if st.button("⏪ Previous") and st.session_state.pkb_page > 1:
                    st.session_state.pkb_page -= 1
                    st.rerun()

            with col3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.pkb_page} of {total_pages}</div>", unsafe_allow_html=True)

            with col4:
                if st.button("Next ⏩") and st.session_state.pkb_page < total_pages:
                    st.session_state.pkb_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️") and st.session_state.pkb_page < total_pages:
                    st.session_state.pkb_page = total_pages
                    st.rerun()
    else:
        st.warning("No PKB data found for the selected dealer.")

def render_parts_inbound_data_page(dealer_id):
    """Render the Parts Inbound data table page"""
    st.subheader("📦 Parts Inbound Data")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search by receipt number or shipping list...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'parts_inbound_page' not in st.session_state:
        st.session_state.parts_inbound_page = 1

    # Get data
    data, total_count = get_parts_inbound_data_table(dealer_id, st.session_state.parts_inbound_page, page_size, search_term)

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.parts_inbound_page}")

    if data:
        # Display data table
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Pagination controls
        total_pages = (total_count + page_size - 1) // page_size

        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First") and st.session_state.parts_inbound_page > 1:
                    st.session_state.parts_inbound_page = 1
                    st.rerun()

            with col2:
                if st.button("⏪ Previous") and st.session_state.parts_inbound_page > 1:
                    st.session_state.parts_inbound_page -= 1
                    st.rerun()

            with col3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.parts_inbound_page} of {total_pages}</div>", unsafe_allow_html=True)

            with col4:
                if st.button("Next ⏩") and st.session_state.parts_inbound_page < total_pages:
                    st.session_state.parts_inbound_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️") and st.session_state.parts_inbound_page < total_pages:
                    st.session_state.parts_inbound_page = total_pages
                    st.rerun()
    else:
        st.warning("No Parts Inbound data found for the selected dealer.")

def render_leasing_data_page(dealer_id):
    """Render the Leasing data table page"""
    st.subheader("💰 Leasing Requirement Data")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search by document ID, SPK ID, or finance company...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'leasing_page' not in st.session_state:
        st.session_state.leasing_page = 1

    # Get data
    data, total_count = get_leasing_data_table(dealer_id, st.session_state.leasing_page, page_size, search_term)

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.leasing_page}")

    if data:
        # Display data table
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Pagination controls
        total_pages = (total_count + page_size - 1) // page_size

        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First") and st.session_state.leasing_page > 1:
                    st.session_state.leasing_page = 1
                    st.rerun()

            with col2:
                if st.button("⏪ Previous") and st.session_state.leasing_page > 1:
                    st.session_state.leasing_page -= 1
                    st.rerun()

            with col3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.leasing_page} of {total_pages}</div>", unsafe_allow_html=True)

            with col4:
                if st.button("Next ⏩") and st.session_state.leasing_page < total_pages:
                    st.session_state.leasing_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️") and st.session_state.leasing_page < total_pages:
                    st.session_state.leasing_page = total_pages
                    st.rerun()
    else:
        st.warning("No Leasing data found for the selected dealer.")


def render_document_handling_data_page(dealer_id):
    """Render the Document Handling data table page"""
    st.subheader("📄 Document Handling Data")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search SO ID, SPK ID, or chassis number...")

    with col2:
        page_size = st.selectbox("📄 Page Size", [10, 25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Get data with search and pagination
    try:
        data_result, total_count = get_document_handling_data_table(dealer_id, page=1, page_size=page_size, search_term=search_term)
    except Exception as e:
        st.error(f"Error loading document handling data: {str(e)}")
        return

    if data_result and len(data_result) > 0:
        # Display summary
        st.info(f"📊 Total records: {total_count} | Showing page 1")
        st.markdown(f"**Records on this page:** {len(data_result)}")

        # Create DataFrame for display
        display_data = []
        for record in data_result:
            # Get first unit for main display - safe access
            units = record.get('units', [])
            first_unit = units[0] if units and len(units) > 0 else {}

            display_data.append({
                "SO ID": record.get('id_so', ''),
                "SPK ID": record.get('id_spk', ''),
                "Units": record.get('unit_count', 0),
                "Chassis Number": first_unit.get('nomor_rangka', '') if first_unit else '',
                "STNK Status": first_unit.get('status_faktur_stnk', '') if first_unit else '',
                "Plate Number": first_unit.get('plat_nomor', '') if first_unit else '',
                "BPKB Receiver": first_unit.get('nama_penerima_bpkb', '') if first_unit else '',
                "STNK Received": first_unit.get('tanggal_terima_stnk_oleh_konsumen', '') if first_unit else '',
                "Created": record.get('created_time', ''),
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SO ID": st.column_config.TextColumn("SO ID", width="medium"),
                    "SPK ID": st.column_config.TextColumn("SPK ID", width="medium"),
                    "Units": st.column_config.NumberColumn("Units", width="small"),
                    "Chassis Number": st.column_config.TextColumn("Chassis Number", width="medium"),
                    "STNK Status": st.column_config.TextColumn("STNK Status", width="small"),
                    "Plate Number": st.column_config.TextColumn("Plate Number", width="medium"),
                    "BPKB Receiver": st.column_config.TextColumn("BPKB Receiver", width="medium"),
                    "STNK Received": st.column_config.TextColumn("STNK Received", width="medium"),
                    "Created": st.column_config.TextColumn("Created", width="medium"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination info
            st.markdown(f"Showing {len(display_data)} records")

            
    else:
        st.warning("No Document Handling data found for the selected dealer.")


def render_unit_inbound_data_page(dealer_id):
    """Render the Unit Inbound data table page"""
    st.subheader("🚚 Unit Inbound from Purchase Order")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search shipping list, invoice, PO ID, or chassis number...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'unit_inbound_page' not in st.session_state:
        st.session_state.unit_inbound_page = 1

    # Get data with error handling
    try:
        data, total_count = get_unit_inbound_data_table(dealer_id, st.session_state.unit_inbound_page, page_size, search_term)
    except Exception as e:
        st.error(f"Error loading unit inbound data: {str(e)}")
        return

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.unit_inbound_page}")

    if data:
        # Create DataFrame for display
        display_data = []
        for record in data:
            # Get first unit for main display - safe access
            units = record.get('units', [])
            first_unit = units[0] if units and len(units) > 0 else {}

            display_data.append({
                "Shipping List": record.get('no_shipping_list', ''),
                "Receive Date": record.get('tanggal_terima', ''),
                "Invoice": record.get('no_invoice', ''),
                "Status": record.get('status_shipping_list', ''),
                "Units": record.get('unit_count', 0),
                "Unit Type": first_unit.get('kode_tipe_unit', '') if first_unit else '',
                "Color": first_unit.get('kode_warna', '') if first_unit else '',
                "Chassis No": first_unit.get('no_rangka', '') if first_unit else '',
                "Engine No": first_unit.get('no_mesin', '') if first_unit else '',
                "RFS Status": first_unit.get('status_rfs', '') if first_unit else '',
                "PO ID": first_unit.get('po_id', '') if first_unit else '',
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Shipping List": st.column_config.TextColumn("Shipping List", width="medium"),
                    "Receive Date": st.column_config.TextColumn("Receive Date", width="small"),
                    "Invoice": st.column_config.TextColumn("Invoice", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Units": st.column_config.NumberColumn("Units", width="small"),
                    "Unit Type": st.column_config.TextColumn("Unit Type", width="small"),
                    "Color": st.column_config.TextColumn("Color", width="small"),
                    "Chassis No": st.column_config.TextColumn("Chassis No", width="medium"),
                    "Engine No": st.column_config.TextColumn("Engine No", width="medium"),
                    "RFS Status": st.column_config.TextColumn("RFS", width="small"),
                    "PO ID": st.column_config.TextColumn("PO ID", width="medium"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First") and st.session_state.unit_inbound_page > 1:
                        st.session_state.unit_inbound_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous") and st.session_state.unit_inbound_page > 1:
                        st.session_state.unit_inbound_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.unit_inbound_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩") and st.session_state.unit_inbound_page < total_pages:
                        st.session_state.unit_inbound_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️") and st.session_state.unit_inbound_page < total_pages:
                        st.session_state.unit_inbound_page = total_pages
                        st.rerun()
    else:
        st.warning("No Unit Inbound data found for the selected dealer.")


def render_delivery_process_data_page(dealer_id):
    """Render the Delivery Process data table page"""
    st.subheader("🚛 Delivery Process (BAST)")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search delivery document, SO, SPK, customer, or receiver name...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'delivery_process_page' not in st.session_state:
        st.session_state.delivery_process_page = 1

    # Get data with error handling
    try:
        data, total_count = get_delivery_process_data_table(dealer_id, st.session_state.delivery_process_page, page_size, search_term)
    except Exception as e:
        st.error(f"Error loading delivery process data: {str(e)}")
        return

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.delivery_process_page}")

    if data:
        # Create DataFrame for display
        display_data = []
        for record in data:
            # Get first detail for main display - safe access
            details = record.get('details', [])
            first_detail = details[0] if details and len(details) > 0 else {}

            display_data.append({
                "Delivery Doc": record.get('delivery_document_id', ''),
                "Delivery Date": record.get('tanggal_pengiriman', ''),
                "Driver": record.get('id_driver', ''),
                "Status": record.get('status_delivery_document', ''),
                "Details": record.get('detail_count', 0),
                "SO Number": first_detail.get('no_so', '') if first_detail else '',
                "SPK ID": first_detail.get('id_spk', '') if first_detail else '',
                "Customer ID": first_detail.get('id_customer', '') if first_detail else '',
                "Chassis No": first_detail.get('no_rangka', '') if first_detail else '',
                "Receiver": first_detail.get('nama_penerima', '') if first_detail else '',
                "Delivery Time": first_detail.get('waktu_pengiriman', '') if first_detail else '',
                "Location": first_detail.get('lokasi_pengiriman', '')[:50] + "..." if first_detail and first_detail.get('lokasi_pengiriman') and len(first_detail.get('lokasi_pengiriman', '')) > 50 else first_detail.get('lokasi_pengiriman', '') if first_detail else '',
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Delivery Doc": st.column_config.TextColumn("Delivery Doc", width="medium"),
                    "Delivery Date": st.column_config.TextColumn("Delivery Date", width="small"),
                    "Driver": st.column_config.TextColumn("Driver", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Details": st.column_config.NumberColumn("Details", width="small"),
                    "SO Number": st.column_config.TextColumn("SO Number", width="medium"),
                    "SPK ID": st.column_config.TextColumn("SPK ID", width="medium"),
                    "Customer ID": st.column_config.TextColumn("Customer ID", width="medium"),
                    "Chassis No": st.column_config.TextColumn("Chassis No", width="medium"),
                    "Receiver": st.column_config.TextColumn("Receiver", width="medium"),
                    "Delivery Time": st.column_config.TextColumn("Time", width="small"),
                    "Location": st.column_config.TextColumn("Location", width="large"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First") and st.session_state.delivery_process_page > 1:
                        st.session_state.delivery_process_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous") and st.session_state.delivery_process_page > 1:
                        st.session_state.delivery_process_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.delivery_process_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩") and st.session_state.delivery_process_page < total_pages:
                        st.session_state.delivery_process_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️") and st.session_state.delivery_process_page < total_pages:
                        st.session_state.delivery_process_page = total_pages
                        st.rerun()

           
    else:
        st.warning("No Delivery Process data found for the selected dealer.")


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_billing_process_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Billing Process data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(BillingProcessData).filter(BillingProcessData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            search_filter = or_(
                BillingProcessData.id_invoice.ilike(f"%{search_term}%"),
                BillingProcessData.id_spk.ilike(f"%{search_term}%"),
                BillingProcessData.id_customer.ilike(f"%{search_term}%"),
                BillingProcessData.note.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        billing_records = query.order_by(BillingProcessData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries
        data = []
        for billing in billing_records:
            data.append({
                "id": str(billing.id),
                "dealer_id": billing.dealer_id,
                "dealer_name": billing.dealer.dealer_name if billing.dealer else "Unknown",
                "id_invoice": billing.id_invoice,
                "id_spk": billing.id_spk,
                "id_customer": billing.id_customer,
                "amount": float(billing.amount) if billing.amount else 0.0,
                "tipe_pembayaran": billing.tipe_pembayaran,
                "cara_bayar": billing.cara_bayar,
                "status": billing.status,
                "note": billing.note,
                "created_time": billing.created_time,
                "modified_time": billing.modified_time,
                "fetched_at": billing.fetched_at.isoformat() if billing.fetched_at else None
            })

        return data, total_count
    finally:
        db.close()


def render_billing_process_data_page(dealer_id):
    """Render the Billing Process data table page"""
    st.subheader("💳 Billing Process")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search invoice, SPK, customer, or notes...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'billing_process_page' not in st.session_state:
        st.session_state.billing_process_page = 1

    # Get data with error handling
    try:
        data, total_count = get_billing_process_data_table(dealer_id, st.session_state.billing_process_page, page_size, search_term)
    except Exception as e:
        st.error(f"Error loading billing process data: {str(e)}")
        return

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.billing_process_page}")

    if data:
        # Create DataFrame for display
        display_data = []
        for record in data:
            display_data.append({
                "Invoice ID": record.get('id_invoice', ''),
                "SPK ID": record.get('id_spk', ''),
                "Customer ID": record.get('id_customer', ''),
                "Amount": f"Rp {record.get('amount', 0):,.0f}",
                "Payment Type": record.get('tipe_pembayaran', ''),
                "Payment Method": record.get('cara_bayar', ''),
                "Status": record.get('status', ''),
                "Note": record.get('note', '')[:50] + "..." if record.get('note') and len(record.get('note', '')) > 50 else record.get('note', ''),
                "Created": record.get('created_time', ''),
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Invoice ID": st.column_config.TextColumn("Invoice ID", width="medium"),
                    "SPK ID": st.column_config.TextColumn("SPK ID", width="medium"),
                    "Customer ID": st.column_config.TextColumn("Customer ID", width="medium"),
                    "Amount": st.column_config.TextColumn("Amount", width="medium"),
                    "Payment Type": st.column_config.TextColumn("Payment Type", width="small"),
                    "Payment Method": st.column_config.TextColumn("Payment Method", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Note": st.column_config.TextColumn("Note", width="large"),
                    "Created": st.column_config.TextColumn("Created", width="medium"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First") and st.session_state.billing_process_page > 1:
                        st.session_state.billing_process_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous") and st.session_state.billing_process_page > 1:
                        st.session_state.billing_process_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.billing_process_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩") and st.session_state.billing_process_page < total_pages:
                        st.session_state.billing_process_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️") and st.session_state.billing_process_page < total_pages:
                        st.session_state.billing_process_page = total_pages
                        st.rerun()

            
    else:
        st.warning("No Billing Process data found for the selected dealer.")


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_unit_invoice_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Unit Invoice data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(UnitInvoiceData).filter(UnitInvoiceData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            # Join with units to search in unit data
            query = query.join(UnitInvoiceUnit, UnitInvoiceData.id == UnitInvoiceUnit.unit_invoice_data_id, isouter=True)
            search_filter = or_(
                UnitInvoiceData.no_invoice.ilike(f"%{search_term}%"),
                UnitInvoiceData.main_dealer_id.ilike(f"%{search_term}%"),
                UnitInvoiceUnit.po_id.ilike(f"%{search_term}%"),
                UnitInvoiceUnit.kode_tipe_unit.ilike(f"%{search_term}%"),
                UnitInvoiceUnit.no_mesin.ilike(f"%{search_term}%"),
                UnitInvoiceUnit.no_rangka.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter).distinct()

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        invoice_records = query.order_by(UnitInvoiceData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with unit details
        data = []
        for invoice in invoice_records:
            # Get units for this invoice
            units = db.query(UnitInvoiceUnit).filter(
                UnitInvoiceUnit.unit_invoice_data_id == invoice.id
            ).all()

            # Get first unit for main display
            first_unit = units[0] if units else None

            data.append({
                "id": str(invoice.id),
                "dealer_id": invoice.dealer_id,
                "dealer_name": invoice.dealer.dealer_name if invoice.dealer else "Unknown",
                "no_invoice": invoice.no_invoice,
                "tanggal_invoice": invoice.tanggal_invoice,
                "tanggal_jatuh_tempo": invoice.tanggal_jatuh_tempo,
                "main_dealer_id": invoice.main_dealer_id,
                "total_harga_sebelum_diskon": float(invoice.total_harga_sebelum_diskon) if invoice.total_harga_sebelum_diskon else 0.0,
                "total_diskon_per_unit": float(invoice.total_diskon_per_unit) if invoice.total_diskon_per_unit else 0.0,
                "potongan_per_invoice": float(invoice.potongan_per_invoice) if invoice.potongan_per_invoice else 0.0,
                "total_ppn": float(invoice.total_ppn) if invoice.total_ppn else 0.0,
                "total_harga": float(invoice.total_harga) if invoice.total_harga else 0.0,
                "created_time": invoice.created_time,
                "modified_time": invoice.modified_time,
                "fetched_at": invoice.fetched_at.isoformat() if invoice.fetched_at else None,
                "unit_count": len(units),
                "units": [
                    {
                        "id": str(unit.id),
                        "kode_tipe_unit": unit.kode_tipe_unit,
                        "kode_warna": unit.kode_warna,
                        "kuantitas": unit.kuantitas,
                        "no_mesin": unit.no_mesin,
                        "no_rangka": unit.no_rangka,
                        "harga_satuan_sebelum_diskon": float(unit.harga_satuan_sebelum_diskon) if unit.harga_satuan_sebelum_diskon else 0.0,
                        "diskon_per_unit": float(unit.diskon_per_unit) if unit.diskon_per_unit else 0.0,
                        "po_id": unit.po_id
                    } for unit in units
                ]
            })

        return data, total_count
    finally:
        db.close()


def render_unit_invoice_data_page(dealer_id):
    """Render the Unit Invoice data table page"""
    st.subheader("📋 Unit Invoice (MD to Dealer)")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search invoice, PO, unit type, chassis, or engine number...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'unit_invoice_page' not in st.session_state:
        st.session_state.unit_invoice_page = 1

    # Get data with error handling
    try:
        data, total_count = get_unit_invoice_data_table(dealer_id, st.session_state.unit_invoice_page, page_size, search_term)
    except Exception as e:
        st.error(f"Error loading unit invoice data: {str(e)}")
        return

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.unit_invoice_page}")

    if data:
        # Create DataFrame for display
        display_data = []
        for record in data:
            # Get first unit for main display - safe access
            units = record.get('units', [])
            first_unit = units[0] if units and len(units) > 0 else {}

            display_data.append({
                "Invoice No": record.get('no_invoice', ''),
                "Invoice Date": record.get('tanggal_invoice', ''),
                "Due Date": record.get('tanggal_jatuh_tempo', ''),
                "Main Dealer": record.get('main_dealer_id', ''),
                "Units": record.get('unit_count', 0),
                "Unit Type": first_unit.get('kode_tipe_unit', '') if first_unit else '',
                "Color": first_unit.get('kode_warna', '') if first_unit else '',
                "Quantity": first_unit.get('kuantitas', '') if first_unit else '',
                "PO ID": first_unit.get('po_id', '') if first_unit else '',
                "Before Discount": f"Rp {record.get('total_harga_sebelum_diskon', 0):,.0f}",
                "Discount": f"Rp {record.get('total_diskon_per_unit', 0):,.0f}",
                "PPN": f"Rp {record.get('total_ppn', 0):,.0f}",
                "Total": f"Rp {record.get('total_harga', 0):,.0f}",
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Invoice No": st.column_config.TextColumn("Invoice No", width="medium"),
                    "Invoice Date": st.column_config.TextColumn("Invoice Date", width="small"),
                    "Due Date": st.column_config.TextColumn("Due Date", width="small"),
                    "Main Dealer": st.column_config.TextColumn("Main Dealer", width="small"),
                    "Units": st.column_config.NumberColumn("Units", width="small"),
                    "Unit Type": st.column_config.TextColumn("Unit Type", width="small"),
                    "Color": st.column_config.TextColumn("Color", width="small"),
                    "Quantity": st.column_config.NumberColumn("Qty", width="small"),
                    "PO ID": st.column_config.TextColumn("PO ID", width="medium"),
                    "Before Discount": st.column_config.TextColumn("Before Discount", width="medium"),
                    "Discount": st.column_config.TextColumn("Discount", width="medium"),
                    "PPN": st.column_config.TextColumn("PPN", width="medium"),
                    "Total": st.column_config.TextColumn("Total", width="medium"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First") and st.session_state.unit_invoice_page > 1:
                        st.session_state.unit_invoice_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous") and st.session_state.unit_invoice_page > 1:
                        st.session_state.unit_invoice_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.unit_invoice_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩") and st.session_state.unit_invoice_page < total_pages:
                        st.session_state.unit_invoice_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️") and st.session_state.unit_invoice_page < total_pages:
                        st.session_state.unit_invoice_page = total_pages
                        st.rerun()

            
    else:
        st.warning("No Unit Invoice data found for the selected dealer.")


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_parts_sales_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get Parts Sales data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(PartsSalesData).filter(PartsSalesData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            # Join with parts to search in parts data
            query = query.join(PartsSalesPart, PartsSalesData.id == PartsSalesPart.parts_sales_data_id, isouter=True)
            search_filter = or_(
                PartsSalesData.no_so.ilike(f"%{search_term}%"),
                PartsSalesData.id_customer.ilike(f"%{search_term}%"),
                PartsSalesData.nama_customer.ilike(f"%{search_term}%"),
                PartsSalesPart.parts_number.ilike(f"%{search_term}%"),
                PartsSalesPart.booking_id_reference.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter).distinct()

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        sales_records = query.order_by(PartsSalesData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with parts details
        data = []
        for sales in sales_records:
            # Get parts for this sales order
            parts = db.query(PartsSalesPart).filter(
                PartsSalesPart.parts_sales_data_id == sales.id
            ).all()

            data.append({
                "id": str(sales.id),
                "dealer_id": sales.dealer_id,
                "dealer_name": sales.dealer.dealer_name if sales.dealer else "Unknown",
                "no_so": sales.no_so,
                "tgl_so": sales.tgl_so,
                "id_customer": sales.id_customer,
                "nama_customer": sales.nama_customer,
                "disc_so": float(sales.disc_so) if sales.disc_so else 0.0,
                "total_harga_so": float(sales.total_harga_so) if sales.total_harga_so else 0.0,
                "created_time": sales.created_time,
                "modified_time": sales.modified_time,
                "fetched_at": sales.fetched_at.isoformat() if sales.fetched_at else None,
                "parts_count": len(parts),
                "parts": [
                    {
                        "id": str(part.id),
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "harga_parts": float(part.harga_parts) if part.harga_parts else 0.0,
                        "promo_id_parts": part.promo_id_parts,
                        "disc_amount": float(part.disc_amount) if part.disc_amount else 0.0,
                        "disc_percentage": part.disc_percentage,
                        "ppn": float(part.ppn) if part.ppn else 0.0,
                        "total_harga_parts": float(part.total_harga_parts) if part.total_harga_parts else 0.0,
                        "uang_muka": float(part.uang_muka) if part.uang_muka else 0.0,
                        "booking_id_reference": part.booking_id_reference
                    } for part in parts
                ]
            })

        return data, total_count
    finally:
        db.close()


def render_parts_sales_data_page(dealer_id):
    """Render the Parts Sales data table page"""
    st.subheader("� Parts Sales")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search SO number, customer, parts number, or booking reference...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'parts_sales_page' not in st.session_state:
        st.session_state.parts_sales_page = 1

    # Get data with error handling
    try:
        data, total_count = get_parts_sales_data_table(dealer_id, st.session_state.parts_sales_page, page_size, search_term)
    except Exception as e:
        st.error(f"Error loading parts sales data: {str(e)}")
        return

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.parts_sales_page}")

    if data:
        # Create DataFrame for display
        display_data = []
        for record in data:
            # Get first part for main display - safe access
            parts = record.get('parts', [])
            first_part = parts[0] if parts and len(parts) > 0 else {}

            display_data.append({
                "SO Number": record.get('no_so', ''),
                "SO Date": record.get('tgl_so', ''),
                "Customer ID": record.get('id_customer', ''),
                "Customer Name": record.get('nama_customer', ''),
                "Parts Count": record.get('parts_count', 0),
                "First Part": first_part.get('parts_number', '') if first_part else '',
                "Part Qty": first_part.get('kuantitas', '') if first_part else '',
                "Part Price": f"Rp {first_part.get('harga_parts', 0):,.0f}" if first_part else '',
                "SO Discount": f"Rp {record.get('disc_so', 0):,.0f}",
                "Total SO": f"Rp {record.get('total_harga_so', 0):,.0f}",
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SO Number": st.column_config.TextColumn("SO Number", width="medium"),
                    "SO Date": st.column_config.TextColumn("SO Date", width="small"),
                    "Customer ID": st.column_config.TextColumn("Customer ID", width="medium"),
                    "Customer Name": st.column_config.TextColumn("Customer Name", width="medium"),
                    "Parts Count": st.column_config.NumberColumn("Parts", width="small"),
                    "First Part": st.column_config.TextColumn("First Part", width="medium"),
                    "Part Qty": st.column_config.NumberColumn("Qty", width="small"),
                    "Part Price": st.column_config.TextColumn("Part Price", width="medium"),
                    "SO Discount": st.column_config.TextColumn("SO Discount", width="medium"),
                    "Total SO": st.column_config.TextColumn("Total SO", width="medium"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First") and st.session_state.parts_sales_page > 1:
                        st.session_state.parts_sales_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous") and st.session_state.parts_sales_page > 1:
                        st.session_state.parts_sales_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.parts_sales_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩") and st.session_state.parts_sales_page < total_pages:
                        st.session_state.parts_sales_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️") and st.session_state.parts_sales_page < total_pages:
                        st.session_state.parts_sales_page = total_pages
                        st.rerun()
    else:
        st.warning("No Parts Sales data found for the selected dealer.")


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_dp_hlo_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get DP HLO data for table display with pagination"""
    SessionLocal = get_database_connection()
    db = SessionLocal()
    try:
        # Base query
        query = db.query(DPHLOData).filter(DPHLOData.dealer_id == dealer_id)

        # Apply search filter if provided
        if search_term:
            # Join with parts to search in parts data
            query = query.join(DPHLOPart, DPHLOData.id == DPHLOPart.dp_hlo_data_id, isouter=True)
            search_filter = or_(
                DPHLOData.id_hlo_document.ilike(f"%{search_term}%"),
                DPHLOData.no_work_order.ilike(f"%{search_term}%"),
                DPHLOData.id_customer.ilike(f"%{search_term}%"),
                DPHLOData.no_invoice_uang_jaminan.ilike(f"%{search_term}%"),
                DPHLOPart.parts_number.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter).distinct()

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        hlo_records = query.order_by(DPHLOData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Convert to list of dictionaries with parts details
        data = []
        for hlo in hlo_records:
            # Get parts for this HLO document
            parts = db.query(DPHLOPart).filter(
                DPHLOPart.dp_hlo_data_id == hlo.id
            ).all()

            data.append({
                "id": str(hlo.id),
                "dealer_id": hlo.dealer_id,
                "dealer_name": hlo.dealer.dealer_name if hlo.dealer else "Unknown",
                "no_invoice_uang_jaminan": hlo.no_invoice_uang_jaminan,
                "id_hlo_document": hlo.id_hlo_document,
                "tanggal_pemesanan_hlo": hlo.tanggal_pemesanan_hlo,
                "no_work_order": hlo.no_work_order,
                "id_customer": hlo.id_customer,
                "created_time": hlo.created_time,
                "modified_time": hlo.modified_time,
                "fetched_at": hlo.fetched_at.isoformat() if hlo.fetched_at else None,
                "parts_count": len(parts),
                "parts": [
                    {
                        "id": str(part.id),
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "harga_parts": float(part.harga_parts) if part.harga_parts else 0.0,
                        "total_harga_parts": float(part.total_harga_parts) if part.total_harga_parts else 0.0,
                        "uang_muka": float(part.uang_muka) if part.uang_muka else 0.0,
                        "sisa_bayar": float(part.sisa_bayar) if part.sisa_bayar else 0.0
                    } for part in parts
                ]
            })

        return data, total_count
    finally:
        db.close()


def render_dp_hlo_data_page(dealer_id):
    """Render the DP HLO data table page"""
    st.subheader("🔧 DP HLO")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search HLO document, work order, customer ID, or parts number...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'dp_hlo_page' not in st.session_state:
        st.session_state.dp_hlo_page = 1

    # Get data with error handling
    try:
        data, total_count = get_dp_hlo_data_table(dealer_id, st.session_state.dp_hlo_page, page_size, search_term)
    except Exception as e:
        st.error(f"Error loading DP HLO data: {str(e)}")
        return

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.dp_hlo_page}")

    if data:
        # Create DataFrame for display
        display_data = []
        for record in data:
            # Get first part for main display - safe access
            parts = record.get('parts', [])
            first_part = parts[0] if parts and len(parts) > 0 else {}

            display_data.append({
                "HLO Document": record.get('id_hlo_document', ''),
                "Invoice UJ": record.get('no_invoice_uang_jaminan', ''),
                "Order Date": record.get('tanggal_pemesanan_hlo', ''),
                "Work Order": record.get('no_work_order', ''),
                "Customer ID": record.get('id_customer', ''),
                "Parts Count": record.get('parts_count', 0),
                "First Part": first_part.get('parts_number', '') if first_part else '',
                "Part Qty": first_part.get('kuantitas', '') if first_part else '',
                "Part Price": f"Rp {first_part.get('harga_parts', 0):,.0f}" if first_part else '',
                "Down Payment": f"Rp {first_part.get('uang_muka', 0):,.0f}" if first_part else '',
                "Remaining": f"Rp {first_part.get('sisa_bayar', 0):,.0f}" if first_part else '',
                "Fetched": record.get('fetched_at', '')[:19] if record.get('fetched_at') else ''
            })

        if display_data:
            df = pd.DataFrame(display_data)

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "HLO Document": st.column_config.TextColumn("HLO Document", width="medium"),
                    "Invoice UJ": st.column_config.TextColumn("Invoice UJ", width="medium"),
                    "Order Date": st.column_config.TextColumn("Order Date", width="small"),
                    "Work Order": st.column_config.TextColumn("Work Order", width="medium"),
                    "Customer ID": st.column_config.TextColumn("Customer ID", width="medium"),
                    "Parts Count": st.column_config.NumberColumn("Parts", width="small"),
                    "First Part": st.column_config.TextColumn("First Part", width="medium"),
                    "Part Qty": st.column_config.NumberColumn("Qty", width="small"),
                    "Part Price": st.column_config.TextColumn("Part Price", width="medium"),
                    "Down Payment": st.column_config.TextColumn("Down Payment", width="medium"),
                    "Remaining": st.column_config.TextColumn("Remaining", width="medium"),
                    "Fetched": st.column_config.TextColumn("Fetched", width="medium")
                }
            )

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First") and st.session_state.dp_hlo_page > 1:
                        st.session_state.dp_hlo_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous") and st.session_state.dp_hlo_page > 1:
                        st.session_state.dp_hlo_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.dp_hlo_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩") and st.session_state.dp_hlo_page < total_pages:
                        st.session_state.dp_hlo_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️") and st.session_state.dp_hlo_page < total_pages:
                        st.session_state.dp_hlo_page = total_pages
                        st.rerun()
    else:
        st.warning("No DP HLO data found for the selected dealer.")


def render_workshop_invoice_data_page(dealer_id):
    """Render the Workshop Invoice data page"""
    st.subheader("🔨 Workshop Invoice (NJB & NSC)")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Get session
    SessionLocal = get_database_connection()
    session = SessionLocal()

    try:
        # Base query
        query = session.query(WorkshopInvoiceData).join(Dealer)

        # Apply dealer filter
        if dealer_id != "All":
            query = query.filter(WorkshopInvoiceData.dealer_id == dealer_id)

        # Get total count
        total_records = query.count()

        if total_records == 0:
            st.warning("No workshop invoice data found for the selected dealer.")
            return

        st.info(f"Found {total_records} workshop invoice records")

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            page_size = st.selectbox("Records per page", [10, 25, 50, 100], index=1, key="workshop_invoice_page_size")

        # Initialize page number in session state
        if 'workshop_invoice_page' not in st.session_state:
            st.session_state.workshop_invoice_page = 1

        total_pages = (total_records + page_size - 1) // page_size

        # Search functionality
        search_term = st.text_input("🔍 Search (Work Order, NJB, NSC, Job ID, Parts Number)", key="workshop_invoice_search")

        # Apply search filter
        if search_term:
            search_pattern = f"%{search_term}%"
            # Join with services and parts for comprehensive search
            query = query.join(WorkshopInvoiceNJB, WorkshopInvoiceData.id == WorkshopInvoiceNJB.workshop_invoice_data_id, isouter=True)
            query = query.join(WorkshopInvoiceNSC, WorkshopInvoiceData.id == WorkshopInvoiceNSC.workshop_invoice_data_id, isouter=True)
            query = query.filter(
                or_(
                    WorkshopInvoiceData.no_work_order.ilike(search_pattern),
                    WorkshopInvoiceData.no_njb.ilike(search_pattern),
                    WorkshopInvoiceData.no_nsc.ilike(search_pattern),
                    WorkshopInvoiceNJB.id_job.ilike(search_pattern),
                    WorkshopInvoiceNSC.id_job.ilike(search_pattern),
                    WorkshopInvoiceNSC.parts_number.ilike(search_pattern)
                )
            ).distinct()

        # Apply pagination
        offset = (st.session_state.workshop_invoice_page - 1) * page_size
        invoices = query.order_by(WorkshopInvoiceData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Prepare data for display
        data = []
        for invoice in invoices:
            # Get services and parts count
            services_count = session.query(WorkshopInvoiceNJB).filter(
                WorkshopInvoiceNJB.workshop_invoice_data_id == invoice.id
            ).count()

            parts_count = session.query(WorkshopInvoiceNSC).filter(
                WorkshopInvoiceNSC.workshop_invoice_data_id == invoice.id
            ).count()

            data.append({
                "Dealer": invoice.dealer.dealer_name,
                "Work Order": invoice.no_work_order or "N/A",
                "NJB Number": invoice.no_njb or "N/A",
                "NJB Date": invoice.tanggal_njb or "N/A",
                "NJB Amount": f"Rp {invoice.total_harga_njb:,.0f}" if invoice.total_harga_njb else "N/A",
                "NSC Number": invoice.no_nsc or "N/A",
                "NSC Date": invoice.tanggal_nsc or "N/A",
                "NSC Amount": f"Rp {invoice.total_harga_nsc:,.0f}" if invoice.total_harga_nsc else "N/A",
                "Services": services_count,
                "Parts": parts_count,
                "Honda SA": invoice.honda_id_sa or "N/A",
                "Honda Mechanic": invoice.honda_id_mekanik or "N/A",
                "Created": invoice.created_time or "N/A",
                "Fetched": invoice.fetched_at.strftime("%Y-%m-%d %H:%M") if invoice.fetched_at else "N/A"
            })

        # Display data table
        if data:
            df = pd.DataFrame(data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "NJB Amount": st.column_config.TextColumn("NJB Amount", help="Total NJB service amount"),
                    "NSC Amount": st.column_config.TextColumn("NSC Amount", help="Total NSC parts amount"),
                    "Services": st.column_config.NumberColumn("Services", help="Number of services"),
                    "Parts": st.column_config.NumberColumn("Parts", help="Number of parts")
                }
            )

            # Arrow pagination controls
            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First", key="workshop_invoice_first") and st.session_state.workshop_invoice_page > 1:
                        st.session_state.workshop_invoice_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous", key="workshop_invoice_prev") and st.session_state.workshop_invoice_page > 1:
                        st.session_state.workshop_invoice_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.workshop_invoice_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩", key="workshop_invoice_next") and st.session_state.workshop_invoice_page < total_pages:
                        st.session_state.workshop_invoice_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️", key="workshop_invoice_last") and st.session_state.workshop_invoice_page < total_pages:
                        st.session_state.workshop_invoice_page = total_pages
                        st.rerun()

            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4, col5 = st.columns(5)

            total_njb = sum([invoice.total_harga_njb or 0 for invoice in invoices])
            total_nsc = sum([invoice.total_harga_nsc or 0 for invoice in invoices])
            total_services = sum([session.query(WorkshopInvoiceNJB).filter(
                WorkshopInvoiceNJB.workshop_invoice_data_id == invoice.id
            ).count() for invoice in invoices])
            total_parts = sum([session.query(WorkshopInvoiceNSC).filter(
                WorkshopInvoiceNSC.workshop_invoice_data_id == invoice.id
            ).count() for invoice in invoices])

            with col1:
                st.metric("Total Invoices", len(invoices))
            with col2:
                st.metric("Total NJB Amount", f"Rp {total_njb:,.0f}")
            with col3:
                st.metric("Total NSC Amount", f"Rp {total_nsc:,.0f}")
            with col4:
                st.metric("Total Services", total_services)
            with col5:
                st.metric("Total Parts", total_parts)
        else:
            st.warning("No workshop invoice data found matching your search criteria.")

    except Exception as e:
        st.error(f"Error loading workshop invoice data: {str(e)}")
    finally:
        session.close()


def render_unpaid_hlo_data_page(dealer_id):
    """Render the Unpaid HLO data page"""
    st.subheader("📋 Unpaid HLO Documents")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Get session
    SessionLocal = get_database_connection()
    session = SessionLocal()

    try:
        # Base query
        query = session.query(UnpaidHLOData).join(Dealer)

        # Apply dealer filter
        if dealer_id != "All":
            query = query.filter(UnpaidHLOData.dealer_id == dealer_id)

        # Get total count
        total_records = query.count()

        if total_records == 0:
            st.warning("No unpaid HLO data found for the selected dealer.")
            return

        st.info(f"Found {total_records} unpaid HLO documents")

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            page_size = st.selectbox("Records per page", [10, 25, 50, 100], index=1, key="unpaid_hlo_page_size")

        # Initialize page number in session state
        if 'unpaid_hlo_page' not in st.session_state:
            st.session_state.unpaid_hlo_page = 1

        total_pages = (total_records + page_size - 1) // page_size

        # Search functionality
        search_term = st.text_input("🔍 Search (HLO Document, Work Order, Customer Name, KTP, Vehicle Details)", key="unpaid_hlo_search")

        # Apply search filter
        if search_term:
            search_pattern = f"%{search_term}%"
            # Join with parts for comprehensive search
            query = query.join(UnpaidHLOPart, UnpaidHLOData.id == UnpaidHLOPart.unpaid_hlo_data_id, isouter=True)
            query = query.filter(
                or_(
                    UnpaidHLOData.id_hlo_document.ilike(search_pattern),
                    UnpaidHLOData.no_work_order.ilike(search_pattern),
                    UnpaidHLOData.nama_customer.ilike(search_pattern),
                    UnpaidHLOData.no_ktp.ilike(search_pattern),
                    UnpaidHLOData.kode_tipe_unit.ilike(search_pattern),
                    UnpaidHLOData.no_mesin.ilike(search_pattern),
                    UnpaidHLOData.no_rangka.ilike(search_pattern),
                    UnpaidHLOPart.parts_number.ilike(search_pattern)
                )
            ).distinct()

        # Apply pagination
        offset = (st.session_state.unpaid_hlo_page - 1) * page_size
        hlo_documents = query.order_by(UnpaidHLOData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Prepare data for display
        data = []
        for hlo in hlo_documents:
            # Get parts count and total amounts
            parts = session.query(UnpaidHLOPart).filter(
                UnpaidHLOPart.unpaid_hlo_data_id == hlo.id
            ).all()

            parts_count = len(parts)
            total_parts_value = sum([part.total_harga_parts or 0 for part in parts])
            total_down_payment = sum([part.uang_muka or 0 for part in parts])
            total_remaining = sum([part.sisa_bayar or 0 for part in parts])

            data.append({
                "Dealer": hlo.dealer.dealer_name,
                "HLO Document": hlo.id_hlo_document or "N/A",
                "HLO Date": hlo.tanggal_pemesanan_hlo or "N/A",
                "Work Order": hlo.no_work_order or "N/A",
                "Customer": hlo.nama_customer or "N/A",
                "KTP": hlo.no_ktp or "N/A",
                "Contact": hlo.no_kontak or "N/A",
                "Vehicle Type": hlo.kode_tipe_unit or "N/A",
                "Year": hlo.tahun_motor or "N/A",
                "Engine No": hlo.no_mesin or "N/A",
                "Chassis No": hlo.no_rangka or "N/A",
                "Parts Count": parts_count,
                "Parts Value": f"Rp {total_parts_value:,.0f}" if total_parts_value else "N/A",
                "Down Payment": f"Rp {total_down_payment:,.0f}" if total_down_payment else "N/A",
                "Remaining": f"Rp {total_remaining:,.0f}" if total_remaining else "N/A",
                "Created": hlo.created_time or "N/A",
                "Fetched": hlo.fetched_at.strftime("%Y-%m-%d %H:%M") if hlo.fetched_at else "N/A"
            })

        # Display data table
        if data:
            df = pd.DataFrame(data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Parts Value": st.column_config.TextColumn("Parts Value", help="Total value of all parts"),
                    "Down Payment": st.column_config.TextColumn("Down Payment", help="Total down payment made"),
                    "Remaining": st.column_config.TextColumn("Remaining", help="Total remaining balance"),
                    "Parts Count": st.column_config.NumberColumn("Parts", help="Number of parts")
                }
            )

            # Arrow pagination controls
            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First", key="unpaid_hlo_first") and st.session_state.unpaid_hlo_page > 1:
                        st.session_state.unpaid_hlo_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous", key="unpaid_hlo_prev") and st.session_state.unpaid_hlo_page > 1:
                        st.session_state.unpaid_hlo_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.unpaid_hlo_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩", key="unpaid_hlo_next") and st.session_state.unpaid_hlo_page < total_pages:
                        st.session_state.unpaid_hlo_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️", key="unpaid_hlo_last") and st.session_state.unpaid_hlo_page < total_pages:
                        st.session_state.unpaid_hlo_page = total_pages
                        st.rerun()

            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4, col5 = st.columns(5)

            total_docs = len(hlo_documents)
            total_parts_all = sum([len(session.query(UnpaidHLOPart).filter(
                UnpaidHLOPart.unpaid_hlo_data_id == hlo.id
            ).all()) for hlo in hlo_documents])
            total_value_all = sum([sum([part.total_harga_parts or 0 for part in session.query(UnpaidHLOPart).filter(
                UnpaidHLOPart.unpaid_hlo_data_id == hlo.id
            ).all()]) for hlo in hlo_documents])
            total_down_all = sum([sum([part.uang_muka or 0 for part in session.query(UnpaidHLOPart).filter(
                UnpaidHLOPart.unpaid_hlo_data_id == hlo.id
            ).all()]) for hlo in hlo_documents])
            total_remaining_all = sum([sum([part.sisa_bayar or 0 for part in session.query(UnpaidHLOPart).filter(
                UnpaidHLOPart.unpaid_hlo_data_id == hlo.id
            ).all()]) for hlo in hlo_documents])

            with col1:
                st.metric("Total Documents", total_docs)
            with col2:
                st.metric("Total Parts", total_parts_all)
            with col3:
                st.metric("Total Value", f"Rp {total_value_all:,.0f}")
            with col4:
                st.metric("Down Payment", f"Rp {total_down_all:,.0f}")
            with col5:
                st.metric("Remaining", f"Rp {total_remaining_all:,.0f}")
        else:
            st.warning("No unpaid HLO data found matching your search criteria.")

    except Exception as e:
        st.error(f"Error loading unpaid HLO data: {str(e)}")
    finally:
        session.close()


def render_parts_invoice_data_page(dealer_id):
    """Render the Parts Invoice data page"""
    st.subheader("📄 Parts Invoice (MD to Dealer)")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Get session
    SessionLocal = get_database_connection()
    session = SessionLocal()

    try:
        # Base query
        query = session.query(PartsInvoiceData).join(Dealer)

        # Apply dealer filter
        if dealer_id != "All":
            query = query.filter(PartsInvoiceData.dealer_id == dealer_id)

        # Get total count
        total_records = query.count()

        if total_records == 0:
            st.warning("No parts invoice data found for the selected dealer.")
            return

        st.info(f"Found {total_records} parts invoice records")

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            page_size = st.selectbox("Records per page", [10, 25, 50, 100], index=1, key="parts_invoice_page_size")

        # Initialize page number in session state
        if 'parts_invoice_page' not in st.session_state:
            st.session_state.parts_invoice_page = 1

        total_pages = (total_records + page_size - 1) // page_size

        # Search functionality
        search_term = st.text_input("🔍 Search (Invoice Number, PO Number, Parts Number, Main Dealer)", key="parts_invoice_search")

        # Apply search filter
        if search_term:
            search_pattern = f"%{search_term}%"
            # Join with parts for comprehensive search
            query = query.join(PartsInvoicePart, PartsInvoiceData.id == PartsInvoicePart.parts_invoice_data_id, isouter=True)
            query = query.filter(
                or_(
                    PartsInvoiceData.no_invoice.ilike(search_pattern),
                    PartsInvoiceData.main_dealer_id.ilike(search_pattern),
                    PartsInvoicePart.no_po.ilike(search_pattern),
                    PartsInvoicePart.parts_number.ilike(search_pattern)
                )
            ).distinct()

        # Apply pagination
        offset = (st.session_state.parts_invoice_page - 1) * page_size
        invoices = query.order_by(PartsInvoiceData.fetched_at.desc()).offset(offset).limit(page_size).all()

        # Prepare data for display
        data = []
        for invoice in invoices:
            # Get parts count and details
            parts = session.query(PartsInvoicePart).filter(
                PartsInvoicePart.parts_invoice_data_id == invoice.id
            ).all()

            parts_count = len(parts)
            total_quantity = sum([part.kuantitas or 0 for part in parts])

            # Get unique PO numbers
            po_numbers = list(set([part.no_po for part in parts if part.no_po]))
            po_display = ", ".join(po_numbers[:3])  # Show first 3 PO numbers
            if len(po_numbers) > 3:
                po_display += f" (+{len(po_numbers) - 3} more)"

            data.append({
                "Dealer": invoice.dealer.dealer_name,
                "Invoice No": invoice.no_invoice or "N/A",
                "Invoice Date": invoice.tgl_invoice or "N/A",
                "Due Date": invoice.tgl_jatuh_tempo or "N/A",
                "Main Dealer": invoice.main_dealer_id or "N/A",
                "PO Numbers": po_display if po_display else "N/A",
                "Parts Count": parts_count,
                "Total Qty": total_quantity,
                "Before Discount": f"Rp {invoice.total_harga_sebelum_diskon:,.0f}" if invoice.total_harga_sebelum_diskon else "N/A",
                "Parts Discount": f"Rp {invoice.total_diskon_per_parts_number:,.0f}" if invoice.total_diskon_per_parts_number else "N/A",
                "Invoice Discount": f"Rp {invoice.potongan_per_invoice:,.0f}" if invoice.potongan_per_invoice else "N/A",
                "PPN": f"Rp {invoice.total_ppn:,.0f}" if invoice.total_ppn else "N/A",
                "Total Amount": f"Rp {invoice.total_harga:,.0f}" if invoice.total_harga else "N/A",
                "Created": invoice.created_time or "N/A",
                "Fetched": invoice.fetched_at.strftime("%Y-%m-%d %H:%M") if invoice.fetched_at else "N/A"
            })

        # Display data table
        if data:
            df = pd.DataFrame(data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Before Discount": st.column_config.TextColumn("Before Discount", help="Total amount before discount"),
                    "Parts Discount": st.column_config.TextColumn("Parts Discount", help="Total discount per parts"),
                    "Invoice Discount": st.column_config.TextColumn("Invoice Discount", help="Additional invoice discount"),
                    "PPN": st.column_config.TextColumn("PPN", help="Total VAT amount"),
                    "Total Amount": st.column_config.TextColumn("Total Amount", help="Final invoice amount"),
                    "Parts Count": st.column_config.NumberColumn("Parts", help="Number of parts"),
                    "Total Qty": st.column_config.NumberColumn("Qty", help="Total quantity")
                }
            )

            # Arrow pagination controls
            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First", key="parts_invoice_first") and st.session_state.parts_invoice_page > 1:
                        st.session_state.parts_invoice_page = 1
                        st.rerun()

                with col2:
                    if st.button("⏪ Previous", key="parts_invoice_prev") and st.session_state.parts_invoice_page > 1:
                        st.session_state.parts_invoice_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.parts_invoice_page} of {total_pages}</div>", unsafe_allow_html=True)

                with col4:
                    if st.button("Next ⏩", key="parts_invoice_next") and st.session_state.parts_invoice_page < total_pages:
                        st.session_state.parts_invoice_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️", key="parts_invoice_last") and st.session_state.parts_invoice_page < total_pages:
                        st.session_state.parts_invoice_page = total_pages
                        st.rerun()

            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            total_invoices = len(invoices)
            total_parts_all = sum([len(session.query(PartsInvoicePart).filter(
                PartsInvoicePart.parts_invoice_data_id == invoice.id
            ).all()) for invoice in invoices])
            total_before_discount = sum([invoice.total_harga_sebelum_diskon or 0 for invoice in invoices])
            total_discount = sum([(invoice.total_diskon_per_parts_number or 0) + (invoice.potongan_per_invoice or 0) for invoice in invoices])
            total_ppn = sum([invoice.total_ppn or 0 for invoice in invoices])
            total_amount = sum([invoice.total_harga or 0 for invoice in invoices])

            with col1:
                st.metric("Total Invoices", total_invoices)
            with col2:
                st.metric("Total Parts", total_parts_all)
            with col3:
                st.metric("Before Discount", f"Rp {total_before_discount:,.0f}")
            with col4:
                st.metric("Total Discount", f"Rp {total_discount:,.0f}")
            with col5:
                st.metric("Total PPN", f"Rp {total_ppn:,.0f}")
            with col6:
                st.metric("Final Amount", f"Rp {total_amount:,.0f}")
        else:
            st.warning("No parts invoice data found matching your search criteria.")

    except Exception as e:
        st.error(f"Error loading parts invoice data: {str(e)}")
    finally:
        session.close()


def render_spk_dealing_process_data_page(dealer_id):
    """Render SPK dealing process data table with search and pagination"""
    st.subheader("📋 SPK Dealing Process Data")
    st.markdown(f"**Dealer:** {dealer_id}")

    # Search and pagination controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search by SPK ID, Prospect ID, Customer Name, or KTP...")

    with col2:
        page_size = st.selectbox("Records per page", [25, 50, 100], index=1)

    with col3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Initialize page number in session state
    if 'spk_dealing_process_page' not in st.session_state:
        st.session_state.spk_dealing_process_page = 1

    # Get data
    data, total_count = get_spk_dealing_process_data_table(dealer_id, st.session_state.spk_dealing_process_page, page_size, search_term)

    # Display summary
    st.info(f"📊 Total records: {total_count} | Showing page {st.session_state.spk_dealing_process_page}")

    if data:
        # Display data table
        df = pd.DataFrame(data)

        # Configure columns for better display
        column_config = {
            "SPK ID": st.column_config.TextColumn("SPK ID", width="medium"),
            "Prospect ID": st.column_config.TextColumn("Prospect ID", width="medium"),
            "Customer Name": st.column_config.TextColumn("Customer Name", width="medium"),
            "KTP Number": st.column_config.TextColumn("KTP Number", width="medium"),
            "Contact": st.column_config.TextColumn("Contact", width="small"),
            "Email": st.column_config.TextColumn("Email", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Order Date": st.column_config.TextColumn("Order Date", width="medium"),
            "Created": st.column_config.TextColumn("Created", width="medium")
        }

        st.dataframe(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )

        # Arrow pagination controls
        total_pages = (total_count + page_size - 1) // page_size

        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First", key="spk_dealing_process_first") and st.session_state.spk_dealing_process_page > 1:
                    st.session_state.spk_dealing_process_page = 1
                    st.rerun()

            with col2:
                if st.button("⏪ Previous", key="spk_dealing_process_prev") and st.session_state.spk_dealing_process_page > 1:
                    st.session_state.spk_dealing_process_page -= 1
                    st.rerun()

            with col3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.spk_dealing_process_page} of {total_pages}</div>", unsafe_allow_html=True)

            with col4:
                if st.button("Next ⏩", key="spk_dealing_process_next") and st.session_state.spk_dealing_process_page < total_pages:
                    st.session_state.spk_dealing_process_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️", key="spk_dealing_process_last") and st.session_state.spk_dealing_process_page < total_pages:
                    st.session_state.spk_dealing_process_page = total_pages
                    st.rerun()
    else:
        st.warning("No SPK dealing process data found for the selected dealer.")


@st.cache_data(ttl=60)
def get_spk_dealing_process_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get SPK dealing process data for table display with pagination"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        params = {
            "dealer_id": dealer_id,
            "page": page,
            "limit": page_size
        }

        if search_term:
            params["search"] = search_term

        response = requests.get(f"{backend_url}/spk_dealing_process/", params=params)

        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                # Format data for display
                formatted_data = []
                for item in result["data"]:
                    formatted_data.append({
                        "SPK ID": item.get("id_spk", "N/A"),
                        "Prospect ID": item.get("id_prospect", "N/A"),
                        "Customer Name": item.get("nama_customer", "N/A"),
                        "KTP Number": item.get("no_ktp", "N/A"),
                        "Contact": item.get("no_kontak", "N/A"),
                        "Email": item.get("email", "N/A"),
                        "Status": item.get("status_spk", "N/A"),
                        "Order Date": item.get("tanggal_pesanan", "N/A"),
                        "Created": item.get("created_time", "N/A")
                    })

                return formatted_data, result["pagination"]["total"]

        return [], 0

    except Exception as e:
        st.error(f"Error fetching SPK dealing process data: {e}")
        return [], 0


# Main content routing
if current_page == "home":
    # New home page with dashboard charts (no dealer filter dependency)
    render_home_page()
elif selected_dealer_id:
    if current_page == "fetch_logs":
        # Fetch logs page (previously home page)
        render_fetch_logs_page(selected_dealer_id)
    elif current_page == "prospect":
        # Prospect data page
        render_prospect_data_page(selected_dealer_id)
    elif current_page == "pkb":
        # PKB data page
        render_pkb_data_page(selected_dealer_id)
    elif current_page == "parts_inbound":
        # Parts Inbound data page
        render_parts_inbound_data_page(selected_dealer_id)
    elif current_page == "leasing":
        # Leasing data page
        render_leasing_data_page(selected_dealer_id)

    elif current_page == "doch_read":
        # Document handling data page
        render_document_handling_data_page(selected_dealer_id)

    elif current_page == "uinb_read":
        # Unit inbound data page
        render_unit_inbound_data_page(selected_dealer_id)

    elif current_page == "bast_read":
        # Delivery process data page
        render_delivery_process_data_page(selected_dealer_id)

    elif current_page == "inv1_read":
        # Billing process data page
        render_billing_process_data_page(selected_dealer_id)

    elif current_page == "mdinvh1_read":
        # Unit invoice data page
        render_unit_invoice_data_page(selected_dealer_id)

    elif current_page == "prsl_read":
        # Parts sales data page
        render_parts_sales_data_page(selected_dealer_id)

    elif current_page == "dphlo_read":
        # DP HLO data page
        render_dp_hlo_data_page(selected_dealer_id)

    elif current_page == "inv2_read":
        # Workshop invoice data page
        render_workshop_invoice_data_page(selected_dealer_id)

    elif current_page == "unpaidhlo_read":
        # Unpaid HLO data page
        render_unpaid_hlo_data_page(selected_dealer_id)

    elif current_page == "mdinvh3_read":
        # Parts invoice data page
        render_parts_invoice_data_page(selected_dealer_id)

    elif current_page == "spk_read":
        # SPK dealing process data page
        render_spk_dealing_process_data_page(selected_dealer_id)
else:
    if current_page != "home":
        st.warning("Please select a dealer from the sidebar to view data.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        📊 Analytics Dashboard | Direct DB Connection | Port 8501
    </div>
    """,
    unsafe_allow_html=True
)
