#!/usr/bin/env python3
"""
Test document handling data history endpoint
"""

import requests
import json
from datetime import datetime, timedelta

def test_document_handling_history():
    """Test document handling data history endpoint"""
    print("🔍 TESTING DOCUMENT HANDLING DATA HISTORY")
    print("=" * 60)
    
    # Service endpoint
    service_url = "http://localhost:8200"
    dealer_id = "12284"
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    date_from = start_date.strftime('%Y-%m-%d')
    date_to = end_date.strftime('%Y-%m-%d')
    
    print(f"🎯 Target: {service_url}")
    print(f"📋 Dealer: {dealer_id}")
    print(f"📅 Date range: {date_from} to {date_to}")
    print()
    
    # Test document handling data history endpoint
    print("1️⃣ TESTING DOCUMENT HANDLING DATA HISTORY ENDPOINT...")
    try:
        response = requests.get(
            f"{service_url}/api/v1/dashboard/document-handling-data-history",
            params={
                "dealer_id": dealer_id,
                "date_from": date_from,
                "date_to": date_to,
                "page": 1,
                "per_page": 5
            },
            timeout=10
        )
        
        print(f"📤 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document handling data history endpoint working")
            print(f"   Success: {result.get('success', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            data = result.get('data', [])
            print(f"   Total records: {len(data)}")
            
            if data:
                print(f"\n📋 FIRST RECORD DETAILS:")
                first_record = data[0]
                print(f"   No: {first_record.get('no', 'N/A')}")
                print(f"   ID SPK: {first_record.get('id_spk', 'N/A')}")
                print(f"   ID SO: {first_record.get('id_so', 'N/A')}")
                print(f"   Tgl Pengajuan STNK: {first_record.get('tgl_pengajuan_stnk', 'N/A')}")
                print(f"   Status Faktur STNK: {first_record.get('status_faktur_stnk', 'N/A')}")
                print(f"   Nomor STNK: {first_record.get('nomor_stnk', 'N/A')}")
                print(f"   Plat Nomor: {first_record.get('plat_nomor', 'N/A')}")
                print(f"   Tgl Terima STNK: {first_record.get('tgl_terima_stnk', 'N/A')}")
                print(f"   Nama Penerima STNK: {first_record.get('nama_penerima_stnk', 'N/A')}")
                print(f"   Tgl Terima BPKB: {first_record.get('tgl_terima_bpkb', 'N/A')}")
                print(f"   Nama Penerima BPKB: {first_record.get('nama_penerima_bpkb', 'N/A')}")
                
                # Check if unit data is now populated
                unit_fields = [
                    'tgl_pengajuan_stnk', 'status_faktur_stnk', 'nomor_stnk', 
                    'plat_nomor', 'tgl_terima_stnk', 'nama_penerima_stnk',
                    'tgl_terima_bpkb', 'nama_penerima_bpkb'
                ]
                
                populated_fields = [field for field in unit_fields if first_record.get(field) is not None]
                null_fields = [field for field in unit_fields if first_record.get(field) is None]
                
                print(f"\n📊 UNIT DATA STATUS:")
                print(f"   ✅ Populated fields ({len(populated_fields)}): {populated_fields}")
                print(f"   ❌ Null fields ({len(null_fields)}): {null_fields}")
                
                if len(populated_fields) > 0:
                    print(f"   🎉 SUCCESS: Unit data is now being joined correctly!")
                else:
                    print(f"   ⚠️ ISSUE: Unit data is still null - join may not be working")
                    
            else:
                print(f"   ⚠️ No data returned")
                
        else:
            print(f"❌ Document handling data history endpoint failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Document handling data history endpoint error: {e}")
    
    print(f"\n✅ Document handling data history test completed")

if __name__ == "__main__":
    test_document_handling_history()
