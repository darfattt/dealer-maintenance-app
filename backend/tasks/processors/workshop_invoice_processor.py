"""
Workshop Invoice Data Processor

This module handles the processing of workshop invoice data from the INV2 API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from .base_processor import BaseDataProcessor
from ..api_clients import WorkshopInvoiceAPIClient
from ..dummy_data_generators import get_dummy_workshop_invoice_data
from database import WorkshopInvoiceData, WorkshopInvoiceNJB, WorkshopInvoiceNSC

logger = logging.getLogger(__name__)


class WorkshopInvoiceDataProcessor(BaseDataProcessor):
    """Processor for workshop invoice data from INV2 API"""
    
    def __init__(self):
        super().__init__("inv2_read")
        self.api_client = WorkshopInvoiceAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch workshop invoice data from API with enhanced validation"""
        try:
            # Extract optional parameters
            no_work_order = kwargs.get('no_work_order', '')

            self.logger.info(f"Fetching workshop invoice data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, no_work_order={no_work_order}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_workshop_invoice_data(
                    dealer.dealer_id, from_time, to_time, no_work_order
                )

            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time,
                dealer.api_key, dealer.secret_key, no_work_order
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

            self.logger.info(f"Successfully fetched workshop invoice data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching workshop invoice data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store workshop invoice records using bulk operations"""
        try:
            from datetime import datetime

            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No workshop invoice data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} workshop invoice records for dealer {dealer_id}")

            # Prepare bulk data for main records
            invoice_records = []
            njb_records = []
            nsc_records = []

            for invoice_record in data:
                try:
                    # Prepare invoice record
                    invoice_data = {
                        'dealer_id': dealer_id,
                        'no_work_order': self.safe_string(invoice_record.get("noWorkOrder")),
                        'no_njb': self.safe_string(invoice_record.get("noNJB")),
                        'tanggal_njb': self.safe_string(invoice_record.get("tanggalNJB")),
                        'total_harga_njb': self.safe_numeric(invoice_record.get("totalHargaNJB")),
                        'no_nsc': self.safe_string(invoice_record.get("noNSC")),
                        'tanggal_nsc': self.safe_string(invoice_record.get("tanggalNSC")),
                        'total_harga_nsc': self.safe_numeric(invoice_record.get("totalHargaNSC")),
                        'honda_id_sa': self.safe_string(invoice_record.get("hondaIdSA")),
                        'honda_id_mekanik': self.safe_string(invoice_record.get("hondaIdMekanik")),
                        'created_time': self.safe_string(invoice_record.get("createdTime")),
                        'modified_time': self.safe_string(invoice_record.get("modifiedTime")),
                        'fetched_at': datetime.utcnow()
                    }
                    invoice_records.append(invoice_data)

                    # Prepare NJB service records
                    njb_services = invoice_record.get("njb", [])
                    for service_record in njb_services:
                        service_data = {
                            'invoice_no_work_order': invoice_record.get("noWorkOrder"),  # Use for mapping
                            'id_job': self.safe_string(service_record.get("idJob")),
                            'harga_servis': self.safe_numeric(service_record.get("hargaServis")),
                            'promo_id_jasa': self.safe_string(service_record.get("promoIdJasa")),
                            'disc_service_amount': self.safe_numeric(service_record.get("discServiceAmount")),
                            'disc_service_percentage': self.safe_string(service_record.get("discServicePercentage")),
                            'total_harga_servis': self.safe_numeric(service_record.get("totalHargaServis")),
                            'created_time': self.safe_string(service_record.get("createdTime")),
                            'modified_time': self.safe_string(service_record.get("modifiedTime")),
                            'fetched_at': datetime.utcnow()
                        }
                        njb_records.append(service_data)

                    # Prepare NSC part records
                    nsc_parts = invoice_record.get("nsc", [])
                    for part_record in nsc_parts:
                        part_data = {
                            'invoice_no_work_order': invoice_record.get("noWorkOrder"),  # Use for mapping
                            'id_job': self.safe_string(part_record.get("idJob")),
                            'parts_number': self.safe_string(part_record.get("partsNumber")),
                            'kuantitas': self.safe_int(part_record.get("kuantitas")),
                            'harga_parts': self.safe_numeric(part_record.get("hargaParts")),
                            'promo_id_parts': self.safe_string(part_record.get("promoIdParts")),
                            'disc_parts_amount': self.safe_numeric(part_record.get("discPartsAmount")),
                            'disc_parts_percentage': self.safe_string(part_record.get("discPartsPercentage")),
                            'ppn': self.safe_numeric(part_record.get("ppn")),
                            'total_harga_parts': self.safe_numeric(part_record.get("totalHargaParts")),
                            'uang_muka': self.safe_numeric(part_record.get("uangMuka")),
                            'created_time': self.safe_string(part_record.get("createdTime")),
                            'modified_time': self.safe_string(part_record.get("modifiedTime")),
                            'fetched_at': datetime.utcnow()
                        }
                        nsc_records.append(part_data)

                except Exception as e:
                    self.logger.error(f"Error preparing workshop invoice record: {e}")
                    continue

            if not invoice_records:
                self.logger.warning(f"No valid workshop invoice records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert invoice records
            main_processed = self.bulk_upsert(
                db,
                WorkshopInvoiceData,
                invoice_records,
                conflict_columns=['dealer_id', 'no_work_order'],
                batch_size=500
            )

            # Process NJB and NSC records if any
            njb_processed = 0
            nsc_processed = 0

            if njb_records or nsc_records:
                # Get invoice ID mapping for foreign keys
                invoice_query = db.query(
                    WorkshopInvoiceData.id,
                    WorkshopInvoiceData.no_work_order
                ).filter(WorkshopInvoiceData.dealer_id == dealer_id)

                invoice_mapping = {}
                for invoice_id, no_work_order in invoice_query:
                    invoice_mapping[no_work_order] = invoice_id

                # Process NJB records
                if njb_records:
                    # Update NJB records with proper foreign keys
                    for njb_record in njb_records:
                        no_work_order = njb_record.pop('invoice_no_work_order')
                        if no_work_order in invoice_mapping:
                            njb_record['workshop_invoice_data_id'] = invoice_mapping[no_work_order]
                        else:
                            continue  # Skip if parent not found

                    # Bulk upsert NJB records
                    njb_processed = self.bulk_upsert(
                        db,
                        WorkshopInvoiceNJB,
                        njb_records,
                        conflict_columns=['workshop_invoice_data_id', 'id_job'],
                        batch_size=500
                    )

                # Process NSC records
                if nsc_records:
                    # Update NSC records with proper foreign keys
                    for nsc_record in nsc_records:
                        no_work_order = nsc_record.pop('invoice_no_work_order')
                        if no_work_order in invoice_mapping:
                            nsc_record['workshop_invoice_data_id'] = invoice_mapping[no_work_order]
                        else:
                            continue  # Skip if parent not found

                    # Bulk upsert NSC records
                    nsc_processed = self.bulk_upsert(
                        db,
                        WorkshopInvoiceNSC,
                        nsc_records,
                        conflict_columns=['workshop_invoice_data_id', 'id_job', 'parts_number'],
                        batch_size=500
                    )

            db.commit()
            self.logger.info(f"Successfully processed {main_processed} workshop invoices, {njb_processed} NJB services, and {nsc_processed} NSC parts for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error processing workshop invoice records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for workshop invoice data"""
        try:
            # Base query
            query = db.query(WorkshopInvoiceData)
            if dealer_id:
                query = query.filter(WorkshopInvoiceData.dealer_id == dealer_id)
            
            total_invoices = query.count()
            
            # Count services and parts
            service_query = db.query(WorkshopInvoiceNJB)
            part_query = db.query(WorkshopInvoiceNSC)
            
            if dealer_id:
                service_query = service_query.join(WorkshopInvoiceData).filter(
                    WorkshopInvoiceData.dealer_id == dealer_id
                )
                part_query = part_query.join(WorkshopInvoiceData).filter(
                    WorkshopInvoiceData.dealer_id == dealer_id
                )
            
            total_services = service_query.count()
            total_parts = part_query.count()
            
            # Total amounts
            from sqlalchemy import func
            total_amounts = db.query(
                func.sum(WorkshopInvoiceData.total_harga_njb).label('total_njb'),
                func.sum(WorkshopInvoiceData.total_harga_nsc).label('total_nsc')
            )
            if dealer_id:
                total_amounts = total_amounts.filter(WorkshopInvoiceData.dealer_id == dealer_id)
            
            amounts = total_amounts.first()
            
            return {
                "total_invoices": total_invoices,
                "total_services": total_services,
                "total_parts": total_parts,
                "total_njb_amount": float(amounts.total_njb or 0),
                "total_nsc_amount": float(amounts.total_nsc or 0),
                "total_amount": float((amounts.total_njb or 0) + (amounts.total_nsc or 0))
            }
            
        except Exception as e:
            logger.error(f"Error getting workshop invoice summary stats: {e}")
            return {
                "total_invoices": 0,
                "total_services": 0,
                "total_parts": 0,
                "total_njb_amount": 0.0,
                "total_nsc_amount": 0.0,
                "total_amount": 0.0
            }
