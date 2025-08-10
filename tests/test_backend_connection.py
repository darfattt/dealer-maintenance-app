#!/usr/bin/env python3
"""
Test backend connection for admin panel
"""

import requests
import os
import socket

def test_hostname_resolution():
    """Test if we can resolve backend hostname"""
    try:
        socket.gethostbyname('backend')
        print("✅ Can resolve 'backend' hostname - likely running in Docker")
        return True
    except socket.gaierror:
        print("❌ Cannot resolve 'backend' hostname - running directly")
        return False

def test_backend_connection(url):
    """Test connection to backend"""
    try:
        print(f"Testing connection to: {url}")
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is accessible at {url}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection refused to {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Connection timeout to {url}")
        return False
    except Exception as e:
        print(f"❌ Error connecting to {url}: {e}")
        return False

def main():
    print("🔍 Testing Backend Connection for Admin Panel")
    print("=" * 50)
    
    # Test hostname resolution
    can_resolve_backend = test_hostname_resolution()
    
    # Test different backend URLs
    urls_to_test = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    if can_resolve_backend:
        urls_to_test.append("http://backend:8000")
    
    print("\n🌐 Testing Backend URLs:")
    print("-" * 30)
    
    working_urls = []
    for url in urls_to_test:
        if test_backend_connection(url):
            working_urls.append(url)
    
    print("\n📊 Results:")
    print("-" * 20)
    if working_urls:
        print(f"✅ Working URLs: {', '.join(working_urls)}")
        recommended_url = working_urls[0]
        print(f"🎯 Recommended BACKEND_URL: {recommended_url}")
        
        # Set environment variable
        os.environ['BACKEND_URL'] = recommended_url
        print(f"🔧 Environment variable set: BACKEND_URL={recommended_url}")
    else:
        print("❌ No working backend URLs found!")
        print("💡 Make sure the backend service is running")
    
    print("\n🚀 To run admin panel with correct backend URL:")
    if working_urls:
        print(f"   set BACKEND_URL={working_urls[0]}")
        print("   cd admin_panel")
        print("   streamlit run admin_app.py --server.port 8503")
    else:
        print("   First start the backend service, then try again")

if __name__ == "__main__":
    main()
