"""
Unit Invoice Data Processor

This module handles the processing of unit invoice data from the MDINVH1 API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import UnitInvoiceAPIClient
from ..dummy_data_generators import get_dummy_unit_invoice_data
from database import UnitInvoiceData, UnitInvoiceUnit, Dealer

logger = logging.getLogger(__name__)


class UnitInvoiceDataProcessor(BaseDataProcessor):
    """Processor for unit invoice data from MDINVH1 API"""
    
    def __init__(self):
        super().__init__("mdinvh1_read")
        self.api_client = UnitInvoiceAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch unit invoice data from API or return dummy data"""
        try:
            # Extract optional parameters
            po_id = kwargs.get('po_id', '')
            no_shipping_list = kwargs.get('no_shipping_list', '')
            
            logger.info(f"Fetching unit invoice data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
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
            
            logger.info(f"Successfully fetched unit invoice data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching unit invoice data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store unit invoice records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No unit invoice data to process for dealer {dealer_id}")
                return 0
            
            processed_count = 0
            
            for invoice_record in data:
                try:
                    # Check if invoice already exists
                    no_invoice = invoice_record.get("noInvoice")
                    if no_invoice:
                        existing = db.query(UnitInvoiceData).filter(
                            UnitInvoiceData.dealer_id == dealer_id,
                            UnitInvoiceData.no_invoice == no_invoice
                        ).first()
                        
                        if existing:
                            logger.debug(f"Invoice {no_invoice} already exists, skipping")
                            continue
                    
                    # Create unit invoice data record
                    invoice_data = UnitInvoiceData(
                        dealer_id=dealer_id,
                        no_invoice=invoice_record.get("noInvoice"),
                        tanggal_invoice=invoice_record.get("tanggalInvoice"),
                        tanggal_jatuh_tempo=invoice_record.get("tanggalJatuhTempo"),
                        main_dealer_id=invoice_record.get("mainDealerId"),
                        total_harga_sebelum_diskon=invoice_record.get("totalHargaSebelumDiskon"),
                        total_diskon_per_unit=invoice_record.get("totalDiskonPerUnit"),
                        potongan_per_invoice=invoice_record.get("potonganPerInvoice"),
                        total_ppn=invoice_record.get("totalPPN"),
                        total_harga=invoice_record.get("totalHarga"),
                        created_time=invoice_record.get("createdTime"),
                        modified_time=invoice_record.get("modifiedTime")
                    )
                    
                    db.add(invoice_data)
                    db.flush()  # Get the ID
                    
                    # Process units
                    units = invoice_record.get("unit", [])
                    for unit_record in units:
                        unit_data = UnitInvoiceUnit(
                            unit_invoice_data_id=invoice_data.id,
                            kode_tipe_unit=unit_record.get("kodeTipeUnit"),
                            kode_warna=unit_record.get("kodeWarna"),
                            kuantitas=unit_record.get("kuantitas"),
                            no_mesin=unit_record.get("noMesin"),
                            no_rangka=unit_record.get("noRangka"),
                            harga_satuan_sebelum_diskon=unit_record.get("hargaSatuanSebelumDiskon"),
                            diskon_per_unit=unit_record.get("diskonPerUnit"),
                            po_id=unit_record.get("poId"),
                            created_time=unit_record.get("createdTime"),
                            modified_time=unit_record.get("modifiedTime")
                        )
                        db.add(unit_data)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing unit invoice record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Processed {processed_count} unit invoice records for dealer {dealer_id}")
            
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing unit invoice records for dealer {dealer_id}: {e}")
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
