#!/usr/bin/env python3
"""
Debug script to test API routes and service connectivity
"""

import requests
import json
import sys
from urllib.parse import urljoin

def test_endpoint(base_url, endpoint, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    url = urljoin(base_url, endpoint)
    
    try:
        print(f"\n🧪 Testing {method} {url}")
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text[:500]}")
        
        return response.status_code < 400
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {str(e)}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"⏰ Timeout Error: {str(e)}")
        return False
    except Exception as e:
        print(f"💥 Unexpected Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🔍 API Routes Debug Tool")
    print("=" * 50)
    
    # Test endpoints
    endpoints_to_test = [
        # Direct service tests
        ("http://localhost:8100", "/api/v1/health", "GET"),
        ("http://localhost:8100", "/", "GET"),
        ("http://localhost:8100", "/api/v1/auth/login", "POST", {
            "email": "admin@dealer-dashboard.com",
            "password": "Admin123!"
        }),
        
        # API Gateway tests
        ("http://localhost:8080", "/health", "GET"),
        ("http://localhost:8080", "/", "GET"),
        ("http://localhost:8080", "/api/v1/health", "GET"),
        ("http://localhost:8080", "/api/v1/auth/login", "POST", {
            "email": "admin@dealer-dashboard.com", 
            "password": "Admin123!"
        }),
        
        # Web app proxy tests
        ("http://localhost:5000", "/api/v1/health", "GET"),
        ("http://localhost:5000", "/api/v1/auth/login", "POST", {
            "email": "admin@dealer-dashboard.com",
            "password": "Admin123!"
        }),
    ]
    
    results = []
    for base_url, endpoint, method, *args in endpoints_to_test:
        data = args[0] if args else None
        success = test_endpoint(base_url, endpoint, method, data)
        results.append((f"{base_url}{endpoint}", method, success))
    
    print("\n" + "=" * 50)
    print("📈 SUMMARY")
    print("=" * 50)
    
    for url, method, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {url}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, _, success in results if success)
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()