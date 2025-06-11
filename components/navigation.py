"""
Navigation Component
Handles sidebar navigation and page routing
"""

import streamlit as st
from typing import Dict, Any

# Page constants
DEALER_MANAGEMENT = "🏢 Dealer Management"
RUN_JOBS = "🚀 Run Jobs"
JOB_HISTORY = "📋 Job History"
CONFIGURATION = "⚙️ Configuration"

# Page mapping
PAGES = {
    DEALER_MANAGEMENT: "dealer_management",
    RUN_JOBS: "run_jobs",
    JOB_HISTORY: "job_history",
    CONFIGURATION: "configuration"
}

def render_sidebar_navigation() -> str:
    """Render sidebar navigation and return current page"""
    st.sidebar.title("⚙️ Admin Panel")
    st.sidebar.markdown("---")
    
    # Initialize session state for page navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = DEALER_MANAGEMENT
    
    # Navigation buttons
    if st.sidebar.button(DEALER_MANAGEMENT, use_container_width=True):
        st.session_state.current_page = DEALER_MANAGEMENT
    
    if st.sidebar.button(RUN_JOBS, use_container_width=True):
        st.session_state.current_page = RUN_JOBS
    
    if st.sidebar.button(JOB_HISTORY, use_container_width=True):
        st.session_state.current_page = JOB_HISTORY
    
    if st.sidebar.button(CONFIGURATION, use_container_width=True):
        st.session_state.current_page = CONFIGURATION
    
    # Add current page indicator
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Current Page:** {st.session_state.current_page}")
    st.sidebar.markdown("---")
    
    # Add system info
    render_system_info()
    
    return st.session_state.current_page

def render_system_info():
    """Render system information in sidebar"""
    with st.sidebar.expander("ℹ️ System Info"):
        st.markdown("""
        **Admin Panel v2.0**
        - 🏢 Dealer Management
        - 🚀 Job Execution
        - 📋 History Tracking
        - ⚙️ Configuration
        
        **Quick Actions:**
        - Add new dealers
        - Run bulk jobs
        - Monitor performance
        - View analytics
        """)

def get_page_config(page: str) -> Dict[str, Any]:
    """Get configuration for the current page"""
    configs = {
        DEALER_MANAGEMENT: {
            "icon": "🏢",
            "title": "Dealer Management",
            "description": "Manage dealer accounts, API credentials, and status",
            "features": ["View Dealers", "Add Dealer", "Edit Dealer"]
        },
        RUN_JOBS: {
            "icon": "🚀",
            "title": "Run Jobs",
            "description": "Execute data fetch jobs for single or multiple dealers",
            "features": ["Single Dealer Jobs", "Bulk Operations", "Real-time Monitoring"]
        },
        JOB_HISTORY: {
            "icon": "📋",
            "title": "Job History",
            "description": "View job execution history and performance analytics",
            "features": ["Execution Logs", "Performance Metrics", "Error Tracking"]
        },
        CONFIGURATION: {
            "icon": "⚙️",
            "title": "Configuration",
            "description": "System settings and configuration management",
            "features": ["API Settings", "Database Config", "Notifications"]
        }
    }
    
    return configs.get(page, {})

def render_page_header(page: str):
    """Render page header with breadcrumb and info"""
    config = get_page_config(page)
    
    if config:
        # Page header
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title(f"{config['icon']} {config['title']}")
            st.caption(config['description'])
        
        with col2:
            # Quick help button
            if st.button("❓ Help", key=f"help_{page}"):
                show_page_help(page, config)

def show_page_help(page: str, config: Dict[str, Any]):
    """Show help information for the current page"""
    with st.expander("📖 Page Help", expanded=True):
        st.markdown(f"**{config['title']} Features:**")
        for feature in config.get('features', []):
            st.markdown(f"• {feature}")
        
        # Page-specific help
        if page == DEALER_MANAGEMENT:
            st.markdown("""
            **How to use:**
            1. **View Dealers**: See all dealers with status indicators
            2. **Add Dealer**: Create new dealer accounts with API credentials
            3. **Edit Dealer**: Update dealer information and status
            
            **Tips:**
            - Use the ✏️ Edit button for quick access to dealer editing
            - Active dealers will appear in job execution options
            - API credentials are required for data fetching
            """)
        
        elif page == RUN_JOBS:
            st.markdown("""
            **How to use:**
            1. **Single Dealer**: Run jobs for individual dealers
            2. **All Dealers**: Execute jobs for all active dealers at once
            3. **Monitor Progress**: Watch real-time job execution status
            
            **Tips:**
            - Only active dealers will be included in bulk operations
            - Use appropriate date ranges for data fetching
            - Check Job History for detailed execution logs
            """)
        
        elif page == JOB_HISTORY:
            st.markdown("""
            **How to use:**
            1. **Filter Logs**: Use dealer and status filters
            2. **Search**: Find specific jobs using the search box
            3. **Export**: Download job history as CSV
            
            **Tips:**
            - Use filters to focus on specific dealers or statuses
            - Search functionality works across all log fields
            - Export data for external analysis
            """)
        
        elif page == CONFIGURATION:
            st.markdown("""
            **Available Settings:**
            1. **API Settings**: View and configure API endpoints
            2. **Database**: Monitor database connection status
            3. **Scheduling**: Future automatic job scheduling
            4. **Notifications**: Future email and alert settings
            
            **Note:**
            - Most settings are read-only in current version
            - Advanced features will be added in future updates
            """)

def render_breadcrumb(page: str):
    """Render breadcrumb navigation"""
    st.markdown(f"**Admin Panel** > **{page}**")
    st.markdown("---")
