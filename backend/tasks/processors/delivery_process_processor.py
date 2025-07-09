"""
Delivery Process Data Processor

This module handles the processing of delivery process data from the BAST API.
It fetches data from the DGI API, processes it, and stores it in the database.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from .base_processor import BaseDataProcessor
from ..api_clients import DeliveryProcessAPIClient
from ..dummy_data_generators import get_dummy_delivery_process_data
from database import DeliveryProcessData, DeliveryProcessDetail, Dealer

logger = logging.getLogger(__name__)


class DeliveryProcessDataProcessor(BaseDataProcessor):
    """Processor for delivery process data from BAST API"""
    
    def __init__(self):
        super().__init__("bast_read")
        self.api_client = DeliveryProcessAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch delivery process data from API or return dummy data"""
        try:
            # Extract optional parameters
            delivery_document_id = kwargs.get('delivery_document_id', '')
            id_spk = kwargs.get('id_spk', '')
            id_customer = kwargs.get('id_customer', '')
            
            logger.info(f"Fetching delivery process data for dealer {dealer.dealer_id}")
            
            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_delivery_process_data(
                    dealer.dealer_id, from_time, to_time, 
                    delivery_document_id, id_spk, id_customer
                )
            
            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time, 
                dealer.api_key, dealer.secret_key,
                delivery_document_id, id_spk, id_customer
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
            
            logger.info(f"Successfully fetched delivery process data: {len(data)} records")
            return api_response
            
        except Exception as e:
            logger.error(f"Error fetching delivery process data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]):
        """Process and store delivery process records using bulk operations"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No delivery process data to process for dealer {dealer_id}")
                return 0

            logger.info(f"Processing {len(data)} delivery process records for dealer {dealer_id}")

            # Prepare bulk data for main records
            delivery_records = []
            detail_records = []

            for delivery_record in data:
                try:
                    # Prepare main delivery record
                    delivery_data = {
                        'dealer_id': dealer_id,
                        'delivery_document_id': delivery_record.get("deliveryDocumentId"),
                        'tanggal_pengiriman': delivery_record.get("tanggalPengiriman"),
                        'id_driver': delivery_record.get("idDriver"),
                        'status_delivery_document': delivery_record.get("statusDeliveryDocument"),
                        'created_time': delivery_record.get("createdTime"),
                        'modified_time': delivery_record.get("modifiedTime"),
                        'fetched_at': datetime.utcnow()
                    }
                    delivery_records.append(delivery_data)

                    # Prepare detail records (will be processed after main records)
                    details = delivery_record.get("detail", [])
                    for detail_record in details:
                        detail_data = {
                            'no_so': detail_record.get("noSO"),
                            'id_spk': detail_record.get("idSPK"),
                            'no_mesin': detail_record.get("noMesin"),
                            'no_rangka': detail_record.get("noRangka"),
                            'id_customer': detail_record.get("idCustomer"),
                            'waktu_pengiriman': detail_record.get("waktuPengiriman"),
                            'checklist_kelengkapan': detail_record.get("checklistKelengkapan"),
                            'lokasi_pengiriman': detail_record.get("lokasiPengiriman"),
                            'latitude': detail_record.get("latitude"),
                            'longitude': detail_record.get("longitude"),
                            'nama_penerima': detail_record.get("namaPenerima"),
                            'no_kontak_penerima': detail_record.get("noKontakPenerima"),
                            'created_time': detail_record.get("createdTime"),
                            'modified_time': detail_record.get("modifiedTime"),
                            # Will need to link to parent after bulk insert
                            'delivery_doc_id': delivery_record.get("deliveryDocumentId")  # Temporary field for linking
                        }
                        detail_records.append(detail_data)

                except Exception as e:
                    logger.error(f"Error preparing delivery record: {e}")
                    continue

            if not delivery_records:
                logger.warning(f"No valid delivery records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert main delivery records
            main_processed = self.bulk_upsert(
                db,
                DeliveryProcessData,
                delivery_records,
                conflict_columns=['dealer_id', 'delivery_document_id'],
                batch_size=500
            )

            # Process detail records if any
            if detail_records:
                # First, get the mapping of delivery document IDs to database IDs
                delivery_doc_ids = [record['delivery_document_id'] for record in delivery_records if record['delivery_document_id']]
                if delivery_doc_ids:
                    delivery_mapping = {}
                    delivery_query = db.query(DeliveryProcessData.id, DeliveryProcessData.delivery_document_id).filter(
                        DeliveryProcessData.dealer_id == dealer_id,
                        DeliveryProcessData.delivery_document_id.in_(delivery_doc_ids)
                    ).all()

                    for delivery_id, doc_id in delivery_query:
                        delivery_mapping[doc_id] = delivery_id

                    # Update detail records with correct foreign keys
                    valid_details = []
                    for detail in detail_records:
                        doc_id = detail.pop('delivery_doc_id', None)
                        if doc_id and doc_id in delivery_mapping:
                            detail['delivery_process_data_id'] = delivery_mapping[doc_id]
                            valid_details.append(detail)

                    if valid_details:
                        # Bulk insert details (no conflict resolution needed as they're child records)
                        for chunk in self.process_in_chunks(valid_details, chunk_size=1000):
                            db.bulk_insert_mappings(DeliveryProcessDetail, chunk)

                        logger.info(f"Processed {len(valid_details)} delivery process details for dealer {dealer_id}")

            db.commit()
            logger.info(f"Successfully processed {main_processed} delivery process records for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing delivery process records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for delivery process data"""
        try:
            # Base query
            query = db.query(DeliveryProcessData)
            if dealer_id:
                query = query.filter(DeliveryProcessData.dealer_id == dealer_id)
            
            total_deliveries = query.count()
            
            # Count delivery details
            detail_query = db.query(DeliveryProcessDetail)
            if dealer_id:
                detail_query = detail_query.join(DeliveryProcessData).filter(
                    DeliveryProcessData.dealer_id == dealer_id
                )
            
            total_details = detail_query.count()
            
            # Status distribution
            from sqlalchemy import func
            status_dist = db.query(
                DeliveryProcessData.status_delivery_document,
                func.count(DeliveryProcessData.id).label('count')
            )
            if dealer_id:
                status_dist = status_dist.filter(DeliveryProcessData.dealer_id == dealer_id)
            
            status_distribution = [
                {"status": row.status_delivery_document or "Unknown", "count": row.count}
                for row in status_dist.group_by(DeliveryProcessData.status_delivery_document).all()
            ]
            
            return {
                "total_deliveries": total_deliveries,
                "total_details": total_details,
                "status_distribution": status_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting delivery process summary stats: {e}")
            return {
                "total_deliveries": 0,
                "total_details": 0,
                "status_distribution": []
            }
