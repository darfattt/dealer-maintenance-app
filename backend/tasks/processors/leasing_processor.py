"""
Leasing Data Processor
Handles fetching and processing of leasing requirement data from DGI API
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from .base_processor import BaseDataProcessor
from database import LeasingData
from tasks.api_clients import LeasingAPIClient
from tasks.dummy_data_generators import should_use_dummy_data, get_dummy_leasing_data

logger = logging.getLogger(__name__)


class LeasingDataProcessor(BaseDataProcessor):
    """Processor for leasing requirement data"""

    def __init__(self):
        super().__init__("leasing")
        self.api_client = LeasingAPIClient()

    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch leasing data from API or dummy source

        Args:
            dealer: Dealer object with credentials
            from_time: Start time for data fetch
            to_time: End time for data fetch
            **kwargs: Additional parameters (id_spk)

        Returns:
            API response data
        """
        try:
            # Extract additional parameters
            id_spk = kwargs.get('id_spk', kwargs.get('no_po', ''))  # Use no_po field for idSPK

            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy data for dealer {dealer.dealer_id}")
                return get_dummy_leasing_data(dealer.dealer_id, from_time, to_time, id_spk)
            else:
                # Use real API client
                self.logger.info(f"Fetching leasing data for dealer {dealer.dealer_id}")
                self.logger.info(f"Parameters: from_time={from_time}, to_time={to_time}, idSPK={id_spk}")

                response = self.api_client.fetch_data(
                    dealer_id=dealer.dealer_id,
                    from_time=from_time,
                    to_time=to_time,
                    api_key=dealer.api_key,
                    secret_key=dealer.secret_key,
                    id_spk=id_spk
                )

                self.logger.info(f"Leasing API call successful for dealer {dealer.dealer_id}")
                return response

        except Exception as api_error:
            self.logger.error(f"Leasing API call failed for dealer {dealer.dealer_id}: {api_error}")
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
        Process and store leasing records in database
        
        Args:
            db: Database session
            dealer_id: Dealer ID
            api_data: API response data
        
        Returns:
            Number of records processed
        """
        try:
            if not api_data or api_data.get('status') != 1:
                self.logger.warning("No valid data to process")
                return 0
            
            records = api_data.get('data', [])
            if not records:
                self.logger.info("No leasing records found")
                return 0
            
            processed_count = 0
            
            for record in records:
                try:
                    # Check if record already exists
                    existing_record = db.query(LeasingData).filter(
                        LeasingData.dealer_id == dealer_id,
                        LeasingData.id_dokumen_pengajuan == record.get('idDokumenPengajuan')
                    ).first()
                    
                    if existing_record:
                        # Update existing record
                        self._update_leasing_record(existing_record, record)
                        self.logger.debug(f"Updated existing leasing record: {record.get('idDokumenPengajuan')}")
                    else:
                        # Create new record
                        leasing_record = self._create_leasing_record(dealer_id, record)
                        db.add(leasing_record)
                        self.logger.debug(f"Created new leasing record: {record.get('idDokumenPengajuan')}")
                    
                    processed_count += 1
                    
                except Exception as record_error:
                    self.logger.error(f"Error processing leasing record {record.get('idDokumenPengajuan', 'unknown')}: {record_error}")
                    continue
            
            # Commit all changes
            db.flush()
            self.logger.info(f"Successfully processed {processed_count} leasing records")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Error processing leasing records: {e}")
            raise
    
    def _create_leasing_record(self, dealer_id: str, record: Dict[str, Any]) -> LeasingData:
        """Create a new LeasingData record from API data"""
        return LeasingData(
            dealer_id=dealer_id,
            id_dokumen_pengajuan=record.get('idDokumenPengajuan'),
            id_spk=record.get('idSPK'),
            jumlah_dp=self._safe_decimal(record.get('jumlahDP')),
            tenor=self._safe_int(record.get('tenor')),
            jumlah_cicilan=self._safe_decimal(record.get('jumlahCicilan')),
            tanggal_pengajuan=record.get('tanggalPengajuan'),
            id_finance_company=record.get('idFinanceCompany'),
            nama_finance_company=record.get('namaFinanceCompany'),
            id_po_finance_company=record.get('idPOFinanceCompany'),
            tanggal_pembuatan_po=record.get('tanggalPembuatanPO'),
            tanggal_pengiriman_po_finance_company=record.get('tanggalPengirimanPOFinanceCompany'),
            created_time=record.get('createdTime'),
            modified_time=record.get('modifiedTime')
        )
    
    def _update_leasing_record(self, existing_record: LeasingData, new_data: Dict[str, Any]):
        """Update existing LeasingData record with new data"""
        existing_record.id_spk = new_data.get('idSPK')
        existing_record.jumlah_dp = self._safe_decimal(new_data.get('jumlahDP'))
        existing_record.tenor = self._safe_int(new_data.get('tenor'))
        existing_record.jumlah_cicilan = self._safe_decimal(new_data.get('jumlahCicilan'))
        existing_record.tanggal_pengajuan = new_data.get('tanggalPengajuan')
        existing_record.id_finance_company = new_data.get('idFinanceCompany')
        existing_record.nama_finance_company = new_data.get('namaFinanceCompany')
        existing_record.id_po_finance_company = new_data.get('idPOFinanceCompany')
        existing_record.tanggal_pembuatan_po = new_data.get('tanggalPembuatanPO')
        existing_record.tanggal_pengiriman_po_finance_company = new_data.get('tanggalPengirimanPOFinanceCompany')
        existing_record.created_time = new_data.get('createdTime')
        existing_record.modified_time = new_data.get('modifiedTime')
        existing_record.fetched_at = datetime.utcnow()
    
    def _safe_decimal(self, value) -> Optional[float]:
        """Safely convert value to decimal/float"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def get_summary_stats(self, db: Session, dealer_id: str) -> Dict[str, Any]:
        """Get summary statistics for leasing data"""
        try:
            # Total records
            total_records = db.query(LeasingData).filter(
                LeasingData.dealer_id == dealer_id
            ).count()
            
            # Records by finance company
            finance_companies = db.execute(text("""
                SELECT nama_finance_company, COUNT(*) as count
                FROM leasing_data 
                WHERE dealer_id = :dealer_id 
                AND nama_finance_company IS NOT NULL
                GROUP BY nama_finance_company
                ORDER BY count DESC
                LIMIT 10
            """), {"dealer_id": dealer_id}).fetchall()
            
            # Average DP and installment
            avg_stats = db.execute(text("""
                SELECT 
                    AVG(jumlah_dp) as avg_dp,
                    AVG(jumlah_cicilan) as avg_cicilan,
                    AVG(tenor) as avg_tenor
                FROM leasing_data 
                WHERE dealer_id = :dealer_id
                AND jumlah_dp IS NOT NULL
                AND jumlah_cicilan IS NOT NULL
                AND tenor IS NOT NULL
            """), {"dealer_id": dealer_id}).fetchone()
            
            return {
                "total_records": total_records,
                "finance_companies": [{"name": row[0], "count": row[1]} for row in finance_companies],
                "averages": {
                    "dp": float(avg_stats[0]) if avg_stats and avg_stats[0] else 0,
                    "cicilan": float(avg_stats[1]) if avg_stats and avg_stats[1] else 0,
                    "tenor": float(avg_stats[2]) if avg_stats and avg_stats[2] else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting leasing summary stats: {e}")
            return {
                "total_records": 0,
                "finance_companies": [],
                "averages": {"dp": 0, "cicilan": 0, "tenor": 0}
            }
