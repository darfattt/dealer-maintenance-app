"""
Unit Invoice Data Processor

This module handles the processing of unit invoice data from the MDINVH1 API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import UnitInvoiceAPIClient
from ..dummy_data_generators import get_dummy_unit_invoice_data
from database import UnitInvoiceData, UnitInvoiceUnit

logger = logging.getLogger(__name__)


class UnitInvoiceDataProcessor(BaseDataProcessor):
    """Processor for unit invoice data from MDINVH1 API"""
    
    def __init__(self):
        super().__init__("mdinvh1_read")
        self.api_client = UnitInvoiceAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch unit invoice data from API with enhanced validation"""
        try:
            # Extract optional parameters
            po_id = kwargs.get('po_id', '')
            no_shipping_list = kwargs.get('no_shipping_list', '')

            self.logger.info(f"Fetching unit invoice data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, po_id={po_id}, no_shipping_list={no_shipping_list}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_unit_invoice_data(
                    dealer.dealer_id, from_time, to_time,
                    po_id, no_shipping_list
                )

            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time,
                dealer.api_key, dealer.secret_key,
                po_id, no_shipping_list
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

            self.logger.info(f"Successfully fetched unit invoice data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching unit invoice data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store unit invoice records using bulk operations"""
        try:
            from datetime import datetime

            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No unit invoice data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} unit invoice records for dealer {dealer_id}")

            # Prepare bulk data for main records
            invoice_records = []
            unit_records = []

            for invoice_record in data:
                try:
                    # Prepare invoice record
                    invoice_data = {
                        'dealer_id': dealer_id,
                        'no_invoice': self.safe_string(invoice_record.get("noInvoice")),
                        'tanggal_invoice': self.safe_string(invoice_record.get("tanggalInvoice")),
                        'tanggal_jatuh_tempo': self.safe_string(invoice_record.get("tanggalJatuhTempo")),
                        'main_dealer_id': self.safe_string(invoice_record.get("mainDealerId")),
                        'total_harga_sebelum_diskon': self.safe_numeric(invoice_record.get("totalHargaSebelumDiskon")),
                        'total_diskon_per_unit': self.safe_numeric(invoice_record.get("totalDiskonPerUnit")),
                        'potongan_per_invoice': self.safe_numeric(invoice_record.get("potonganPerInvoice")),
                        'total_ppn': self.safe_numeric(invoice_record.get("totalPPN")),
                        'total_harga': self.safe_numeric(invoice_record.get("totalHarga")),
                        'created_time': self.safe_string(invoice_record.get("createdTime")),
                        'modified_time': self.safe_string(invoice_record.get("modifiedTime")),
                        'fetched_at': datetime.utcnow()
                    }
                    invoice_records.append(invoice_data)

                    # Prepare unit records for this invoice
                    units = invoice_record.get("unit", [])
                    for unit_record in units:
                        unit_data = {
                            'invoice_no_invoice': invoice_record.get("noInvoice"),  # Use for mapping
                            'kode_tipe_unit': self.safe_string(unit_record.get("kodeTipeUnit")),
                            'kode_warna': self.safe_string(unit_record.get("kodeWarna")),
                            'kuantitas': self.safe_int(unit_record.get("kuantitas")),
                            'no_mesin': self.safe_string(unit_record.get("noMesin")),
                            'no_rangka': self.safe_string(unit_record.get("noRangka")),
                            'harga_satuan_sebelum_diskon': self.safe_numeric(unit_record.get("hargaSatuanSebelumDiskon")),
                            'diskon_per_unit': self.safe_numeric(unit_record.get("diskonPerUnit")),
                            'po_id': self.safe_string(unit_record.get("poId")),
                            'created_time': self.safe_string(unit_record.get("createdTime")),
                            'modified_time': self.safe_string(unit_record.get("modifiedTime")),
                            'fetched_at': datetime.utcnow()
                        }
                        unit_records.append(unit_data)

                except Exception as e:
                    self.logger.error(f"Error preparing unit invoice record: {e}")
                    continue

            if not invoice_records:
                self.logger.warning(f"No valid unit invoice records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert invoice records
            main_processed = self.bulk_upsert(
                db,
                UnitInvoiceData,
                invoice_records,
                conflict_columns=['dealer_id', 'no_invoice'],
                batch_size=500
            )

            # Process unit records if any
            unit_processed = 0
            if unit_records:
                # Get invoice ID mapping for foreign keys
                invoice_query = db.query(
                    UnitInvoiceData.id,
                    UnitInvoiceData.no_invoice
                ).filter(UnitInvoiceData.dealer_id == dealer_id)

                invoice_mapping = {}
                for invoice_id, no_invoice in invoice_query:
                    invoice_mapping[no_invoice] = invoice_id

                # Update unit records with proper foreign keys
                for unit_record in unit_records:
                    no_invoice = unit_record.pop('invoice_no_invoice')
                    if no_invoice in invoice_mapping:
                        unit_record['unit_invoice_data_id'] = invoice_mapping[no_invoice]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert unit records
                unit_processed = self.bulk_upsert(
                    db,
                    UnitInvoiceUnit,
                    unit_records,
                    conflict_columns=['unit_invoice_data_id', 'no_rangka'],
                    batch_size=500
                )

            self.logger.info(f"Successfully processed {main_processed} unit invoice records and {unit_processed} units for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing unit invoice records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for unit invoice data"""
        try:
            # Base query
            query = db.query(UnitInvoiceData)
            if dealer_id:
                query = query.filter(UnitInvoiceData.dealer_id == dealer_id)
            
            total_invoices = query.count()
            
            # Count units
            unit_query = db.query(UnitInvoiceUnit)
            if dealer_id:
                unit_query = unit_query.join(UnitInvoiceData).filter(
                    UnitInvoiceData.dealer_id == dealer_id
                )
            
            total_units = unit_query.count()
            
            # Total amounts
            from sqlalchemy import func
            total_amounts = db.query(
                func.sum(UnitInvoiceData.total_harga_sebelum_diskon).label('total_before_discount'),
                func.sum(UnitInvoiceData.total_diskon_per_unit).label('total_discount'),
                func.sum(UnitInvoiceData.total_ppn).label('total_ppn'),
                func.sum(UnitInvoiceData.total_harga).label('total_amount')
            )
            if dealer_id:
                total_amounts = total_amounts.filter(UnitInvoiceData.dealer_id == dealer_id)
            
            amounts = total_amounts.first()
            
            # Unit type distribution
            unit_type_dist = db.query(
                UnitInvoiceUnit.kode_tipe_unit,
                func.sum(UnitInvoiceUnit.kuantitas).label('total_quantity')
            )
            if dealer_id:
                unit_type_dist = unit_type_dist.join(UnitInvoiceData).filter(
                    UnitInvoiceData.dealer_id == dealer_id
                )
            
            unit_type_distribution = [
                {"unit_type": row.kode_tipe_unit or "Unknown", "quantity": row.total_quantity or 0}
                for row in unit_type_dist.group_by(UnitInvoiceUnit.kode_tipe_unit).all()
            ]
            
            return {
                "total_invoices": total_invoices,
                "total_units": total_units,
                "total_before_discount": float(amounts.total_before_discount or 0),
                "total_discount": float(amounts.total_discount or 0),
                "total_ppn": float(amounts.total_ppn or 0),
                "total_amount": float(amounts.total_amount or 0),
                "unit_type_distribution": unit_type_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting unit invoice summary stats: {e}")
            return {
                "total_invoices": 0,
                "total_units": 0,
                "total_before_discount": 0.0,
                "total_discount": 0.0,
                "total_ppn": 0.0,
                "total_amount": 0.0,
                "unit_type_distribution": []
            }
