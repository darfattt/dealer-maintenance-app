"""
Parts Inbound data processor - handles Parts Inbound data fetching and processing
"""
from datetime import datetime
from typing import Dict, Any

from database import Dealer, PartsInboundData, PartsInboundPO
from ..api_clients import PartsInboundAPIClient
from ..dummy_data_generators import get_dummy_parts_inbound_data, should_use_dummy_data
from .base_processor import BaseDataProcessor


class PartsInboundDataProcessor(BaseDataProcessor):
    """Processor for Parts Inbound data"""
    
    def __init__(self):
        super().__init__("parts_inbound_data")
    
    def fetch_api_data(self, dealer: Dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch Parts Inbound data from API with enhanced validation"""
        try:
            no_po = kwargs.get("no_po", "")

            self.logger.info(f"Fetching parts inbound data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, no_po={no_po}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_parts_inbound_data(dealer.dealer_id, from_time, to_time, no_po)

            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy Parts Inbound data for dealer {dealer.dealer_id}")
                return get_dummy_parts_inbound_data(dealer.dealer_id, from_time, to_time, no_po)

            # Make API call
            client = PartsInboundAPIClient()
            api_response = client.fetch_data(dealer.dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key, no_po)

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

            self.logger.info(f"Successfully fetched parts inbound data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching parts inbound data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store parts inbound records using bulk operations"""
        try:
            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No parts inbound data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} parts inbound records for dealer {dealer_id}")

            # Prepare bulk data for main records
            inbound_records = []
            po_records = []

            for parts_inbound in data:
                try:
                    # Prepare main parts inbound record
                    inbound_data = {
                        'dealer_id': dealer_id,
                        'no_penerimaan': parts_inbound.get("noPenerimaan"),
                        'tgl_penerimaan': parts_inbound.get("tglPenerimaan"),
                        'no_shipping_list': parts_inbound.get("noShippingList"),
                        'created_time': parts_inbound.get("createdTime"),
                        'modified_time': parts_inbound.get("modifiedTime"),
                        'fetched_at': datetime.utcnow()
                    }
                    inbound_records.append(inbound_data)

                    # Prepare PO records (will be processed after main records)
                    po_items = self.ensure_list_data(parts_inbound.get("po"))
                    for po_item in po_items:
                        po_data = {
                            'no_po': po_item.get("noPO"),
                            'jenis_order': po_item.get("jenisOrder"),
                            'id_warehouse': po_item.get("idWarehouse"),
                            'parts_number': po_item.get("partsNumber"),
                            'kuantitas': po_item.get("kuantitas"),
                            'uom': po_item.get("uom"),
                            'created_time': po_item.get("createdTime"),
                            'modified_time': po_item.get("modifiedTime"),
                            # Will need to link to parent after bulk insert
                            'penerimaan_no': parts_inbound.get("noPenerimaan")  # Temporary field for linking
                        }
                        po_records.append(po_data)

                except Exception as e:
                    self.logger.error(f"Error preparing parts inbound record: {e}")
                    continue

            if not inbound_records:
                self.logger.warning(f"No valid parts inbound records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert main inbound records
            main_processed = self.bulk_upsert(
                db,
                PartsInboundData,
                inbound_records,
                conflict_columns=['dealer_id', 'no_penerimaan'],
                batch_size=500
            )

            # Process PO records if any
            if po_records:
                # First, get the mapping of penerimaan numbers to database IDs
                penerimaan_nos = [record['no_penerimaan'] for record in inbound_records if record['no_penerimaan']]
                if penerimaan_nos:
                    inbound_mapping = {}
                    inbound_query = db.query(PartsInboundData.id, PartsInboundData.no_penerimaan).filter(
                        PartsInboundData.dealer_id == dealer_id,
                        PartsInboundData.no_penerimaan.in_(penerimaan_nos)
                    ).all()

                    for inbound_id, penerimaan_no in inbound_query:
                        inbound_mapping[penerimaan_no] = inbound_id

                    # Update PO records with correct foreign keys
                    valid_pos = []
                    for po in po_records:
                        penerimaan_no = po.pop('penerimaan_no', None)
                        if penerimaan_no and penerimaan_no in inbound_mapping:
                            po['parts_inbound_data_id'] = inbound_mapping[penerimaan_no]
                            valid_pos.append(po)

                    if valid_pos:
                        # Bulk insert POs (no conflict resolution needed as they're child records)
                        for chunk in self.process_in_chunks(valid_pos, chunk_size=1000):
                            db.bulk_insert_mappings(PartsInboundPO, chunk)

                        self.logger.info(f"Processed {len(valid_pos)} parts inbound PO items for dealer {dealer_id}")

            db.commit()
            self.logger.info(f"Successfully processed {main_processed} parts inbound records for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error processing parts inbound records for dealer {dealer_id}: {e}")
            raise

    def get_summary_stats(self, db, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for parts inbound data"""
        try:
            from sqlalchemy import func

            # Base query
            query = db.query(PartsInboundData)
            if dealer_id:
                query = query.filter(PartsInboundData.dealer_id == dealer_id)

            total_inbound = query.count()

            # Count PO items
            po_query = db.query(PartsInboundPO)
            if dealer_id:
                po_query = po_query.join(PartsInboundData).filter(PartsInboundData.dealer_id == dealer_id)

            total_po_items = po_query.count()

            # Total quantities
            total_quantities = db.query(
                func.sum(PartsInboundPO.kuantitas).label('total_quantity')
            )
            if dealer_id:
                total_quantities = total_quantities.join(PartsInboundData).filter(
                    PartsInboundData.dealer_id == dealer_id
                )

            quantities = total_quantities.first()

            # Order type distribution
            order_dist = db.query(
                PartsInboundPO.jenis_order,
                func.count(PartsInboundPO.id).label('count')
            )
            if dealer_id:
                order_dist = order_dist.join(PartsInboundData).filter(PartsInboundData.dealer_id == dealer_id)

            order_distribution = [
                {"order_type": row.jenis_order or "Unknown", "count": row.count}
                for row in order_dist.group_by(PartsInboundPO.jenis_order).limit(10).all()
            ]

            # Top parts by quantity
            top_parts = db.query(
                PartsInboundPO.parts_number,
                func.sum(PartsInboundPO.kuantitas).label('total_qty')
            )
            if dealer_id:
                top_parts = top_parts.join(PartsInboundData).filter(PartsInboundData.dealer_id == dealer_id)

            top_parts_list = [
                {"parts_number": row.parts_number or "Unknown", "total_quantity": int(row.total_qty or 0)}
                for row in top_parts.group_by(PartsInboundPO.parts_number).order_by(func.sum(PartsInboundPO.kuantitas).desc()).limit(10).all()
            ]

            return {
                "total_inbound": total_inbound,
                "total_po_items": total_po_items,
                "total_quantity": int(quantities.total_quantity or 0),
                "order_distribution": order_distribution,
                "top_parts": top_parts_list
            }

        except Exception as e:
            self.logger.error(f"Error getting parts inbound summary stats: {e}")
            return {
                "total_inbound": 0,
                "total_po_items": 0,
                "total_quantity": 0,
                "order_distribution": [],
                "top_parts": []
            }
