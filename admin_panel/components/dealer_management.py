"""
Dealer Management Component
Handles all dealer-related operations: view, add, edit
"""

import streamlit as st
import pandas as pd
import requests
import os
from typing import Dict, List, Any, Optional
from .api_utils import get_dealers, create_dealer, update_dealer

def render_dealer_management():
    """Render the dealer management page"""
    st.header("🏢 Dealer Management")
    
    # Tabs for different dealer operations
    tab1, tab2, tab3 = st.tabs(["📋 View Dealers", "➕ Add Dealer", "✏️ Edit Dealer"])
    
    with tab1:
        render_view_dealers()
    
    with tab2:
        render_add_dealer()
    
    with tab3:
        render_edit_dealer()

def render_view_dealers():
    """Render the view dealers tab"""
    st.subheader("📋 Existing Dealers")
    dealers = get_dealers()
    
    if dealers:
        # Create a more interactive table
        for i, dealer in enumerate(dealers):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 2, 1])
                
                with col1:
                    status_icon = "✅" if dealer.get('is_active', True) else "❌"
                    st.write(f"**{dealer['dealer_id']}** {status_icon}")
                
                with col2:
                    st.write(dealer['dealer_name'])
                
                with col3:
                    st.write("Active" if dealer.get('is_active', True) else "Inactive")
                
                with col4:
                    created_date = pd.to_datetime(dealer['created_at']).strftime('%Y-%m-%d')
                    st.write(created_date)
                
                with col5:
                    if st.button("✏️ Edit", key=f"edit_{dealer['dealer_id']}", help="Edit this dealer"):
                        st.session_state.edit_dealer_id = dealer['dealer_id']
                        st.session_state.current_page = "🏢 Dealer Management"
                        st.rerun()
            
            st.divider()
    else:
        st.info("No dealers found. Add a dealer to get started.")

def render_add_dealer():
    """Render the add dealer tab"""
    st.subheader("➕ Add New Dealer")

    # Token generation section (outside form)
    st.markdown("**🔑 Token Generation Preview**")
    st.info("💡 Enter API Key and Secret Key below, then use the form to add the dealer. Token generation will be available after saving.")

    col1, col2 = st.columns(2)
    with col1:
        preview_api_key = st.text_input("Preview API Key", placeholder="API Key for DGI", key="preview_api_key")
        if st.button("🔄 Generate Preview Token", help="Generate token preview"):
            preview_secret_key = st.session_state.get('preview_secret_key', '')
            if preview_api_key and preview_secret_key:
                token_result = generate_api_token(preview_api_key, preview_secret_key)
                if token_result:
                    st.success("✅ Token generated successfully!")
                    st.code(f"Token: {token_result['api_token'][:20]}...")
                    st.info(f"Timestamp: {token_result['api_time']}")
            else:
                st.warning("⚠️ Please enter both API Key and Secret Key")

    with col2:
        preview_secret_key = st.text_input("Preview Secret Key", type="password", placeholder="Secret Key for DGI", key="preview_secret_key")
        if st.button("⏰ Get Current Time", help="Get current Unix timestamp"):
            import time
            current_time = int(time.time())
            st.info(f"Current timestamp: {current_time}")

    st.markdown("---")

    with st.form("add_dealer_form"):
        col1, col2 = st.columns(2)

        with col1:
            dealer_id = st.text_input("Dealer ID", placeholder="e.g., 00999")
            dealer_name = st.text_input("Dealer Name", placeholder="e.g., Default Dealer")

        with col2:
            api_key = st.text_input("API Key", placeholder="API Key for DGI")
            secret_key = st.text_input("Secret Key", type="password", placeholder="Secret Key for DGI")

        is_active = st.checkbox("Active", value=True)

        submitted = st.form_submit_button("➕ Add Dealer", use_container_width=True)
        
        if submitted:
            if dealer_id and dealer_name:
                dealer_data = {
                    "dealer_id": dealer_id,
                    "dealer_name": dealer_name,
                    "api_key": api_key if api_key else None,
                    "secret_key": secret_key if secret_key else None,
                    "is_active": is_active
                }
                
                result = create_dealer(dealer_data)
                if result:
                    st.success(f"✅ Dealer {dealer_id} created successfully!")
                    st.rerun()
            else:
                st.error("❌ Please fill in Dealer ID and Name")

def render_edit_dealer():
    """Render the edit dealer tab"""
    st.subheader("✏️ Edit Dealer")
    
    dealers = get_dealers()
    if not dealers:
        st.info("No dealers available to edit.")
        return
    
    # Dealer selection for editing
    dealer_options = {d['dealer_id']: f"{d['dealer_id']} - {d['dealer_name']}" for d in dealers}
    
    # Check if we have a pre-selected dealer from the edit button
    default_index = 0
    if 'edit_dealer_id' in st.session_state:
        try:
            dealer_ids = list(dealer_options.keys())
            default_index = dealer_ids.index(st.session_state.edit_dealer_id)
        except ValueError:
            default_index = 0
    
    selected_dealer_id = st.selectbox(
        "Select Dealer to Edit",
        options=list(dealer_options.keys()),
        format_func=lambda x: dealer_options[x],
        index=default_index
    )
    
    if selected_dealer_id:
        # Get current dealer data
        current_dealer = next(d for d in dealers if d['dealer_id'] == selected_dealer_id)
        
        # Token generation section (outside form)
        st.markdown("**🔑 Token Generation Preview**")
        st.info("💡 Current saved credentials will be used for token generation. Update credentials in the form below if needed.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate Preview Token", key="edit_generate_preview", help="Generate token using saved credentials"):
                # Get current saved credentials
                saved_api_key = current_dealer.get('api_key', '')
                saved_secret_key = current_dealer.get('secret_key', '')

                if saved_api_key and saved_secret_key:
                    token_result = generate_api_token(saved_api_key, saved_secret_key)
                    if token_result:
                        st.success("✅ Token generated successfully!")
                        st.code(f"Token: {token_result['api_token'][:20]}...")
                        st.info(f"Timestamp: {token_result['api_time']}")
                else:
                    st.warning("⚠️ Please save API Key and Secret Key first using the form below")

        with col2:
            if st.button("⏰ Get Current Time", key="edit_current_time", help="Get current Unix timestamp"):
                import time
                current_time = int(time.time())
                st.info(f"Current timestamp: {current_time}")
       
        st.markdown("---")

        with st.form("edit_dealer_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_dealer_id = st.text_input("Dealer ID", value=current_dealer['dealer_id'], disabled=True)
                edit_dealer_name = st.text_input("Dealer Name", value=current_dealer['dealer_name'])

            with col2:
                edit_api_key = st.text_input("API Key", value=current_dealer.get('api_key', ''))
                edit_secret_key = st.text_input("Secret Key", value=current_dealer.get('secret_key', ''), type="password")

            edit_is_active = st.checkbox("Active", value=current_dealer.get('is_active', True))
            
            col1, col2 = st.columns(2)
            with col1:
                update_submitted = st.form_submit_button("💾 Update Dealer", use_container_width=True)
            with col2:
                if st.form_submit_button("🗑️ Delete Dealer", use_container_width=True, type="secondary"):
                    st.warning("Delete functionality will be implemented in future version")
            
            if update_submitted:
                if edit_dealer_name:
                    dealer_data = {
                        "dealer_name": edit_dealer_name,
                        "api_key": edit_api_key if edit_api_key else None,
                        "secret_key": edit_secret_key if edit_secret_key else None,
                        "is_active": edit_is_active
                    }
                    
                    result = update_dealer(selected_dealer_id, dealer_data)
                    if result:
                        st.success(f"✅ Dealer {selected_dealer_id} updated successfully!")
                        # Clear the edit selection
                        if 'edit_dealer_id' in st.session_state:
                            del st.session_state.edit_dealer_id
                        st.rerun()
                else:
                    st.error("❌ Please fill in Dealer Name")

def generate_api_token(api_key: str, secret_key: str) -> Optional[dict]:
    """Generate API token using backend service"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.post(f"{backend_url}/generate-token", json={
            "api_key": api_key,
            "secret_key": secret_key
        })
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to generate token: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error generating token: {e}")
        return None
