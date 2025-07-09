#!/usr/bin/env python3
"""
Payment Revenue Integration Test

This script tests the complete payment revenue integration:
1. Backend API endpoint functionality
2. Data accuracy and formatting
3. Error handling
4. Response structure validation
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_revenue_api():
    """Test the payment revenue API endpoint"""
    print("=" * 60)
    print("PAYMENT REVENUE INTEGRATION TEST")
    print("=" * 60)
    
    # Test parameters
    base_url = "http://localhost:8001"
    endpoint = "/api/v1/dashboard/payment-revenue/total"
    test_cases = [
        {
            "name": "Standard Date Range",
            "params": {
                "dealer_id": "12284",
                "date_from": "2020-01-01",
                "date_to": "2025-12-31"
            }
        },
        {
            "name": "Narrow Date Range",
            "params": {
                "dealer_id": "12284", 
                "date_from": "2024-01-01",
                "date_to": "2024-12-31"
            }
        },
        {
            "name": "Different Dealer",
            "params": {
                "dealer_id": "99999",
                "date_from": "2020-01-01", 
                "date_to": "2025-12-31"
            }
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Make API request
            url = f"{base_url}{endpoint}"
            response = requests.get(url, params=test_case['params'], timeout=10)
            
            print(f"Request URL: {response.url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API Response received successfully")
                
                # Validate response structure
                required_fields = ['success', 'message', 'total_revenue', 'total_records']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                    all_passed = False
                else:
                    print("✅ Response structure is valid")
                    
                    # Validate data types
                    if not isinstance(data['success'], bool):
                        print("❌ 'success' field should be boolean")
                        all_passed = False
                    
                    if not isinstance(data['total_revenue'], (int, float)):
                        print("❌ 'total_revenue' field should be numeric")
                        all_passed = False
                    
                    if not isinstance(data['total_records'], int):
                        print("❌ 'total_records' field should be integer")
                        all_passed = False
                    
                    if all([isinstance(data['success'], bool),
                           isinstance(data['total_revenue'], (int, float)),
                           isinstance(data['total_records'], int)]):
                        print("✅ Data types are correct")
                
                # Display results
                print(f"Success: {data.get('success')}")
                print(f"Message: {data.get('message')}")
                print(f"Total Revenue: {data.get('total_revenue'):,.2f}")
                print(f"Total Records: {data.get('total_records')}")
                
                # Format as Indonesian currency for display
                if data.get('total_revenue'):
                    formatted_revenue = f"Rp {data['total_revenue']:,.0f}".replace(',', '.')
                    print(f"Formatted Revenue: {formatted_revenue}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                all_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error: {e}")
            all_passed = False
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            all_passed = False
    
    # Test error cases
    print(f"\n{len(test_cases) + 1}. Testing Error Cases")
    print("-" * 40)
    
    error_test_cases = [
        {
            "name": "Invalid Date Format",
            "params": {
                "dealer_id": "12284",
                "date_from": "invalid-date",
                "date_to": "2025-12-31"
            },
            "expected_status": 400
        },
        {
            "name": "Missing Parameters",
            "params": {
                "dealer_id": "12284"
                # Missing date_from and date_to
            },
            "expected_status": 422
        }
    ]
    
    for error_case in error_test_cases:
        print(f"\nTesting: {error_case['name']}")
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, params=error_case['params'], timeout=10)
            
            if response.status_code == error_case['expected_status']:
                print(f"✅ Correctly returned status {response.status_code}")
            else:
                print(f"❌ Expected status {error_case['expected_status']}, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing error case: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("✅ Payment Revenue API integration is working correctly")
        print("✅ Frontend widget should display revenue data properly")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("❌ Please check the issues above")
        return False

def test_frontend_integration():
    """Test frontend integration by checking if the test page is accessible"""
    print(f"\n4. Testing Frontend Integration")
    print("-" * 40)
    
    try:
        frontend_url = "http://localhost:3000/test-payment-revenue-widget"
        response = requests.get(frontend_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Frontend test page is accessible")
            print(f"✅ Visit {frontend_url} to test the widget manually")
            return True
        else:
            print(f"❌ Frontend test page returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        print("ℹ️  Make sure the frontend is running with 'npm run dev'")
        return False

if __name__ == "__main__":
    print("Starting Payment Revenue Integration Test...")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API
    api_success = test_revenue_api()
    
    # Test frontend
    frontend_success = test_frontend_integration()
    
    # Final result
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    
    if api_success and frontend_success:
        print("🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("🎉 Payment Revenue feature is ready for production use")
        sys.exit(0)
    else:
        print("💥 INTEGRATION TEST FAILED")
        print("💥 Please fix the issues before deploying")
        sys.exit(1)
