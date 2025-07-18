"""
Parts Sales Data Processor

This module handles the processing of parts sales data from the PRSL API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from .base_processor import BaseDataProcessor
from ..api_clients import PartsSalesAPIClient
from ..dummy_data_generators import get_dummy_parts_sales_data
from database import PartsSalesData, PartsSalesPart

logger = logging.getLogger(__name__)


class PartsSalesDataProcessor(BaseDataProcessor):
    """Processor for parts sales data from PRSL API"""
    
    def __init__(self):
        super().__init__("prsl_read")
        self.api_client = PartsSalesAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch parts sales data from API with enhanced validation"""
        try:
            # Extract optional parameters
            no_po = kwargs.get('no_po', '')

            self.logger.info(f"Fetching parts sales data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, no_po={no_po}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
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

            self.logger.info(f"Successfully fetched parts sales data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching parts sales data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store parts sales records using bulk operations"""
        try:
            from datetime import datetime

            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No parts sales data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} parts sales records for dealer {dealer_id}")

            # Prepare bulk data for main records
            sales_records = []
            part_records = []

            for sales_record in data:
                try:
                    # Prepare sales record
                    sales_data = {
                        'dealer_id': dealer_id,
                        'no_so': self.safe_string(sales_record.get("noSO")),
                        'tgl_so': self.safe_string(sales_record.get("tglSO")),
                        'id_customer': self.safe_string(sales_record.get("idCustomer")),
                        'nama_customer': self.safe_string(sales_record.get("namaCustomer")),
                        'disc_so': self.safe_numeric(sales_record.get("discSO")),
                        'total_harga_so': self.safe_numeric(sales_record.get("totalHargaSO")),
                        'created_time': self.safe_string(sales_record.get("createdTime")),
                        'modified_time': self.safe_string(sales_record.get("modifiedTime")),
                        'fetched_at': datetime.utcnow()
                    }
                    sales_records.append(sales_data)

                    # Prepare part records for this sales order
                    parts = sales_record.get("parts", [])
                    for part_record in parts:
                        part_data = {
                            'sales_no_so': sales_record.get("noSO"),  # Use for mapping
                            'parts_number': self.safe_string(part_record.get("partsNumber")),
                            'kuantitas': self.safe_int(part_record.get("kuantitas")),
                            'harga_parts': self.safe_numeric(part_record.get("hargaParts")),
                            'promo_id_parts': self.safe_string(part_record.get("promoIdParts")),
                            'disc_amount': self.safe_numeric(part_record.get("discAmount")),
                            'disc_percentage': self.safe_string(part_record.get("discPercentage")),
                            'ppn': self.safe_numeric(part_record.get("ppn")),
                            'total_harga_parts': self.safe_numeric(part_record.get("totalHargaParts")),
                            'uang_muka': self.safe_numeric(part_record.get("uangMuka")),
                            'booking_id_reference': self.safe_string(part_record.get("bookingIdReference")),
                            'created_time': self.safe_string(part_record.get("createdTime")),
                            'modified_time': self.safe_string(part_record.get("modifiedTime")),
                            'fetched_at': datetime.utcnow()
                        }
                        part_records.append(part_data)

                except Exception as e:
                    self.logger.error(f"Error preparing parts sales record: {e}")
                    continue

            if not sales_records:
                self.logger.warning(f"No valid parts sales records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert sales records
            main_processed = self.bulk_upsert(
                db,
                PartsSalesData,
                sales_records,
                conflict_columns=['dealer_id', 'no_so'],
                batch_size=500
            )

            # Process part records if any
            part_processed = 0
            if part_records:
                # Get sales ID mapping for foreign keys
                sales_query = db.query(
                    PartsSalesData.id,
                    PartsSalesData.no_so
                ).filter(PartsSalesData.dealer_id == dealer_id)

                sales_mapping = {}
                for sales_id, no_so in sales_query:
                    sales_mapping[no_so] = sales_id

                # Update part records with proper foreign keys
                for part_record in part_records:
                    no_so = part_record.pop('sales_no_so')
                    if no_so in sales_mapping:
                        part_record['parts_sales_data_id'] = sales_mapping[no_so]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert part records
                part_processed = self.bulk_upsert(
                    db,
                    PartsSalesPart,
                    part_records,
                    conflict_columns=['parts_sales_data_id', 'parts_number'],
                    batch_size=500
                )

            self.logger.info(f"Successfully processed {main_processed} parts sales records and {part_processed} parts for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing parts sales records for dealer {dealer_id}: {e}")
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
