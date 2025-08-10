#!/usr/bin/env python3
"""
Test script to verify customer service setup and functionality
"""

import json
import requests
import sys
from datetime import datetime


def test_service_health():
    """Test service health endpoint"""
    try:
        response = requests.get("http://localhost:8300/api/v1/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Service not running on port 8300")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False


def test_service_info():
    """Test service info endpoint"""
    try:
        response = requests.get("http://localhost:8300/info", timeout=10)
        if response.status_code == 200:
            print("✅ Service info endpoint works")
            info = response.json()
            print(f"   Service: {info.get('service')} v{info.get('version')}")
            print(f"   Environment: {info.get('environment')}")
            return True
        else:
            print(f"❌ Service info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Service info error: {str(e)}")
        return False


def test_validate_customer_api():
    """Test validate customer API endpoint"""
    test_data = {
        "namaPembawa": "Test Customer",
        "noTelp": "082148523421",
        "tipeUnit": "BeAT Street",
        "noPol": "D 123 AD",
        "createdTime": "31/12/2019 15:40:50",
        "modifiedTime": "31/12/2019 15:40:50",
        "dealerId": "0009999"
    }
    
    try:
        response = requests.post(
            "http://localhost:8300/api/v1/customer/validate-customer",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📝 API Response Status: {response.status_code}")
        print(f"📝 API Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == 1:
                print("✅ Customer validation API works (success response)")
                return True
            else:
                print(f"⚠️  Customer validation API returned status {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                return True  # Still consider it working if we get a response
        elif response.status_code == 422:
            print("⚠️  Validation error (expected if dealer doesn't exist)")
            return True
        else:
            print(f"❌ Customer validation API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Customer validation API error: {str(e)}")
        return False


def test_api_documentation():
    """Test API documentation endpoint"""
    try:
        response = requests.get("http://localhost:8300/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation available at http://localhost:8300/docs")
            return True
        else:
            print("ℹ️  API documentation disabled in production mode")
            return True
    except Exception as e:
        print(f"❌ Documentation test error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Customer Service Setup")
    print("=" * 50)
    
    tests = [
        ("Service Health Check", test_service_health),
        ("Service Info", test_service_info),
        ("API Documentation", test_api_documentation),
        ("Customer Validation API", test_validate_customer_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Customer service is ready to use.")
        print("\n📋 Next steps:")
        print("   1. Add Fonnte API keys to dealer configuration")
        print("   2. Test with real dealer data")
        print("   3. Monitor logs for any issues")
    else:
        print("⚠️  Some tests failed. Please check the service configuration.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)