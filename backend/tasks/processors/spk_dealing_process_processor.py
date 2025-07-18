"""
SPK Dealing Process Data Processor

This module handles fetching and processing SPK dealing process data from the DGI API.
It manages the complex nested data structure including units and family members.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

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
        """Fetch SPK dealing process data from API with enhanced validation"""
        try:
            # Extract optional parameters
            id_prospect = kwargs.get('id_prospect', '')
            id_sales_people = kwargs.get('id_sales_people', '')

            self.logger.info(f"Fetching SPK dealing process data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, id_prospect={id_prospect}, id_sales_people={id_sales_people}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
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

            # Validate API response
            if not api_response or not isinstance(api_response, dict):
                raise ValueError("Invalid API response format - response is None or not a dictionary")

            if api_response.get("status") != 1:
                error_message = api_response.get("message", "Unknown API error")
                self.logger.error(f"API returned error status: {error_message}")
                return {
                    "status": 0,
                    "message": f"API Error: {error_message}",
                    "data": []
                }

            # Safely get data with proper validation
            data = api_response.get('data', [])
            if data is None:
                data = []

            self.logger.info(f"Successfully fetched SPK dealing process data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching SPK dealing process data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store SPK dealing process records using bulk operations"""
        try:
            from datetime import datetime

            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No SPK dealing process data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} SPK dealing process records for dealer {dealer_id}")

            # Prepare bulk data for main records
            spk_records = []
            unit_records = []
            family_records = []

            for spk_record in data:
                try:
                    # Prepare SPK record
                    spk_data = {
                        'dealer_id': dealer_id,
                        'id_spk': spk_record.get("idSpk"),
                        'id_prospect': spk_record.get("idProspect"),
                        'nama_customer': spk_record.get("namaCustomer"),
                        'no_ktp': spk_record.get("noKtp"),
                        'alamat': spk_record.get("alamat"),
                        'kode_propinsi': spk_record.get("kodePropinsi"),
                        'kode_kota': spk_record.get("kodeKota"),
                        'kode_kecamatan': spk_record.get("kodeKecamatan"),
                        'kode_kelurahan': spk_record.get("kodeKelurahan"),
                        'kode_pos': spk_record.get("kodePos"),
                        'no_kontak': spk_record.get("noKontak"),
                        'nama_bpkb': spk_record.get("namaBPKB"),
                        'no_ktp_bpkb': spk_record.get("noKTPBPKB"),
                        'alamat_bpkb': spk_record.get("alamatBPKB"),
                        'kode_propinsi_bpkb': spk_record.get("kodePropinsiBPKB"),
                        'kode_kota_bpkb': spk_record.get("kodeKotaBPKB"),
                        'kode_kecamatan_bpkb': spk_record.get("kodeKecamatanBPKB"),
                        'kode_kelurahan_bpkb': spk_record.get("kodeKelurahanBPKB"),
                        'kode_pos_bpkb': spk_record.get("kodePosBPKB"),
                        'latitude': spk_record.get("latitude"),
                        'longitude': spk_record.get("longitude"),
                        'npwp': spk_record.get("NPWP"),
                        'no_kk': spk_record.get("noKK"),
                        'alamat_kk': spk_record.get("alamatKK"),
                        'kode_propinsi_kk': spk_record.get("kodePropinsiKK"),
                        'kode_kota_kk': spk_record.get("kodeKotaKK"),
                        'kode_kecamatan_kk': spk_record.get("kodeKecamatanKK"),
                        'kode_kelurahan_kk': spk_record.get("kodeKelurahanKK"),
                        'kode_pos_kk': spk_record.get("kodePosKK"),
                        'fax': spk_record.get("fax"),
                        'email': spk_record.get("email"),
                        'id_sales_people': spk_record.get("idSalesPeople"),
                        'id_event': spk_record.get("idEvent"),
                        'tanggal_pesanan': spk_record.get("tanggalPesanan"),
                        'status_spk': spk_record.get("statusSPK"),
                        'created_time': spk_record.get("createdTime"),
                        'modified_time': spk_record.get("modifiedTime"),
                        'fetched_at': datetime.utcnow()
                    }
                    spk_records.append(spk_data)

                    # Prepare unit records for this SPK
                    units = spk_record.get("unit", [])
                    for unit_record in units:
                        unit_data = {
                            'spk_id_spk': spk_record.get("idSpk"),  # Use for mapping
                            'kode_tipe_unit': self.safe_string(unit_record.get("kodeTipeUnit")),
                            'kode_warna': self.safe_string(unit_record.get("kodeWarna")),
                            'quantity': self.safe_int(unit_record.get("quantity")),
                            'harga_jual': self.safe_numeric(unit_record.get("hargaJual")),
                            'diskon': self.safe_numeric(unit_record.get("diskon")),
                            'amount_ppn': self.safe_numeric(unit_record.get("amountPPN")),
                            'faktur_pajak': self.safe_string(unit_record.get("fakturPajak")),
                            'tipe_pembayaran': self.safe_string(unit_record.get("tipePembayaran")),
                            'jumlah_tanda_jadi': self.safe_numeric(unit_record.get("jumlahTandaJadi")),
                            'tanggal_pengiriman': self.safe_string(unit_record.get("tanggalPengiriman")),
                            'id_sales_program': self.safe_string(unit_record.get("idSalesProgram")),
                            'id_apparel': self.safe_string(unit_record.get("idApparel")),
                            'created_time': self.safe_string(unit_record.get("createdTime")),
                            'modified_time': self.safe_string(unit_record.get("modifiedTime")),
                            'fetched_at': datetime.utcnow()
                        }
                        unit_records.append(unit_data)

                    # Prepare family member records for this SPK
                    family_members = spk_record.get("dataAnggotaKeluarga", [])
                    for family_record in family_members:
                        family_data = {
                            'spk_id_spk': spk_record.get("idSpk"),  # Use for mapping
                            'anggota_kk': family_record.get("anggotaKK"),
                            'created_time': family_record.get("createdTime"),
                            'modified_time': family_record.get("modifiedTime"),
                            'fetched_at': datetime.utcnow()
                        }
                        family_records.append(family_data)

                except Exception as e:
                    self.logger.error(f"Error preparing SPK dealing process record: {e}")
                    continue

            if not spk_records:
                self.logger.warning(f"No valid SPK dealing process records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert SPK records
            main_processed = self.bulk_upsert(
                db,
                SPKDealingProcessData,
                spk_records,
                conflict_columns=['dealer_id', 'id_spk'],
                batch_size=500
            )

            # Process unit records if any
            unit_processed = 0
            if unit_records:
                # Get SPK ID mapping for foreign keys
                spk_query = db.query(
                    SPKDealingProcessData.id,
                    SPKDealingProcessData.id_spk
                ).filter(SPKDealingProcessData.dealer_id == dealer_id)

                spk_mapping = {}
                for spk_id, id_spk in spk_query:
                    spk_mapping[id_spk] = spk_id

                # Update unit records with proper foreign keys
                for unit_record in unit_records:
                    id_spk = unit_record.pop('spk_id_spk')
                    if id_spk in spk_mapping:
                        unit_record['spk_dealing_process_data_id'] = spk_mapping[id_spk]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert unit records
                unit_processed = self.bulk_upsert(
                    db,
                    SPKDealingProcessUnit,
                    unit_records,
                    conflict_columns=['spk_dealing_process_data_id', 'kode_tipe_unit', 'kode_warna'],
                    batch_size=500
                )

            # Process family member records if any
            family_processed = 0
            if family_records:
                # Update family records with proper foreign keys
                for family_record in family_records:
                    id_spk = family_record.pop('spk_id_spk')
                    if id_spk in spk_mapping:
                        family_record['spk_dealing_process_data_id'] = spk_mapping[id_spk]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert family member records
                family_processed = self.bulk_upsert(
                    db,
                    SPKDealingProcessFamilyMember,
                    family_records,
                    conflict_columns=['spk_dealing_process_data_id', 'anggota_kk'],
                    batch_size=500
                )

            self.logger.info(f"Successfully processed {main_processed} SPK records, {unit_processed} units, and {family_processed} family members for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing SPK dealing process records for dealer {dealer_id}: {e}")
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
