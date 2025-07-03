#!/usr/bin/env python3
"""
Test to check if the route is accessible without database dependency
"""

import requests

def test_route_accessibility():
    """Test if the route is accessible"""
    
    base_url = "http://localhost:8000"
    
    # Test the new endpoint with invalid parameters to see if route is found
    print("Testing route accessibility...")
    try:
        # Use invalid parameters to trigger validation error instead of 404
        response = requests.get(f"{base_url}/api/v1/dashboard/payment-data-history", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print("✓ Route found! (422 = validation error, which means route exists)")
        elif response.status_code == 404:
            print("✗ Route not found (404)")
        else:
            print(f"? Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_route_accessibility()
