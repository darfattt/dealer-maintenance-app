#!/usr/bin/env python3
"""
Test dashboard-dealer service dateutil functionality
"""

import requests
import json
from datetime import datetime, timedelta

def test_dashboard_dateutil():
    """Test dashboard-dealer service dateutil endpoints"""
    print("🔍 TESTING DASHBOARD-DEALER SERVICE DATEUTIL")
    print("=" * 60)
    
    # Service endpoint
    service_url = "http://localhost:8200"
    dealer_id = "12284"
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    date_from = start_date.strftime('%Y-%m-%d')
    date_to = end_date.strftime('%Y-%m-%d')
    
    print(f"🎯 Target: {service_url}")
    print(f"📋 Dealer: {dealer_id}")
    print(f"📅 Date range: {date_from} to {date_to}")
    print()
    
    # Test 1: Check service health
    print("1️⃣ CHECKING SERVICE HEALTH...")
    try:
        response = requests.get(f"{service_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard-dealer service is healthy")
        else:
            print(f"⚠️ Service health check returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return

    # Test 2: Test STNK Diterima endpoint
    print("\n2️⃣ TESTING STNK DITERIMA ENDPOINT...")
    try:
        response = requests.get(
            f"{service_url}/api/v1/dashboard/document-handling/stnk-diterima",
            params={
                "dealer_id": dealer_id,
                "date_from": date_from,
                "date_to": date_to
            },
            timeout=10
        )
        
        print(f"📤 STNK Diterima status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ STNK Diterima endpoint working")
            print(f"   Current count: {result.get('current_count', 'N/A')}")
            print(f"   Previous count: {result.get('previous_count', 'N/A')}")
            print(f"   Trend: {result.get('trend', 'N/A')}")
            print(f"   Percentage: {result.get('percentage', 'N/A')}%")
        else:
            print(f"❌ STNK Diterima endpoint failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ STNK Diterima endpoint error: {e}")
    
    # Test 3: Test BPKB Diterima endpoint
    print("\n3️⃣ TESTING BPKB DITERIMA ENDPOINT...")
    try:
        response = requests.get(
            f"{service_url}/api/v1/dashboard/document-handling/bpkb-diterima",
            params={
                "dealer_id": dealer_id,
                "date_from": date_from,
                "date_to": date_to
            },
            timeout=10
        )
        
        print(f"📤 BPKB Diterima status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BPKB Diterima endpoint working")
            print(f"   Current count: {result.get('current_count', 'N/A')}")
            print(f"   Previous count: {result.get('previous_count', 'N/A')}")
            print(f"   Trend: {result.get('trend', 'N/A')}")
            print(f"   Percentage: {result.get('percentage', 'N/A')}%")
        else:
            print(f"❌ BPKB Diterima endpoint failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ BPKB Diterima endpoint error: {e}")
    
    # Test 4: Test Permohonan Faktur endpoint
    print("\n4️⃣ TESTING PERMOHONAN FAKTUR ENDPOINT...")
    try:
        response = requests.get(
            f"{service_url}/api/v1/dashboard/document-handling/permohonan-faktur",
            params={
                "dealer_id": dealer_id,
                "date_from": date_from,
                "date_to": date_to
            },
            timeout=10
        )
        
        print(f"📤 Permohonan Faktur status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Permohonan Faktur endpoint working")
            print(f"   Current count: {result.get('current_count', 'N/A')}")
            print(f"   Previous count: {result.get('previous_count', 'N/A')}")
            print(f"   Trend: {result.get('trend', 'N/A')}")
            print(f"   Percentage: {result.get('percentage', 'N/A')}%")
        else:
            print(f"❌ Permohonan Faktur endpoint failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Permohonan Faktur endpoint error: {e}")
    
    print(f"\n✅ Dashboard-dealer service dateutil test completed")

if __name__ == "__main__":
    test_dashboard_dateutil()
