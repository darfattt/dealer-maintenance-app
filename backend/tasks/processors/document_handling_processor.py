"""
Document Handling Data Processor
Handles fetching and processing of document handling data from DGI API
"""

import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from .base_processor import BaseDataProcessor
from database import DocumentHandlingData, DocumentHandlingUnit
from tasks.api_clients import DocumentHandlingAPIClient
from tasks.dummy_data_generators import should_use_dummy_data, get_dummy_document_handling_data

logger = logging.getLogger(__name__)


class DocumentHandlingDataProcessor(BaseDataProcessor):
    """Processor for document handling data"""
    
    def __init__(self):
        super().__init__("doch_read")
        self.api_client = DocumentHandlingAPIClient()
    
    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch document handling data from API with enhanced validation"""
        try:
            # Extract additional parameters
            id_spk = kwargs.get('id_spk', kwargs.get('no_po', ''))  # Use no_po field for idSPK
            id_customer = kwargs.get('id_customer', '')

            self.logger.info(f"Fetching document handling data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, idSPK={id_spk}, idCustomer={id_customer}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_document_handling_data(dealer.dealer_id, from_time, to_time, id_spk, id_customer)

            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy document handling data for dealer {dealer.dealer_id}")
                return get_dummy_document_handling_data(dealer.dealer_id, from_time, to_time, id_spk, id_customer)

            # Make API call
            api_response = self.api_client.fetch_data(
                dealer_id=dealer.dealer_id,
                from_time=from_time,
                to_time=to_time,
                api_key=dealer.api_key,
                secret_key=dealer.secret_key,
                id_spk=id_spk,
                id_customer=id_customer
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

            self.logger.info(f"Successfully fetched document handling data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching document handling data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store document handling records using bulk operations"""
        try:
            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No document handling data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} document handling records for dealer {dealer_id}")

            # Prepare bulk data for main records
            document_records = []
            unit_records = []

            for document in data:
                try:
                    # Prepare document record
                    document_data = {
                        'dealer_id': dealer_id,
                        'id_so': document.get('idSO'),
                        'id_spk': document.get('idSPK'),
                        'created_time': document.get('createdTime'),
                        'modified_time': document.get('modifiedTime'),
                        'fetched_at': datetime.utcnow()
                    }
                    document_records.append(document_data)

                    # Prepare unit records for this document
                    units = self.ensure_list_data(document.get("unit"))
                    for unit in units:
                        unit_data = {
                            'document_id_so': document.get('idSO'),  # Use for mapping
                            'nomor_rangka': unit.get("nomorRangka"),
                            'nomor_faktur_stnk': unit.get("nomorFakturSTNK"),
                            'tanggal_pengajuan_stnk_ke_biro': unit.get("tanggalPengajuanSTNKKeBiro"),
                            'status_faktur_stnk': unit.get("statusFakturSTNK"),
                            'nomor_stnk': unit.get("nomorSTNK"),
                            'tanggal_penerimaan_stnk_dari_biro': unit.get("tanggalPenerimaanSTNKDariBiro"),
                            'plat_nomor': unit.get("platNomor"),
                            'nomor_bpkb': unit.get("nomorBPKB"),
                            'tanggal_penerimaan_bpkb_dari_biro': unit.get("tanggalPenerimaanBPKBDariBiro"),
                            'tanggal_terima_stnk_oleh_konsumen': unit.get("tanggalTerimaSTNKOlehKonsumen"),
                            'tanggal_terima_bpkb_oleh_konsumen': unit.get("tanggalTerimaBPKBOlehKonsumen"),
                            'nama_penerima_bpkb': unit.get("namaPenerimaBPKB"),
                            'nama_penerima_stnk': unit.get("namaPenerimaSTNK"),
                            'jenis_id_penerima_bpkb': unit.get("jenisIdPenerimaBPKB"),
                            'jenis_id_penerima_stnk': unit.get("jenisIdPenerimaSTNK"),
                            'no_id_penerima_bpkb': unit.get("noIdPenerimaBPKB"),
                            'no_id_penerima_stnk': unit.get("noIdPenerimaSTNK"),
                            'created_time': unit.get("createdTime"),
                            'modified_time': unit.get("modifiedTime"),
                            'fetched_at': datetime.utcnow()
                        }
                        unit_records.append(unit_data)

                except Exception as e:
                    self.logger.error(f"Error preparing document handling record: {e}")
                    continue

            if not document_records:
                self.logger.warning(f"No valid document handling records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert document records
            main_processed = self.bulk_upsert(
                db,
                DocumentHandlingData,
                document_records,
                conflict_columns=['dealer_id', 'id_so'],
                batch_size=500
            )

            # Process unit records if any
            unit_processed = 0
            if unit_records:
                # Get document ID mapping for foreign keys
                document_query = db.query(
                    DocumentHandlingData.id,
                    DocumentHandlingData.id_so
                ).filter(DocumentHandlingData.dealer_id == dealer_id)

                document_mapping = {}
                for doc_id, id_so in document_query:
                    document_mapping[id_so] = doc_id

                # Update unit records with proper foreign keys
                for unit_record in unit_records:
                    id_so = unit_record.pop('document_id_so')
                    if id_so in document_mapping:
                        unit_record['document_handling_data_id'] = document_mapping[id_so]
                    else:
                        continue  # Skip if parent not found

                # Bulk upsert unit records
                unit_processed = self.bulk_upsert(
                    db,
                    DocumentHandlingUnit,
                    unit_records,
                    conflict_columns=['document_handling_data_id', 'nomor_rangka'],
                    batch_size=500
                )

            self.logger.info(f"Successfully processed {main_processed} document handling records and {unit_processed} units for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing document handling records for dealer {dealer_id}: {e}")
            raise
    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for document handling data"""
        try:
            query = db.query(DocumentHandlingData)
            if dealer_id:
                query = query.filter(DocumentHandlingData.dealer_id == dealer_id)
            
            total_documents = query.count()
            
            # Get unit statistics
            unit_query = db.query(DocumentHandlingUnit).join(DocumentHandlingData)
            if dealer_id:
                unit_query = unit_query.filter(DocumentHandlingData.dealer_id == dealer_id)
            
            total_units = unit_query.count()
            
            # Get status distribution
            status_stats = {}
            try:
                status_query = unit_query.filter(DocumentHandlingUnit.status_faktur_stnk.isnot(None))
                for status, count in status_query.with_entities(
                    DocumentHandlingUnit.status_faktur_stnk,
                    db.func.count(DocumentHandlingUnit.id)
                ).group_by(DocumentHandlingUnit.status_faktur_stnk).all():
                    status_stats[status] = count
            except Exception as status_error:
                self.logger.warning(f"Error getting status statistics: {status_error}")
                status_stats = {}
            
            return {
                "total_documents": total_documents,
                "total_units": total_units,
                "status_distribution": status_stats,
                "dealer_id": dealer_id
            }
            
        except Exception as e:
            self.logger.error(f"Error getting summary stats: {e}")
            return {
                "total_documents": 0,
                "total_units": 0,
                "status_distribution": {},
                "dealer_id": dealer_id,
                "error": str(e)
            }
