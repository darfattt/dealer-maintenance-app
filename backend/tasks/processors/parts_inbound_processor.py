"""
Parts Inbound data processor - handles Parts Inbound data fetching and processing
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import text

from database import Dealer, PartsInboundData, PartsInboundPO
from ..api_clients import PartsInboundAPIClient
from ..dummy_data_generators import get_dummy_parts_inbound_data, should_use_dummy_data
from .base_processor import BaseDataProcessor


class PartsInboundDataProcessor(BaseDataProcessor):
    """Processor for Parts Inbound data"""
    
    def __init__(self):
        super().__init__("parts_inbound_data")
    
    def fetch_api_data(self, dealer: Dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch Parts Inbound data from API or dummy source"""
        no_po = kwargs.get("no_po", "")
        
        try:
            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy Parts Inbound data for dealer {dealer.dealer_id}")
                return get_dummy_parts_inbound_data(dealer.dealer_id, from_time, to_time, no_po)
            else:
                # Use real API client
                client = PartsInboundAPIClient()
                api_data = client.fetch_data(dealer.dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key, no_po)
                self.logger.info(f"Parts Inbound API call successful for dealer {dealer.dealer_id}")
                return api_data
        except Exception as api_error:
            self.logger.error(f"Parts Inbound API call failed for dealer {dealer.dealer_id}: {api_error}")
            # Return error response instead of dummy data
            return {
                "status": 0,
                "message": f"API call failed: {str(api_error)}",
                "data": [],
                "error_type": "api_error",
                "dealer_id": dealer.dealer_id
            }
    
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process Parts Inbound records and save to database"""
        records_processed = 0
        parts_inbound_records = self.ensure_list_data(api_data.get("data"))

        # Ensure database session is in good state
        try:
            db.execute(text("SELECT 1"))
        except Exception as session_error:
            self.logger.warning(f"Database session issue, attempting to recover: {session_error}")
            # Try to rollback and continue
            try:
                db.rollback()
            except Exception:
                pass
        
        for parts_inbound in parts_inbound_records:
            # Check if Parts Inbound record already exists
            existing_parts_inbound = None
            try:
                existing_parts_inbound = db.query(PartsInboundData).filter(
                    PartsInboundData.dealer_id == dealer_id,
                    PartsInboundData.no_penerimaan == parts_inbound.get("noPenerimaan")
                ).first()
            except Exception as query_error:
                self.logger.warning(f"Error querying existing Parts Inbound record: {query_error}")
                # Continue with creating new record if query fails
                existing_parts_inbound = None
            
            if existing_parts_inbound:
                # Update existing record
                parts_inbound_record = existing_parts_inbound
                parts_inbound_record.modified_time = parts_inbound.get("modifiedTime")
                parts_inbound_record.fetched_at = datetime.utcnow()
            else:
                # Create new record
                parts_inbound_record = PartsInboundData(
                    dealer_id=dealer_id,
                    no_penerimaan=parts_inbound.get("noPenerimaan"),
                    tgl_penerimaan=parts_inbound.get("tglPenerimaan"),
                    no_shipping_list=parts_inbound.get("noShippingList"),
                    created_time=parts_inbound.get("createdTime"),
                    modified_time=parts_inbound.get("modifiedTime")
                )
                db.add(parts_inbound_record)
                # Flush to get the ID for relationships
                db.flush()

            # Handle PO items (only for new records to avoid duplicates)
            if not existing_parts_inbound:
                po_items = self.ensure_list_data(parts_inbound.get("po"))
                
                for po_item in po_items:
                    parts_inbound_po = PartsInboundPO(
                        parts_inbound_data_id=parts_inbound_record.id,
                        no_po=po_item.get("noPO"),
                        jenis_order=po_item.get("jenisOrder"),
                        id_warehouse=po_item.get("idWarehouse"),
                        parts_number=po_item.get("partsNumber"),
                        kuantitas=po_item.get("kuantitas"),
                        uom=po_item.get("uom"),
                        created_time=po_item.get("createdTime"),
                        modified_time=po_item.get("modifiedTime")
                    )
                    db.add(parts_inbound_po)
            
            records_processed += 1
        
        return records_processed
