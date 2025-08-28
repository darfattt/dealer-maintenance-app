#!/usr/bin/env python3
"""
Test script for phone number masking functionality
"""
import sys
import os

# Add the backend-microservices/services/customer directory to Python path
sys.path.append('/mnt/e/darfat/work/dgi/dealer-management-app/dealer-maintenance-app/backend-microservices/services/customer')

from app.utils.phone_masking import mask_phone_number

def test_phone_masking():
    """Test phone number masking with various formats"""
    
    test_cases = [
        # (input, expected_output)
        ("08123456789", "081*****89"),  # Standard Indonesian mobile
        ("6281234567890", "628*****90"),  # Indonesian with country code
        ("081234567890", "081*****90"),   # 12-digit Indonesian
        ("08123456", "081*****56"),       # 8-digit number
        ("0812", "0812"),               # Too short - return as-is
        ("123", "123"),                 # Too short - return as-is
        ("", ""),                       # Empty string
        (None, ""),                     # None input
        ("081-234-5678", "081*****78"),   # With dashes (should strip non-digits)
        ("+62 812 3456 789", "628*****89"), # With spaces and + (should strip non-digits)
        ("08123456789012345", "081*****45"), # Very long number
    ]
    
    print("Testing phone number masking functionality:")
    print("=" * 50)
    
    all_passed = True
    for i, (input_phone, expected) in enumerate(test_cases, 1):
        try:
            result = mask_phone_number(input_phone)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            if result != expected:
                all_passed = False
            
            print(f"Test {i:2d}: {status}")
            print(f"  Input:    '{input_phone}'")
            print(f"  Expected: '{expected}'")
            print(f"  Got:      '{result}'")
            print()
            
        except Exception as e:
            print(f"Test {i:2d}: ❌ ERROR - Exception occurred")
            print(f"  Input:    '{input_phone}'")
            print(f"  Error:    {str(e)}")
            print()
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests PASSED!")
    else:
        print("⚠️  Some tests FAILED!")
    
    return all_passed

if __name__ == "__main__":
    test_phone_masking()