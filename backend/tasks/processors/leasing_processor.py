"""
Leasing Data Processor
Handles fetching and processing of leasing requirement data from DGI API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

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
        """Fetch leasing data from API with enhanced validation"""
        try:
            # Extract additional parameters
            id_spk = kwargs.get('id_spk', kwargs.get('no_po', ''))  # Use no_po field for idSPK

            self.logger.info(f"Fetching leasing data for dealer {dealer.dealer_id}")
            self.logger.debug(f"Parameters: from_time={from_time}, to_time={to_time}, idSPK={id_spk}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.warning(f"Dealer {dealer.dealer_id} missing API credentials, using dummy data")
                return get_dummy_leasing_data(dealer.dealer_id, from_time, to_time, id_spk)

            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy leasing data for dealer {dealer.dealer_id}")
                return get_dummy_leasing_data(dealer.dealer_id, from_time, to_time, id_spk)

            # Make API call
            api_response = self.api_client.fetch_data(
                dealer_id=dealer.dealer_id,
                from_time=from_time,
                to_time=to_time,
                api_key=dealer.api_key,
                secret_key=dealer.secret_key,
                id_spk=id_spk
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

            self.logger.info(f"Successfully fetched leasing data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching leasing data for dealer {dealer.dealer_id}: {e}")
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store leasing records using bulk operations"""
        try:
            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No leasing data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} leasing records for dealer {dealer_id}")

            # Prepare bulk data for main records
            leasing_records = []

            for record in data:
                try:
                    # Prepare leasing record
                    leasing_data = {
                        'dealer_id': dealer_id,
                        'id_dokumen_pengajuan': record.get('idDokumenPengajuan'),
                        'id_spk': record.get('idSPK'),
                        'jumlah_dp': self.safe_numeric(record.get('jumlahDP')),
                        'tenor': self.safe_int(record.get('tenor')),
                        'jumlah_cicilan': self.safe_numeric(record.get('jumlahCicilan')),
                        'tanggal_pengajuan': record.get('tanggalPengajuan'),
                        'id_finance_company': record.get('idFinanceCompany'),
                        'nama_finance_company': record.get('namaFinanceCompany'),
                        'id_po_finance_company': record.get('idPOFinanceCompany'),
                        'tanggal_pembuatan_po': record.get('tanggalPembuatanPO'),
                        'tanggal_pengiriman_po_finance_company': record.get('tanggalPengirimanPOFinanceCompany'),
                        'created_time': record.get('createdTime'),
                        'modified_time': record.get('modifiedTime'),
                        'fetched_at': datetime.utcnow()
                    }
                    leasing_records.append(leasing_data)

                except Exception as e:
                    self.logger.error(f"Error preparing leasing record: {e}")
                    continue

            if not leasing_records:
                self.logger.warning(f"No valid leasing records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert leasing records
            main_processed = self.bulk_upsert(
                db,
                LeasingData,
                leasing_records,
                conflict_columns=['dealer_id', 'id_dokumen_pengajuan'],
                batch_size=500
            )

            self.logger.info(f"Successfully processed {main_processed} leasing records for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing leasing records for dealer {dealer_id}: {e}")
            raise
    


    
    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for leasing data"""
        try:
            from sqlalchemy import func

            # Base query
            query = db.query(LeasingData)
            if dealer_id:
                query = query.filter(LeasingData.dealer_id == dealer_id)

            total_records = query.count()

            # Records by finance company
            finance_query = db.query(
                LeasingData.nama_finance_company,
                func.count(LeasingData.id).label('count')
            )
            if dealer_id:
                finance_query = finance_query.filter(LeasingData.dealer_id == dealer_id)

            finance_companies = [
                {"name": row.nama_finance_company or "Unknown", "count": row.count}
                for row in finance_query.filter(
                    LeasingData.nama_finance_company.isnot(None)
                ).group_by(LeasingData.nama_finance_company).order_by(
                    func.count(LeasingData.id).desc()
                ).limit(10).all()
            ]

            # Average DP, installment, and tenor
            avg_query = db.query(
                func.avg(LeasingData.jumlah_dp).label('avg_dp'),
                func.avg(LeasingData.jumlah_cicilan).label('avg_cicilan'),
                func.avg(LeasingData.tenor).label('avg_tenor')
            )
            if dealer_id:
                avg_query = avg_query.filter(LeasingData.dealer_id == dealer_id)

            avg_stats = avg_query.filter(
                LeasingData.jumlah_dp.isnot(None),
                LeasingData.jumlah_cicilan.isnot(None),
                LeasingData.tenor.isnot(None)
            ).first()

            return {
                "total_records": total_records,
                "finance_companies": finance_companies,
                "averages": {
                    "dp": float(avg_stats.avg_dp or 0),
                    "cicilan": float(avg_stats.avg_cicilan or 0),
                    "tenor": float(avg_stats.avg_tenor or 0)
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting leasing summary stats: {e}")
            return {
                "total_records": 0,
                "finance_companies": [],
                "averages": {"dp": 0, "cicilan": 0, "tenor": 0}
            }
