#!/usr/bin/env python3
"""
Test the fetch logs API endpoint
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_fetch_logs_api():
    """Test the fetch logs API endpoint"""
    try:
        url = f"{BACKEND_URL}/logs/fetch-logs/"
        print(f"🔍 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved {len(data)} records")
            
            if data:
                print(f"\n📊 Sample Record Structure:")
                sample = data[0]
                for key, value in sample.items():
                    print(f"  {key}: {value} ({type(value).__name__})")
                
                print(f"\n🔑 Available Fields:")
                print(f"  {list(sample.keys())}")
                
                # Check for required fields
                required_fields = ['dealer_id', 'status', 'completed_at']
                missing_fields = [field for field in required_fields if field not in sample]
                if missing_fields:
                    print(f"\n⚠️  Missing required fields: {missing_fields}")
                else:
                    print(f"\n✅ All required fields present")
                    
            else:
                print("📝 No records found (empty response)")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fetch_logs_api()
