"""
Run Jobs Component
Handles job execution for single dealers and bulk operations
"""

import streamlit as st
import time
from datetime import date, timedelta
from typing import Dict, List, Any
from .api_utils import get_dealers, run_manual_job, get_job_status, run_jobs_for_all_dealers
from .job_types import code_to_label

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

        # Data type selection
        st.markdown("**📊 Select Data Type to Fetch:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            fetch_prospect = st.checkbox("🎯 Prospect", value=True, help="Fetch customer prospect data")

        with col2:
            fetch_pkb = st.checkbox("🔧 Manage WO - PKB", value=False, help="Fetch service record data")

        with col3:
            fetch_parts_inbound = st.checkbox("📦 Part Inbound - PINB", value=False, help="Fetch parts receiving data")

        if not fetch_prospect and not fetch_pkb and not fetch_parts_inbound:
            st.warning("⚠️ Please select at least one data type to fetch")

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            run_single_job = st.form_submit_button("🔄 Run Data Fetch Job", use_container_width=True)

    if run_single_job:
        if fetch_prospect or fetch_pkb or fetch_parts_inbound:
            execute_single_job(selected_dealer, from_date, to_date, fetch_prospect, fetch_pkb, fetch_parts_inbound)
        else:
            st.error("❌ Please select at least one data type to fetch")

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

        # Data type selection for bulk jobs
        st.markdown("**📊 Select Data Types to Fetch for All Dealers:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            fetch_prospect_all = st.checkbox("🎯 Prospect", value=True, key="prospect_all", help="Fetch customer prospect data")

        with col2:
            fetch_pkb_all = st.checkbox("🔧 Manage WO - PKB", value=False, key="pkb_all", help="Fetch service record data")

        with col3:
            fetch_parts_inbound_all = st.checkbox("📦 Part Inbound - PINB", value=False, key="parts_inbound_all", help="Fetch parts receiving data")

        if not fetch_prospect_all and not fetch_pkb_all and not fetch_parts_inbound_all:
            st.warning("⚠️ Please select at least one data type to fetch")

        st.markdown("---")
        st.warning("⚠️ This will start jobs for ALL active dealers. This may take some time.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            run_all_jobs = st.form_submit_button("🚀 Run Jobs for All Dealers", use_container_width=True)

    if run_all_jobs:
        if fetch_prospect_all or fetch_pkb_all or fetch_parts_inbound_all:
            execute_bulk_jobs(active_dealers, from_date_all, to_date_all, fetch_prospect_all, fetch_pkb_all, fetch_parts_inbound_all)
        else:
            st.error("❌ Please select at least one data type to fetch")

def execute_single_job(dealer_id: str, from_date: date, to_date: date, fetch_prospect: bool, fetch_pkb: bool, fetch_parts_inbound: bool):
    """Execute a single dealer job"""
    if from_date <= to_date:
        from_time = f"{from_date} 00:00:00"
        to_time = f"{to_date} 23:59:59"

        jobs_started = []

        # Start prospect data job if selected
        if fetch_prospect:
            with st.spinner("🔄 Starting Prospect job..."):
                result = run_manual_job(dealer_id, from_time, to_time, "prospect")
                if result:
                    jobs_started.append((code_to_label("prospect"), result))

        # Start PKB data job if selected
        if fetch_pkb:
            with st.spinner("🔄 Starting Manage WO - PKB job..."):
                result = run_manual_job(dealer_id, from_time, to_time, "pkb")
                if result:
                    jobs_started.append((code_to_label("pkb"), result))

        # Start Parts Inbound data job if selected
        if fetch_parts_inbound:
            with st.spinner("🔄 Starting Part Inbound - PINB job..."):
                result = run_manual_job(dealer_id, from_time, to_time, "parts_inbound")
                if result:
                    jobs_started.append((code_to_label("parts_inbound"), result))

        if jobs_started:
            st.success(f"✅ {len(jobs_started)} job(s) started successfully!")

            # Show job details for each started job
            for job_type, result in jobs_started:
                st.subheader(f"📊 {job_type} Job")
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
            st.error("❌ Failed to start any jobs")
    else:
        st.error("❌ From date must be before or equal to To date")

def execute_bulk_jobs(active_dealers: List[Dict[str, Any]], from_date: date, to_date: date, fetch_prospect: bool, fetch_pkb: bool, fetch_parts_inbound: bool):
    """Execute jobs for all active dealers"""
    if from_date <= to_date:
        from_time = f"{from_date} 00:00:00"
        to_time = f"{to_date} 23:59:59"

        all_results = []

        # Execute prospect data jobs if selected
        if fetch_prospect:
            with st.spinner(f"🔄 Starting Prospect jobs for {len(active_dealers)} dealers..."):
                prospect_results = run_jobs_for_all_dealers(from_time, to_time, "prospect")
                if prospect_results:
                    all_results.extend([(r, code_to_label("prospect")) for r in prospect_results])

        # Execute PKB data jobs if selected
        if fetch_pkb:
            with st.spinner(f"🔄 Starting Manage WO - PKB jobs for {len(active_dealers)} dealers..."):
                pkb_results = run_jobs_for_all_dealers(from_time, to_time, "pkb")
                if pkb_results:
                    all_results.extend([(r, code_to_label("pkb")) for r in pkb_results])

        # Execute Parts Inbound data jobs if selected
        if fetch_parts_inbound:
            with st.spinner(f"🔄 Starting Part Inbound - PINB jobs for {len(active_dealers)} dealers..."):
                parts_inbound_results = run_jobs_for_all_dealers(from_time, to_time, "parts_inbound")
                if parts_inbound_results:
                    all_results.extend([(r, code_to_label("parts_inbound")) for r in parts_inbound_results])

        if all_results:
            st.success(f"✅ Started {len(all_results)} job(s)!")

            # Show results summary
            display_bulk_job_results(all_results)

            st.info("💡 Check 'Job History' page to monitor the progress of all jobs.")
        else:
            st.error("❌ Failed to start any jobs")
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
        
        # Use st.empty() and rerun instead of sleep
        st.rerun()
        wait_time += 2
    
    if wait_time >= max_wait:
        status_placeholder.warning("⏳ Job is taking longer than expected. Check Job History for updates.")

def display_bulk_job_results(results: List[tuple]):
    """Display results of bulk job execution"""
    # Show results summary
    col1, col2, col3 = st.columns(3)

    successful_jobs = [r for r, _ in results if r.get('status') != 'failed']
    failed_jobs = [r for r, _ in results if r.get('status') == 'failed']

    with col1:
        st.metric("Total Jobs", len(results))
    with col2:
        st.metric("Successful", len(successful_jobs))
    with col3:
        st.metric("Failed", len(failed_jobs))

    # Show detailed results
    st.subheader("📋 Job Execution Results")

    for result, job_type in results:
        if result.get('status') == 'failed':
            st.error(f"❌ **{result['dealer_id']}** ({result['dealer_name']}) - {job_type}: {result.get('error', 'Unknown error')}")
        else:
            st.success(f"✅ **{result['dealer_id']}** ({result['dealer_name']}) - {job_type}: Task ID {result.get('task_id', 'N/A')}")
