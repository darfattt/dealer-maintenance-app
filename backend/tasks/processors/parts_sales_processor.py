"""
Parts Sales Data Processor

This module handles the processing of parts sales data from the PRSL API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import PartsSalesAPIClient
from ..dummy_data_generators import get_dummy_parts_sales_data
from database import PartsSalesData, PartsSalesPart, Dealer

logger = logging.getLogger(__name__)


class PartsSalesDataProcessor(BaseDataProcessor):
    """Processor for parts sales data from PRSL API"""
    
    def __init__(self):
        super().__init__("prsl_read")
        self.api_client = PartsSalesAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch parts sales data from API or return dummy data"""
        try:
            # Extract optional parameters
            no_po = kwargs.get('no_po', '')
            
            logger.info(f"Fetching parts sales data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_parts_sales_data(
                    dealer.dealer_id, from_time, to_time, no_po
                )
            
            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time, 
                dealer.api_key, dealer.secret_key, no_po
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
            
            logger.info(f"Successfully fetched parts sales data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching parts sales data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store parts sales records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No parts sales data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for sales_record in data:
                try:
                    # Check if sales order already exists
                    no_so = sales_record.get("noSO")
                    if no_so:
                        existing = db.query(PartsSalesData).filter(
                            PartsSalesData.dealer_id == dealer_id,
                            PartsSalesData.no_so == no_so
                        ).first()
                        
                        if existing:
                            logger.debug(f"Sales order {no_so} already exists, skipping")
                            continue
                    
                    # Create parts sales data record
                    sales_data = PartsSalesData(
                        dealer_id=dealer_id,
                        no_so=sales_record.get("noSO"),
                        tgl_so=sales_record.get("tglSO"),
                        id_customer=sales_record.get("idCustomer"),
                        nama_customer=sales_record.get("namaCustomer"),
                        disc_so=sales_record.get("discSO"),
                        total_harga_so=sales_record.get("totalHargaSO"),
                        created_time=sales_record.get("createdTime"),
                        modified_time=sales_record.get("modifiedTime")
                    )
                    
                    db.add(sales_data)
                    db.flush()  # Get the ID
                    
                    # Process parts
                    parts = sales_record.get("parts", [])
                    for part_record in parts:
                        part_data = PartsSalesPart(
                            parts_sales_data_id=sales_data.id,
                            parts_number=part_record.get("partsNumber"),
                            kuantitas=part_record.get("kuantitas"),
                            harga_parts=part_record.get("hargaParts"),
                            promo_id_parts=part_record.get("promoIdParts"),
                            disc_amount=part_record.get("discAmount"),
                            disc_percentage=part_record.get("discPercentage"),
                            ppn=part_record.get("ppn"),
                            total_harga_parts=part_record.get("totalHargaParts"),
                            uang_muka=part_record.get("uangMuka"),
                            booking_id_reference=part_record.get("bookingIdReference"),
                            created_time=part_record.get("createdTime"),
                            modified_time=part_record.get("modifiedTime")
                        )
                        db.add(part_data)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing parts sales record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Processed {processed_count} parts sales records for dealer {dealer_id}")
            
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing parts sales records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for parts sales data"""
        try:
            # Base query
            query = db.query(PartsSalesData)
            if dealer_id:
                query = query.filter(PartsSalesData.dealer_id == dealer_id)
            
            total_orders = query.count()
            
            # Count parts
            part_query = db.query(PartsSalesPart)
            if dealer_id:
                part_query = part_query.join(PartsSalesData).filter(
                    PartsSalesData.dealer_id == dealer_id
                )
            
            total_parts = part_query.count()
            
            # Total amounts
            from sqlalchemy import func
            total_amounts = db.query(
                func.sum(PartsSalesData.total_harga_so).label('total_sales'),
                func.sum(PartsSalesData.disc_so).label('total_discount')
            )
            if dealer_id:
                total_amounts = total_amounts.filter(PartsSalesData.dealer_id == dealer_id)
            
            amounts = total_amounts.first()
            
            # Parts distribution
            parts_dist = db.query(
                PartsSalesPart.parts_number,
                func.sum(PartsSalesPart.kuantitas).label('total_quantity')
            )
            if dealer_id:
                parts_dist = parts_dist.join(PartsSalesData).filter(
                    PartsSalesData.dealer_id == dealer_id
                )
            
            parts_distribution = [
                {"parts_number": row.parts_number or "Unknown", "quantity": row.total_quantity or 0}
                for row in parts_dist.group_by(PartsSalesPart.parts_number).limit(10).all()
            ]
            
            return {
                "total_orders": total_orders,
                "total_parts": total_parts,
                "total_sales": float(amounts.total_sales or 0),
                "total_discount": float(amounts.total_discount or 0),
                "parts_distribution": parts_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting parts sales summary stats: {e}")
            return {
                "total_orders": 0,
                "total_parts": 0,
                "total_sales": 0.0,
                "total_discount": 0.0,
                "parts_distribution": []
            }
