"""
Unpaid HLO Data Processor

This module handles the processing of unpaid HLO data from the UNPAIDHLO API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from .base_processor import BaseDataProcessor
from ..api_clients import UnpaidHLOAPIClient
from ..dummy_data_generators import get_dummy_unpaid_hlo_data
from database import UnpaidHLOData, UnpaidHLOPart

logger = logging.getLogger(__name__)


class UnpaidHLODataProcessor(BaseDataProcessor):
    """Processor for unpaid HLO data from UNPAIDHLO API"""
    
    def __init__(self):
        super().__init__("unpaidhlo_read")
        self.api_client = UnpaidHLOAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch unpaid HLO data from API with enhanced validation"""
        try:
            # Extract optional parameters
            no_work_order = kwargs.get('no_work_order', '')
            id_hlo_document = kwargs.get('id_hlo_document', '')

            self.logger.info(f"Fetching unpaid HLO data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, no_work_order={no_work_order}, id_hlo_document={id_hlo_document}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_unpaid_hlo_data(
                    dealer.dealer_id, from_time, to_time,
                    no_work_order, id_hlo_document
                )

            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time,
                dealer.api_key, dealer.secret_key,
                no_work_order, id_hlo_document
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

            self.logger.info(f"Successfully fetched unpaid HLO data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching unpaid HLO data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store unpaid HLO records using bulk operations"""
        try:
            from datetime import datetime

            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No unpaid HLO data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} unpaid HLO records for dealer {dealer_id}")

            # Prepare bulk data for main records
            hlo_records = []
            part_records = []

            for hlo_record in data:
                try:
                    # Prepare HLO record
                    hlo_data = {
                        'dealer_id': dealer_id,
                        'id_hlo_document': hlo_record.get("idHLODocument"),
                        'tanggal_pemesanan_hlo': hlo_record.get("tanggalPemesananHLO"),
                        'no_work_order': hlo_record.get("noWorkOrder"),
                        'no_buku_claim_c2': hlo_record.get("noBukuClaimC2"),
                        'no_ktp': hlo_record.get("noKTP"),
                        'nama_customer': hlo_record.get("namaCustomer"),
                        'alamat': hlo_record.get("alamat"),
                        'kode_propinsi': hlo_record.get("kodePropinsi"),
                        'kode_kota': hlo_record.get("kodeKota"),
                        'kode_kecamatan': hlo_record.get("kodeKecamatan"),
                        'kode_kelurahan': hlo_record.get("kodeKelurahan"),
                        'kode_pos': hlo_record.get("kodePos"),
                        'no_kontak': hlo_record.get("noKontak"),
                        'kode_tipe_unit': hlo_record.get("kodeTipeUnit"),
                        'tahun_motor': hlo_record.get("tahunMotor"),
                        'no_mesin': hlo_record.get("noMesin"),
                        'no_rangka': hlo_record.get("noRangka"),
                        'flag_numbering': hlo_record.get("flagNumbering"),
                        'vehicle_off_road': hlo_record.get("vehicleOffRoad"),
                        'job_return': hlo_record.get("jobReturn"),
                        'created_time': hlo_record.get("createdTime"),
                        'modified_time': hlo_record.get("modifiedTime"),
                        'fetched_at': datetime.utcnow()
                    }
                    hlo_records.append(hlo_data)

                    # Prepare part records for this HLO document
                    parts = hlo_record.get("parts", [])
                    for part_record in parts:
                        part_data = {
                            'hlo_id_hlo_document': hlo_record.get("idHLODocument"),  # Use for mapping
                            'parts_number': part_record.get("partsNumber"),
                            'kuantitas': part_record.get("kuantitas"),
                            'harga_parts': part_record.get("hargaParts"),
                            'total_harga_parts': part_record.get("totalHargaParts"),
                            'uang_muka': part_record.get("uangMuka"),
                            'sisa_bayar': part_record.get("sisaBayar"),
                            'created_time': part_record.get("createdTime"),
                            'modified_time': part_record.get("modifiedTime"),
                            'fetched_at': datetime.utcnow()
                        }
                        part_records.append(part_data)

                except Exception as e:
                    self.logger.error(f"Error preparing unpaid HLO record: {e}")
                    continue

            if not hlo_records:
                self.logger.warning(f"No valid unpaid HLO records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert HLO records
            main_processed = self.bulk_upsert(
                db,
                UnpaidHLOData,
                hlo_records,
                conflict_columns=['dealer_id', 'id_hlo_document'],
                batch_size=500
            )

            # Process part records if any
            part_processed = 0
            if part_records:
                # Get HLO ID mapping for foreign keys
                hlo_query = db.query(
                    UnpaidHLOData.id,
                    UnpaidHLOData.id_hlo_document
                ).filter(UnpaidHLOData.dealer_id == dealer_id)

                hlo_mapping = {}
                for hlo_id, id_hlo_document in hlo_query:
                    hlo_mapping[id_hlo_document] = hlo_id

                # Update part records with proper foreign keys
                for part_record in part_records:
                    id_hlo_document = part_record.pop('hlo_id_hlo_document')
                    if id_hlo_document in hlo_mapping:
                        part_record['unpaid_hlo_data_id'] = hlo_mapping[id_hlo_document]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert part records
                part_processed = self.bulk_upsert(
                    db,
                    UnpaidHLOPart,
                    part_records,
                    conflict_columns=['unpaid_hlo_data_id', 'parts_number'],
                    batch_size=500
                )

            db.commit()
            self.logger.info(f"Successfully processed {main_processed} unpaid HLO records and {part_processed} parts for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error processing unpaid HLO records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for unpaid HLO data"""
        try:
            # Base query
            query = db.query(UnpaidHLOData)
            if dealer_id:
                query = query.filter(UnpaidHLOData.dealer_id == dealer_id)
            
            total_documents = query.count()
            
            # Count parts
            part_query = db.query(UnpaidHLOPart)
            if dealer_id:
                part_query = part_query.join(UnpaidHLOData).filter(
                    UnpaidHLOData.dealer_id == dealer_id
                )
            
            total_parts = part_query.count()
            
            # Total amounts
            from sqlalchemy import func
            total_amounts = db.query(
                func.sum(UnpaidHLOPart.total_harga_parts).label('total_parts_value'),
                func.sum(UnpaidHLOPart.uang_muka).label('total_down_payment'),
                func.sum(UnpaidHLOPart.sisa_bayar).label('total_remaining')
            )
            if dealer_id:
                total_amounts = total_amounts.join(UnpaidHLOData).filter(
                    UnpaidHLOData.dealer_id == dealer_id
                )
            
            amounts = total_amounts.first()
            
            # Vehicle type distribution
            vehicle_dist = db.query(
                UnpaidHLOData.kode_tipe_unit,
                func.count(UnpaidHLOData.id).label('count')
            )
            if dealer_id:
                vehicle_dist = vehicle_dist.filter(UnpaidHLOData.dealer_id == dealer_id)
            
            vehicle_distribution = [
                {"vehicle_type": row.kode_tipe_unit or "Unknown", "count": row.count}
                for row in vehicle_dist.group_by(UnpaidHLOData.kode_tipe_unit).limit(10).all()
            ]
            
            return {
                "total_documents": total_documents,
                "total_parts": total_parts,
                "total_parts_value": float(amounts.total_parts_value or 0),
                "total_down_payment": float(amounts.total_down_payment or 0),
                "total_remaining": float(amounts.total_remaining or 0),
                "vehicle_distribution": vehicle_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting unpaid HLO summary stats: {e}")
            return {
                "total_documents": 0,
                "total_parts": 0,
                "total_parts_value": 0.0,
                "total_down_payment": 0.0,
                "total_remaining": 0.0,
                "vehicle_distribution": []
            }
