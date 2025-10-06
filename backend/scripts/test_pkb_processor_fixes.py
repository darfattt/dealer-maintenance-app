#!/usr/bin/env python3
"""
Test script to validate that the PKB processor fixes are correct
"""

import sys
import ast
sys.path.append('.')

def test_python_syntax():
    """Test that all modified files have correct Python syntax"""
    files_to_check = [
        'backend/tasks/processors/pkb_processor.py',
        'backend/database.py'
    ]
    
    print("=== Testing Python Syntax ===")
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            ast.parse(code)
            print(f"✓ {file_path} - Syntax OK")
        except SyntaxError as e:
            print(f"✗ {file_path} - Syntax Error: {e}")
            return False
        except Exception as e:
            print(f"✗ {file_path} - Error: {e}")
            return False
    
    return True

def test_transaction_management_removed():
    """Test that manual transaction management has been removed from PKB processor"""
    print("\n=== Testing Transaction Management Removal ===")
    
    try:
        with open('backend/tasks/processors/pkb_processor.py', 'r') as f:
            content = f.read()
        
        # Check that db.commit() and db.rollback() are not present in process_records method
        if 'db.commit()' in content:
            print("✗ Found db.commit() - manual transaction management still present")
            return False
        
        if 'db.rollback()' in content:
            print("✗ Found db.rollback() - manual transaction management still present")
            return False
        
        print("✓ Manual transaction management removed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error checking transaction management: {e}")
        return False

def test_bulk_upsert_usage():
    """Test that bulk_upsert is used instead of bulk_insert_mappings"""
    print("\n=== Testing Bulk Upsert Usage ===")
    
    try:
        with open('backend/tasks/processors/pkb_processor.py', 'r') as f:
            content = f.read()
        
        # Check that bulk_insert_mappings is not used
        if 'bulk_insert_mappings' in content:
            print("✗ Found bulk_insert_mappings - should use bulk_upsert instead")
            return False
        
        # Check that bulk_upsert is used for services and parts
        bulk_upsert_count = content.count('self.bulk_upsert(')
        if bulk_upsert_count < 3:  # Main records + services + parts
            print(f"✗ Expected at least 3 bulk_upsert calls, found {bulk_upsert_count}")
            return False
        
        print("✓ Bulk upsert is used correctly for all record types")
        return True
        
    except Exception as e:
        print(f"✗ Error checking bulk upsert usage: {e}")
        return False

def test_unique_constraints():
    """Test that UniqueConstraint definitions have been added to database models"""
    print("\n=== Testing UniqueConstraint Definitions ===")
    
    try:
        with open('backend/database.py', 'r') as f:
            content = f.read()
        
        required_constraints = [
            'uq_pkb_dealer_work_order',
            'uq_pkb_service_data_id_job', 
            'uq_pkb_part_data_id_job_parts_number'
        ]
        
        missing_constraints = []
        for constraint in required_constraints:
            if constraint not in content:
                missing_constraints.append(constraint)
        
        if missing_constraints:
            print(f"✗ Missing constraints: {missing_constraints}")
            return False
        
        print("✓ All required UniqueConstraint definitions are present")
        return True
        
    except Exception as e:
        print(f"✗ Error checking unique constraints: {e}")
        return False

def main():
    """Run all tests"""
    print("=== PKB Processor Fix Validation ===")
    
    tests = [
        test_python_syntax,
        test_transaction_management_removed,
        test_bulk_upsert_usage,
        test_unique_constraints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All PKB processor fixes are correct!")
        print("\nThe PKB processor should now work without transaction abort issues.")
        print("Next steps:")
        print("1. Run the database migration script to add the unique constraints")
        print("2. Test the PKB processor from the admin panel")
        return True
    else:
        print("✗ Some tests failed. Please fix the issues before testing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)