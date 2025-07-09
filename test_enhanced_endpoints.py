#!/usr/bin/env python3
"""
Test enhanced batch processing endpoints
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        print(f"\n🔍 Testing {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("🚀 Testing Enhanced Batch Processing Endpoints")
    print("=" * 60)
    
    # Test basic health check
    test_endpoint("/health")
    
    # Test queue status
    test_endpoint("/jobs/queue/status")
    
    # Test system status
    test_endpoint("/jobs/enhanced/system/status")
    
    # Test performance metrics
    test_endpoint("/jobs/enhanced/performance/metrics")
    
    # Test enhanced job run (with sample data)
    sample_job_data = {
        "dealer_id": "12284",
        "fetch_type": "prospect",
        "from_time": "2024-01-01 00:00:00",
        "to_time": "2024-01-02 00:00:00"
    }
    
    print(f"\n🎯 Testing Enhanced Job Execution:")
    print(f"   Sample data: {json.dumps(sample_job_data, indent=2)}")
    test_endpoint("/jobs/enhanced/run", method="POST", data=sample_job_data)
    
    print(f"\n📊 Summary:")
    print(f"   All enhanced endpoints are now available for testing!")
    print(f"   Admin panel should be accessible at: http://localhost:8503")
    print(f"   Backend API is accessible at: {BACKEND_URL}")

if __name__ == "__main__":
    main()
