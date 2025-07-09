#!/usr/bin/env python3
"""
Test server startup and route registration
"""

import sys
import os
import threading
import time
import requests
import uvicorn

# Add current directory to path
sys.path.append('.')

def start_server():
    """Start the server in a separate thread"""
    try:
        from main import app
        print("Starting server...")
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
    except Exception as e:
        print(f"Server startup error: {e}")

def test_server():
    """Test the server after startup"""
    base_url = "http://127.0.0.1:8001"
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(20):
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code == 200:
                print(f"Server started successfully after {i+1} attempts")
                break
        except:
            time.sleep(1)
    else:
        print("Server failed to start")
        return
    
    # Test the payment data history endpoint
    print("Testing payment data history endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/dashboard/payment-data-history",
            params={
                "dealer_id": "12284",
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "page": 1,
                "per_page": 5
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total records: {data.get('total_records')}")
            print("✓ API endpoint working correctly!")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir('backend-microservices/services/dashboard-dealer')
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a bit for server to start
    time.sleep(3)
    
    # Test the server
    test_server()
    
    print("Test completed")
