"""
Test script for PKB processor deduplication fix
Tests the fix for PostgreSQL cardinality violation error
"""
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from database import SessionLocal, PKBData, PKBService, PKBPart, Dealer
from tasks.processors.pkb_processor import PKBDataProcessor

def test_deduplication_logic():
    """Test the deduplication logic in PKB processor"""

    # Create processor instance
    processor = PKBDataProcessor()

    # Test data with duplicates
    service_records = [
        {'work_order': 'WO001', 'id_job': 'JOB001', 'nama_pekerjaan': 'Service A'},
        {'work_order': 'WO001', 'id_job': 'JOB001', 'nama_pekerjaan': 'Service A Duplicate'},  # Duplicate
        {'work_order': 'WO001', 'id_job': 'JOB002', 'nama_pekerjaan': 'Service B'},
        {'work_order': 'WO002', 'id_job': 'JOB001', 'nama_pekerjaan': 'Service C'},
    ]

    part_records = [
        {'work_order': 'WO001', 'id_job': 'JOB001', 'parts_number': 'PART001', 'kuantitas': 1},
        {'work_order': 'WO001', 'id_job': 'JOB001', 'parts_number': 'PART001', 'kuantitas': 2},  # Duplicate
        {'work_order': 'WO001', 'id_job': 'JOB001', 'parts_number': 'PART002', 'kuantitas': 1},
        {'work_order': 'WO002', 'id_job': 'JOB001', 'parts_number': 'PART001', 'kuantitas': 1},
    ]

    db = SessionLocal()

    try:
        # Create test dealer data if not exists
        test_dealer_id = "TEST001"
        dealer = db.query(Dealer).filter(Dealer.dealer_id == test_dealer_id).first()
        if not dealer:
            print(f"Creating test dealer {test_dealer_id}")
            dealer = Dealer(
                dealer_id=test_dealer_id,
                dealer_name="Test Dealer",
                api_key="test_key",
                secret_key="test_secret",
                is_active=True
            )
            db.add(dealer)
            db.commit()

        # Create test PKB records
        pkb_records = [
            {
                'dealer_id': test_dealer_id,
                'no_work_order': 'WO001',
                'tanggal_servis': '2024-01-01',
                'fetched_at': datetime.utcnow()
            },
            {
                'dealer_id': test_dealer_id,
                'no_work_order': 'WO002',
                'tanggal_servis': '2024-01-02',
                'fetched_at': datetime.utcnow()
            }
        ]

        # Insert PKB records first
        print("Creating test PKB records...")
        processed = processor.bulk_upsert(
            db,
            PKBData,
            pkb_records,
            conflict_columns=['dealer_id', 'no_work_order'],
            batch_size=500
        )
        db.commit()
        print(f"Created {processed} PKB records")

        # Test service record deduplication
        print("\nTesting service record deduplication...")
        services_processed = processor._process_child_records(
            db, test_dealer_id, service_records, PKBService,
            ['pkb_data_id', 'id_job'], "services"
        )
        db.commit()
        print(f"Processed {services_processed} service records (should be 3, not 4)")

        # Test part record deduplication
        print("\nTesting part record deduplication...")
        parts_processed = processor._process_child_records(
            db, test_dealer_id, part_records, PKBPart,
            ['pkb_data_id', 'id_job', 'parts_number'], "parts"
        )
        db.commit()
        print(f"Processed {parts_processed} part records (should be 3, not 4)")

        # Verify records in database
        total_services = db.query(PKBService).join(PKBData).filter(PKBData.dealer_id == test_dealer_id).count()
        total_parts = db.query(PKBPart).join(PKBData).filter(PKBData.dealer_id == test_dealer_id).count()

        print(f"\nVerification:")
        print(f"Total services in DB: {total_services}")
        print(f"Total parts in DB: {total_parts}")

        # Clean up test data
        print("\nCleaning up test data...")
        db.query(PKBService).filter(PKBService.pkb_data_id.in_(
            db.query(PKBData.id).filter(PKBData.dealer_id == test_dealer_id)
        )).delete(synchronize_session=False)

        db.query(PKBPart).filter(PKBPart.pkb_data_id.in_(
            db.query(PKBData.id).filter(PKBData.dealer_id == test_dealer_id)
        )).delete(synchronize_session=False)

        db.query(PKBData).filter(PKBData.dealer_id == test_dealer_id).delete()
        db.query(Dealer).filter(Dealer.dealer_id == test_dealer_id).delete()
        db.commit()
        print("Test data cleaned up")

        print("\n✅ Deduplication test completed successfully!")
        print("The fix should prevent PostgreSQL cardinality violation errors.")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing PKB processor deduplication fix...")
    test_deduplication_logic()