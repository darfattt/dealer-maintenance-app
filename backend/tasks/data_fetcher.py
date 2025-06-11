from celery import current_task
from celery_app import celery_app
from database import SessionLocal, Dealer, ProspectData, ProspectUnit, FetchLog, FetchConfiguration, PKBData, PKBService, PKBPart
from datetime import datetime, timedelta, date
import logging
from typing import Dict, List, Any

# Import our modular components
from .api_clients import ProspectAPIClient, PKBAPIClient, initialize_default_api_configs
from .dummy_data_generators import get_dummy_prospect_data, get_dummy_pkb_data, should_use_dummy_data

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API configurations on module load
try:
    initialize_default_api_configs()
except Exception as e:
    logger.warning(f"Failed to initialize API configs: {e}")

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
        
        # Use API client for data fetching
        try:
            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer_id):
                logger.info(f"Using dummy data for dealer {dealer_id}")
                api_data = get_dummy_prospect_data(dealer_id, from_time, to_time)
            else:
                # Use real API client
                client = ProspectAPIClient()
                api_data = client.fetch_data(dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key)
                logger.info(f"Prospect API call successful for dealer {dealer_id}")
        except Exception as api_error:
            logger.warning(f"Prospect API call failed for dealer {dealer_id}: {api_error}")
            logger.info("Falling back to dummy data for demonstration")
            # Fallback to dummy data
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

@celery_app.task(bind=True)
def fetch_pkb_data(self, dealer_id: str, from_time: str = None, to_time: str = None):
    """
    Fetch PKB (Service Record) data for a specific dealer
    """
    db = SessionLocal()
    start_time = datetime.utcnow()

    try:
        # Get dealer information
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise ValueError(f"Dealer {dealer_id} not found")

        if not dealer.is_active:
            logger.info(f"Dealer {dealer_id} is inactive, skipping PKB fetch")
            return {"status": "skipped", "reason": "dealer_inactive"}

        # Set default time range if not provided
        if not from_time or not to_time:
            today = date.today()
            from_time = f"{today} 01:01:00"
            to_time = f"{today} 23:59:00"

        # Use API client for PKB data fetching
        try:
            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer_id):
                logger.info(f"Using dummy PKB data for dealer {dealer_id}")
                api_data = get_dummy_pkb_data(dealer_id, from_time, to_time)
            else:
                # Use real API client
                client = PKBAPIClient()
                api_data = client.fetch_data(dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key)
                logger.info(f"PKB API call successful for dealer {dealer_id}")
        except Exception as api_error:
            logger.warning(f"PKB API call failed for dealer {dealer_id}: {api_error}")
            logger.info("Falling back to dummy PKB data for demonstration")
            # Fallback to dummy data
            api_data = get_dummy_pkb_data(dealer_id, from_time, to_time)

        # Process the response
        if api_data.get("status") != 1:
            raise ValueError(f"PKB API returned error: {api_data.get('message', 'Unknown error')}")

        records_processed = 0
        pkb_records = api_data.get("data", [])

        for pkb in pkb_records:
            # Check if PKB record already exists
            existing_pkb = db.query(PKBData).filter(
                PKBData.dealer_id == dealer_id,
                PKBData.no_work_order == pkb.get("noWorkOrder")
            ).first()

            if existing_pkb:
                # Update existing record
                pkb_record = existing_pkb
                pkb_record.modified_time = pkb.get("modifiedTime")
                pkb_record.fetched_at = datetime.utcnow()
            else:
                # Create new record
                pkb_record = PKBData(
                    dealer_id=dealer_id,
                    no_work_order=pkb.get("noWorkOrder"),
                    no_sa_form=pkb.get("noSAForm"),
                    tanggal_servis=pkb.get("tanggalServis"),
                    waktu_pkb=pkb.get("waktuPKB"),
                    no_polisi=pkb.get("noPolisi"),
                    no_rangka=pkb.get("noRangka"),
                    no_mesin=pkb.get("noMesin"),
                    kode_tipe_unit=pkb.get("kodeTipeUnit"),
                    tahun_motor=pkb.get("tahunMotor"),
                    informasi_bensin=pkb.get("informasiBensin"),
                    km_terakhir=pkb.get("kmTerakhir"),
                    tipe_coming_customer=pkb.get("tipeComingCustomer"),
                    nama_pemilik=pkb.get("namaPemilik"),
                    alamat_pemilik=pkb.get("alamatPemilik"),
                    kode_propinsi_pemilik=pkb.get("kodePropinsiPemilik"),
                    kode_kota_pemilik=pkb.get("kodeKotaPemilik"),
                    kode_kecamatan_pemilik=pkb.get("kodeKecamatanPemilik"),
                    kode_kelurahan_pemilik=pkb.get("kodeKelurahanPemilik"),
                    kode_pos_pemilik=pkb.get("kodePosPemilik"),
                    alamat_pembawa=pkb.get("alamatPembawa"),
                    kode_propinsi_pembawa=pkb.get("kodePropinsiPembawa"),
                    kode_kota_pembawa=pkb.get("kodeKotaPembawa"),
                    kode_kecamatan_pembawa=pkb.get("kodeKecamatanPembawa"),
                    kode_kelurahan_pembawa=pkb.get("kodeKelurahanPembawa"),
                    kode_pos_pembawa=pkb.get("kodePosPembawa"),
                    nama_pembawa=pkb.get("namaPembawa"),
                    no_telp_pembawa=pkb.get("noTelpPembawa"),
                    hubungan_dengan_pemilik=pkb.get("hubunganDenganPemilik"),
                    keluhan_konsumen=pkb.get("keluhanKonsumen"),
                    rekomendasi_sa=pkb.get("rekomendasiSA"),
                    honda_id_sa=pkb.get("hondaIdSA"),
                    honda_id_mekanik=pkb.get("hondaIdMekanik"),
                    saran_mekanik=pkb.get("saranMekanik"),
                    asal_unit_entry=pkb.get("asalUnitEntry"),
                    id_pit=pkb.get("idPIT"),
                    jenis_pit=pkb.get("jenisPIT"),
                    waktu_pendaftaran=pkb.get("waktuPendaftaran"),
                    waktu_selesai=pkb.get("waktuSelesai"),
                    total_frt=pkb.get("totalFRT"),
                    set_up_pembayaran=pkb.get("setUpPembayaran"),
                    catatan_tambahan=pkb.get("catatanTambahan"),
                    konfirmasi_pekerjaan_tambahan=pkb.get("konfirmasiPekerjaanTambahan"),
                    no_buku_claim_c2=pkb.get("noBukuClaimC2"),
                    no_work_order_job_return=pkb.get("noWorkOrderJobReturn"),
                    total_biaya_service=pkb.get("totalBiayaService"),
                    waktu_pekerjaan=pkb.get("waktuPekerjaan"),
                    status_work_order=pkb.get("statusWorkOrder"),
                    created_time=pkb.get("createdTime"),
                    modified_time=pkb.get("modifiedTime")
                )
                db.add(pkb_record)

            # Handle services (only for new records to avoid duplicates)
            if not existing_pkb:
                for service in pkb.get("services", []):
                    pkb_service = PKBService(
                        pkb_data_id=pkb_record.id,
                        id_job=service.get("idJob"),
                        nama_pekerjaan=service.get("namaPekerjaan"),
                        jenis_pekerjaan=service.get("jenisPekerjaan"),
                        biaya_service=service.get("biayaService"),
                        promo_id_jasa=service.get("promoIdJasa"),
                        disc_service_amount=service.get("discServiceAmount"),
                        disc_service_percentage=service.get("discServicePercentage"),
                        total_harga_servis=service.get("totalHargaServis"),
                        created_time=service.get("createdTime"),
                        modified_time=service.get("modifiedTime")
                    )
                    db.add(pkb_service)

                # Handle parts
                for part in pkb.get("parts", []):
                    pkb_part = PKBPart(
                        pkb_data_id=pkb_record.id,
                        id_job=part.get("idJob"),
                        parts_number=part.get("partsNumber"),
                        harga_parts=part.get("hargaParts"),
                        promo_id_parts=part.get("promoIdParts"),
                        disc_parts_amount=part.get("discPartsAmount"),
                        disc_parts_percentage=part.get("discPartsPercentage"),
                        ppn=part.get("ppn"),
                        total_harga_parts=part.get("totalHargaParts"),
                        uang_muka=part.get("uangMuka"),
                        kuantitas=part.get("kuantitas"),
                        created_time=part.get("createdTime"),
                        modified_time=part.get("modifiedTime")
                    )
                    db.add(pkb_part)

            records_processed += 1

        # Commit all changes
        db.commit()

        # Log successful fetch
        duration = int((datetime.utcnow() - start_time).total_seconds())
        fetch_log = FetchLog(
            dealer_id=dealer_id,
            fetch_type="pkb_data",
            status="success",
            records_fetched=records_processed,
            fetch_duration_seconds=duration,
            started_at=start_time,
            completed_at=datetime.utcnow()
        )
        db.add(fetch_log)
        db.commit()

        logger.info(f"Successfully fetched {records_processed} PKB records for dealer {dealer_id}")

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
            fetch_type="pkb_data",
            status="failed",
            records_fetched=0,
            error_message=str(e),
            fetch_duration_seconds=duration,
            started_at=start_time,
            completed_at=datetime.utcnow()
        )
        db.add(fetch_log)
        db.commit()

        logger.error(f"Failed to fetch PKB data for dealer {dealer_id}: {e}")
        raise

    finally:
        db.close()




