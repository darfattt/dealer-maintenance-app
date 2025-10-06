#!/usr/bin/env python3
"""
Test script to insert sample Parts Inbound data for testing the dashboard
"""

import os
import sys
from datetime import datetime, date, timedelta
import random
import uuid

# Add the backend directory to the path
sys.path.append('backend')

from database import SessionLocal, PartsInboundData, PartsInboundPO

def create_sample_parts_inbound_data(dealer_id="12284", count=20):
    """Create sample Parts Inbound data"""
    db = SessionLocal()
    try:
        # Sample data lists
        parts_numbers = [
            "272A0KCJ660", "372A0KCJ660", "15400-KVB-901", "06435-KVB-000", 
            "91201-KVB-003", "42450-KVB-000", "35010-KVB-000", "17220-KVB-000",
            "44300-KVB-000", "53200-KVB-000", "64300-KVB-000", "72100-KVB-000"
        ]
        
        warehouses = ["WH123", "WH124", "WH125", "WH126", "WH127"]
        jenis_orders = ["1", "2", "3"]  # Different order types
        uoms = ["pcs", "set", "unit", "box"]
        
        for i in range(count):
            # Create Parts Inbound data
            receipt_date = date.today() - timedelta(days=random.randint(0, 30))
            receipt_num = random.randint(1, 999)
            
            parts_inbound = PartsInboundData(
                dealer_id=dealer_id,
                no_penerimaan=f"RCV/{dealer_id}/{receipt_date.strftime('%y')}/{receipt_date.strftime('%m')}/{receipt_num:04d}",
                tgl_penerimaan=receipt_date.strftime("%d/%m/%Y"),
                no_shipping_list=f"SPL/{dealer_id}/{receipt_date.strftime('%y')}/{receipt_date.strftime('%m')}/{receipt_num:04d}",
                created_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                modified_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                fetched_at=datetime.now()
            )
            
            db.add(parts_inbound)
            db.flush()  # Get the ID
            
            # Add PO items
            num_po_items = random.randint(1, 4)
            for po_idx in range(num_po_items):
                po_number = f"PO{dealer_id}{receipt_date.strftime('%y%m')}{random.randint(1000, 9999)}"
                
                po_item = PartsInboundPO(
                    parts_inbound_data_id=parts_inbound.id,
                    no_po=po_number,
                    jenis_order=random.choice(jenis_orders),
                    id_warehouse=random.choice(warehouses),
                    parts_number=random.choice(parts_numbers),
                    kuantitas=random.randint(10, 500),
                    uom=random.choice(uoms),
                    created_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    modified_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                )
                
                db.add(po_item)
        
        db.commit()
        print(f"✅ Created {count} sample Parts Inbound records for dealer {dealer_id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Parts Inbound data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating sample Parts Inbound data for dashboard testing...")
    
    # Create sample data for dealer 12284 (dummy data dealer)
    create_sample_parts_inbound_data("12284", 20)
    
    # Create some data for dealer 00999 as well
    create_sample_parts_inbound_data("00999", 15)
    
    print("✅ Sample Parts Inbound data creation completed!")
    print("🔗 Access Analytics Dashboard: http://localhost:8501")
