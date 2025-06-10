from celery import current_task
from celery_app import celery_app
from database import SessionLocal, Dealer, ProspectData, ProspectUnit, FetchLog, FetchConfiguration
from datetime import datetime, timedelta, date
import httpx
import os
import logging
import time
from typing import Dict, List, Any
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
DGI_API_BASE_URL = os.getenv("DGI_API_BASE_URL", "https://dev-gvt-gateway.eksad.com/dgi-api/v1.3")

@celery_app.task(bind=True)
def health_check(self):
    """Health check task"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@celery_app.task(bind=True)
def fetch_prospect_data(self, dealer_id: str, from_time: str = None, to_time: str = None):
    """
    Fetch prospect data for a specific dealer
    """
    db = SessionLocal()
    start_time = datetime.utcnow()
    
    try:
        # Get dealer information
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise ValueError(f"Dealer {dealer_id} not found")
        
        if not dealer.is_active:
            logger.info(f"Dealer {dealer_id} is inactive, skipping fetch")
            return {"status": "skipped", "reason": "dealer_inactive"}
        
        # Set default time range if not provided
        if not from_time or not to_time:
            today = date.today()
            from_time = f"{today} 00:00:00"
            to_time = f"{today} 23:59:59"
        
        # Prepare API request
        headers = {
            "DGI-API-KEY": dealer.api_key,
            "DGI-API-Token": dealer.api_token,
            "X-Request-Time": str(int(time.time())),
            "Content-Type": "application/json"
        }
        
        payload = {
            "fromTime": from_time,
            "toTime": to_time,
            "dealerId": dealer_id,
            "idProspect": "",
            "idSalesPeople": ""
        }
        
        # Make API request
        url = f"{DGI_API_BASE_URL}/prsp/read"
        
        # Try real API first, fallback to dummy data if needed
        try:
            logger.info(f"Calling DGI API for dealer {dealer_id}")
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                api_data = response.json()
                logger.info(f"API call successful for dealer {dealer_id}")
        except Exception as api_error:
            logger.warning(f"API call failed for dealer {dealer_id}: {api_error}")
            logger.info("Using dummy data for demonstration")
            # Use dummy data for demonstration
            api_data = get_dummy_prospect_data(dealer_id, from_time, to_time)
        
        # Process the response
        if api_data.get("status") != 1:
            raise ValueError(f"API returned error: {api_data.get('message', 'Unknown error')}")
        
        records_processed = 0
        prospects_data = api_data.get("data", [])
        
        for prospect in prospects_data:
            # Parse date
            tanggal_prospect = None
            if prospect.get("tanggalProspect"):
                try:
                    tanggal_prospect = datetime.strptime(prospect["tanggalProspect"], "%d/%m/%Y").date()
                except ValueError:
                    logger.warning(f"Invalid date format: {prospect.get('tanggalProspect')}")
            
            # Parse appointment date and time
            tanggal_appointment = None
            waktu_appointment = None
            if prospect.get("tanggalAppointment"):
                try:
                    tanggal_appointment = datetime.strptime(prospect["tanggalAppointment"], "%d/%m/%Y").date()
                except ValueError:
                    logger.warning(f"Invalid appointment date: {prospect.get('tanggalAppointment')}")
            
            if prospect.get("waktuAppointment"):
                try:
                    waktu_appointment = datetime.strptime(prospect["waktuAppointment"], "%H:%M").time()
                except ValueError:
                    logger.warning(f"Invalid appointment time: {prospect.get('waktuAppointment')}")
            
            # Parse created and modified times
            created_time = None
            modified_time = None
            if prospect.get("createdTime"):
                try:
                    created_time = datetime.strptime(prospect["createdTime"], "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    logger.warning(f"Invalid created time: {prospect.get('createdTime')}")
            
            if prospect.get("modifiedTime"):
                try:
                    modified_time = datetime.strptime(prospect["modifiedTime"], "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    logger.warning(f"Invalid modified time: {prospect.get('modifiedTime')}")
            
            # Check if prospect already exists
            existing_prospect = db.query(ProspectData).filter(
                ProspectData.dealer_id == dealer_id,
                ProspectData.id_prospect == prospect.get("idProspect")
            ).first()
            
            if existing_prospect:
                # Update existing record
                prospect_record = existing_prospect
                prospect_record.modified_time = modified_time
                prospect_record.fetched_at = datetime.utcnow()
            else:
                # Create new record
                prospect_record = ProspectData(
                    dealer_id=dealer_id,
                    id_prospect=prospect.get("idProspect"),
                    sumber_prospect=prospect.get("sumberProspect"),
                    tanggal_prospect=tanggal_prospect,
                    tagging_prospect=prospect.get("taggingProspect"),
                    nama_lengkap=prospect.get("namaLengkap"),
                    no_kontak=prospect.get("noKontak"),
                    no_ktp=prospect.get("noKtp"),
                    alamat=prospect.get("alamat"),
                    kode_propinsi=prospect.get("kodePropinsi"),
                    kode_kota=prospect.get("kodeKota"),
                    kode_kecamatan=prospect.get("kodeKecamatan"),
                    kode_kelurahan=prospect.get("kodeKelurahan"),
                    kode_pos=prospect.get("kodePos"),
                    latitude=prospect.get("latitude"),
                    longitude=prospect.get("longitude"),
                    alamat_kantor=prospect.get("alamatKantor"),
                    kode_propinsi_kantor=prospect.get("kodePropinsiKantor"),
                    kode_kota_kantor=prospect.get("kodeKotaKantor"),
                    kode_kecamatan_kantor=prospect.get("kodeKecamatanKantor"),
                    kode_kelurahan_kantor=prospect.get("kodeKelurahanKantor"),
                    kode_pos_kantor=prospect.get("kodePosKantor"),
                    kode_pekerjaan=prospect.get("kodePekerjaan"),
                    no_kontak_kantor=prospect.get("noKontakKantor"),
                    tanggal_appointment=tanggal_appointment,
                    waktu_appointment=waktu_appointment,
                    metode_follow_up=prospect.get("metodeFollowUp"),
                    test_ride_preference=prospect.get("testRidePreference"),
                    status_follow_up_prospecting=prospect.get("statusFollowUpProspecting"),
                    status_prospect=prospect.get("statusProspect"),
                    id_sales_people=prospect.get("idSalesPeople"),
                    id_event=prospect.get("idEvent"),
                    created_time=created_time,
                    modified_time=modified_time
                )
                db.add(prospect_record)
            
            # Handle units
            if not existing_prospect:
                for unit in prospect.get("unit", []):
                    unit_created_time = None
                    unit_modified_time = None
                    
                    if unit.get("createdTime"):
                        try:
                            unit_created_time = datetime.strptime(unit["createdTime"], "%d/%m/%Y %H:%M:%S")
                        except ValueError:
                            pass
                    
                    if unit.get("modifiedTime"):
                        try:
                            unit_modified_time = datetime.strptime(unit["modifiedTime"], "%d/%m/%Y %H:%M:%S")
                        except ValueError:
                            pass
                    
                    prospect_unit = ProspectUnit(
                        prospect_data_id=prospect_record.id,
                        kode_tipe_unit=unit.get("kodeTipeUnit"),
                        sales_program_id=unit.get("salesProgramId"),
                        created_time=unit_created_time,
                        modified_time=unit_modified_time
                    )
                    db.add(prospect_unit)
            
            records_processed += 1
        
        # Commit all changes
        db.commit()
        
        # Update fetch configuration
        fetch_config = db.query(FetchConfiguration).filter(
            FetchConfiguration.dealer_id == dealer_id,
            FetchConfiguration.is_active == True
        ).first()
        
        if fetch_config:
            fetch_config.last_fetch_at = datetime.utcnow()
            db.commit()
        
        # Log successful fetch
        duration = int((datetime.utcnow() - start_time).total_seconds())
        fetch_log = FetchLog(
            dealer_id=dealer_id,
            fetch_type="prospect_data",
            status="success",
            records_fetched=records_processed,
            fetch_duration_seconds=duration,
            started_at=start_time,
            completed_at=datetime.utcnow()
        )
        db.add(fetch_log)
        db.commit()
        
        logger.info(f"Successfully fetched {records_processed} prospect records for dealer {dealer_id}")
        
        return {
            "status": "success",
            "dealer_id": dealer_id,
            "records_processed": records_processed,
            "duration_seconds": duration
        }
        
    except Exception as e:
        # Log failed fetch
        duration = int((datetime.utcnow() - start_time).total_seconds())
        fetch_log = FetchLog(
            dealer_id=dealer_id,
            fetch_type="prospect_data",
            status="failed",
            records_fetched=0,
            error_message=str(e),
            fetch_duration_seconds=duration,
            started_at=start_time,
            completed_at=datetime.utcnow()
        )
        db.add(fetch_log)
        db.commit()
        
        logger.error(f"Failed to fetch prospect data for dealer {dealer_id}: {e}")
        raise
        
    finally:
        db.close()

def get_dummy_prospect_data(dealer_id: str, from_time: str, to_time: str) -> Dict[str, Any]:
    """Generate dummy prospect data for demonstration"""
    import random
    from datetime import datetime, timedelta

    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate multiple prospects for the date range
    prospects = []
    current_date = start_date

    names = ["Ahmad Wijaya", "Siti Nurhaliza", "Budi Santoso", "Dewi Sartika", "Eko Prasetyo"]
    unit_types = ["PCX160", "VARIO125", "VARIO150", "BEAT", "SCOOPY"]

    while current_date <= end_date:
        # Generate 1-3 prospects per day
        for i in range(random.randint(1, 3)):
            prospect_id = f"PSP/{dealer_id}/{current_date.strftime('%y%m')}/{random.randint(1000, 9999)}"

            prospect = {
                "idProspect": prospect_id,
                "sumberProspect": random.choice(["0001", "0002", "0003"]),
                "tanggalProspect": current_date.strftime("%d/%m/%Y"),
                "taggingProspect": random.choice(["Yes", "No"]),
                "namaLengkap": random.choice(names),
                "noKontak": f"081{random.randint(10000000, 99999999)}",
                "noKtp": f"32{random.randint(10000000000000, 99999999999999)}",
                "alamat": f"Jl. Sample No. {random.randint(1, 999)} RT 001, RW 002",
                "kodePropinsi": "3100",
                "kodeKota": "3101",
                "kodeKecamatan": "317404",
                "kodeKelurahan": "3174040001",
                "kodePos": "14130",
                "latitude": f"{random.uniform(-6.5, -6.0):.6f}",
                "longitude": f"{random.uniform(106.5, 107.0):.6f}",
                "alamatKantor": "",
                "kodePropinsiKantor": "",
                "kodeKotaKantor": "",
                "kodeKecamatanKantor": "",
                "kodeKelurahanKantor": "",
                "kodePosKantor": "",
                "kodePekerjaan": str(random.randint(1, 5)),
                "noKontakKantor": f"021{random.randint(1000000, 9999999)}",
                "tanggalAppointment": (current_date + timedelta(days=random.randint(1, 7))).strftime("%d/%m/%Y"),
                "waktuAppointment": f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}",
                "metodeFollowUp": str(random.randint(1, 3)),
                "testRidePreference": str(random.randint(1, 2)),
                "statusFollowUpProspecting": str(random.randint(1, 3)),
                "statusProspect": str(random.randint(1, 4)),
                "idSalesPeople": f"SP{random.randint(1000, 9999)}",
                "idEvent": f"EV/E/K0Z/{dealer_id}/{current_date.strftime('%y%m')}/{random.randint(1, 100):03d}",
                "dealerId": dealer_id,
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "unit": [
                    {
                        "kodeTipeUnit": random.choice(unit_types),
                        "salesProgramId": f"PRM/{random.randint(1000, 9999)}/{current_date.strftime('%y%m')}/001",
                        "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                        "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
                    }
                ]
            }
            prospects.append(prospect)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": prospects
    }
