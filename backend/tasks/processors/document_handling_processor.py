"""
Document Handling Data Processor
Handles fetching and processing of document handling data from DGI API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

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
        """
        Fetch document handling data from API or dummy source
        
        Args:
            dealer: Dealer object with credentials
            from_time: Start time for data fetch
            to_time: End time for data fetch
            **kwargs: Additional parameters (id_spk, id_customer)
        
        Returns:
            API response data
        """
        try:
            # Extract additional parameters
            id_spk = kwargs.get('id_spk', kwargs.get('no_po', ''))  # Use no_po field for idSPK
            id_customer = kwargs.get('id_customer', '')
            
            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy data for dealer {dealer.dealer_id}")
                return get_dummy_document_handling_data(dealer.dealer_id, from_time, to_time, id_spk, id_customer)
            else:
                # Use real API client
                self.logger.info(f"Fetching document handling data for dealer {dealer.dealer_id}")
                self.logger.info(f"Parameters: from_time={from_time}, to_time={to_time}, idSPK={id_spk}, idCustomer={id_customer}")
                
                response = self.api_client.fetch_data(
                    dealer_id=dealer.dealer_id,
                    from_time=from_time,
                    to_time=to_time,
                    api_key=dealer.api_key,
                    secret_key=dealer.secret_key,
                    id_spk=id_spk,
                    id_customer=id_customer
                )
                
                self.logger.info(f"Document Handling API call successful for dealer {dealer.dealer_id}")
                return response
                
        except Exception as api_error:
            self.logger.error(f"Document Handling API call failed for dealer {dealer.dealer_id}: {api_error}")
            # Return error response instead of dummy data
            return {
                "status": 0,
                "message": f"API call failed: {str(api_error)}",
                "data": [],
                "error_type": "api_error",
                "dealer_id": dealer.dealer_id
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """
        Process and store document handling records in database
        
        Args:
            db: Database session
            dealer_id: Dealer ID
            api_data: API response data
            
        Returns:
            Number of records processed
        """
        records_processed = 0
        document_records = self.ensure_list_data(api_data.get("data"))

        # Ensure database session is in good state
        try:
            db.execute(text("SELECT 1"))
        except Exception as session_error:
            self.logger.warning(f"Database session issue, attempting to recover: {session_error}")
            try:
                db.rollback()
            except Exception:
                pass
        
        for document in document_records:
            try:
                # Check if document already exists
                existing_document = None
                try:
                    existing_document = db.query(DocumentHandlingData).filter(
                        DocumentHandlingData.dealer_id == dealer_id,
                        DocumentHandlingData.id_so == document.get("idSO")
                    ).first()
                except Exception as query_error:
                    self.logger.warning(f"Error querying existing document: {query_error}")
                    existing_document = None
                
                if existing_document:
                    # Update existing record
                    document_record = existing_document
                    document_record.modified_time = document.get("modifiedTime")
                    document_record.fetched_at = datetime.utcnow()
                else:
                    # Create new record
                    document_record = DocumentHandlingData(
                        dealer_id=dealer_id,
                        id_so=document.get("idSO"),
                        id_spk=document.get("idSPK"),
                        created_time=document.get("createdTime"),
                        modified_time=document.get("modifiedTime")
                    )
                    db.add(document_record)
                    # Flush to get the ID for relationships
                    db.flush()

                # Handle units (only for new records to avoid duplicates)
                if not existing_document:
                    units = self.ensure_list_data(document.get("unit"))
                    for unit in units:
                        document_unit = DocumentHandlingUnit(
                            document_handling_data_id=document_record.id,
                            nomor_rangka=unit.get("nomorRangka"),
                            nomor_faktur_stnk=unit.get("nomorFakturSTNK"),
                            tanggal_pengajuan_stnk_ke_biro=unit.get("tanggalPengajuanSTNKKeBiro"),
                            status_faktur_stnk=unit.get("statusFakturSTNK"),
                            nomor_stnk=unit.get("nomorSTNK"),
                            tanggal_penerimaan_stnk_dari_biro=unit.get("tanggalPenerimaanSTNKDariBiro"),
                            plat_nomor=unit.get("platNomor"),
                            nomor_bpkb=unit.get("nomorBPKB"),
                            tanggal_penerimaan_bpkb_dari_biro=unit.get("tanggalPenerimaanBPKBDariBiro"),
                            tanggal_terima_stnk_oleh_konsumen=unit.get("tanggalTerimaSTNKOlehKonsumen"),
                            tanggal_terima_bpkb_oleh_konsumen=unit.get("tanggalTerimaBPKBOlehKonsumen"),
                            nama_penerima_bpkb=unit.get("namaPenerimaBPKB"),
                            nama_penerima_stnk=unit.get("namaPenerimaSTNK"),
                            jenis_id_penerima_bpkb=unit.get("jenisIdPenerimaBPKB"),
                            jenis_id_penerima_stnk=unit.get("jenisIdPenerimaSTNK"),
                            no_id_penerima_bpkb=unit.get("noIdPenerimaBPKB"),
                            no_id_penerima_stnk=unit.get("noIdPenerimaSTNK"),
                            created_time=unit.get("createdTime"),
                            modified_time=unit.get("modifiedTime")
                        )
                        db.add(document_unit)
                
                records_processed += 1
                
            except Exception as record_error:
                self.logger.error(f"Error processing document record: {record_error}")
                # Continue with next record
                continue
        
        return records_processed
    
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
