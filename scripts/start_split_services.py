#!/usr/bin/env python3
"""
Start split services for Dealer Dashboard
- Analytics Dashboard (Port 8501) - Direct DB connection
- Admin Panel (Port 8502) - API-based management
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import uvicorn
        import streamlit
        import celery
        import redis
        import psycopg2
        import sqlalchemy
        print("✅ All Python dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def check_services():
    """Check if PostgreSQL and Redis are running"""
    services_ok = True
    
    # Check PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="dealer_dashboard",
            user="dealer_user",
            password="dealer_pass"
        )
        conn.close()
        print("✅ PostgreSQL is running")
    except Exception:
        print("❌ PostgreSQL is not running or not configured")
        print("   Start with: docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=dealer_dashboard -e POSTGRES_USER=dealer_user -e POSTGRES_PASSWORD=dealer_pass postgres:15-alpine")
        services_ok = False
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
    except Exception:
        print("❌ Redis is not running")
        print("   Start with: docker run -d --name redis -p 6379:6379 redis:7-alpine")
        services_ok = False
    
    return services_ok

def start_split_services():
    """Start all services in split architecture"""
    
    print("🚀 Starting Dealer Dashboard - Split Architecture")
    print("=" * 60)
    print("📊 Analytics Dashboard: Port 8501 (Direct DB)")
    print("⚙️ Admin Panel: Port 8502 (API-based)")
    print("🔧 Backend API: Port 8000")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check external services
    if not check_services():
        print("\n💡 Quick start external services:")
        print("docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=dealer_dashboard -e POSTGRES_USER=dealer_user -e POSTGRES_PASSWORD=dealer_pass postgres:15-alpine")
        print("docker run -d --name redis -p 6379:6379 redis:7-alpine")
        return False
    
    # Setup development data
    print("\n📊 Setting up development data...")
    try:
        subprocess.run([sys.executable, "insert_sample_data.py", "more"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️  Failed to setup development data (may already exist)")
    
    print("\n🔧 Starting services...")
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("Starting FastAPI backend (Port 8000)...")
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        processes.append(("Backend API", backend_process))
        time.sleep(3)
        
        # Start Celery worker
        print("Starting Celery worker...")
        celery_process = subprocess.Popen([
            sys.executable, "-m", "celery", "-A", "celery_app", 
            "worker", "--loglevel=info"
        ])
        processes.append(("Celery Worker", celery_process))
        time.sleep(3)
        
        # Start Analytics Dashboard (Direct DB)
        print("Starting Analytics Dashboard (Port 8501)...")
        analytics_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "dashboard_analytics.py",
            "--server.port", "8501", "--server.address", "0.0.0.0"
        ])
        processes.append(("Analytics Dashboard", analytics_process))
        time.sleep(3)
        
        # Start Admin Panel (API-based)
        print("Starting Admin Panel (Port 8502)...")
        admin_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "admin_app.py",
            "--server.port", "8502", "--server.address", "0.0.0.0"
        ])
        processes.append(("Admin Panel", admin_process))
        
        print("\n🎉 All services started successfully!")
        print("\n🌐 Access URLs:")
        print("📊 Analytics Dashboard: http://localhost:8501")
        print("⚙️ Admin Panel: http://localhost:8502")
        print("🔧 Backend API: http://localhost:8000/docs")
        print("📈 API Health: http://localhost:8000/health")
        
        print("\n🏗️ Architecture:")
        print("📊 Analytics Dashboard (8501) → Direct DB Connection")
        print("⚙️ Admin Panel (8502) → Backend API (8000) → Database")
        print("🔄 Celery Worker → Background Jobs → Database")
        
        print("\n📋 Default Dealer:")
        print("- Dealer ID: 00999")
        print("- Name: Default Dealer")
        print("- Sample Data: 20+ prospect records")
        
        print("\n💡 Usage:")
        print("1. Analytics Dashboard: View charts and metrics")
        print("2. Admin Panel: Manage dealers, run jobs, view history")
        print("3. Both services work independently")
        
        print("\n💡 Press Ctrl+C to stop all services")
        
        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
                # Check if any process died
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} process stopped unexpectedly")
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        
    finally:
        # Clean up processes
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 Force killed {name}")
            except Exception as e:
                print(f"⚠️  Error stopping {name}: {e}")
    
    return True

if __name__ == "__main__":
    start_split_services()
