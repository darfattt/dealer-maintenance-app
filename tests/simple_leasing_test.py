#!/usr/bin/env python3
"""
Simple test for Leasing Data History API - just test the schema
"""

import sys
import os

# Add the backend path to sys.path
backend_path = os.path.join(os.path.dirname(__file__), 'backend-microservices', 'services', 'dashboard-dealer')
sys.path.insert(0, backend_path)

def test_leasing_schema():
    """Test the leasing data history schema"""
    print("Testing Leasing Data History Schema...")
    print("=" * 40)
    
    try:
        from app.schemas.dashboard import LeasingDataHistoryItem, LeasingDataHistoryResponse
        
        # Test creating a sample item
        sample_item = LeasingDataHistoryItem(
            no=1,
            id_spk="SPK001234",
            id_dokumen_pengajuan="DOC001234",
            tgl_pengajuan="2024-01-15",
            jumlah_dp=5000000.0,
            tenor=24,
            jumlah_cicilan=2500000.0,
            nama_finance_company="BCA Finance"
        )
        
        print("✅ LeasingDataHistoryItem created successfully:")
        print(f"  No: {sample_item.no}")
        print(f"  ID SPK: {sample_item.id_spk}")
        print(f"  ID Dokumen Pengajuan: {sample_item.id_dokumen_pengajuan}")
        print(f"  Tanggal Pengajuan: {sample_item.tgl_pengajuan}")
        print(f"  Jumlah DP: {sample_item.jumlah_dp}")
        print(f"  Tenor: {sample_item.tenor}")
        print(f"  Jumlah Cicilan: {sample_item.jumlah_cicilan}")
        print(f"  Nama Finance Company: {sample_item.nama_finance_company}")
        print()
        
        # Test creating a response
        sample_response = LeasingDataHistoryResponse(
            success=True,
            message="Test successful",
            data=[sample_item],
            total_records=1,
            page=1,
            per_page=20,
            total_pages=1
        )
        
        print("✅ LeasingDataHistoryResponse created successfully:")
        print(f"  Success: {sample_response.success}")
        print(f"  Message: {sample_response.message}")
        print(f"  Data Count: {len(sample_response.data)}")
        print(f"  Total Records: {sample_response.total_records}")
        print(f"  Page: {sample_response.page}")
        print(f"  Per Page: {sample_response.per_page}")
        print(f"  Total Pages: {sample_response.total_pages}")
        print()
        
        print("✅ All schema tests passed!")
        
    except Exception as e:
        print(f"❌ Error during schema testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_leasing_schema()
