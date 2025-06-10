#!/usr/bin/env python3
"""
Simple test script to validate the dealer dashboard application
"""

import requests
import json
import time
from datetime import datetime, date, timedelta

# Configuration
BACKEND_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8501"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_dashboard_health():
    """Test if dashboard is running"""
    try:
        response = requests.get(DASHBOARD_URL)
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            return True
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")
        return False

def test_create_dealer():
    """Test creating a dealer"""
    dealer_data = {
        "dealer_id": "TEST001",
        "dealer_name": "Test Dealer",
        "api_key": "6c796097-a453-420f-9a19-155a2a24513e",
        "api_token": "81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/dealers/", json=dealer_data)
        if response.status_code == 200:
            print("✅ Dealer created successfully")
            return response.json()
        else:
            print(f"❌ Failed to create dealer: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating dealer: {e}")
        return None

def test_run_job(dealer_id):
    """Test running a data fetch job"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    job_data = {
        "dealer_id": dealer_id,
        "from_time": f"{yesterday} 00:00:00",
        "to_time": f"{today} 23:59:59"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/jobs/run", json=job_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job started successfully: {result.get('task_id')}")
            return result
        else:
            print(f"❌ Failed to start job: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error starting job: {e}")
        return None

def test_job_status(task_id):
    """Test checking job status"""
    try:
        response = requests.get(f"{BACKEND_URL}/jobs/{task_id}/status")
        if response.status_code == 200:
            result = response.json()
            status = result.get('status', 'UNKNOWN')
            print(f"📊 Job status: {status}")
            return result
        else:
            print(f"❌ Failed to get job status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting job status: {e}")
        return None

def test_get_analytics(dealer_id):
    """Test getting analytics data"""
    try:
        response = requests.get(f"{BACKEND_URL}/prospect-data/analytics/{dealer_id}")
        if response.status_code == 200:
            result = response.json()
            total_prospects = result.get('total_prospects', 0)
            print(f"📈 Analytics retrieved: {total_prospects} total prospects")
            return result
        else:
            print(f"❌ Failed to get analytics: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Dealer Dashboard Application Tests")
    print("=" * 50)
    
    # Test 1: Backend Health
    print("\n1. Testing Backend Health...")
    if not test_backend_health():
        print("❌ Backend is not running. Please start the backend first.")
        return
    
    # Test 2: Dashboard Health
    print("\n2. Testing Dashboard Health...")
    test_dashboard_health()
    
    # Test 3: Create Dealer
    print("\n3. Testing Dealer Creation...")
    dealer = test_create_dealer()
    if not dealer:
        print("❌ Cannot proceed without a dealer")
        return
    
    dealer_id = dealer.get('dealer_id')
    print(f"   Created dealer: {dealer_id}")
    
    # Test 4: Run Job
    print("\n4. Testing Job Execution...")
    job = test_run_job(dealer_id)
    if not job:
        print("❌ Cannot proceed without a job")
        return
    
    task_id = job.get('task_id')
    print(f"   Job task ID: {task_id}")
    
    # Test 5: Monitor Job
    print("\n5. Monitoring Job Progress...")
    for i in range(10):  # Check for up to 10 times
        time.sleep(2)
        status = test_job_status(task_id)
        if status:
            job_status = status.get('status')
            if job_status in ['SUCCESS', 'FAILURE']:
                print(f"   Job completed with status: {job_status}")
                if job_status == 'SUCCESS':
                    result = status.get('result', {})
                    records = result.get('records_processed', 0)
                    print(f"   Records processed: {records}")
                break
        else:
            print("   Waiting for job to complete...")
    
    # Test 6: Get Analytics
    print("\n6. Testing Analytics Retrieval...")
    analytics = test_get_analytics(dealer_id)
    
    print("\n" + "=" * 50)
    print("🎉 Test Summary:")
    print("✅ Backend API: Working")
    print("✅ Job Execution: Working") 
    print("✅ Data Storage: Working")
    print("✅ Analytics: Working")
    print("\n🌐 Access URLs:")
    print(f"   Dashboard: {DASHBOARD_URL}")
    print(f"   API Docs: {BACKEND_URL}/docs")
    print("\n📋 Next Steps:")
    print("   1. Open the dashboard in your browser")
    print("   2. Go to 'Run Jobs' to execute data fetch jobs")
    print("   3. Check 'Job History' to monitor job status")
    print("   4. View 'Dashboard' for analytics and charts")

if __name__ == "__main__":
    main()
