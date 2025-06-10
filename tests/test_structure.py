"""
Test script to verify the reorganized project structure
"""

import os
import sys

def test_project_structure():
    """Test that all expected directories and files exist"""
    print("🧪 Testing Project Structure...")
    
    # Expected directories
    expected_dirs = [
        'components',
        'docker',
        'scripts', 
        'docs',
        'tests',
        'tasks',
        'utils'
    ]
    
    # Expected files in root
    expected_root_files = [
        'admin_app.py',
        'dashboard_analytics.py',
        'main.py',
        'database.py',
        'celery_app.py',
        'requirements.txt',
        'docker-compose.yml',
        'start.bat',
        'README.md'
    ]
    
    # Expected component files
    expected_component_files = [
        'components/api_utils.py',
        'components/navigation.py',
        'components/dealer_management.py',
        'components/run_jobs.py',
        'components/job_history.py',
        'components/configuration.py'
    ]
    
    # Expected docker files
    expected_docker_files = [
        'docker/Dockerfile',
        'docker/init.sql',
        'docker/docker-compose.simple.yml',
        'docker/docker-compose.split.yml'
    ]
    
    # Expected script files
    expected_script_files = [
        'scripts/start.bat',
        'scripts/start_dev.py',
        'scripts/insert_sample_data.py',
        'scripts/fix_pandas_issues.py'
    ]
    
    # Expected test files
    expected_test_files = [
        'tests/test_api.py',
        'tests/test_app.py',
        'tests/test_services.py'
    ]
    
    # Expected doc files
    expected_doc_files = [
        'docs/MODULAR_ARCHITECTURE.md',
        'docs/ADMIN_PANEL_FEATURES.md',
        'docs/TROUBLESHOOTING.md'
    ]
    
    all_tests_passed = True
    
    # Test directories
    print("\n📁 Testing Directories:")
    for dir_name in expected_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"  ✅ {dir_name}")
        else:
            print(f"  ❌ {dir_name} - Missing")
            all_tests_passed = False
    
    # Test root files
    print("\n📄 Testing Root Files:")
    for file_name in expected_root_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_tests_passed = False
    
    # Test component files
    print("\n🧩 Testing Component Files:")
    for file_name in expected_component_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_tests_passed = False
    
    # Test docker files
    print("\n🐳 Testing Docker Files:")
    for file_name in expected_docker_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_tests_passed = False
    
    # Test script files
    print("\n📜 Testing Script Files:")
    for file_name in expected_script_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_tests_passed = False
    
    # Test test files
    print("\n🧪 Testing Test Files:")
    for file_name in expected_test_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_tests_passed = False
    
    # Test doc files
    print("\n📚 Testing Documentation Files:")
    for file_name in expected_doc_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing")
            all_tests_passed = False
    
    return all_tests_passed

def test_imports():
    """Test that key imports work correctly"""
    print("\n🔗 Testing Imports...")
    
    try:
        # Test component imports
        from components.api_utils import get_dealers
        print("  ✅ components.api_utils")
        
        from components.navigation import render_sidebar_navigation
        print("  ✅ components.navigation")
        
        from components.dealer_management import render_dealer_management
        print("  ✅ components.dealer_management")
        
        from components.run_jobs import render_run_jobs
        print("  ✅ components.run_jobs")
        
        from components.job_history import render_job_history
        print("  ✅ components.job_history")
        
        from components.configuration import render_configuration
        print("  ✅ components.configuration")
        
        # Test main app imports
        import main
        print("  ✅ main")
        
        import database
        print("  ✅ database")
        
        import celery_app
        print("  ✅ celery_app")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Testing Reorganized Project Structure")
    print("=" * 50)
    
    structure_test = test_project_structure()
    import_test = test_imports()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    
    if structure_test:
        print("  ✅ Project Structure: PASSED")
    else:
        print("  ❌ Project Structure: FAILED")
    
    if import_test:
        print("  ✅ Import Tests: PASSED")
    else:
        print("  ❌ Import Tests: FAILED")
    
    if structure_test and import_test:
        print("\n🎉 All tests PASSED! Project structure is correctly organized.")
        return 0
    else:
        print("\n❌ Some tests FAILED! Please check the project structure.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
