"""
Job History Component
Handles job history display and filtering
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from .api_utils import get_dealers, get_fetch_logs

def render_job_history():
    """Render the job history page"""
    st.header("📋 Job Execution History")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        dealers = get_dealers()
        dealer_options = ["All Dealers"] + [d['dealer_id'] for d in dealers]
        selected_dealer_filter = st.selectbox("Filter by Dealer", dealer_options)
    
    with col2:
        status_options = ["All Status", "success", "failed", "running"]
        selected_status_filter = st.selectbox("Filter by Status", status_options)
    
    # Fetch logs
    dealer_id_filter = None if selected_dealer_filter == "All Dealers" else selected_dealer_filter
    
    logs = get_fetch_logs(dealer_id_filter)
    
    if logs:
        display_job_metrics(logs, selected_status_filter)
        display_job_logs_table(logs, selected_status_filter)
    else:
        st.info("No job history found.")

def display_job_metrics(logs: List[Dict[str, Any]], status_filter: str):
    """Display job execution metrics"""
    # Convert to DataFrame for easier filtering
    df = pd.DataFrame(logs)
    df['completed_at'] = pd.to_datetime(df['completed_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Filter by status if needed
    if status_filter != "All Status":
        df = df[df['status'] == status_filter]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", len(df))
    
    with col2:
        success_count = len(df[df['status'] == 'success'])
        st.metric("Successful", success_count)
    
    with col3:
        failed_count = len(df[df['status'] == 'failed'])
        st.metric("Failed", failed_count)
    
    with col4:
        if len(df) > 0:
            avg_duration = df['fetch_duration_seconds'].mean()
            st.metric("Avg Duration", f"{avg_duration:.1f}s")
        else:
            st.metric("Avg Duration", "N/A")
    
    st.markdown("---")

def display_job_logs_table(logs: List[Dict[str, Any]], status_filter: str):
    """Display job logs in a table format"""
    # Convert to DataFrame
    df = pd.DataFrame(logs)
    df['completed_at'] = pd.to_datetime(df['completed_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Filter by status if needed
    if status_filter != "All Status":
        df = df[df['status'] == status_filter]
    
    if len(df) == 0:
        st.info(f"No jobs found with status: {status_filter}")
        return
    
    # Prepare display columns
    display_columns = ['dealer_id', 'status', 'records_fetched', 'fetch_duration_seconds', 'completed_at']
    if 'error_message' in df.columns:
        display_columns.append('error_message')
    
    # Create a more interactive display
    st.subheader("📊 Job Execution Logs")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search logs", placeholder="Search by dealer ID, status, etc.")
    
    if search_term:
        # Filter dataframe based on search term
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df = df[mask]
    
    # Display the filtered dataframe
    if len(df) > 0:
        # Style the dataframe based on status
        def style_status(val):
            if val == 'success':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'failed':
                return 'background-color: #f8d7da; color: #721c24'
            elif val == 'running':
                return 'background-color: #d1ecf1; color: #0c5460'
            return ''
        
        # Apply styling and display
        styled_df = df[display_columns].style.map(style_status, subset=['status'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Add pagination for large datasets
        if len(df) > 50:
            st.info(f"Showing {min(50, len(df))} of {len(df)} records. Use search to filter results.")
        
        # Export functionality
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"job_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No logs match your search criteria.")

def display_job_details(job_id: str):
    """Display detailed information for a specific job"""
    # This could be expanded to show more detailed job information
    # For now, it's a placeholder for future enhancement
    st.info(f"Detailed view for job {job_id} - Feature coming soon!")

def render_job_analytics():
    """Render job analytics and trends"""
    st.subheader("📈 Job Analytics")
    
    logs = get_fetch_logs()
    if not logs:
        st.info("No job data available for analytics.")
        return
    
    df = pd.DataFrame(logs)
    df['completed_at'] = pd.to_datetime(df['completed_at'])
    df['date'] = df['completed_at'].dt.date
    
    # Daily job counts
    daily_counts = df.groupby('date').size().reset_index(name='job_count')
    
    if len(daily_counts) > 0:
        st.line_chart(daily_counts.set_index('date')['job_count'])
    
    # Success rate by dealer
    dealer_stats = df.groupby('dealer_id').agg({
        'status': ['count', lambda x: (x == 'success').sum()],
        'fetch_duration_seconds': 'mean'
    }).round(2)
    
    dealer_stats.columns = ['Total Jobs', 'Successful Jobs', 'Avg Duration (s)']
    dealer_stats['Success Rate (%)'] = (dealer_stats['Successful Jobs'] / dealer_stats['Total Jobs'] * 100).round(1)
    
    st.subheader("📊 Dealer Performance")
    st.dataframe(dealer_stats, use_container_width=True)
