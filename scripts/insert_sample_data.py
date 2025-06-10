#!/usr/bin/env python3
"""
Insert sample data for dealer 00999 to demonstrate dashboard
"""

import os
import sys
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Dealer, ProspectData, ProspectUnit, FetchLog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")

def insert_sample_record():
    """Insert one sample prospect record for dealer 00999"""
    
    print("📊 Inserting sample data for dealer 00999...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Ensure dealer 00999 exists
        dealer = db.query(Dealer).filter(Dealer.dealer_id == "00999").first()
        if not dealer:
            dealer = Dealer(
                dealer_id="00999",
                dealer_name="Default Dealer",
                api_key="6c796097-a453-420f-9a19-155a2a24513e",
                api_token="81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c",
                is_active=True
            )
            db.add(dealer)
            db.commit()
            print("✅ Created dealer 00999")
        else:
            print("✅ Dealer 00999 already exists")
        
        # Check if we already have data
        existing_count = db.query(ProspectData).filter(ProspectData.dealer_id == "00999").count()
        print(f"📊 Current prospect records: {existing_count}")
        
        # Insert one sample prospect record
        today = date.today()
        sample_prospect = ProspectData(
            dealer_id="00999",
            id_prospect=f"PSP/00999/{today.strftime('%y%m')}/00001",
            sumber_prospect="0001",
            tanggal_prospect=today,
            tagging_prospect="Yes",
            nama_lengkap="Ahmad Wijaya",
            no_kontak="081234567890",
            no_ktp="3201070506090001",
            alamat="Jl. Sudirman No. 123, Jakarta Pusat",
            kode_propinsi="3100",
            kode_kota="3101",
            kode_kecamatan="317404",
            kode_kelurahan="3174040001",
            kode_pos="14130",
            latitude="-6.208763",
            longitude="106.845599",
            alamat_kantor="Jl. Thamrin No. 456, Jakarta Pusat",
            kode_propinsi_kantor="3100",
            kode_kota_kantor="3101",
            kode_kecamatan_kantor="317404",
            kode_kelurahan_kantor="3174040001",
            kode_pos_kantor="14130",
            kode_pekerjaan="1",
            no_kontak_kantor="0214244364",
            tanggal_appointment=today + timedelta(days=3),
            waktu_appointment=datetime.strptime("15:30", "%H:%M").time(),
            metode_follow_up="1",
            test_ride_preference="1",
            status_follow_up_prospecting="1",
            status_prospect="2",  # In Progress
            id_sales_people="SP001",
            id_event=f"EV/00999/{today.strftime('%y%m')}/001",
            created_time=datetime.now(),
            modified_time=datetime.now()
        )
        
        db.add(sample_prospect)
        db.flush()  # Get the ID
        
        # Add sample unit for this prospect
        sample_unit = ProspectUnit(
            prospect_data_id=sample_prospect.id,
            kode_tipe_unit="PCX160",
            sales_program_id="PRM/0001/2312/001",
            created_time=datetime.now(),
            modified_time=datetime.now()
        )
        
        db.add(sample_unit)
        
        # Add a sample fetch log
        sample_log = FetchLog(
            dealer_id="00999",
            fetch_type="prospect_data",
            status="success",
            records_fetched=1,
            fetch_duration_seconds=15,
            started_at=datetime.now() - timedelta(seconds=15),
            completed_at=datetime.now()
        )
        
        db.add(sample_log)
        
        # Commit all changes
        db.commit()
        
        print("✅ Sample data inserted successfully!")
        print("\n📊 Sample Record Details:")
        print(f"   Prospect ID: {sample_prospect.id_prospect}")
        print(f"   Customer: {sample_prospect.nama_lengkap}")
        print(f"   Date: {sample_prospect.tanggal_prospect}")
        print(f"   Status: {sample_prospect.status_prospect}")
        print(f"   Unit: PCX160")
        
        # Show current totals
        total_prospects = db.query(ProspectData).filter(ProspectData.dealer_id == "00999").count()
        total_logs = db.query(FetchLog).filter(FetchLog.dealer_id == "00999").count()
        
        print(f"\n📈 Database Summary:")
        print(f"   Total Prospects: {total_prospects}")
        print(f"   Total Fetch Logs: {total_logs}")
        
        print(f"\n🌐 Next Steps:")
        print(f"   1. Start the application:")
        print(f"      - Backend: uvicorn main:app --reload")
        print(f"      - Dashboard: streamlit run dashboard.py")
        print(f"   2. Open dashboard: http://localhost:8501")
        print(f"   3. Go to 'Dashboard' page")
        print(f"   4. Select 'Default Dealer (00999)'")
        print(f"   5. View the analytics charts!")
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def insert_more_sample_data(num_records=10):
    """Insert multiple sample records for better dashboard visualization"""
    
    print(f"📊 Inserting {num_records} sample records for dealer 00999...")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Sample data arrays
        names = [
            "Ahmad Wijaya", "Siti Nurhaliza", "Budi Santoso", "Dewi Sartika", "Eko Prasetyo",
            "Fitri Handayani", "Gunawan Susanto", "Hesti Purnamasari", "Indra Kusuma", "Joko Widodo"
        ]
        
        unit_types = ["PCX160", "VARIO125", "VARIO150", "BEAT", "SCOOPY"]
        statuses = ["1", "2", "3", "4"]  # New, In Progress, Completed, Cancelled
        
        base_date = date.today() - timedelta(days=7)
        
        for i in range(num_records):
            prospect_date = base_date + timedelta(days=i % 7)
            
            prospect = ProspectData(
                dealer_id="00999",
                id_prospect=f"PSP/00999/{prospect_date.strftime('%y%m')}/{i+1:05d}",
                sumber_prospect="0001",
                tanggal_prospect=prospect_date,
                tagging_prospect="Yes" if i % 2 == 0 else "No",
                nama_lengkap=names[i % len(names)],
                no_kontak=f"081{23456789 + i:08d}",
                no_ktp=f"32{10000000000000 + i:014d}",
                alamat=f"Jl. Sample No. {i+1}, Jakarta",
                kode_propinsi="3100",
                kode_kota="3101",
                kode_kecamatan="317404",
                kode_kelurahan="3174040001",
                kode_pos="14130",
                latitude=f"{-6.2 + (i * 0.01):.6f}",
                longitude=f"{106.8 + (i * 0.01):.6f}",
                kode_pekerjaan=str((i % 5) + 1),
                tanggal_appointment=prospect_date + timedelta(days=3),
                waktu_appointment=datetime.strptime(f"{9 + (i % 8)}:30", "%H:%M").time(),
                metode_follow_up=str((i % 3) + 1),
                test_ride_preference=str((i % 2) + 1),
                status_follow_up_prospecting=str((i % 3) + 1),
                status_prospect=statuses[i % len(statuses)],
                id_sales_people=f"SP{1000 + i}",
                id_event=f"EV/00999/{prospect_date.strftime('%y%m')}/{i+1:03d}",
                created_time=datetime.combine(prospect_date, datetime.min.time().replace(hour=9 + (i % 8))),
                modified_time=datetime.combine(prospect_date, datetime.min.time().replace(hour=9 + (i % 8)))
            )
            
            db.add(prospect)
            db.flush()
            
            # Add unit for each prospect
            unit = ProspectUnit(
                prospect_data_id=prospect.id,
                kode_tipe_unit=unit_types[i % len(unit_types)],
                sales_program_id=f"PRM/{1000 + i}/{prospect_date.strftime('%y%m')}/001",
                created_time=prospect.created_time,
                modified_time=prospect.modified_time
            )
            
            db.add(unit)
        
        # Add some fetch logs
        for i in range(3):
            log_date = datetime.now() - timedelta(days=i)
            fetch_log = FetchLog(
                dealer_id="00999",
                fetch_type="prospect_data",
                status="success",
                records_fetched=num_records // 3,
                fetch_duration_seconds=20 + i * 5,
                started_at=log_date,
                completed_at=log_date + timedelta(seconds=20 + i * 5)
            )
            db.add(fetch_log)
        
        db.commit()
        
        total_prospects = db.query(ProspectData).filter(ProspectData.dealer_id == "00999").count()
        print(f"✅ Successfully inserted {num_records} records!")
        print(f"📊 Total prospects for dealer 00999: {total_prospects}")
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "more":
        # Insert multiple records for better visualization
        insert_more_sample_data(20)
    else:
        # Insert just one record
        insert_sample_record()
