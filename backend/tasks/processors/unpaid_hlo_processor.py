"""
Unpaid HLO Data Processor

This module handles the processing of unpaid HLO data from the UNPAIDHLO API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import UnpaidHLOAPIClient
from ..dummy_data_generators import get_dummy_unpaid_hlo_data
from database import UnpaidHLOData, UnpaidHLOPart, Dealer

logger = logging.getLogger(__name__)


class UnpaidHLODataProcessor(BaseDataProcessor):
    """Processor for unpaid HLO data from UNPAIDHLO API"""
    
    def __init__(self):
        super().__init__("unpaidhlo_read")
        self.api_client = UnpaidHLOAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch unpaid HLO data from API or return dummy data"""
        try:
            # Extract optional parameters
            no_work_order = kwargs.get('no_work_order', '')
            id_hlo_document = kwargs.get('id_hlo_document', '')
            
            logger.info(f"Fetching unpaid HLO data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
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
                logger.error(f"API returned error status: {error_message}")
                # Return actual error instead of falling back to dummy data
                return {
                    "status": 0,
                    "message": f"API Error: {error_message}",
                    "data": []
                }
            
            # Safely get data with proper validation
            data = api_response.get('data', [])
            if data is None:
                data = []
            
            logger.info(f"Successfully fetched unpaid HLO data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching unpaid HLO data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store unpaid HLO records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No unpaid HLO data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for hlo_record in data:
                try:
                    # Check if HLO document already exists
                    id_hlo_document = hlo_record.get("idHLODocument")
                    if id_hlo_document:
                        existing = db.query(UnpaidHLOData).filter(
                            UnpaidHLOData.dealer_id == dealer_id,
                            UnpaidHLOData.id_hlo_document == id_hlo_document
                        ).first()
                        
                        if existing:
                            logger.debug(f"Unpaid HLO document {id_hlo_document} already exists, skipping")
                            continue
                    
                    # Create unpaid HLO data record
                    hlo_data = UnpaidHLOData(
                        dealer_id=dealer_id,
                        id_hlo_document=hlo_record.get("idHLODocument"),
                        tanggal_pemesanan_hlo=hlo_record.get("tanggalPemesananHLO"),
                        no_work_order=hlo_record.get("noWorkOrder"),
                        no_buku_claim_c2=hlo_record.get("noBukuClaimC2"),
                        no_ktp=hlo_record.get("noKTP"),
                        nama_customer=hlo_record.get("namaCustomer"),
                        alamat=hlo_record.get("alamat"),
                        kode_propinsi=hlo_record.get("kodePropinsi"),
                        kode_kota=hlo_record.get("kodeKota"),
                        kode_kecamatan=hlo_record.get("kodeKecamatan"),
                        kode_kelurahan=hlo_record.get("kodeKelurahan"),
                        kode_pos=hlo_record.get("kodePos"),
                        no_kontak=hlo_record.get("noKontak"),
                        kode_tipe_unit=hlo_record.get("kodeTipeUnit"),
                        tahun_motor=hlo_record.get("tahunMotor"),
                        no_mesin=hlo_record.get("noMesin"),
                        no_rangka=hlo_record.get("noRangka"),
                        flag_numbering=hlo_record.get("flagNumbering"),
                        vehicle_off_road=hlo_record.get("vehicleOffRoad"),
                        job_return=hlo_record.get("jobReturn"),
                        created_time=hlo_record.get("createdTime"),
                        modified_time=hlo_record.get("modifiedTime")
                    )
                    
                    db.add(hlo_data)
                    db.flush()  # Get the ID
                    
                    # Process parts
                    parts = hlo_record.get("parts", [])
                    for part_record in parts:
                        part_data = UnpaidHLOPart(
                            unpaid_hlo_data_id=hlo_data.id,
                            parts_number=part_record.get("partsNumber"),
                            kuantitas=part_record.get("kuantitas"),
                            harga_parts=part_record.get("hargaParts"),
                            total_harga_parts=part_record.get("totalHargaParts"),
                            uang_muka=part_record.get("uangMuka"),
                            sisa_bayar=part_record.get("sisaBayar"),
                            created_time=part_record.get("createdTime"),
                            modified_time=part_record.get("modifiedTime")
                        )
                        db.add(part_data)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing unpaid HLO record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Processed {processed_count} unpaid HLO records for dealer {dealer_id}")
            
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing unpaid HLO records for dealer {dealer_id}: {e}")
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
