"""
API utility functions for admin panel components
"""

import requests
import streamlit as st
import os
from typing import Dict, List, Any, Optional

# Configuration
# Force localhost when running outside Docker (detect by checking if we can resolve 'backend' hostname)
import socket
try:
    socket.gethostbyname('backend')
    # If we can resolve 'backend', we're likely in Docker
    BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
except socket.gaierror:
    # If we can't resolve 'backend', we're running directly - use localhost
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_dealers() -> List[Dict[str, Any]]:
    """Fetch dealers from API"""
    try:
        response = requests.get(f"{BACKEND_URL}/dealers/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch dealers: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []

def get_fetch_logs(dealer_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch job logs from API"""
    try:
        url = f"{BACKEND_URL}/logs/fetch-logs/"
        params = {}
        if dealer_id:
            params['dealer_id'] = dealer_id

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch logs: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []

def create_dealer(dealer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create new dealer"""
    try:
        response = requests.post(f"{BACKEND_URL}/dealers/", json=dealer_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to create dealer: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error creating dealer: {e}")
        return None

def update_dealer(dealer_id: str, dealer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update existing dealer"""
    try:
        response = requests.put(f"{BACKEND_URL}/dealers/{dealer_id}", json=dealer_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to update dealer: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error updating dealer: {e}")
        return None

def run_manual_job(dealer_id: str, from_time: Optional[str] = None, to_time: Optional[str] = None, fetch_type: str = "prospect") -> Optional[Dict[str, Any]]:
    """Trigger manual job execution"""
    try:
        payload = {"dealer_id": dealer_id, "fetch_type": fetch_type}
        if from_time:
            payload["from_time"] = from_time
        if to_time:
            payload["to_time"] = to_time
            
        response = requests.post(f"{BACKEND_URL}/jobs/run", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to run job: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error running job: {e}")
        return None

def get_job_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get job status"""
    try:
        response = requests.get(f"{BACKEND_URL}/jobs/{task_id}/status")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def run_jobs_for_all_dealers(from_time: Optional[str] = None, to_time: Optional[str] = None, fetch_type: str = "prospect") -> List[Dict[str, Any]]:
    """Run jobs for all active dealers"""
    try:
        dealers = get_dealers()
        active_dealers = [d for d in dealers if d.get('is_active', True)]

        if not active_dealers:
            st.warning("No active dealers found")
            return []

        results = []
        for dealer in active_dealers:
            payload = {"dealer_id": dealer['dealer_id'], "fetch_type": fetch_type}
            if from_time:
                payload["from_time"] = from_time
            if to_time:
                payload["to_time"] = to_time
                
            try:
                response = requests.post(f"{BACKEND_URL}/jobs/run", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    result['dealer_name'] = dealer['dealer_name']
                    results.append(result)
                else:
                    results.append({
                        'dealer_id': dealer['dealer_id'],
                        'dealer_name': dealer['dealer_name'],
                        'status': 'failed',
                        'error': f"HTTP {response.status_code}"
                    })
            except Exception as e:
                results.append({
                    'dealer_id': dealer['dealer_id'],
                    'dealer_name': dealer['dealer_name'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    except Exception as e:
        st.error(f"Error running jobs for all dealers: {e}")
        return []
