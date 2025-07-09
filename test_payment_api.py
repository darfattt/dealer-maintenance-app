#!/usr/bin/env python3
"""
Test script for Payment Data History API
"""

import requests
import json
import sys

def test_payment_data_history_api():
    """Test the payment data history API endpoint"""
    
    # API configuration
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/dashboard/payment-data-history"
    
    # Test parameters
    params = {
        "dealer_id": "12284",
        "date_from": "2024-01-01", 
        "date_to": "2024-12-31",
        "page": 1,
        "per_page": 5
    }
    
    print("Testing Payment Data History API...")
    print(f"URL: {endpoint}")
    print(f"Parameters: {params}")
    print("-" * 50)
    
    try:
        # Test server connectivity first
        print("1. Testing server connectivity...")
        health_response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Server status: {health_response.status_code}")
        print(f"   Server response: {health_response.json()}")
        
        # Test the payment data history endpoint
        print("\n2. Testing payment data history endpoint...")
        response = requests.get(endpoint, params=params, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Total Records: {data.get('total_records', 0)}")
            print(f"   Page: {data.get('page', 0)}")
            print(f"   Per Page: {data.get('per_page', 0)}")
            print(f"   Total Pages: {data.get('total_pages', 0)}")
            print(f"   Data Count: {len(data.get('data', []))}")
            
            # Show first few records
            if data.get('data'):
                print("\n   Sample Records:")
                for i, record in enumerate(data['data'][:3]):
                    print(f"   Record {i+1}: {record}")
                    
        else:
            print(f"   Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"   Connection Error: {e}")
        print("   Make sure the server is running on http://localhost:8000")
        
    except requests.exceptions.Timeout as e:
        print(f"   Timeout Error: {e}")
        
    except Exception as e:
        print(f"   Unexpected Error: {e}")

if __name__ == "__main__":
    test_payment_data_history_api()
