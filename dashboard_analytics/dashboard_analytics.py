import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database import Dealer, ProspectData, ProspectUnit, FetchLog

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

# Main app
st.markdown('<div class="main-header">📊 Dealer Analytics Dashboard</div>', unsafe_allow_html=True)

# Sidebar for dealer selection
st.sidebar.title("📊 Analytics Dashboard")
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

# Main content
if selected_dealer_id:
    # Get analytics data
    analytics = get_prospect_analytics(selected_dealer_id)
    
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

    recent_logs = get_recent_fetch_logs(selected_dealer_id)
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
