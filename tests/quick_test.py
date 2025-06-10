#!/usr/bin/env python3
"""
Quick test script to insert sample data and test the dashboard
This script can be run even without full development setup
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_packages():
    """Check if required packages are available"""
    required_packages = ['sqlalchemy', 'psycopg2', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install sqlalchemy psycopg2-binary python-dotenv")
        return False
    
    return True

def start_database():
    """Start PostgreSQL database using Docker"""
    print("🐳 Starting PostgreSQL database...")
    
    try:
        # Check if container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=postgres', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        
        if 'postgres' in result.stdout:
            print("📦 PostgreSQL container exists, starting...")
            subprocess.run(['docker', 'start', 'postgres'], check=True)
        else:
            print("📦 Creating new PostgreSQL container...")
            subprocess.run([
                'docker', 'run', '-d', '--name', 'postgres', 
                '-p', '5432:5432',
                '-e', 'POSTGRES_DB=dealer_dashboard',
                '-e', 'POSTGRES_USER=dealer_user', 
                '-e', 'POSTGRES_PASSWORD=dealer_pass',
                'postgres:15-alpine'
            ], check=True)
        
        print("⏳ Waiting for PostgreSQL to start...")
        time.sleep(10)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start PostgreSQL: {e}")
        return False

def insert_sample_data():
    """Insert sample data using the Python script"""
    print("📊 Inserting sample data...")
    
    try:
        # Run the insert script
        result = subprocess.run([sys.executable, 'insert_sample_data.py', 'more'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sample data inserted successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Failed to insert sample data: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running insert script: {e}")
        return False

def test_api_directly():
    """Test the API endpoints directly"""
    print("🧪 Testing API endpoints...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API health check passed")
        else:
            print("❌ API health check failed")
            return False
        
        # Test dealers endpoint
        response = requests.get('http://localhost:8000/dealers/', timeout=5)
        if response.status_code == 200:
            dealers = response.json()
            print(f"✅ Found {len(dealers)} dealers")
        else:
            print("❌ Dealers endpoint failed")
        
        # Test analytics endpoint
        response = requests.get('http://localhost:8000/prospect-data/analytics/00999', timeout=5)
        if response.status_code == 200:
            analytics = response.json()
            total_prospects = analytics.get('total_prospects', 0)
            print(f"✅ Analytics working - {total_prospects} total prospects")
            return True
        else:
            print("❌ Analytics endpoint failed")
            return False
            
    except ImportError:
        print("⚠️  requests package not available, skipping API test")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Quick Test - Dealer Dashboard")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('dashboard.py').exists():
        print("❌ Please run this script from the dealer-dashboard directory")
        return False
    
    # Check Python packages
    if not check_python_packages():
        return False
    
    # Start database
    if not start_database():
        return False
    
    # Insert sample data
    if not insert_sample_data():
        return False
    
    print("\n🎉 Sample data inserted successfully!")
    print("\n📊 Dashboard Test Data Summary:")
    print("   - Dealer ID: 00999")
    print("   - Prospect Records: 20+")
    print("   - Date Range: Last 7 days")
    print("   - Unit Types: PCX160, VARIO125, BEAT, etc.")
    print("   - Various Status: New, In Progress, Completed")
    
    print("\n🚀 Next Steps:")
    print("   1. Start the backend API:")
    print("      uvicorn main:app --reload")
    print("   2. Start the dashboard:")
    print("      streamlit run dashboard.py")
    print("   3. Open: http://localhost:8501")
    print("   4. Go to 'Dashboard' page")
    print("   5. Select 'Default Dealer (00999)'")
    print("   6. View the analytics charts!")
    
    # If API is running, test it
    print("\n🧪 Testing if API is already running...")
    if test_api_directly():
        print("\n✅ API is running and working!")
        print("🌐 You can now open the dashboard: http://localhost:8501")
    else:
        print("\n⚠️  API is not running. Start it with: uvicorn main:app --reload")
    
    print("\n🛑 To stop database: docker stop postgres")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
