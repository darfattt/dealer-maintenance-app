"""
Workshop Invoice Data Processor

This module handles the processing of workshop invoice data from the INV2 API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import WorkshopInvoiceAPIClient
from ..dummy_data_generators import get_dummy_workshop_invoice_data
from database import WorkshopInvoiceData, WorkshopInvoiceNJB, WorkshopInvoiceNSC, Dealer

logger = logging.getLogger(__name__)


class WorkshopInvoiceDataProcessor(BaseDataProcessor):
    """Processor for workshop invoice data from INV2 API"""
    
    def __init__(self):
        super().__init__("inv2_read")
        self.api_client = WorkshopInvoiceAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch workshop invoice data from API or return dummy data"""
        try:
            # Extract optional parameters
            no_work_order = kwargs.get('no_work_order', '')
            
            logger.info(f"Fetching workshop invoice data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
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
            
            logger.info(f"Successfully fetched workshop invoice data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching workshop invoice data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store workshop invoice records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No workshop invoice data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for invoice_record in data:
                try:
                    # Check if invoice already exists
                    no_work_order = invoice_record.get("noWorkOrder")
                    if no_work_order:
                        existing = db.query(WorkshopInvoiceData).filter(
                            WorkshopInvoiceData.dealer_id == dealer_id,
                            WorkshopInvoiceData.no_work_order == no_work_order
                        ).first()
                        
                        if existing:
                            logger.debug(f"Workshop invoice {no_work_order} already exists, skipping")
                            continue
                    
                    # Create workshop invoice data record
                    invoice_data = WorkshopInvoiceData(
                        dealer_id=dealer_id,
                        no_work_order=invoice_record.get("noWorkOrder"),
                        no_njb=invoice_record.get("noNJB"),
                        tanggal_njb=invoice_record.get("tanggalNJB"),
                        total_harga_njb=invoice_record.get("totalHargaNJB"),
                        no_nsc=invoice_record.get("noNSC"),
                        tanggal_nsc=invoice_record.get("tanggalNSC"),
                        total_harga_nsc=invoice_record.get("totalHargaNSC"),
                        honda_id_sa=invoice_record.get("hondaIdSA"),
                        honda_id_mekanik=invoice_record.get("hondaIdMekanik"),
                        created_time=invoice_record.get("createdTime"),
                        modified_time=invoice_record.get("modifiedTime")
                    )
                    
                    db.add(invoice_data)
                    db.flush()  # Get the ID
                    
                    # Process NJB services
                    njb_services = invoice_record.get("njb", [])
                    for service_record in njb_services:
                        service_data = WorkshopInvoiceNJB(
                            workshop_invoice_data_id=invoice_data.id,
                            id_job=service_record.get("idJob"),
                            harga_servis=service_record.get("hargaServis"),
                            promo_id_jasa=service_record.get("promoIdJasa"),
                            disc_service_amount=service_record.get("discServiceAmount"),
                            disc_service_percentage=service_record.get("discServicePercentage"),
                            total_harga_servis=service_record.get("totalHargaServis"),
                            created_time=service_record.get("createdTime"),
                            modified_time=service_record.get("modifiedTime")
                        )
                        db.add(service_data)
                    
                    # Process NSC parts
                    nsc_parts = invoice_record.get("nsc", [])
                    for part_record in nsc_parts:
                        part_data = WorkshopInvoiceNSC(
                            workshop_invoice_data_id=invoice_data.id,
                            id_job=part_record.get("idJob"),
                            parts_number=part_record.get("partsNumber"),
                            kuantitas=part_record.get("kuantitas"),
                            harga_parts=part_record.get("hargaParts"),
                            promo_id_parts=part_record.get("promoIdParts"),
                            disc_parts_amount=part_record.get("discPartsAmount"),
                            disc_parts_percentage=part_record.get("discPartsPercentage"),
                            ppn=part_record.get("ppn"),
                            total_harga_parts=part_record.get("totalHargaParts"),
                            uang_muka=part_record.get("uangMuka"),
                            created_time=part_record.get("createdTime"),
                            modified_time=part_record.get("modifiedTime")
                        )
                        db.add(part_data)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing workshop invoice record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Processed {processed_count} workshop invoice records for dealer {dealer_id}")
            
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing workshop invoice records for dealer {dealer_id}: {e}")
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
