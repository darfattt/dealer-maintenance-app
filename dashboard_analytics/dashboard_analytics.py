import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker
from database import Dealer, ProspectData, ProspectUnit, FetchLog, PKBData, PKBService, PKBPart, PartsInboundData, PartsInboundPO, LeasingData, DocumentHandlingData, DocumentHandlingUnit, UnitInboundData, UnitInboundUnit, DeliveryProcessData, DeliveryProcessDetail, BillingProcessData, UnitInvoiceData, UnitInvoiceUnit

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")

# Create database connection
@st.cache_resource
def get_database_connection():
    engine = create_engine(DATABASE_URL)
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
    "👥 Prospect Data": "prospect",
    "🔧 PKB Data": "pkb",
    "📦 Parts Inbound": "parts_inbound",
    "💰 Leasing Data": "leasing",
    "📄 Document Handling": "doch_read",
    "🚚 Unit Inbound": "uinb_read",
    "🚛 Delivery Process": "bast_read",
    "💳 Billing Process": "inv1_read",
    "📋 Unit Invoice": "mdinvh1_read"
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

def render_home_page(dealer_id):
    """Render the home analytics page"""
    # Get analytics data
    analytics = get_prospect_analytics(dealer_id)

    # Key metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Prospects",
            value=analytics['total_prospects'],
            delta=None
        )

    with col2:
        st.metric(
            label="Recent (7 days)",
            value=analytics['recent_prospects'],
            delta=None
        )

    with col3:
        st.metric(
            label="Active Prospects",
            value=analytics['active_prospects'],
            delta=None
        )

    with col4:
        success_rate = 85  # Placeholder
        st.metric(
            label="Success Rate",
            value=f"{success_rate}%",
            delta="5%"
        )

    st.markdown("---")

    # Charts section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Daily Prospect Trends")
        if analytics['daily_counts']:
            df_daily = pd.DataFrame(analytics['daily_counts'])
            df_daily['date'] = pd.to_datetime(df_daily['date'])

            fig_line = px.line(
                df_daily,
                x='date',
                y='count',
                title="Daily Prospect Count",
                markers=True
            )
            fig_line.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Prospects",
                showlegend=False
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No daily data available")

    with col2:
        st.subheader("📊 Status Distribution")
        if analytics['status_distribution']:
            df_status = pd.DataFrame(analytics['status_distribution'])

            # Map status codes to labels
            status_labels = {
                '1': 'New',
                '2': 'In Progress',
                '3': 'Completed',
                '4': 'Cancelled'
            }
            df_status['status_label'] = df_status['status'].map(status_labels)

            fig_pie = px.pie(
                df_status,
                values='count',
                names='status_label',
                title="Prospect Status Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No status data available")

    # Unit distribution chart
    st.subheader("🏍️ Unit Type Distribution")
    if analytics['unit_distribution']:
        df_units = pd.DataFrame(analytics['unit_distribution'])

        fig_bar = px.bar(
            df_units,
            x='unit',
            y='count',
            title="Preferred Unit Types",
            color='count',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(
            xaxis_title="Unit Type",
            yaxis_title="Number of Prospects",
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No unit data available")

    # Recent activity
    st.markdown("---")
    st.subheader("🕒 Recent Data Fetch Activity")

    recent_logs = get_recent_fetch_logs(dealer_id)
    if recent_logs and len(recent_logs) > 0:
        df_logs = pd.DataFrame(recent_logs)

        # Display as metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            # Safe access to first row
            last_fetch_time = recent_logs[0]['completed_at'] if recent_logs else "No data"
            st.metric("Last Fetch", last_fetch_time)

        with col2:
            success_count = len([log for log in recent_logs if log['status'] == 'success'])
            st.metric("Recent Success", f"{success_count}/{len(recent_logs)}")

        with col3:
            avg_duration = sum([log['duration'] or 0 for log in recent_logs]) / len(recent_logs)
            st.metric("Avg Duration", f"{avg_duration:.1f}s")

        # Display logs table
        st.dataframe(
            df_logs[['status', 'records_fetched', 'duration', 'completed_at']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent fetch activity found")

        # Show placeholder metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Last Fetch", "No data")
        with col2:
            st.metric("Recent Success", "0/0")
        with col3:
            st.metric("Avg Duration", "N/A")

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

            # Auto-refresh option
            if st.checkbox("🔄 Auto-refresh (30s)"):
                time.sleep(30)
                st.rerun()
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

            # Auto-refresh option
            if st.checkbox("🔄 Auto-refresh (30s)"):
                time.sleep(30)
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

            # Auto-refresh option
            if st.checkbox("🔄 Auto-refresh (30s)"):
                time.sleep(30)
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

            # Auto-refresh option
            if st.checkbox("🔄 Auto-refresh (30s)"):
                time.sleep(30)
                st.rerun()
    else:
        st.warning("No Unit Invoice data found for the selected dealer.")


# Main content routing
if selected_dealer_id:
    if current_page == "home":
        # Home page - existing analytics dashboard
        render_home_page(selected_dealer_id)
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
