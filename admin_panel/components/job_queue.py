"""
Job Queue Management Component
Sequential job execution to prevent database conflicts
"""

import streamlit as st
import requests
import time
from typing import Dict, Any, List
from datetime import datetime, date, time, timedelta

from .api_utils import BACKEND_URL


def combine_date_time(date_input, time_input):
    """Combine date and time inputs into datetime string"""
    if date_input is None:
        return None

    if time_input is None:
        # Use start of day (00:00:00) if no time specified
        return f"{date_input} 00:00:00"

    return f"{date_input} {time_input}"


def render_job_queue():
    """Render the job queue management page"""
    st.header("🔄 Job Queue Management")

    # Auto-refresh control
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        auto_refresh = st.checkbox("Auto-refresh (5 seconds)", value=False, key="auto_refresh_toggle")
    with col2:
        if st.button("🔄 Refresh Now", key="manual_refresh_btn"):
            st.rerun()
    with col3:
        if st.button("🗑️ Clear Completed", key="clear_completed_btn"):
            clear_completed_jobs()
            st.rerun()

    # Queue Status Section
    st.subheader("📊 Queue Status")

    # Get queue status
    queue_status = get_queue_status()

    if queue_status:
        display_queue_status(queue_status)
        display_current_job(queue_status.get('current_job'))
        display_queued_jobs(queue_status.get('queued_jobs', []))
    else:
        st.error("Failed to fetch queue status")

    st.divider()

    # Add New Job Section
    st.subheader("➕ Add Jobs to Queue")
    st.info("📋 **Required fields marked with *** | Default: Yesterday to Today (00:00-23:59)**")

    # Get dealers list for dropdown
    dealers = get_dealers_list()
    dealer_options = []
    if dealers:
        dealer_options = [f"{dealer['dealer_id']} - {dealer.get('dealer_name', 'Unknown')}" for dealer in dealers]
    else:
        dealer_options = ["12284 - Sample Dealer", "00999 - Test Dealer"]  # Fallback options

    # Enhanced job form with multiple dealer selection
    with st.form("job_form"):
        # Multiple dealer selection (required)
        selected_dealers = st.multiselect(
            "Select Dealers *",
            dealer_options,
            default=[dealer_options[0]] if dealer_options else [],
            help="Select one or more dealers (required)"
        )

        # Multiple fetch types selection (required)
        fetch_types = st.multiselect(
            "Job Types *",
            ["prospect", "pkb", "parts_inbound"],
            default=["prospect"],
            help="Select one or more job types to add to queue (required)"
        )

        # Date pickers for time range (required with defaults)
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            # Default to yesterday
            yesterday = date.today() - timedelta(days=1)
            from_date = st.date_input("From Date *", value=yesterday)
        with col_date2:
            # Default to today
            today = date.today()
            to_date = st.date_input("To Date *", value=today)

        # Time inputs with default values
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            from_time_input = st.time_input("From Time", value=time(0, 0))  # Default 00:00
        with col_time2:
            to_time_input = st.time_input("To Time", value=time(23, 59))  # Default 23:59

        # PO Number for Parts Inbound
        no_po = st.text_input("PO Number (Parts Inbound only)", placeholder="Optional")

        if st.form_submit_button("🚀 Add Jobs to Queue"):
            # Validate required fields
            if not selected_dealers:
                st.error("❌ Please select at least one dealer (required)")
            elif not fetch_types:
                st.error("❌ Please select at least one job type (required)")
            elif not from_date:
                st.error("❌ From Date is required")
            elif not to_date:
                st.error("❌ To Date is required")
            elif from_date > to_date:
                st.error("❌ From Date cannot be later than To Date")
            else:
                # Extract dealer IDs
                dealer_ids = [dealer.split(" - ")[0] for dealer in selected_dealers]

                # Combine date and time
                from_datetime = combine_date_time(from_date, from_time_input)
                to_datetime = combine_date_time(to_date, to_time_input)

                # Add jobs for each combination of dealer and fetch type
                total_jobs = 0
                success_jobs = 0

                for dealer_id in dealer_ids:
                    for fetch_type in fetch_types:
                        total_jobs += 1
                        if add_single_job_to_queue(dealer_id, fetch_type, from_datetime, to_datetime, no_po):
                            success_jobs += 1

                if success_jobs > 0:
                    st.success(f"✅ Added {success_jobs}/{total_jobs} job(s) to queue")
                    if success_jobs < total_jobs:
                        st.warning(f"⚠️ {total_jobs - success_jobs} job(s) failed to add")
                    st.rerun()
                else:
                    st.error("❌ Failed to add any jobs to queue")

    # Simple auto-refresh - only when enabled
    if auto_refresh:
        time.sleep(5)
        st.rerun()


def display_queue_status(queue_status: Dict[str, Any]):
    """Display overall queue status"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Queue Length", queue_status.get('queue_length', 0))
    
    with col2:
        is_processing = queue_status.get('is_processing', False)
        st.metric("Status", "🟢 Processing" if is_processing else "🔴 Idle")
    
    with col3:
        current_job = queue_status.get('current_job')
        st.metric("Current Job", "Running" if current_job else "None")
    
    with col4:
        st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))


def display_current_job(current_job: Dict[str, Any]):
    """Display currently running job"""
    if current_job:
        st.subheader("🏃 Currently Running Job")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**Job ID:** {current_job['id'][:8]}...")
        with col2:
            st.write(f"**Dealer:** {current_job['dealer_id']}")
        with col3:
            st.write(f"**Type:** {current_job['fetch_type'].title()}")
        with col4:
            status_color = "🟢" if current_job['status'] == 'running' else "🔴"
            st.write(f"**Status:** {status_color} {current_job['status'].title()}")
        
        if current_job.get('started_at'):
            started_time = datetime.fromisoformat(current_job['started_at'])
            duration = datetime.now() - started_time
            st.write(f"**Running for:** {duration.seconds} seconds")
    else:
        st.info("No job currently running")


def display_queued_jobs(queued_jobs: List[Dict[str, Any]]):
    """Display queued jobs"""
    st.subheader(f"📋 Queued Jobs ({len(queued_jobs)})")
    
    if not queued_jobs:
        st.info("No jobs in queue")
        return
    
    for i, job in enumerate(queued_jobs):
        with st.expander(f"Job {i+1}: {job['fetch_type'].title()} - {job['dealer_id']} ({job['status']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Job ID:** {job['id']}")
                st.write(f"**Dealer ID:** {job['dealer_id']}")
                st.write(f"**Job Type:** {job['fetch_type'].title()}")
                st.write(f"**Status:** {job['status'].title()}")
                st.write(f"**Created:** {job.get('created_at', 'Unknown')}")
                
                if job.get('error_message'):
                    st.error(f"Error: {job['error_message']}")
                
                if job.get('result'):
                    st.success(f"Result: {job['result']}")
            
            with col2:
                if job['status'] == 'queued':
                    if st.button(f"❌ Cancel", key=f"cancel_{job['id']}"):
                        cancel_job(job['id'])
                        st.rerun()


def get_queue_status() -> Dict[str, Any]:
    """Get queue status from API"""
    try:
        response = requests.get(f"{BACKEND_URL}/jobs/queue/status")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch queue status: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Error fetching queue status: {e}")
        return {}


def get_dealers_list() -> List[Dict[str, Any]]:
    """Get list of dealers from API"""
    try:
        response = requests.get(f"{BACKEND_URL}/dealers")
        if response.status_code == 200:
            dealers = response.json()
            return dealers if isinstance(dealers, list) else []
        else:
            st.error(f"Failed to fetch dealers: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching dealers: {e}")
        return []


def add_single_job_to_queue(dealer_id: str, fetch_type: str, from_time: str = None, to_time: str = None, no_po: str = None) -> bool:
    """Add a single job to the queue"""
    try:
        data = {
            "dealer_id": dealer_id,
            "fetch_type": fetch_type,
            "from_time": from_time,
            "to_time": to_time,
            "no_po": no_po
        }

        # Remove None values to avoid sending them to API
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{BACKEND_URL}/jobs/queue", json=data)

        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Job added to queue: {result['job_id'][:8]}...")
            return True
        else:
            st.error(f"Failed to add job: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        st.error(f"Error adding job to queue: {e}")
        return False





def cancel_job(job_id: str):
    """Cancel a queued job"""
    try:
        response = requests.delete(f"{BACKEND_URL}/jobs/queue/{job_id}")
        
        if response.status_code == 200:
            st.success("✅ Job cancelled")
        else:
            st.error(f"Failed to cancel job: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error cancelling job: {e}")


def clear_completed_jobs():
    """Clear completed jobs from queue"""
    try:
        response = requests.delete(f"{BACKEND_URL}/jobs/queue/completed")
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Cleared {result['cleared_count']} completed jobs")
        else:
            st.error(f"Failed to clear completed jobs: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error clearing completed jobs: {e}")
