#!/usr/bin/env python3
"""
Test script for Leasing Data History API integration
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend path to sys.path
backend_path = os.path.join(os.path.dirname(__file__), 'backend-microservices', 'services', 'dashboard-dealer')
sys.path.insert(0, backend_path)

from app.controllers.dashboard_controller import DashboardController
from app.database import get_db_session

async def test_leasing_data_history():
    """Test the leasing data history API integration"""
    print("Testing Leasing Data History API Integration...")
    print("=" * 50)
    
    # Get database session
    db = next(get_db_session())
    
    try:
        # Create controller
        controller = DashboardController(db)
        
        # Test parameters
        dealer_id = "12284"
        date_from = "2024-01-01"
        date_to = "2024-12-31"
        page = 1
        per_page = 20
        
        print(f"Testing with parameters:")
        print(f"  Dealer ID: {dealer_id}")
        print(f"  Date From: {date_from}")
        print(f"  Date To: {date_to}")
        print(f"  Page: {page}")
        print(f"  Per Page: {per_page}")
        print()
        
        # Call the API method
        result = await controller.get_leasing_data_history(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page
        )
        
        # Display results
        print("API Response:")
        print(f"  Success: {result.success}")
        print(f"  Message: {result.message}")
        print(f"  Total Records: {result.total_records}")
        print(f"  Page: {result.page}")
        print(f"  Per Page: {result.per_page}")
        print(f"  Total Pages: {result.total_pages}")
        print(f"  Data Count: {len(result.data)}")
        print()
        
        if result.data:
            print("Sample Data (first 3 records):")
            for i, item in enumerate(result.data[:3]):
                print(f"  Record {i+1}:")
                print(f"    No: {item.no}")
                print(f"    ID SPK: {item.id_spk}")
                print(f"    ID Dokumen Pengajuan: {item.id_dokumen_pengajuan}")
                print(f"    Tanggal Pengajuan: {item.tgl_pengajuan}")
                print(f"    Jumlah DP: {item.jumlah_dp}")
                print(f"    Tenor: {item.tenor}")
                print(f"    Jumlah Cicilan: {item.jumlah_cicilan}")
                print(f"    Nama Finance Company: {item.nama_finance_company}")
                print()
        else:
            print("No data returned")
            
        print("✅ Leasing Data History API integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_leasing_data_history())
