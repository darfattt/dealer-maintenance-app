"""
Comprehensive test script to verify the reorganized project structure
and functionality after moving files to appropriate folders
"""

import os
import sys
import requests
import time
from typing import Dict, List, Any

def test_folder_structure():
    """Test that all folders are properly organized"""
    print("🧪 Testing 3-Folder Application Structure...")

    expected_structure = {
        'backend': [
            'main.py',
            'database.py',
            'celery_app.py',
            'logging_config.py',
            'requirements.txt',
            'Dockerfile',
            'tasks',
            'utils'
        ],
        'dashboard_analytics': [
            'dashboard_analytics.py',
            'requirements.txt',
            'Dockerfile'
        ],
        'admin_panel': [
            'admin_app.py',
            'requirements.txt',
            'Dockerfile',
            'components'
        ],
        'docker': [
            'Dockerfile',
            'docker-compose.yml',
            'docker-compose.simple.yml',
            'docker-compose.split.yml',
            'init.sql',
            'monitoring'
        ],
        'scripts': [
            'start.bat',
            'start_dev.py',
            'insert_sample_data.py',
            'fix_pandas_issues.py'
        ],
        'tests': [
            'test_api.py',
            'test_app.py',
            'test_services.py',
            'test_structure.py',
            'test_reorganized_structure.py'
        ],
        'docs': [
            'MODULAR_ARCHITECTURE.md',
            'ADMIN_PANEL_FEATURES.md',
            'TROUBLESHOOTING.md',
            'PROJECT_STRUCTURE.md'
        ]
    }
    
    all_passed = True
    
    for folder, expected_files in expected_structure.items():
        print(f"\n📁 Testing {folder}/ folder:")
        
        if not os.path.exists(folder):
            print(f"  ❌ Folder {folder} does not exist")
            all_passed = False
            continue
            
        for file_name in expected_files:
            file_path = os.path.join(folder, file_name)
            if os.path.exists(file_path):
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name} - Missing")
                all_passed = False
    
    return all_passed

def test_root_files():
    """Test that essential root files are present"""
    print("\n📄 Testing Root Files:")

    essential_root_files = [
        'requirements.txt',  # Main requirements file
        'docker-compose.yml',
        'start.bat',
        'README.md',
        'REORGANIZATION_COMPLETE.md'
    ]
    
    all_passed = True
    
    for file_name in essential_root_files:
        if os.path.exists(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_passed = False
    
    return all_passed

def test_docker_paths():
    """Test that docker-compose.yml has correct paths"""
    print("\n🐳 Testing Docker Configuration:")

    try:
        with open('docker-compose.yml', 'r') as f:
            content = f.read()

        # Check for updated paths for 3-folder structure
        path_checks = [
            ('context: ./backend', 'Backend context path'),
            ('context: ./dashboard_analytics', 'Dashboard analytics context path'),
            ('context: ./admin_panel', 'Admin panel context path'),
            ('./docker/init.sql', 'init.sql path'),
            ('./docker/monitoring/', 'monitoring path')
        ]
        
        all_passed = True
        
        for path_check, description in path_checks:
            if path_check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} - Not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error reading docker-compose.yml: {e}")
        return False

def test_service_health():
    """Test that all services are responding"""
    print("\n🏥 Testing Service Health:")
    
    services = [
        ('Backend API', 'http://localhost:8000/health'),
        ('Analytics Dashboard', 'http://localhost:8501/_stcore/health'),
        ('Admin Panel', 'http://localhost:8502/_stcore/health')
    ]
    
    all_passed = True
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {service_name}")
            else:
                print(f"  ⚠️ {service_name} - Status {response.status_code}")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {service_name} - Connection failed: {e}")
            all_passed = False
    
    return all_passed

def test_admin_panel_functionality():
    """Test admin panel modular components"""
    print("\n⚙️ Testing Admin Panel Functionality:")
    
    try:
        # Test API endpoints that admin panel uses
        backend_url = "http://localhost:8000"
        
        endpoints = [
            ('/dealers/', 'Dealers endpoint'),
            ('/fetch-logs/', 'Fetch logs endpoint'),
            ('/health', 'Health endpoint')
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 422]:  # 422 is OK for some endpoints without params
                    print(f"  ✅ {description}")
                else:
                    print(f"  ⚠️ {description} - Status {response.status_code}")
                    all_passed = False
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {description} - Failed: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error testing admin panel: {e}")
        return False

def test_file_cleanup():
    """Test that unused files were removed"""
    print("\n🧹 Testing File Cleanup:")
    
    files_that_should_be_removed = [
        'admin_app_modular.py',
        'admin_app_original.py',
        'dashboard.py'
    ]
    
    all_passed = True
    
    for file_name in files_that_should_be_removed:
        if not os.path.exists(file_name):
            print(f"  ✅ {file_name} - Properly removed")
        else:
            print(f"  ⚠️ {file_name} - Still exists (should be removed)")
            all_passed = False
    
    return all_passed

def test_documentation():
    """Test that documentation is properly organized"""
    print("\n📚 Testing Documentation:")
    
    doc_files = [
        'docs/MODULAR_ARCHITECTURE.md',
        'docs/ADMIN_PANEL_FEATURES.md',
        'docs/PROJECT_STRUCTURE.md'
    ]
    
    all_passed = True
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            # Check if file has content
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content) > 100:  # Basic content check
                    print(f"  ✅ {doc_file}")
                else:
                    print(f"  ⚠️ {doc_file} - File too small")
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {doc_file} - Error reading: {e}")
                all_passed = False
        else:
            print(f"  ❌ {doc_file} - Missing")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🎯 Testing Reorganized Project Structure")
    print("=" * 60)
    
    tests = [
        ("Folder Structure", test_folder_structure),
        ("Root Files", test_root_files),
        ("Docker Paths", test_docker_paths),
        ("Service Health", test_service_health),
        ("Admin Panel Functionality", test_admin_panel_functionality),
        ("File Cleanup", test_file_cleanup),
        ("Documentation", test_documentation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:<25} {status}")
        if passed:
            passed_tests += 1
    
    print(f"\n📊 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests PASSED! Project reorganization successful!")
        print("\n🌐 Access your applications:")
        print("  📊 Analytics Dashboard: http://localhost:8501")
        print("  ⚙️ Admin Panel: http://localhost:8502")
        print("  🔧 API Documentation: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) FAILED! Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
