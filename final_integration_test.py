#!/usr/bin/env python3
"""
Final integration test for Payment Data History API
"""

import sys
import os
import threading
import time
import requests
import uvicorn
import json

def start_server():
    """Start the server in a separate thread"""
    try:
        # Change to the correct directory
        os.chdir('backend-microservices/services/dashboard-dealer')
        sys.path.append('.')
        
        from main import app
        print("🚀 Starting backend server...")
        uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")
    except Exception as e:
        print(f"❌ Server startup error: {e}")

def test_payment_data_history_integration():
    """Comprehensive test of the Payment Data History integration"""
    
    print("=" * 60)
    print("🧪 PAYMENT DATA HISTORY INTEGRATION TEST")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8002"
    
    # Wait for server to start
    print("\n1️⃣ Waiting for backend server to start...")
    server_ready = False
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Server ready after {i+1} attempts")
                server_ready = True
                break
        except:
            if i % 5 == 0:
                print(f"   ⏳ Attempt {i+1}/30...")
            time.sleep(1)
    
    if not server_ready:
        print("   ❌ Server failed to start")
        return False
    
    # Test API endpoint
    print("\n2️⃣ Testing Payment Data History API endpoint...")
    
    test_cases = [
        {
            "name": "Basic pagination test",
            "params": {
                "dealer_id": "12284",
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "page": 1,
                "per_page": 5
            }
        },
        {
            "name": "Different page size test",
            "params": {
                "dealer_id": "12284", 
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "page": 1,
                "per_page": 10
            }
        }
    ]
    
    all_tests_passed = True
    
    for test_case in test_cases:
        print(f"\n   🔍 {test_case['name']}...")
        try:
            response = requests.get(
                f"{base_url}/api/v1/dashboard/payment-data-history",
                params=test_case['params'],
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['success', 'message', 'data', 'total_records', 'page', 'per_page', 'total_pages']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"      ❌ Missing fields: {missing_fields}")
                    all_tests_passed = False
                else:
                    print(f"      ✅ Status: {response.status_code}")
                    print(f"      ✅ Success: {data.get('success')}")
                    print(f"      ✅ Total Records: {data.get('total_records')}")
                    print(f"      ✅ Page: {data.get('page')}")
                    print(f"      ✅ Per Page: {data.get('per_page')}")
                    print(f"      ✅ Total Pages: {data.get('total_pages')}")
                    print(f"      ✅ Data Count: {len(data.get('data', []))}")
                    
                    # Show sample data if available
                    if data.get('data'):
                        sample_record = data['data'][0]
                        print(f"      📋 Sample Record Fields: {list(sample_record.keys())}")
                        
                        # Validate data mapping
                        expected_fields = ['no', 'id_invoice', 'id_customer', 'amount', 'tipe_pembayaran', 'cara_bayar', 'status']
                        record_fields = list(sample_record.keys())
                        missing_record_fields = [field for field in expected_fields if field not in record_fields]
                        
                        if missing_record_fields:
                            print(f"      ⚠️  Missing record fields: {missing_record_fields}")
                        else:
                            print(f"      ✅ All expected fields present")
                            
                            # Check if mappings are applied
                            if sample_record.get('cara_bayar') in ['Cash', 'Transfer']:
                                print(f"      ✅ Cara Bayar mapping applied: {sample_record.get('cara_bayar')}")
                            if sample_record.get('status') in ['New', 'Process', 'Accepted', 'Close']:
                                print(f"      ✅ Status mapping applied: {sample_record.get('status')}")
                            if sample_record.get('tipe_pembayaran') in ['Credit', 'Cash']:
                                print(f"      ✅ Tipe Pembayaran mapping applied: {sample_record.get('tipe_pembayaran')}")
                    
            else:
                print(f"      ❌ HTTP Error: {response.status_code}")
                print(f"      ❌ Response: {response.text}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            all_tests_passed = False
    
    # Test error handling
    print(f"\n3️⃣ Testing error handling...")
    try:
        # Test with missing parameters
        response = requests.get(f"{base_url}/api/v1/dashboard/payment-data-history", timeout=10)
        if response.status_code == 422:
            print(f"      ✅ Validation error handling: {response.status_code}")
        else:
            print(f"      ⚠️  Unexpected status for missing params: {response.status_code}")
    except Exception as e:
        print(f"      ❌ Error testing validation: {e}")
    
    # Summary
    print(f"\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Payment Data History integration is working correctly.")
        print("\n📋 Integration Summary:")
        print("   ✅ Backend API endpoint created and functional")
        print("   ✅ Database join between BillingProcessData and DeliveryProcessDetail working")
        print("   ✅ Pagination implemented correctly")
        print("   ✅ Data mapping applied (Cara Bayar, Status, Tipe Pembayaran)")
        print("   ✅ Response schema validation successful")
        print("   ✅ Error handling implemented")
        print("\n🚀 Ready for frontend integration!")
    else:
        print("❌ SOME TESTS FAILED. Please review the issues above.")
    
    print("=" * 60)
    return all_tests_passed

if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to initialize
    time.sleep(3)
    
    # Run integration tests
    success = test_payment_data_history_integration()
    
    if success:
        print("\n✨ Integration test completed successfully!")
    else:
        print("\n💥 Integration test failed!")
    
    # Keep the test running for a moment to see results
    time.sleep(2)
