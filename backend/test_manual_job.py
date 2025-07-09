#!/usr/bin/env python3
"""
Test manual job execution for document handling
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_manual_job():
    """Test manual job execution"""
    print("🔍 TESTING MANUAL DOCUMENT HANDLING JOB")
    print("=" * 60)
    
    # Job parameters
    dealer_id = "12284"
    from_time = "2024-01-01 00:00:00"
    to_time = "2024-01-31 23:59:59"
    
    # API endpoint
    backend_url = "http://localhost:8000"
    
    print(f"🎯 Target: {backend_url}")
    print(f"📋 Dealer: {dealer_id}")
    print(f"📅 Time range: {from_time} to {to_time}")
    print()
    
    # Test 1: Check backend health
    print("1️⃣ CHECKING BACKEND HEALTH...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"⚠️ Backend health check returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return
    
    # Test 2: Submit job
    print("\n2️⃣ SUBMITTING DOCUMENT HANDLING JOB...")
    job_data = {
        "dealer_id": dealer_id,
        "fetch_type": "doch_read",
        "from_time": from_time,
        "to_time": to_time,
        "no_po": ""
    }
    
    try:
        response = requests.post(
            f"{backend_url}/jobs/run",
            json=job_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📤 Job submission status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job submitted successfully")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Status: {result.get('status')}")
            
            task_id = result.get('task_id')
            
            # Test 3: Monitor job status
            print(f"\n3️⃣ MONITORING JOB STATUS...")
            for i in range(10):  # Check for up to 10 times
                try:
                    status_response = requests.get(
                        f"{backend_url}/jobs/{task_id}/status",
                        timeout=5
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   Check {i+1}: Status = {status_data.get('status')}, Progress = {status_data.get('progress')}")
                        
                        if status_data.get('status') in ['SUCCESS', 'FAILURE']:
                            print(f"🏁 Job completed with status: {status_data.get('status')}")
                            if status_data.get('result'):
                                print(f"   Result: {json.dumps(status_data.get('result'), indent=2)}")
                            break
                    else:
                        print(f"   Check {i+1}: Status check failed with code {status_response.status_code}")
                        
                except Exception as e:
                    print(f"   Check {i+1}: Status check error: {e}")
                
                time.sleep(2)  # Wait 2 seconds between checks
            
        else:
            print(f"❌ Job submission failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Job submission error: {e}")
        return
    
    # Test 4: Check database after job
    print(f"\n4️⃣ CHECKING DATABASE AFTER JOB...")
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Database connection
        database_url = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")
        
        # Parse the database URL
        if database_url.startswith("postgresql://"):
            url_parts = database_url[13:].split("@")
            user_pass = url_parts[0].split(":")
            host_db = url_parts[1].split("/")
            host_port = host_db[0].split(":")
            
            db_config = {
                "host": host_port[0],
                "port": int(host_port[1]) if len(host_port) > 1 else 5432,
                "database": host_db[1],
                "user": user_pass[0],
                "password": user_pass[1]
            }
            
            conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            cursor.execute("SET search_path TO dealer_integration, public")
            
            # Check document handling data
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM document_handling_data 
                WHERE dealer_id = %s
            """, (dealer_id,))
            doc_count = cursor.fetchone()['count']
            print(f"📄 Document handling records: {doc_count}")
            
            # Check fetch logs
            cursor.execute("""
                SELECT status, records_fetched, error_message, started_at, completed_at
                FROM fetch_logs 
                WHERE dealer_id = %s AND fetch_type = 'doch_read'
                ORDER BY started_at DESC
                LIMIT 1
            """, (dealer_id,))
            
            log = cursor.fetchone()
            if log:
                print(f"📊 Latest fetch log:")
                print(f"   Status: {log['status']}")
                print(f"   Records: {log['records_fetched']}")
                print(f"   Started: {log['started_at']}")
                print(f"   Completed: {log['completed_at']}")
                if log['error_message']:
                    print(f"   Error: {log['error_message']}")
            else:
                print("❌ No fetch logs found")
            
            conn.close()
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    print(f"\n✅ Manual job test completed")

if __name__ == "__main__":
    test_manual_job()
