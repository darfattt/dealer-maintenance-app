"""
DP HLO Data Processor

This module handles the processing of DP HLO data from the DPHLO API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import DPHLOAPIClient
from ..dummy_data_generators import get_dummy_dp_hlo_data
from database import DPHLOData, DPHLOPart, Dealer

logger = logging.getLogger(__name__)


class DPHLODataProcessor(BaseDataProcessor):
    """Processor for DP HLO data from DPHLO API"""
    
    def __init__(self):
        super().__init__("dphlo_read")
        self.api_client = DPHLOAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch DP HLO data from API or return dummy data"""
        try:
            # Extract optional parameters
            no_work_order = kwargs.get('no_work_order', '')
            id_hlo_document = kwargs.get('id_hlo_document', '')
            
            logger.info(f"Fetching DP HLO data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_dp_hlo_data(
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
            
            logger.info(f"Successfully fetched DP HLO data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching DP HLO data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store DP HLO records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No DP HLO data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for hlo_record in data:
                try:
                    # Check if HLO document already exists
                    id_hlo_document = hlo_record.get("idHLODocument")
                    if id_hlo_document:
                        existing = db.query(DPHLOData).filter(
                            DPHLOData.dealer_id == dealer_id,
                            DPHLOData.id_hlo_document == id_hlo_document
                        ).first()
                        
                        if existing:
                            logger.debug(f"HLO document {id_hlo_document} already exists, skipping")
                            continue
                    
                    # Create DP HLO data record
                    hlo_data = DPHLOData(
                        dealer_id=dealer_id,
                        no_invoice_uang_jaminan=hlo_record.get("noInvoiceUangJaminan"),
                        id_hlo_document=hlo_record.get("idHLODocument"),
                        tanggal_pemesanan_hlo=hlo_record.get("tanggalPemesananHLO"),
                        no_work_order=hlo_record.get("noWorkOrder"),
                        id_customer=hlo_record.get("idCustomer"),
                        created_time=hlo_record.get("createdTime"),
                        modified_time=hlo_record.get("modifiedTime")
                    )
                    
                    db.add(hlo_data)
                    db.flush()  # Get the ID
                    
                    # Process parts
                    parts = hlo_record.get("parts", [])
                    for part_record in parts:
                        part_data = DPHLOPart(
                            dp_hlo_data_id=hlo_data.id,
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
                    logger.error(f"Error processing DP HLO record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Processed {processed_count} DP HLO records for dealer {dealer_id}")
            
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing DP HLO records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for DP HLO data"""
        try:
            # Base query
            query = db.query(DPHLOData)
            if dealer_id:
                query = query.filter(DPHLOData.dealer_id == dealer_id)
            
            total_documents = query.count()
            
            # Count parts
            part_query = db.query(DPHLOPart)
            if dealer_id:
                part_query = part_query.join(DPHLOData).filter(
                    DPHLOData.dealer_id == dealer_id
                )
            
            total_parts = part_query.count()
            
            # Total amounts
            from sqlalchemy import func
            total_amounts = db.query(
                func.sum(DPHLOPart.total_harga_parts).label('total_parts_value'),
                func.sum(DPHLOPart.uang_muka).label('total_down_payment'),
                func.sum(DPHLOPart.sisa_bayar).label('total_remaining')
            )
            if dealer_id:
                total_amounts = total_amounts.join(DPHLOData).filter(
                    DPHLOData.dealer_id == dealer_id
                )
            
            amounts = total_amounts.first()
            
            # Parts distribution
            parts_dist = db.query(
                DPHLOPart.parts_number,
                func.sum(DPHLOPart.kuantitas).label('total_quantity')
            )
            if dealer_id:
                parts_dist = parts_dist.join(DPHLOData).filter(
                    DPHLOData.dealer_id == dealer_id
                )
            
            parts_distribution = [
                {"parts_number": row.parts_number or "Unknown", "quantity": row.total_quantity or 0}
                for row in parts_dist.group_by(DPHLOPart.parts_number).limit(10).all()
            ]
            
            # Work order distribution
            wo_dist = db.query(
                DPHLOData.no_work_order,
                func.count(DPHLOData.id).label('count')
            )
            if dealer_id:
                wo_dist = wo_dist.filter(DPHLOData.dealer_id == dealer_id)
            
            work_order_distribution = [
                {"work_order": row.no_work_order or "Unknown", "count": row.count}
                for row in wo_dist.group_by(DPHLOData.no_work_order).limit(10).all()
            ]
            
            return {
                "total_documents": total_documents,
                "total_parts": total_parts,
                "total_parts_value": float(amounts.total_parts_value or 0),
                "total_down_payment": float(amounts.total_down_payment or 0),
                "total_remaining": float(amounts.total_remaining or 0),
                "parts_distribution": parts_distribution,
                "work_order_distribution": work_order_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting DP HLO summary stats: {e}")
            return {
                "total_documents": 0,
                "total_parts": 0,
                "total_parts_value": 0.0,
                "total_down_payment": 0.0,
                "total_remaining": 0.0,
                "parts_distribution": [],
                "work_order_distribution": []
            }
