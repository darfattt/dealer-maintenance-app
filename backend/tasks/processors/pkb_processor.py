"""
PKB data processor - handles PKB (Service Record) data fetching and processing
"""
from datetime import datetime, date
from typing import Dict, Any
from sqlalchemy import text

from database import Dealer, PKBData, PKBService, PKBPart
from ..api_clients import PKBAPIClient
from ..dummy_data_generators import get_dummy_pkb_data, should_use_dummy_data
from .base_processor import BaseDataProcessor


class PKBDataProcessor(BaseDataProcessor):
    """Processor for PKB (Service Record) data"""
    
    def __init__(self):
        super().__init__("pkb")
    
    def set_default_time_range(self, from_time: str, to_time: str) -> tuple[str, str]:
        """Set default time range for PKB data (different from base)"""
        if not from_time or not to_time:
            today = date.today()
            from_time = f"{today} 01:01:00"
            to_time = f"{today} 23:59:00"
        return from_time, to_time
    
    def fetch_api_data(self, dealer: Dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch PKB data from API or dummy source"""
        try:
            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy PKB data for dealer {dealer.dealer_id}")
                return get_dummy_pkb_data(dealer.dealer_id, from_time, to_time)
            else:
                # Use real API client
                client = PKBAPIClient()
                api_data = client.fetch_data(dealer.dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key)
                self.logger.info(f"PKB API call successful for dealer {dealer.dealer_id}")
                return api_data
        except Exception as api_error:
            self.logger.warning(f"PKB API call failed for dealer {dealer.dealer_id}: {api_error}")
            self.logger.info("Falling back to dummy PKB data for demonstration")
            # Fallback to dummy data
            return get_dummy_pkb_data(dealer.dealer_id, from_time, to_time)
    
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process PKB records and save to database"""
        records_processed = 0
        pkb_records = self.ensure_list_data(api_data.get("data"))

        # Ensure database session is in good state
        try:
            db.execute(text("SELECT 1"))
        except Exception as session_error:
            self.logger.warning(f"Database session issue, attempting to recover: {session_error}")
            # Try to rollback and continue
            try:
                db.rollback()
            except Exception:
                pass
        
        for pkb in pkb_records:
            # Check if PKB record already exists
            existing_pkb = None
            try:
                existing_pkb = db.query(PKBData).filter(
                    PKBData.dealer_id == dealer_id,
                    PKBData.no_work_order == pkb.get("noWorkOrder")
                ).first()
            except Exception as query_error:
                self.logger.warning(f"Error querying existing PKB record: {query_error}")
                # Continue with creating new record if query fails
                existing_pkb = None
            
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
                # Flush to get the ID for relationships
                db.flush()

            # Handle services (only for new records to avoid duplicates)
            if not existing_pkb:
                services = self.ensure_list_data(pkb.get("services"))
                for service in services:
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
                parts = self.ensure_list_data(pkb.get("parts"))
                for part in parts:
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
        
        return records_processed
