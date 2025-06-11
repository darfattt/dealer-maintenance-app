#!/usr/bin/env python3
"""
Test script to insert sample prospect and PKB data for testing the dashboard
"""

import os
import sys
from datetime import datetime, date, timedelta
import random
import uuid

# Add the backend directory to the path
sys.path.append('backend')

from database import SessionLocal, ProspectData, ProspectUnit, PKBData, PKBService, PKBPart

def create_sample_prospect_data(dealer_id="00999", count=50):
    """Create sample prospect data"""
    db = SessionLocal()
    try:
        # Sample data lists
        names = [
            "Ahmad Wijaya", "Siti Nurhaliza", "Budi Santoso", "Dewi Sartika", "Eko Prasetyo",
            "Fitri Handayani", "Gunawan Susanto", "Hani Rahmawati", "Indra Kusuma", "Joko Widodo",
            "Kartika Sari", "Lukman Hakim", "Maya Sari", "Nanda Pratama", "Oki Setiana"
        ]
        
        phone_prefixes = ["0812", "0813", "0821", "0822", "0851", "0852", "0856"]
        sources = ["1", "2", "3", "4"]  # Different prospect sources
        statuses = ["1", "2", "3", "4"]  # Different statuses
        unit_types = ["PCX160", "VARIO125", "BEAT125", "SCOOPY125", "ADV160", "CBR150R"]
        
        for i in range(count):
            # Create prospect data
            prospect_date = date.today() - timedelta(days=random.randint(0, 30))
            
            prospect = ProspectData(
                dealer_id=dealer_id,
                id_prospect=f"PRSP{random.randint(100000, 999999)}",
                sumber_prospect=random.choice(sources),
                tanggal_prospect=prospect_date,
                tagging_prospect="1",
                nama_lengkap=random.choice(names),
                no_kontak=f"{random.choice(phone_prefixes)}{random.randint(10000000, 99999999)}",
                no_ktp=f"{random.randint(1000000000000000, 9999999999999999)}",
                alamat=f"Jl. Test No. {random.randint(1, 100)}, Jakarta",
                kode_propinsi="31",
                kode_kota="3171",
                kode_kecamatan="317101",
                kode_kelurahan="31710101",
                kode_pos="10110",
                status_prospect=random.choice(statuses),
                id_sales_people=f"SP{random.randint(1000, 9999)}",
                created_time=datetime.now() - timedelta(days=random.randint(0, 30)),
                modified_time=datetime.now(),
                fetched_at=datetime.now()
            )
            
            db.add(prospect)
            db.flush()  # Get the ID
            
            # Add prospect unit
            unit = ProspectUnit(
                prospect_data_id=prospect.id,
                kode_tipe_unit=random.choice(unit_types),
                sales_program_id=f"SP{random.randint(1000, 9999)}",
                created_time=datetime.now(),
                modified_time=datetime.now()
            )
            
            db.add(unit)
        
        db.commit()
        print(f"✅ Created {count} sample prospect records for dealer {dealer_id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating prospect data: {e}")
    finally:
        db.close()

def create_sample_pkb_data(dealer_id="00999", count=30):
    """Create sample PKB data"""
    db = SessionLocal()
    try:
        # Sample data lists
        owner_names = [
            "Ahmad Wijaya", "Siti Nurhaliza", "Budi Santoso", "Dewi Sartika", "Eko Prasetyo",
            "Fitri Handayani", "Gunawan Susanto", "Hani Rahmawati", "Indra Kusuma", "Joko Widodo"
        ]
        
        unit_types = ["PCX160", "VARIO125", "BEAT125", "SCOOPY125", "ADV160", "CBR150R"]
        plate_prefixes = ["B", "D", "F", "H", "L", "N"]
        statuses = ["1", "2", "3", "4"]
        
        for i in range(count):
            service_date = (date.today() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
            
            pkb = PKBData(
                dealer_id=dealer_id,
                no_work_order=f"WO{random.randint(100000, 999999)}",
                no_sa_form=f"SA{random.randint(10000, 99999)}",
                tanggal_servis=service_date,
                waktu_pkb=f"{random.randint(8, 17):02d}:{random.randint(0, 59):02d}",
                no_polisi=f"{random.choice(plate_prefixes)} {random.randint(1000, 9999)} {random.choice(['AA', 'AB', 'AC', 'AD'])}",
                no_rangka=f"MH{random.randint(1000000000000000, 9999999999999999)}",
                no_mesin=f"JF{random.randint(1000000, 9999999)}",
                kode_tipe_unit=random.choice(unit_types),
                tahun_motor=str(random.randint(2018, 2024)),
                informasi_bensin=str(random.randint(1, 4)),
                km_terakhir=random.randint(1000, 50000),
                tipe_coming_customer="1",
                nama_pemilik=random.choice(owner_names),
                alamat_pemilik=f"Jl. Service No. {random.randint(1, 100)}, Jakarta",
                kode_propinsi_pemilik="31",
                kode_kota_pemilik="3171",
                total_biaya_service=random.randint(50000, 500000),
                status_work_order=random.choice(statuses),
                created_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                modified_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                fetched_at=datetime.now()
            )
            
            db.add(pkb)
            db.flush()  # Get the ID
            
            # Add some services
            services = [
                {"nama": "Ganti Oli", "biaya": 75000},
                {"nama": "Tune Up", "biaya": 150000},
                {"nama": "Ganti Ban", "biaya": 200000},
                {"nama": "Service Berkala", "biaya": 100000}
            ]
            
            selected_services = random.sample(services, random.randint(1, 3))
            for service in selected_services:
                pkb_service = PKBService(
                    pkb_data_id=pkb.id,
                    id_job=f"JOB{random.randint(1000, 9999)}",
                    nama_pekerjaan=service["nama"],
                    jenis_pekerjaan="Service",
                    biaya_service=service["biaya"],
                    total_harga_servis=service["biaya"],
                    created_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    modified_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                db.add(pkb_service)
            
            # Add some parts
            parts = [
                {"number": "15400-KVB-901", "harga": 45000},
                {"number": "06435-KVB-000", "harga": 25000},
                {"number": "91201-KVB-003", "harga": 15000}
            ]
            
            if random.choice([True, False]):  # 50% chance to add parts
                selected_parts = random.sample(parts, random.randint(1, 2))
                for part in selected_parts:
                    pkb_part = PKBPart(
                        pkb_data_id=pkb.id,
                        id_job=f"JOB{random.randint(1000, 9999)}",
                        parts_number=part["number"],
                        harga_parts=part["harga"],
                        total_harga_parts=part["harga"],
                        kuantitas=1,
                        created_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        modified_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    db.add(pkb_part)
        
        db.commit()
        print(f"✅ Created {count} sample PKB records for dealer {dealer_id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating PKB data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating sample data for dashboard testing...")
    
    # Create sample data for dealer 00999
    create_sample_prospect_data("00999", 50)
    create_sample_pkb_data("00999", 30)
    
    # Create some data for dealer 12284 as well
    create_sample_prospect_data("12284", 25)
    create_sample_pkb_data("12284", 15)
    
    print("✅ Sample data creation completed!")
    print("🔗 Access Analytics Dashboard: http://localhost:8501")
