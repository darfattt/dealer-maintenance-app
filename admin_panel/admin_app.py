"""
Admin Panel for Dealer Dashboard
Modular component-based architecture for better maintainability
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Admin Panel - Dealer Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components
from components.navigation import render_sidebar_navigation, render_page_header, render_breadcrumb
from components.dealer_management import render_dealer_management
from components.run_jobs import render_run_jobs
from components.job_history import render_job_history
from components.job_queue import render_job_queue
from components.configuration import render_configuration

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
    .component-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    # Render sidebar navigation and get current page
    current_page = render_sidebar_navigation()
    
    # Render page header
    render_page_header(current_page)
    
    # Render breadcrumb
    render_breadcrumb(current_page)
    
    # Route to appropriate component based on current page
    with st.container():
        if current_page == "🏢 Dealer Management":
            render_dealer_management()

        elif current_page == "🚀 Run Jobs":
            render_run_jobs()

        elif current_page == "🔄 Job Queue":
            render_job_queue()

        elif current_page == "📋 Job History":
            render_job_history()

        elif current_page == "⚙️ Configuration":
            render_configuration()

        else:
            st.error(f"Unknown page: {current_page}")

if __name__ == "__main__":
    main()
