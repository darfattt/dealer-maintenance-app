"""
SPK Dealing Process Data Processor

This module handles fetching and processing SPK dealing process data from the DGI API.
It manages the complex nested data structure including units and family members.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from .base_processor import BaseDataProcessor
from ..api_clients import SPKDealingProcessAPIClient
from ..dummy_data_generators import get_dummy_spk_dealing_process_data
from database import SPKDealingProcessData, SPKDealingProcessUnit, SPKDealingProcessFamilyMember

logger = logging.getLogger(__name__)


class SPKDealingProcessDataProcessor(BaseDataProcessor):
    """Processor for SPK dealing process data from SPK API"""
    
    def __init__(self):
        super().__init__("spk_read")
        self.api_client = SPKDealingProcessAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch SPK dealing process data from API or return dummy data"""
        try:
            # Extract optional parameters
            id_prospect = kwargs.get('id_prospect', '')
            id_sales_people = kwargs.get('id_sales_people', '')
            
            logger.info(f"Fetching SPK dealing process data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_spk_dealing_process_data(
                    dealer.dealer_id, from_time, to_time, 
                    id_prospect, id_sales_people
                )
            
            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time, 
                dealer.api_key, dealer.secret_key,
                id_prospect, id_sales_people
            )
            
            if api_response.get("status") == 1:
                logger.info(f"Successfully fetched SPK dealing process data for dealer {dealer.dealer_id}")
                return api_response
            else:
                error_msg = api_response.get("message", "Unknown API error")
                logger.warning(f"API returned error for dealer {dealer.dealer_id}: {error_msg}")
                return {
                    "status": 0,
                    "message": f"API Error: {error_msg}",
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error fetching SPK dealing process data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store SPK dealing process records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No SPK dealing process data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for spk_record in data:
                try:
                    # Check for existing record to prevent duplicates
                    existing_spk = db.query(SPKDealingProcessData).filter(
                        and_(
                            SPKDealingProcessData.dealer_id == dealer_id,
                            SPKDealingProcessData.id_spk == spk_record.get("idSpk")
                        )
                    ).first()
                    
                    if existing_spk:
                        logger.debug(f"SPK record {spk_record.get('idSpk')} already exists, skipping")
                        continue
                    
                    # Create main SPK record
                    spk_data = SPKDealingProcessData(
                        dealer_id=dealer_id,
                        id_spk=spk_record.get("idSpk"),
                        id_prospect=spk_record.get("idProspect"),
                        nama_customer=spk_record.get("namaCustomer"),
                        no_ktp=spk_record.get("noKtp"),
                        alamat=spk_record.get("alamat"),
                        kode_propinsi=spk_record.get("kodePropinsi"),
                        kode_kota=spk_record.get("kodeKota"),
                        kode_kecamatan=spk_record.get("kodeKecamatan"),
                        kode_kelurahan=spk_record.get("kodeKelurahan"),
                        kode_pos=spk_record.get("kodePos"),
                        no_kontak=spk_record.get("noKontak"),
                        nama_bpkb=spk_record.get("namaBPKB"),
                        no_ktp_bpkb=spk_record.get("noKTPBPKB"),
                        alamat_bpkb=spk_record.get("alamatBPKB"),
                        kode_propinsi_bpkb=spk_record.get("kodePropinsiBPKB"),
                        kode_kota_bpkb=spk_record.get("kodeKotaBPKB"),
                        kode_kecamatan_bpkb=spk_record.get("kodeKecamatanBPKB"),
                        kode_kelurahan_bpkb=spk_record.get("kodeKelurahanBPKB"),
                        kode_pos_bpkb=spk_record.get("kodePosBPKB"),
                        latitude=spk_record.get("latitude"),
                        longitude=spk_record.get("longitude"),
                        npwp=spk_record.get("NPWP"),
                        no_kk=spk_record.get("noKK"),
                        alamat_kk=spk_record.get("alamatKK"),
                        kode_propinsi_kk=spk_record.get("kodePropinsiKK"),
                        kode_kota_kk=spk_record.get("kodeKotaKK"),
                        kode_kecamatan_kk=spk_record.get("kodeKecamatanKK"),
                        kode_kelurahan_kk=spk_record.get("kodeKelurahanKK"),
                        kode_pos_kk=spk_record.get("kodePosKK"),
                        fax=spk_record.get("fax"),
                        email=spk_record.get("email"),
                        id_sales_people=spk_record.get("idSalesPeople"),
                        id_event=spk_record.get("idEvent"),
                        tanggal_pesanan=spk_record.get("tanggalPesanan"),
                        status_spk=spk_record.get("statusSPK"),
                        created_time=spk_record.get("createdTime"),
                        modified_time=spk_record.get("modifiedTime")
                    )
                    
                    db.add(spk_data)
                    db.flush()  # Get the ID for relationships
                    
                    # Process unit data
                    units = spk_record.get("unit", [])
                    for unit_record in units:
                        unit_data = SPKDealingProcessUnit(
                            spk_dealing_process_data_id=spk_data.id,
                            kode_tipe_unit=unit_record.get("kodeTipeUnit"),
                            kode_warna=unit_record.get("kodeWarna"),
                            quantity=unit_record.get("quantity"),
                            harga_jual=unit_record.get("hargaJual"),
                            diskon=unit_record.get("diskon"),
                            amount_ppn=unit_record.get("amountPPN"),
                            faktur_pajak=unit_record.get("fakturPajak"),
                            tipe_pembayaran=unit_record.get("tipePembayaran"),
                            jumlah_tanda_jadi=unit_record.get("jumlahTandaJadi"),
                            tanggal_pengiriman=unit_record.get("tanggalPengiriman"),
                            id_sales_program=unit_record.get("idSalesProgram"),
                            id_apparel=unit_record.get("idApparel"),
                            created_time=unit_record.get("createdTime"),
                            modified_time=unit_record.get("modifiedTime")
                        )
                        db.add(unit_data)
                    
                    # Process family member data
                    family_members = spk_record.get("dataAnggotaKeluarga", [])
                    for family_record in family_members:
                        family_data = SPKDealingProcessFamilyMember(
                            spk_dealing_process_data_id=spk_data.id,
                            anggota_kk=family_record.get("anggotaKK"),
                            created_time=family_record.get("createdTime"),
                            modified_time=family_record.get("modifiedTime")
                        )
                        db.add(family_data)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing SPK record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Successfully processed {processed_count} SPK dealing process records for dealer {dealer_id}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing SPK dealing process records for dealer {dealer_id}: {e}")
            db.rollback()
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for SPK dealing process data"""
        try:
            query = db.query(SPKDealingProcessData)
            
            if dealer_id:
                query = query.filter(SPKDealingProcessData.dealer_id == dealer_id)
            
            total_records = query.count()
            
            # Status distribution
            status_distribution = db.query(
                SPKDealingProcessData.status_spk,
                func.count(SPKDealingProcessData.id).label('count')
            ).filter(
                SPKDealingProcessData.dealer_id == dealer_id if dealer_id else True
            ).group_by(SPKDealingProcessData.status_spk).all()
            
            return {
                "total_records": total_records,
                "status_distribution": [
                    {"status": status, "count": count} 
                    for status, count in status_distribution
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting SPK dealing process summary stats: {e}")
            return {"total_records": 0, "status_distribution": []}
