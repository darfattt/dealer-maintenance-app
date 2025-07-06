#!/usr/bin/env python3
"""
Test all admin panel functionality
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_all_admin_endpoints():
    """Test all endpoints used by the admin panel"""
    
    endpoints_to_test = [
        {
            "name": "Health Check",
            "url": "/health",
            "method": "GET"
        },
        {
            "name": "Dealers List",
            "url": "/dealers/",
            "method": "GET"
        },
        {
            "name": "Fetch Logs",
            "url": "/logs/fetch-logs/",
            "method": "GET"
        },
        {
            "name": "Queue Status",
            "url": "/jobs/queue/status",
            "method": "GET"
        },
        {
            "name": "Enhanced System Status",
            "url": "/jobs/enhanced/system/status",
            "method": "GET"
        }
    ]
    
    print("🚀 Testing Admin Panel Backend Endpoints")
    print("=" * 60)
    
    results = {}
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{BACKEND_URL}{endpoint['url']}"
            print(f"\n🔍 Testing: {endpoint['name']}")
            print(f"   URL: {url}")
            
            if endpoint['method'] == "GET":
                response = requests.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Success: Retrieved {len(data)} records")
                    if data:
                        print(f"   📋 Sample fields: {list(data[0].keys())}")
                elif isinstance(data, dict):
                    print(f"   ✅ Success: {list(data.keys())}")
                else:
                    print(f"   ✅ Success: {type(data).__name__}")
                
                results[endpoint['name']] = {
                    "status": "✅ PASS",
                    "data_type": type(data).__name__,
                    "record_count": len(data) if isinstance(data, list) else 1
                }
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
                results[endpoint['name']] = {
                    "status": "❌ FAIL",
                    "error": f"{response.status_code} - {response.text[:50]}"
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[endpoint['name']] = {
                "status": "❌ EXCEPTION",
                "error": str(e)
            }
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results.items():
        status = result['status']
        print(f"{status} {name}")
        if "✅" in status:
            passed += 1
        else:
            failed += 1
            if 'error' in result:
                print(f"     Error: {result['error']}")
    
    print(f"\n🎯 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All admin panel endpoints are working correctly!")
        print("🌐 Admin panel should be fully functional at: http://localhost:8503")
    else:
        print("⚠️  Some endpoints have issues. Check the errors above.")
    
    return results

def test_sample_job_submission():
    """Test submitting a sample job"""
    print(f"\n🎯 Testing Job Submission")
    print("-" * 40)
    
    sample_job = {
        "dealer_id": "12284",
        "fetch_type": "prospect",
        "from_time": "2024-01-01 00:00:00",
        "to_time": "2024-01-02 00:00:00"
    }
    
    try:
        url = f"{BACKEND_URL}/jobs/enhanced/run"
        print(f"🔍 Submitting job to: {url}")
        print(f"📋 Job data: {json.dumps(sample_job, indent=2)}")
        
        response = requests.post(url, json=sample_job, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job submitted successfully!")
            print(f"   Job ID: {result.get('job_id', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Job submission failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during job submission: {e}")
        return False

if __name__ == "__main__":
    # Test all endpoints
    results = test_all_admin_endpoints()
    
    # Test job submission if basic endpoints work
    if all("✅" in result['status'] for result in results.values()):
        test_sample_job_submission()
    
    print(f"\n🏁 Testing Complete!")
    print(f"📱 Access admin panel at: http://localhost:8503")
    print(f"🔧 Backend API available at: {BACKEND_URL}")
