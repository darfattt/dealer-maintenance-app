"""
Configuration Component
Handles system configuration and settings
"""

import streamlit as st
import os
import requests
from typing import Dict, Any, List

def render_configuration():
    """Render the configuration page"""
    st.header("⚙️ System Configuration")
    
    # Tabs for different configuration sections
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 API Settings", "📊 Database", "⏰ Scheduling", "🔔 Notifications"])
    
    with tab1:
        render_api_configuration()
    
    with tab2:
        render_database_configuration()
    
    with tab3:
        render_scheduling_configuration()
    
    with tab4:
        render_notification_configuration()

def render_api_configuration():
    """Render API configuration settings"""
    st.subheader("🔧 API Configuration")

    # Get current API configurations
    api_configs = get_api_configurations()

    # DGI API Configuration Management
    with st.expander("📡 DGI API Configuration", expanded=True):
        st.markdown("**Current API Configurations:**")

        if api_configs:
            for config in api_configs:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                with col1:
                    st.text_input(
                        f"Base URL ({config['config_name']})",
                        value=config['base_url'],
                        disabled=True,
                        key=f"base_url_{config['config_name']}"
                    )

                with col2:
                    st.text_input(
                        "Description",
                        value=config['description'],
                        disabled=True,
                        key=f"desc_{config['config_name']}"
                    )

                with col3:
                    status_color = "🟢" if config['is_active'] else "🔴"
                    st.write(f"{status_color} {'Active' if config['is_active'] else 'Inactive'}")

                with col4:
                    if st.button("✏️ Edit", key=f"edit_{config['config_name']}"):
                        edit_api_configuration(config)
        else:
            st.info("No API configurations found. Default configuration will be used.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔧 Initialize Default Configurations"):
                    initialize_api_configurations()
            with col2:
                if st.button("🔄 Force Re-initialize All"):
                    force_reinitialize_api_configurations()

        st.markdown("---")

        # Add new configuration
        st.markdown("**➕ Add New API Configuration**")
        try:
            render_add_api_config_form()
        except Exception as e:
            st.error(f"Error rendering add API config form: {e}")

    # System Configuration
    with st.expander("⚙️ System Settings"):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Backend URL",
                value=os.getenv("BACKEND_URL", "http://localhost:8000"),
                disabled=True,
                help="Internal backend API URL"
            )

            st.text_input(
                "Default Timeout (seconds)",
                value="30",
                disabled=True,
                help="Default timeout for API calls"
            )

        with col2:
            st.text_input(
                "Default Retry Attempts",
                value="3",
                disabled=True,
                help="Default number of retry attempts for failed API calls"
            )

            st.text_input(
                "Max Concurrent Jobs",
                value="5",
                disabled=True,
                help="Maximum concurrent background jobs"
            )
    
    # API Health Check
    with st.expander("🏥 API Health Status"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Check Backend API"):
                check_backend_health()
        
        with col2:
            if st.button("🔍 Check DGI API"):
                check_dgi_api_health()
        
        with col3:
            if st.button("🔍 Check All Services"):
                check_all_services_health()

def render_database_configuration():
    """Render database configuration settings"""
    st.subheader("📊 Database Configuration")
    
    with st.expander("🗄️ PostgreSQL Settings", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Database URL", 
                value="postgresql://dealer_user:***@localhost:5432/dealer_dashboard", 
                disabled=True,
                type="password",
                help="PostgreSQL connection string"
            )
            
            st.text_input(
                "Connection Pool Size",
                value="10",
                disabled=True,
                help="Maximum number of database connections"
            )
        
        with col2:
            st.text_input(
                "Query Timeout (seconds)",
                value="30",
                disabled=True,
                help="Database query timeout"
            )
            
            st.text_input(
                "Connection Timeout (seconds)",
                value="10",
                disabled=True,
                help="Database connection timeout"
            )
    
    # Database Health Check
    with st.expander("🏥 Database Health Status"):
        if st.button("🔍 Check Database Connection"):
            check_database_health()

def render_scheduling_configuration():
    """Render scheduling configuration settings"""
    st.subheader("⏰ Scheduling Configuration")
    
    st.info("🚧 Automatic scheduling features will be implemented in future versions.")
    
    with st.expander("📅 Planned Scheduling Features", expanded=True):
        st.markdown("""
        **Upcoming Features:**
        - 🕐 **Cron-based Scheduling**: Set up automatic data fetch jobs
        - 📊 **Recurring Jobs**: Daily, weekly, monthly job execution
        - 🔄 **Job Dependencies**: Chain jobs with dependencies
        - 📧 **Notification Integration**: Email alerts for job completion
        - 📈 **Performance Monitoring**: Job execution analytics
        - 🛡️ **Error Handling**: Automatic retry and escalation
        """)
    
    # Placeholder for future scheduling settings
    with st.expander("⚙️ Current Job Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox(
                "Default Job Frequency",
                ["Manual Only", "Daily", "Weekly", "Monthly"],
                disabled=True,
                help="Default frequency for new dealers"
            )
            
            st.time_input(
                "Default Execution Time",
                disabled=True,
                help="Default time for scheduled jobs"
            )
        
        with col2:
            st.number_input(
                "Max Concurrent Jobs",
                value=5,
                disabled=True,
                help="Maximum number of jobs running simultaneously"
            )
            
            st.number_input(
                "Job Timeout (minutes)",
                value=30,
                disabled=True,
                help="Maximum time for job execution"
            )

def render_notification_configuration():
    """Render notification configuration settings"""
    st.subheader("🔔 Notification Configuration")
    
    st.info("🚧 Notification features will be implemented in future versions.")
    
    with st.expander("📧 Email Notifications", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "SMTP Server",
                placeholder="smtp.gmail.com",
                disabled=True,
                help="Email server for notifications"
            )
            
            st.text_input(
                "SMTP Port",
                value="587",
                disabled=True,
                help="Email server port"
            )
        
        with col2:
            st.text_input(
                "From Email",
                placeholder="admin@company.com",
                disabled=True,
                help="Sender email address"
            )
            
            st.text_input(
                "Admin Email",
                placeholder="admin@company.com",
                disabled=True,
                help="Administrator email for alerts"
            )
    
    with st.expander("📱 Notification Settings"):
        st.checkbox("Job Completion Notifications", disabled=True, help="Send email when jobs complete")
        st.checkbox("Job Failure Alerts", disabled=True, help="Send email when jobs fail")
        st.checkbox("Daily Summary Reports", disabled=True, help="Send daily job summary")
        st.checkbox("Weekly Performance Reports", disabled=True, help="Send weekly performance summary")

def check_backend_health():
    """Check backend API health"""
    try:
        import requests
        response = requests.get(f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend API is healthy")
        else:
            st.error(f"❌ Backend API returned status {response.status_code}")
    except Exception as e:
        st.error(f"❌ Backend API check failed: {e}")

def check_dgi_api_health():
    """Check DGI API health"""
    st.info("🔍 DGI API health check requires dealer credentials. Use 'Run Jobs' to test API connectivity.")

def check_all_services_health():
    """Check all services health"""
    st.info("🔍 Checking all services...")
    check_backend_health()
    check_database_health()

def check_database_health():
    """Check database health"""
    try:
        import psycopg2
        import os

        # Database connection parameters
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "dealer_dashboard")
        db_user = os.getenv("DB_USER", "dealer_user")
        db_password = os.getenv("DB_PASSWORD", "dealer_password")

        # Try to connect to database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )

        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            st.success("✅ Database connection is healthy")
        else:
            st.error("❌ Database query failed")

    except ImportError:
        st.error("❌ Database check failed: psycopg2 module not installed")
    except Exception as e:
        st.error(f"❌ Database check failed: {e}")

# API Configuration Management Functions
def get_api_configurations() -> List[Dict[str, Any]]:
    """Get all API configurations from backend"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.get(f"{backend_url}/api-configurations/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch API configurations: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching API configurations: {e}")
        return []

def initialize_api_configurations():
    """Initialize default API configurations"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.post(f"{backend_url}/api-configurations/initialize")
        if response.status_code == 200:
            st.success("✅ Default API configurations initialized successfully!")
            st.rerun()
        else:
            st.error(f"Failed to initialize API configurations: {response.status_code}")
    except Exception as e:
        st.error(f"Error initializing API configurations: {e}")


def force_reinitialize_api_configurations():
    """Force re-initialize all API configurations"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.post(f"{backend_url}/api-configurations/force-reinitialize")
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"Failed to force re-initialize API configurations: {response.status_code}")
    except Exception as e:
        st.error(f"Error force re-initializing API configurations: {e}")

def edit_api_configuration(config: Dict[str, Any]):
    """Edit an existing API configuration"""
    st.subheader(f"✏️ Edit {config['config_name']}")

    with st.form(f"edit_config_{config['config_name']}"):
        new_base_url = st.text_input(
            "Base URL",
            value=config['base_url'],
            help="Base URL for the API (e.g., https://dev-gvt-gateway.eksad.com/dgi-api/v1.3)"
        )

        new_description = st.text_area(
            "Description",
            value=config['description'],
            help="Description of this API configuration"
        )

        new_timeout = st.number_input(
            "Timeout (seconds)",
            value=config.get('timeout_seconds', 30),
            min_value=5,
            max_value=300,
            help="Request timeout in seconds"
        )

        new_retry_attempts = st.number_input(
            "Retry Attempts",
            value=config.get('retry_attempts', 3),
            min_value=0,
            max_value=10,
            help="Number of retry attempts for failed requests"
        )

        new_is_active = st.checkbox(
            "Active",
            value=config['is_active'],
            help="Whether this configuration is active"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes"):
                update_api_configuration(config['id'], {
                    'base_url': new_base_url,
                    'description': new_description,
                    'timeout_seconds': new_timeout,
                    'retry_attempts': new_retry_attempts,
                    'is_active': new_is_active
                })

        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.rerun()

def render_add_api_config_form():
    """Render form to add new API configuration"""
    with st.form("add_api_config"):
        config_name = st.text_input(
            "Configuration Name",
            placeholder="e.g., dgi_prospect_api",
            help="Unique name for this API configuration"
        )

        base_url = st.text_input(
            "Base URL",
            value="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            help="Base URL for the API"
        )

        description = st.text_area(
            "Description",
            placeholder="Description of this API configuration",
            help="Brief description of what this API is used for"
        )

        col1, col2 = st.columns(2)
        with col1:
            timeout_seconds = st.number_input(
                "Timeout (seconds)",
                value=30,
                min_value=5,
                max_value=300
            )

        with col2:
            retry_attempts = st.number_input(
                "Retry Attempts",
                value=3,
                min_value=0,
                max_value=10
            )

        is_active = st.checkbox("Active", value=True)

        if st.form_submit_button("➕ Add Configuration"):
            if config_name and base_url:
                create_api_configuration({
                    'config_name': config_name,
                    'base_url': base_url,
                    'description': description,
                    'timeout_seconds': timeout_seconds,
                    'retry_attempts': retry_attempts,
                    'is_active': is_active
                })
            else:
                st.error("Please fill in all required fields")

def create_api_configuration(config_data: Dict[str, Any]):
    """Create a new API configuration"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.post(f"{backend_url}/api-configurations/", json=config_data)
        if response.status_code == 200:
            st.success("✅ API configuration created successfully!")
            st.rerun()
        else:
            st.error(f"Failed to create API configuration: {response.status_code}")
    except Exception as e:
        st.error(f"Error creating API configuration: {e}")

def update_api_configuration(config_id: str, config_data: Dict[str, Any]):
    """Update an existing API configuration"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.put(f"{backend_url}/api-configurations/{config_id}", json=config_data)
        if response.status_code == 200:
            st.success("✅ API configuration updated successfully!")
            st.rerun()
        else:
            st.error(f"Failed to update API configuration: {response.status_code}")
    except Exception as e:
        st.error(f"Error updating API configuration: {e}")
