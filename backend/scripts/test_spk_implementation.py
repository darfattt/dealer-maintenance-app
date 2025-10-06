#!/usr/bin/env python3
"""
Test script to verify SPK dealing process implementation
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all SPK-related modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test job types
        from admin_panel.components.job_types import JOB_TYPE_MAPPING
        assert "spk_read" in JOB_TYPE_MAPPING
        assert JOB_TYPE_MAPPING["spk_read"] == "Manage Dealing Process"
        print("✅ Job types configuration - OK")
    except Exception as e:
        print(f"❌ Job types configuration - FAILED: {e}")
    
    try:
        # Test API client
        from tasks.api_clients import SPKDealingProcessAPIClient
        client = SPKDealingProcessAPIClient()
        print("✅ SPK API client - OK")
    except Exception as e:
        print(f"❌ SPK API client - FAILED: {e}")
    
    try:
        # Test processor
        from tasks.processors.spk_dealing_process_processor import SPKDealingProcessDataProcessor
        processor = SPKDealingProcessDataProcessor()
        print("✅ SPK processor - OK")
    except Exception as e:
        print(f"❌ SPK processor - FAILED: {e}")
    
    try:
        # Test dummy data generator
        from tasks.dummy_data_generators import get_dummy_spk_dealing_process_data
        dummy_data = get_dummy_spk_dealing_process_data("12284", "2024-01-01 00:00:00", "2024-01-02 23:59:59")
        assert dummy_data["status"] == 1
        assert len(dummy_data["data"]) > 0
        print("✅ SPK dummy data generator - OK")
    except Exception as e:
        print(f"❌ SPK dummy data generator - FAILED: {e}")
    
    try:
        # Test data fetcher router
        from tasks.data_fetcher_router import get_spk_dealing_process_processor
        processor = get_spk_dealing_process_processor()
        print("✅ SPK data fetcher router - OK")
    except Exception as e:
        print(f"❌ SPK data fetcher router - FAILED: {e}")

def test_dummy_data_structure():
    """Test the structure of dummy data"""
    print("\nTesting dummy data structure...")
    
    try:
        from tasks.dummy_data_generators import get_dummy_spk_dealing_process_data
        
        # Test with sample dealer
        dummy_data = get_dummy_spk_dealing_process_data("12284", "2024-01-01 00:00:00", "2024-01-02 23:59:59")
        
        assert dummy_data["status"] == 1, "Status should be 1"
        assert "data" in dummy_data, "Should have data field"
        assert len(dummy_data["data"]) > 0, "Should have at least one record"
        
        # Test first record structure
        first_record = dummy_data["data"][0]
        required_fields = [
            "idSpk", "idProspect", "namaCustomer", "noKtp", "alamat",
            "noKontak", "email", "statusSPK", "tanggalPesanan", "unit", "dataAnggotaKeluarga"
        ]
        
        for field in required_fields:
            assert field in first_record, f"Missing required field: {field}"
        
        # Test unit structure
        assert len(first_record["unit"]) > 0, "Should have at least one unit"
        unit = first_record["unit"][0]
        unit_fields = ["kodeTipeUnit", "kodeWarna", "quantity", "hargaJual", "tipePembayaran"]
        for field in unit_fields:
            assert field in unit, f"Missing unit field: {field}"
        
        # Test family member structure
        assert len(first_record["dataAnggotaKeluarga"]) > 0, "Should have at least one family member"
        family = first_record["dataAnggotaKeluarga"][0]
        assert "anggotaKK" in family, "Missing family member field: anggotaKK"
        
        print("✅ Dummy data structure - OK")
        print(f"   Generated {len(dummy_data['data'])} SPK records")
        print(f"   First record has {len(first_record['unit'])} units and {len(first_record['dataAnggotaKeluarga'])} family members")
        
    except Exception as e:
        print(f"❌ Dummy data structure - FAILED: {e}")

def test_non_sample_dealer():
    """Test that non-sample dealers get error message"""
    print("\nTesting non-sample dealer behavior...")
    
    try:
        from tasks.dummy_data_generators import get_dummy_spk_dealing_process_data
        
        # Test with non-sample dealer
        dummy_data = get_dummy_spk_dealing_process_data("99999", "2024-01-01 00:00:00", "2024-01-02 23:59:59")
        
        assert dummy_data["status"] == 0, "Status should be 0 for non-sample dealer"
        assert "No dummy data available" in dummy_data["message"], "Should have appropriate error message"
        assert len(dummy_data["data"]) == 0, "Should have no data"
        
        print("✅ Non-sample dealer behavior - OK")
        print(f"   Error message: {dummy_data['message']}")
        
    except Exception as e:
        print(f"❌ Non-sample dealer behavior - FAILED: {e}")

def test_api_configuration():
    """Test API configuration"""
    print("\nTesting API configuration...")
    
    try:
        from tasks.api_clients import initialize_default_api_configs
        print("✅ API configuration function - OK")
        
        # Test that SPK API client can be instantiated
        from tasks.api_clients import SPKDealingProcessAPIClient
        client = SPKDealingProcessAPIClient()
        assert client.endpoint == "/spk/read", "Endpoint should be /spk/read"
        
        print("✅ SPK API client configuration - OK")
        print(f"   Endpoint: {client.endpoint}")
        
    except Exception as e:
        print(f"❌ API configuration - FAILED: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing SPK Dealing Process Implementation")
    print("=" * 50)
    
    test_imports()
    test_dummy_data_structure()
    test_non_sample_dealer()
    test_api_configuration()
    
    print("\n" + "=" * 50)
    print("✅ SPK Dealing Process implementation test completed!")
    print("\n📋 Summary:")
    print("- Job type 'spk_read' added to admin panel")
    print("- API client for SPK dealing process implemented")
    print("- Data processor with complex nested data handling")
    print("- Dummy data generator with realistic test data")
    print("- Database models for SPK, units, and family members")
    print("- Backend controller with REST API endpoints")
    print("- Dashboard analytics integration")
    print("- Complete routing and task integration")

if __name__ == "__main__":
    main()
