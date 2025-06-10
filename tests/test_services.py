#!/usr/bin/env python3
"""
Test script to verify all services are working correctly
"""

import requests
import time
import sys

def test_service(name, url, timeout=10):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: HTTP {response.status_code} - OK")
            return True
        else:
            print(f"⚠️  {name}: HTTP {response.status_code} - Warning")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused - Service not running")
        return False
    except requests.exceptions.Timeout:
        print(f"⏳ {name}: Timeout - Service slow to respond")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def test_database():
    """Test database connection"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="dealer_dashboard", 
            user="dealer_user",
            password="dealer_pass"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dealers WHERE dealer_id = '00999'")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✅ Database: Connected - Found dealer 00999")
            return True
        else:
            print(f"⚠️  Database: Connected - No dealer 00999 found")
            return False
    except Exception as e:
        print(f"❌ Database: Error - {str(e)}")
        return False

def test_redis():
    """Test Redis connection"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print(f"✅ Redis: Connected - OK")
        return True
    except Exception as e:
        print(f"❌ Redis: Error - {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Split Architecture Services")
    print("=" * 50)
    
    services = [
        ("Backend API", "http://localhost:8000/health"),
        ("Analytics Dashboard", "http://localhost:8501"),
        ("Admin Panel", "http://localhost:8502"),
    ]
    
    results = []
    
    # Test services
    for name, url in services:
        result = test_service(name, url)
        results.append((name, result))
        time.sleep(1)  # Small delay between tests
    
    print()
    
    # Test database
    db_result = test_database()
    results.append(("Database", db_result))
    
    # Test Redis
    redis_result = test_redis()
    results.append(("Redis", redis_result))
    
    print()
    print("📊 Test Summary")
    print("-" * 30)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<20} {status}")
        if not result:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All services are working correctly!")
        print()
        print("🌐 Access URLs:")
        print("📊 Analytics Dashboard: http://localhost:8501")
        print("⚙️ Admin Panel: http://localhost:8502")
        print("🔧 Backend API: http://localhost:8000/docs")
        print()
        print("✅ Split architecture is ready for use!")
    else:
        print("⚠️  Some services have issues. Check the logs above.")
        print()
        print("🔧 Troubleshooting:")
        print("1. Check if Docker containers are running: docker ps")
        print("2. Restart services: docker restart dealer_backend")
        print("3. Check logs: docker logs dealer_backend")
        print("4. Run: python start_split_services.py")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
