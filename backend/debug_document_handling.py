#!/usr/bin/env python3
"""
Debug script to test document handling processor for dealer 12284
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, DocumentHandlingData, DocumentHandlingUnit, Dealer
from tasks.processors.document_handling_processor import DocumentHandlingDataProcessor
from tasks.dummy_data_generators import should_use_dummy_data, get_dummy_document_handling_data

def test_dummy_data_generation():
    """Test if dummy data is generated correctly"""
    print("=" * 60)
    print("TESTING DUMMY DATA GENERATION")
    print("=" * 60)
    
    dealer_id = "12284"
    from_time = "2024-01-01 00:00:00"
    to_time = "2024-01-31 23:59:59"
    
    print(f"Dealer ID: {dealer_id}")
    print(f"Should use dummy data: {should_use_dummy_data(dealer_id)}")
    
    # Test dummy data generation
    dummy_data = get_dummy_document_handling_data(dealer_id, from_time, to_time)
    
    print(f"Dummy data status: {dummy_data.get('status')}")
    print(f"Dummy data message: {dummy_data.get('message')}")
    print(f"Number of records: {len(dummy_data.get('data', []))}")
    
    if dummy_data.get('data'):
        print("\nFirst record structure:")
        first_record = dummy_data['data'][0]
        print(f"  idSO: {first_record.get('idSO')}")
        print(f"  idSPK: {first_record.get('idSPK')}")
        print(f"  dealerId: {first_record.get('dealerId')}")
        print(f"  createdTime: {first_record.get('createdTime')}")
        print(f"  Number of units: {len(first_record.get('unit', []))}")
        
        if first_record.get('unit'):
            print(f"  First unit structure:")
            first_unit = first_record['unit'][0]
            print(f"    nomorRangka: {first_unit.get('nomorRangka')}")
            print(f"    statusFakturSTNK: {first_unit.get('statusFakturSTNK')}")
    
    return dummy_data

def test_database_connection():
    """Test database connection and dealer existence"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # Test basic connection
        result = db.execute("SELECT 1").fetchone()
        print("✅ Database connection successful")
        
        # Check if dealer exists
        dealer = db.query(Dealer).filter(Dealer.dealer_id == "12284").first()
        if dealer:
            print(f"✅ Dealer 12284 found: {dealer.dealer_name}")
            print(f"   API Key: {dealer.api_key[:10]}..." if dealer.api_key else "   API Key: None")
            print(f"   Secret Key: {dealer.secret_key[:10]}..." if dealer.secret_key else "   Secret Key: None")
        else:
            print("❌ Dealer 12284 not found in database")
            return None
        
        # Check existing document handling data
        existing_count = db.query(DocumentHandlingData).filter(
            DocumentHandlingData.dealer_id == "12284"
        ).count()
        print(f"📊 Existing document handling records: {existing_count}")
        
        # Check existing units
        existing_units = db.query(DocumentHandlingUnit).join(DocumentHandlingData).filter(
            DocumentHandlingData.dealer_id == "12284"
        ).count()
        print(f"📊 Existing document handling units: {existing_units}")
        
        db.close()
        return dealer
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_processor_execution():
    """Test the actual processor execution"""
    print("\n" + "=" * 60)
    print("TESTING PROCESSOR EXECUTION")
    print("=" * 60)
    
    try:
        processor = DocumentHandlingDataProcessor()
        
        # Test parameters
        dealer_id = "12284"
        from_time = "2024-01-01 00:00:00"
        to_time = "2024-01-31 23:59:59"
        
        print(f"Executing processor for dealer {dealer_id}")
        print(f"Time range: {from_time} to {to_time}")
        
        # Execute the processor
        result = processor.execute(dealer_id, from_time, to_time)
        
        print(f"Execution result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Processor execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_database_after_execution():
    """Check database state after execution"""
    print("\n" + "=" * 60)
    print("CHECKING DATABASE AFTER EXECUTION")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # Check document handling data
        documents = db.query(DocumentHandlingData).filter(
            DocumentHandlingData.dealer_id == "12284"
        ).all()
        
        print(f"📊 Total documents after execution: {len(documents)}")
        
        for i, doc in enumerate(documents):
            print(f"  Document {i+1}:")
            print(f"    ID: {doc.id}")
            print(f"    SO ID: {doc.id_so}")
            print(f"    SPK ID: {doc.id_spk}")
            print(f"    Created: {doc.created_time}")
            print(f"    Fetched at: {doc.fetched_at}")
            
            # Check units for this document
            units = db.query(DocumentHandlingUnit).filter(
                DocumentHandlingUnit.document_handling_data_id == doc.id
            ).all()
            print(f"    Units: {len(units)}")
            
            for j, unit in enumerate(units):
                print(f"      Unit {j+1}: {unit.nomor_rangka} (Status: {unit.status_faktur_stnk})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def main():
    """Main debug function"""
    print("🔍 DOCUMENT HANDLING PROCESSOR DEBUG SCRIPT")
    print("🎯 Testing dealer 12284 dummy data insertion")
    print()
    
    # Step 1: Test dummy data generation
    dummy_data = test_dummy_data_generation()
    
    # Step 2: Test database connection
    dealer = test_database_connection()
    if not dealer:
        print("❌ Cannot proceed without dealer in database")
        return
    
    # Step 3: Test processor execution
    result = test_processor_execution()
    
    # Step 4: Check database state
    check_database_after_execution()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
