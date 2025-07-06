"""
Parts Invoice Data Processor

This module handles the processing of parts invoice data from the MDINVH3 API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from .base_processor import BaseDataProcessor
from ..api_clients import PartsInvoiceAPIClient
from ..dummy_data_generators import get_dummy_parts_invoice_data
from database import PartsInvoiceData, PartsInvoicePart

logger = logging.getLogger(__name__)


class PartsInvoiceDataProcessor(BaseDataProcessor):
    """Processor for parts invoice data from MDINVH3 API"""
    
    def __init__(self):
        super().__init__("mdinvh3_read")
        self.api_client = PartsInvoiceAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch parts invoice data from API with enhanced validation"""
        try:
            # Extract optional parameters
            no_po = kwargs.get('no_po', '')

            self.logger.info(f"Fetching parts invoice data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, no_po={no_po}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_parts_invoice_data(
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

            self.logger.info(f"Successfully fetched parts invoice data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching parts invoice data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store parts invoice records using bulk operations"""
        try:
            from datetime import datetime

            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No parts invoice data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} parts invoice records for dealer {dealer_id}")

            # Prepare bulk data for main records
            invoice_records = []
            part_records = []

            for invoice_record in data:
                try:
                    # Prepare invoice record
                    invoice_data = {
                        'dealer_id': dealer_id,
                        'no_invoice': invoice_record.get("noInvoice"),
                        'tgl_invoice': invoice_record.get("tglInvoice"),
                        'tgl_jatuh_tempo': invoice_record.get("tglJatuhTempo"),
                        'main_dealer_id': invoice_record.get("mainDealerId"),
                        'total_harga_sebelum_diskon': invoice_record.get("totalHargaSebelumDiskon"),
                        'total_diskon_per_parts_number': invoice_record.get("totalDiskonPerPartsNumber"),
                        'potongan_per_invoice': invoice_record.get("potonganPerInvoice"),
                        'total_ppn': invoice_record.get("totalPPN"),
                        'total_harga': invoice_record.get("totalHarga"),
                        'created_time': invoice_record.get("createdTime"),
                        'modified_time': invoice_record.get("modifiedTime"),
                        'fetched_at': datetime.utcnow()
                    }
                    invoice_records.append(invoice_data)

                    # Prepare part records for this invoice
                    parts = invoice_record.get("parts", [])
                    for part_record in parts:
                        part_data = {
                            'invoice_no_invoice': invoice_record.get("noInvoice"),  # Use for mapping
                            'no_po': part_record.get("noPO"),
                            'jenis_order': part_record.get("jenisOrder"),
                            'parts_number': part_record.get("partsNumber"),
                            'kuantitas': part_record.get("kuantitas"),
                            'uom': part_record.get("uom"),
                            'harga_satuan_sebelum_diskon': part_record.get("hargaSatuanSebelumDiskon"),
                            'diskon_per_parts_number': part_record.get("diskonPerPartsNumber"),
                            'created_time': part_record.get("createdTime"),
                            'modified_time': part_record.get("modifiedTime"),
                            'fetched_at': datetime.utcnow()
                        }
                        part_records.append(part_data)

                except Exception as e:
                    self.logger.error(f"Error preparing parts invoice record: {e}")
                    continue

            if not invoice_records:
                self.logger.warning(f"No valid parts invoice records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert invoice records
            main_processed = self.bulk_upsert(
                db,
                PartsInvoiceData,
                invoice_records,
                conflict_columns=['dealer_id', 'no_invoice'],
                batch_size=500
            )

            # Process part records if any
            part_processed = 0
            if part_records:
                # Get invoice ID mapping for foreign keys
                invoice_query = db.query(
                    PartsInvoiceData.id,
                    PartsInvoiceData.no_invoice
                ).filter(PartsInvoiceData.dealer_id == dealer_id)

                invoice_mapping = {}
                for invoice_id, no_invoice in invoice_query:
                    invoice_mapping[no_invoice] = invoice_id

                # Update part records with proper foreign keys
                for part_record in part_records:
                    no_invoice = part_record.pop('invoice_no_invoice')
                    if no_invoice in invoice_mapping:
                        part_record['parts_invoice_data_id'] = invoice_mapping[no_invoice]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert part records
                part_processed = self.bulk_upsert(
                    db,
                    PartsInvoicePart,
                    part_records,
                    conflict_columns=['parts_invoice_data_id', 'parts_number', 'no_po'],
                    batch_size=500
                )

            db.commit()
            self.logger.info(f"Successfully processed {main_processed} parts invoice records and {part_processed} parts for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error processing parts invoice records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for parts invoice data"""
        try:
            # Base query
            query = db.query(PartsInvoiceData)
            if dealer_id:
                query = query.filter(PartsInvoiceData.dealer_id == dealer_id)
            
            total_invoices = query.count()
            
            # Count parts
            part_query = db.query(PartsInvoicePart)
            if dealer_id:
                part_query = part_query.join(PartsInvoiceData).filter(
                    PartsInvoiceData.dealer_id == dealer_id
                )
            
            total_parts = part_query.count()
            
            # Total amounts
            from sqlalchemy import func
            total_amounts = db.query(
                func.sum(PartsInvoiceData.total_harga_sebelum_diskon).label('total_before_discount'),
                func.sum(PartsInvoiceData.total_diskon_per_parts_number).label('total_discount'),
                func.sum(PartsInvoiceData.potongan_per_invoice).label('total_invoice_discount'),
                func.sum(PartsInvoiceData.total_ppn).label('total_ppn'),
                func.sum(PartsInvoiceData.total_harga).label('total_amount')
            )
            if dealer_id:
                total_amounts = total_amounts.filter(PartsInvoiceData.dealer_id == dealer_id)
            
            amounts = total_amounts.first()
            
            # Parts distribution
            parts_dist = db.query(
                PartsInvoicePart.parts_number,
                func.sum(PartsInvoicePart.kuantitas).label('total_quantity')
            )
            if dealer_id:
                parts_dist = parts_dist.join(PartsInvoiceData).filter(
                    PartsInvoiceData.dealer_id == dealer_id
                )
            
            parts_distribution = [
                {"parts_number": row.parts_number or "Unknown", "quantity": row.total_quantity or 0}
                for row in parts_dist.group_by(PartsInvoicePart.parts_number).limit(10).all()
            ]
            
            # Order type distribution
            order_type_dist = db.query(
                PartsInvoicePart.jenis_order,
                func.count(PartsInvoicePart.id).label('count')
            )
            if dealer_id:
                order_type_dist = order_type_dist.join(PartsInvoiceData).filter(
                    PartsInvoiceData.dealer_id == dealer_id
                )
            
            order_type_distribution = [
                {"order_type": row.jenis_order or "Unknown", "count": row.count}
                for row in order_type_dist.group_by(PartsInvoicePart.jenis_order).all()
            ]
            
            return {
                "total_invoices": total_invoices,
                "total_parts": total_parts,
                "total_before_discount": float(amounts.total_before_discount or 0),
                "total_discount": float(amounts.total_discount or 0),
                "total_invoice_discount": float(amounts.total_invoice_discount or 0),
                "total_ppn": float(amounts.total_ppn or 0),
                "total_amount": float(amounts.total_amount or 0),
                "parts_distribution": parts_distribution,
                "order_type_distribution": order_type_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting parts invoice summary stats: {e}")
            return {
                "total_invoices": 0,
                "total_parts": 0,
                "total_before_discount": 0.0,
                "total_discount": 0.0,
                "total_invoice_discount": 0.0,
                "total_ppn": 0.0,
                "total_amount": 0.0,
                "parts_distribution": [],
                "order_type_distribution": []
            }
