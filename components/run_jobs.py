"""
Run Jobs Component
Handles job execution for single dealers and bulk operations
"""

import streamlit as st
import time
from datetime import date, timedelta
from typing import Dict, List, Any
from .api_utils import get_dealers, run_manual_job, get_job_status, run_jobs_for_all_dealers

def render_run_jobs():
    """Render the run jobs page"""
    st.header("🚀 Run Data Fetch Jobs")
    
    dealers = get_dealers()
    if not dealers:
        st.warning("⚠️ No dealers available. Please add a dealer first.")
        return
    
    # Tabs for different job types
    tab1, tab2 = st.tabs(["🎯 Single Dealer", "🌐 All Dealers"])
    
    with tab1:
        render_single_dealer_jobs(dealers)
    
    with tab2:
        render_bulk_dealer_jobs(dealers)

def render_single_dealer_jobs(dealers: List[Dict[str, Any]]):
    """Render single dealer job execution"""
    st.subheader("🎯 Run Job for Single Dealer")
    
    # Job execution form for single dealer
    with st.form("run_single_job_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            active_dealers = [d for d in dealers if d.get('is_active', True)]
            if not active_dealers:
                st.warning("No active dealers available")
                return
                
            selected_dealer = st.selectbox(
                "Select Dealer",
                options=[d['dealer_id'] for d in active_dealers],
                format_func=lambda x: f"{x} - {next(d['dealer_name'] for d in dealers if d['dealer_id'] == x)}"
            )
        
        with col2:
            from_date = st.date_input(
                "From Date",
                value=date.today() - timedelta(days=7),
                max_value=date.today()
            )
        
        with col3:
            to_date = st.date_input(
                "To Date",
                value=date.today(),
                max_value=date.today()
            )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            run_single_job = st.form_submit_button("🔄 Run Data Fetch Job", use_container_width=True)
    
    if run_single_job:
        execute_single_job(selected_dealer, from_date, to_date)

def render_bulk_dealer_jobs(dealers: List[Dict[str, Any]]):
    """Render bulk dealer job execution"""
    st.subheader("🌐 Run Jobs for All Active Dealers")
    
    # Show active dealers count
    active_dealers = [d for d in dealers if d.get('is_active', True)]
    st.info(f"📊 Found {len(active_dealers)} active dealers")
    
    if not active_dealers:
        st.warning("⚠️ No active dealers found. Please activate dealers first.")
        return
    
    # Display active dealers
    with st.expander("👀 View Active Dealers", expanded=False):
        for dealer in active_dealers:
            st.write(f"• **{dealer['dealer_id']}** - {dealer['dealer_name']}")
    
    # Job execution form for all dealers
    with st.form("run_all_jobs_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            from_date_all = st.date_input(
                "From Date",
                value=date.today() - timedelta(days=7),
                max_value=date.today(),
                key="from_date_all"
            )
        
        with col2:
            to_date_all = st.date_input(
                "To Date",
                value=date.today(),
                max_value=date.today(),
                key="to_date_all"
            )
        
        st.markdown("---")
        st.warning("⚠️ This will start jobs for ALL active dealers. This may take some time.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            run_all_jobs = st.form_submit_button("🚀 Run Jobs for All Dealers", use_container_width=True)
    
    if run_all_jobs:
        execute_bulk_jobs(active_dealers, from_date_all, to_date_all)

def execute_single_job(dealer_id: str, from_date: date, to_date: date):
    """Execute a single dealer job"""
    if from_date <= to_date:
        from_time = f"{from_date} 00:00:00"
        to_time = f"{to_date} 23:59:59"
        
        with st.spinner("🔄 Starting job..."):
            result = run_manual_job(dealer_id, from_time, to_time)
            
            if result:
                st.success("✅ Job started successfully!")
                
                # Show job details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Task ID", result['task_id'])
                with col2:
                    st.metric("Dealer ID", result['dealer_id'])
                with col3:
                    st.metric("Status", result['status'])
                
                # Monitor job progress
                monitor_job_progress(result['task_id'])
    else:
        st.error("❌ From date must be before or equal to To date")

def execute_bulk_jobs(active_dealers: List[Dict[str, Any]], from_date: date, to_date: date):
    """Execute jobs for all active dealers"""
    if from_date <= to_date:
        from_time = f"{from_date} 00:00:00"
        to_time = f"{to_date} 23:59:59"
        
        with st.spinner(f"🔄 Starting jobs for {len(active_dealers)} dealers..."):
            results = run_jobs_for_all_dealers(from_time, to_time)
            
            if results:
                st.success(f"✅ Started {len(results)} jobs!")
                
                # Show results summary
                display_bulk_job_results(results)
                
                st.info("💡 Check 'Job History' page to monitor the progress of all jobs.")
    else:
        st.error("❌ From date must be before or equal to To date")

def monitor_job_progress(task_id: str):
    """Monitor and display job progress"""
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    max_wait = 60  # Maximum wait time in seconds
    wait_time = 0
    
    while wait_time < max_wait:
        status = get_job_status(task_id)
        
        if status:
            progress_placeholder.progress(min(wait_time / max_wait, 0.9))
            
            if status['status'] == 'SUCCESS':
                progress_placeholder.progress(1.0)
                status_placeholder.success("✅ Job completed successfully!")
                break
            elif status['status'] == 'FAILURE':
                status_placeholder.error("❌ Job failed!")
                break
            else:
                status_placeholder.info(f"🔄 Job status: {status['status']}")
        
        time.sleep(2)
        wait_time += 2
    
    if wait_time >= max_wait:
        status_placeholder.warning("⏳ Job is taking longer than expected. Check Job History for updates.")

def display_bulk_job_results(results: List[Dict[str, Any]]):
    """Display results of bulk job execution"""
    # Show results summary
    col1, col2, col3 = st.columns(3)
    
    successful_jobs = [r for r in results if r.get('status') != 'failed']
    failed_jobs = [r for r in results if r.get('status') == 'failed']
    
    with col1:
        st.metric("Total Jobs", len(results))
    with col2:
        st.metric("Successful", len(successful_jobs))
    with col3:
        st.metric("Failed", len(failed_jobs))
    
    # Show detailed results
    st.subheader("📋 Job Execution Results")
    
    for result in results:
        if result.get('status') == 'failed':
            st.error(f"❌ **{result['dealer_id']}** ({result['dealer_name']}): {result.get('error', 'Unknown error')}")
        else:
            st.success(f"✅ **{result['dealer_id']}** ({result['dealer_name']}): Task ID {result.get('task_id', 'N/A')}")
