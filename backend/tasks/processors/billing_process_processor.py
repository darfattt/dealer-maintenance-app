"""
Billing Process Data Processor

This module handles the processing of billing process data from the INV1 API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import BillingProcessAPIClient
from ..dummy_data_generators import get_dummy_billing_process_data
from database import BillingProcessData, Dealer

logger = logging.getLogger(__name__)


class BillingProcessDataProcessor(BaseDataProcessor):
    """Processor for billing process data from INV1 API"""
    
    def __init__(self):
        super().__init__("inv1_read")
        self.api_client = BillingProcessAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch billing process data from API or return dummy data"""
        try:
            # Extract optional parameters
            id_spk = kwargs.get('id_spk', '')
            id_customer = kwargs.get('id_customer', '')
            
            logger.info(f"Fetching billing process data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_billing_process_data(
                    dealer.dealer_id, from_time, to_time, 
                    id_spk, id_customer
                )
            
            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time, 
                dealer.api_key, dealer.secret_key,
                id_spk, id_customer
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
            
            logger.info(f"Successfully fetched billing process data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching billing process data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store billing process records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No billing process data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for invoice_record in data:
                try:
                    # Check if invoice already exists
                    id_invoice = invoice_record.get("idInvoice")
                    if id_invoice:
                        existing = db.query(BillingProcessData).filter(
                            BillingProcessData.dealer_id == dealer_id,
                            BillingProcessData.id_invoice == id_invoice
                        ).first()
                        
                        if existing:
                            logger.debug(f"Invoice {id_invoice} already exists, skipping")
                            continue
                    
                    # Create billing process data record
                    billing_data = BillingProcessData(
                        dealer_id=dealer_id,
                        id_invoice=invoice_record.get("idInvoice"),
                        id_spk=invoice_record.get("idSPK"),
                        id_customer=invoice_record.get("idCustomer"),
                        amount=invoice_record.get("amount"),
                        tipe_pembayaran=invoice_record.get("tipePembayaran"),
                        cara_bayar=invoice_record.get("caraBayar"),
                        status=invoice_record.get("status"),
                        note=invoice_record.get("note"),
                        created_time=invoice_record.get("createdTime"),
                        modified_time=invoice_record.get("modifiedTime")
                    )
                    
                    db.add(billing_data)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing billing record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Processed {processed_count} billing process records for dealer {dealer_id}")
            
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing billing process records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for billing process data"""
        try:
            # Base query
            query = db.query(BillingProcessData)
            if dealer_id:
                query = query.filter(BillingProcessData.dealer_id == dealer_id)
            
            total_invoices = query.count()
            
            # Status distribution
            from sqlalchemy import func
            status_dist = db.query(
                BillingProcessData.status,
                func.count(BillingProcessData.id).label('count')
            )
            if dealer_id:
                status_dist = status_dist.filter(BillingProcessData.dealer_id == dealer_id)
            
            status_distribution = [
                {"status": row.status or "Unknown", "count": row.count}
                for row in status_dist.group_by(BillingProcessData.status).all()
            ]
            
            # Payment type distribution
            payment_type_dist = db.query(
                BillingProcessData.tipe_pembayaran,
                func.count(BillingProcessData.id).label('count')
            )
            if dealer_id:
                payment_type_dist = payment_type_dist.filter(BillingProcessData.dealer_id == dealer_id)
            
            payment_type_distribution = [
                {"payment_type": row.tipe_pembayaran or "Unknown", "count": row.count}
                for row in payment_type_dist.group_by(BillingProcessData.tipe_pembayaran).all()
            ]
            
            # Total amount
            total_amount = db.query(func.sum(BillingProcessData.amount))
            if dealer_id:
                total_amount = total_amount.filter(BillingProcessData.dealer_id == dealer_id)
            
            total_amount_value = total_amount.scalar() or 0
            
            return {
                "total_invoices": total_invoices,
                "total_amount": float(total_amount_value),
                "status_distribution": status_distribution,
                "payment_type_distribution": payment_type_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting billing process summary stats: {e}")
            return {
                "total_invoices": 0,
                "total_amount": 0.0,
                "status_distribution": [],
                "payment_type_distribution": []
            }
