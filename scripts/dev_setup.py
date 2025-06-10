#!/usr/bin/env python3
"""
Development setup script for Dealer Dashboard
- Creates dummy data for testing
- Sets up default dealer
- Populates database with sample prospect data
"""

import os
import sys
from datetime import datetime, date, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Dealer, ProspectData, ProspectUnit, FetchLog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")

def create_dummy_prospects(dealer_id: str, num_prospects: int = 50) -> list:
    """Generate dummy prospect data for testing"""
    
    # Sample data for realistic prospects
    names = [
        "Ahmad Wijaya", "Siti Nurhaliza", "Budi Santoso", "Dewi Sartika", "Eko Prasetyo",
        "Fitri Handayani", "Gunawan Susanto", "Hesti Purnamasari", "Indra Kusuma", "Joko Widodo",
        "Kartika Sari", "Lukman Hakim", "Maya Sari", "Nanda Pratama", "Oki Setiana",
        "Putri Diani", "Qori Sandioriva", "Rini Soemarno", "Sari Nila", "Tono Suratman",
        "Udin Sedunia", "Vina Panduwinata", "Wawan Setiawan", "Xenia Gratia", "Yuni Shara",
        "Zaskia Gotik", "Arief Rahman", "Bella Saphira", "Cinta Laura", "Dian Sastro"
    ]
    
    phones = [
        "081234567890", "082345678901", "083456789012", "084567890123", "085678901234",
        "086789012345", "087890123456", "088901234567", "089012345678", "081123456789"
    ]
    
    addresses = [
        "Jl. Sudirman No. 123, Jakarta Pusat",
        "Jl. Thamrin No. 456, Jakarta Pusat", 
        "Jl. Gatot Subroto No. 789, Jakarta Selatan",
        "Jl. Kuningan No. 321, Jakarta Selatan",
        "Jl. Kemang No. 654, Jakarta Selatan",
        "Jl. Senopati No. 987, Jakarta Selatan",
        "Jl. Menteng No. 147, Jakarta Pusat",
        "Jl. Cikini No. 258, Jakarta Pusat",
        "Jl. Kelapa Gading No. 369, Jakarta Utara",
        "Jl. Sunter No. 741, Jakarta Utara"
    ]
    
    unit_types = ["PCX160", "VARIO125", "VARIO150", "BEAT", "SCOOPY", "CBR150R", "CB150R", "CRF150L"]
    
    prospects = []
    base_date = date.today() - timedelta(days=30)
    
    for i in range(num_prospects):
        prospect_date = base_date + timedelta(days=random.randint(0, 30))
        
        prospect = {
            "dealer_id": dealer_id,
            "id_prospect": f"PSP/{dealer_id}/{prospect_date.strftime('%y%m')}/{i+1:05d}",
            "sumber_prospect": random.choice(["0001", "0002", "0003", "0004"]),
            "tanggal_prospect": prospect_date,
            "tagging_prospect": random.choice(["Yes", "No"]),
            "nama_lengkap": random.choice(names),
            "no_kontak": random.choice(phones),
            "no_ktp": f"32{random.randint(10000000000000, 99999999999999)}",
            "alamat": random.choice(addresses),
            "kode_propinsi": "3100",
            "kode_kota": random.choice(["3101", "3102", "3103", "3104", "3105"]),
            "kode_kecamatan": f"31{random.randint(1000, 9999)}",
            "kode_kelurahan": f"31{random.randint(10000000, 99999999)}",
            "kode_pos": f"{random.randint(10000, 19999)}",
            "latitude": f"{random.uniform(-6.5, -6.0):.6f}",
            "longitude": f"{random.uniform(106.5, 107.0):.6f}",
            "kode_pekerjaan": random.choice(["1", "2", "3", "4", "5"]),
            "no_kontak_kantor": random.choice(phones),
            "tanggal_appointment": prospect_date + timedelta(days=random.randint(1, 7)),
            "waktu_appointment": f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}",
            "metode_follow_up": random.choice(["1", "2", "3"]),
            "test_ride_preference": random.choice(["1", "2"]),
            "status_follow_up_prospecting": random.choice(["1", "2", "3"]),
            "status_prospect": random.choice(["1", "2", "3", "4"]),
            "id_sales_people": f"SP{random.randint(1000, 9999)}",
            "id_event": f"EV/{dealer_id}/{prospect_date.strftime('%y%m')}/{random.randint(1, 100):03d}",
            "created_time": datetime.combine(prospect_date, datetime.min.time().replace(hour=random.randint(8, 17))),
            "modified_time": datetime.combine(prospect_date, datetime.min.time().replace(hour=random.randint(8, 17))),
            "units": [
                {
                    "kode_tipe_unit": random.choice(unit_types),
                    "sales_program_id": f"PRM/{random.randint(1000, 9999)}/{prospect_date.strftime('%y%m')}/001",
                    "created_time": datetime.combine(prospect_date, datetime.min.time().replace(hour=random.randint(8, 17))),
                    "modified_time": datetime.combine(prospect_date, datetime.min.time().replace(hour=random.randint(8, 17)))
                }
            ]
        }
        prospects.append(prospect)
    
    return prospects

def setup_development_data():
    """Set up development database with dummy data"""
    
    print("🚀 Setting up development environment...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Check if default dealer exists
        dealer = db.query(Dealer).filter(Dealer.dealer_id == "00999").first()
        if not dealer:
            # Create default dealer
            dealer = Dealer(
                dealer_id="00999",
                dealer_name="Default Dealer",
                api_key="6c796097-a453-420f-9a19-155a2a24513e",
                api_token="81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c",
                is_active=True
            )
            db.add(dealer)
            db.commit()
            print("✅ Default dealer created (ID: 00999)")
        else:
            print("✅ Default dealer already exists")
        
        # Check if we already have prospect data
        existing_prospects = db.query(ProspectData).filter(ProspectData.dealer_id == "00999").count()
        
        if existing_prospects == 0:
            print("📊 Generating dummy prospect data...")
            
            # Generate dummy prospects
            dummy_prospects = create_dummy_prospects("00999", 100)
            
            for prospect_data in dummy_prospects:
                # Extract units data
                units_data = prospect_data.pop("units", [])
                
                # Create prospect record
                prospect = ProspectData(**prospect_data)
                db.add(prospect)
                db.flush()  # Get the ID
                
                # Create unit records
                for unit_data in units_data:
                    unit = ProspectUnit(
                        prospect_data_id=prospect.id,
                        **unit_data
                    )
                    db.add(unit)
            
            db.commit()
            print(f"✅ Created {len(dummy_prospects)} dummy prospect records")
            
            # Create some fetch logs
            for i in range(10):
                log_date = datetime.now() - timedelta(days=i)
                fetch_log = FetchLog(
                    dealer_id="00999",
                    fetch_type="prospect_data",
                    status=random.choice(["success", "success", "success", "failed"]),  # Mostly success
                    records_fetched=random.randint(5, 25),
                    fetch_duration_seconds=random.randint(10, 60),
                    started_at=log_date,
                    completed_at=log_date + timedelta(seconds=random.randint(10, 60))
                )
                db.add(fetch_log)
            
            db.commit()
            print("✅ Created sample fetch logs")
            
        else:
            print(f"✅ Found {existing_prospects} existing prospect records")
        
        print("\n🎉 Development environment ready!")
        print("\n📋 Next steps:")
        print("1. Start the backend: uvicorn main:app --reload")
        print("2. Start Celery worker: celery -A celery_app worker --loglevel=info")
        print("3. Start dashboard: streamlit run dashboard.py")
        print("\n🌐 Access URLs:")
        print("- Dashboard: http://localhost:8501")
        print("- API Docs: http://localhost:8000/docs")
        print("- API Health: http://localhost:8000/health")
        
    except Exception as e:
        print(f"❌ Error setting up development data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_development_data()
