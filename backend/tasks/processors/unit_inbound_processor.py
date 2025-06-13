"""
Unit Inbound Data Processor
Handles fetching, processing, and storing unit inbound data from purchase orders
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import UnitInboundAPIClient
from ..dummy_data_generators import get_dummy_unit_inbound_data
from database import UnitInboundData, UnitInboundUnit, Dealer

logger = logging.getLogger(__name__)


class UnitInboundDataProcessor(BaseDataProcessor):
    """Processor for unit inbound data from purchase orders"""
    
    def __init__(self):
        super().__init__("uinb_read")
        self.api_client = UnitInboundAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch unit inbound data from DGI API
        
        Args:
            dealer: Dealer object with API credentials
            from_time: Start time for data fetch
            to_time: End time for data fetch
            **kwargs: Optional parameters (po_id, no_shipping_list)
        
        Returns:
            API response data or error information
        """
        try:
            # Extract optional parameters
            po_id = kwargs.get('po_id', '')
            no_shipping_list = kwargs.get('no_shipping_list', '')
            
            logger.info(f"Fetching unit inbound data for dealer {dealer.dealer_id}")
            logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, po_id={po_id}, no_shipping_list={no_shipping_list}")
            logger.info(f"api key: {dealer.api_key}, secret key: {dealer.secret_key} for dealer {dealer.dealer_id}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.warning(f"Dealer {dealer.dealer_id} missing API credentials")
                return get_dummy_unit_inbound_data(dealer.dealer_id, from_time, to_time, po_id, no_shipping_list)
            
            # Make API call
            api_response = self.api_client.fetch_data(
                dealer_id=dealer.dealer_id,
                from_time=from_time,
                to_time=to_time,
                api_key=dealer.api_key,
                secret_key=dealer.secret_key,
                po_id=po_id,
                no_shipping_list=no_shipping_list
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

            logger.info(f"Successfully fetched unit inbound data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching unit inbound data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """
        Process and store unit inbound records in database
        
        Args:
            db: Database session
            dealer_id: Dealer ID
            api_data: API response data
        
        Returns:
            Number of records processed
        """
        try:
            if api_data.get("status") != 1:
                logger.warning(f"Skipping processing due to API error: {api_data.get('message')}")
                return 0
            
            records = api_data.get("data", [])
            if not records:
                logger.info("No unit inbound records to process")
                return 0
            
            processed_count = 0
            
            for record in records:
                try:
                    # Check for duplicate by shipping list number
                    no_shipping_list = record.get("noShippingList", "")
                    if no_shipping_list:
                        existing = db.query(UnitInboundData).filter(
                            UnitInboundData.dealer_id == dealer_id,
                            UnitInboundData.no_shipping_list == no_shipping_list
                        ).first()
                        
                        if existing:
                            logger.debug(f"Skipping duplicate shipping list: {no_shipping_list}")
                            continue
                    
                    # Create main unit inbound record
                    unit_inbound_data = UnitInboundData(
                        dealer_id=dealer_id,
                        no_shipping_list=record.get("noShippingList"),
                        tanggal_terima=record.get("tanggalTerima"),
                        main_dealer_id=record.get("mainDealerId"),
                        no_invoice=record.get("noInvoice"),
                        status_shipping_list=record.get("statusShippingList"),
                        created_time=record.get("createdTime"),
                        modified_time=record.get("modifiedTime"),
                        fetched_at=datetime.utcnow()
                    )
                    
                    db.add(unit_inbound_data)
                    db.flush()  # Get the ID for relationships
                    
                    # Process unit details
                    units = record.get("unit", [])
                    for unit_data in units:
                        unit = UnitInboundUnit(
                            unit_inbound_data_id=unit_inbound_data.id,
                            kode_tipe_unit=unit_data.get("kodeTipeUnit"),
                            kode_warna=unit_data.get("kodeWarna"),
                            kuantitas_terkirim=unit_data.get("kuantitasTerkirim"),
                            kuantitas_diterima=unit_data.get("kuantitasDiterima"),
                            no_mesin=unit_data.get("noMesin"),
                            no_rangka=unit_data.get("noRangka"),
                            status_rfs=unit_data.get("statusRFS"),
                            po_id=unit_data.get("poId"),
                            kelengkapan_unit=unit_data.get("kelengkapanUnit"),
                            no_goods_receipt=unit_data.get("noGoodsReceipt"),
                            doc_nrfs_id=unit_data.get("docNRFSId"),
                            created_time=unit_data.get("createdTime"),
                            modified_time=unit_data.get("modifiedTime")
                        )
                        db.add(unit)
                    
                    processed_count += 1
                    logger.debug(f"Processed unit inbound record: {no_shipping_list} with {len(units)} units")
                    
                except Exception as e:
                    logger.error(f"Error processing individual unit inbound record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Successfully processed {processed_count} unit inbound records for dealer {dealer_id}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing unit inbound records for dealer {dealer_id}: {e}")
            db.rollback()
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """
        Get summary statistics for unit inbound data
        
        Args:
            db: Database session
            dealer_id: Optional dealer ID filter
        
        Returns:
            Summary statistics
        """
        try:
            # Base query
            query = db.query(UnitInboundData)
            if dealer_id:
                query = query.filter(UnitInboundData.dealer_id == dealer_id)
            
            # Get counts
            total_shipments = query.count()
            
            # Get unit counts
            unit_query = db.query(UnitInboundUnit)
            if dealer_id:
                unit_query = unit_query.join(UnitInboundData).filter(UnitInboundData.dealer_id == dealer_id)
            
            total_units = unit_query.count()
            
            # Status distribution
            from sqlalchemy import func
            status_dist = db.query(
                UnitInboundData.status_shipping_list,
                func.count(UnitInboundData.id).label('count')
            )
            if dealer_id:
                status_dist = status_dist.filter(UnitInboundData.dealer_id == dealer_id)

            status_distribution = [
                {"status": row.status_shipping_list or "Unknown", "count": row.count}
                for row in status_dist.group_by(UnitInboundData.status_shipping_list).all()
            ]

            # RFS status distribution
            rfs_dist = db.query(
                UnitInboundUnit.status_rfs,
                func.count(UnitInboundUnit.id).label('count')
            )
            if dealer_id:
                rfs_dist = rfs_dist.join(UnitInboundData).filter(UnitInboundData.dealer_id == dealer_id)

            rfs_distribution = [
                {"status": row.status_rfs or "Unknown", "count": row.count}
                for row in rfs_dist.group_by(UnitInboundUnit.status_rfs).all()
            ]
            
            return {
                "total_shipments": total_shipments,
                "total_units": total_units,
                "status_distribution": status_distribution,
                "rfs_distribution": rfs_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting unit inbound summary stats: {e}")
            return {
                "total_shipments": 0,
                "total_units": 0,
                "status_distribution": [],
                "rfs_distribution": []
            }
