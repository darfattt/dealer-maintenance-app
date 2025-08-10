#!/usr/bin/env python3
"""
Simple test to check server status
"""

import requests
import time

def test_server():
    """Test server connectivity and endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print(f"Server is ready after {i+1} attempts")
                break
        except:
            print(f"Attempt {i+1}: Server not ready, waiting...")
            time.sleep(2)
    else:
        print("Server failed to start after 10 attempts")
        return
    
    # Test known working endpoint
    print("\nTesting known working endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard/payment-revenue/total?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31", timeout=10)
        print(f"Payment revenue endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing payment revenue: {e}")
    
    # Test new endpoint
    print("\nTesting new payment data history endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard/payment-data-history?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31&page=1&per_page=5", timeout=10)
        print(f"Payment data history endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total records: {data.get('total_records')}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing payment data history: {e}")

if __name__ == "__main__":
    test_server()
