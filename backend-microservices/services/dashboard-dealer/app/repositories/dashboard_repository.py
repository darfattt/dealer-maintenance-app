"""
Repository for dashboard data operations
"""

import os
import sys
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.logger import setup_logger
from app.models.unit_inbound import UnitInboundData
from app.models.billing_process import BillingProcessData
from app.models.delivery_process import DeliveryProcessData, DeliveryProcessDetail
from app.models.prospect_data import ProspectData
from app.models.spk_dealing_process import SPKDealingProcessData, SPKDealingProcessUnit
from app.models.leasing_data import LeasingData
from app.models.document_handling import DocumentHandlingData, DocumentHandlingUnit
from app.schemas.dashboard import UnitInboundStatusItem, PaymentTypeItem, DeliveryProcessStatusItem, ProspectFollowUpItem, SPKStatusItem, TopLeasingItem, StatusProspectItem, MetodeFollowUpItem, SumberProspectItem, SebaranProspectItem, ProspectDataTableItem, TopDealingUnitItem, TopDriverItem, DeliveryLocationItem, DeliveryDataHistoryItem, SPKDealingProcessDataItem
from app.utils.status_mapper import UnitInboundStatusMapper

logger = setup_logger(__name__)


class DashboardRepository:
    """Repository for dashboard analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_unit_inbound_status_counts(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> List[UnitInboundStatusItem]:
        """
        Get count of unit inbound data grouped by status_shipping_list
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of UnitInboundStatusItem with status and count
        """
        try:
            logger.info(f"Querying unit inbound data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build the query with flexible date filtering to handle both formats
            # Format 1: YYYY-MM-DD (test data)
            # Format 2: DD/MM/YYYY (real API data)

            # Use a safer approach with CASE statements to avoid date parsing errors
            query = self.db.query(
                UnitInboundData.status_shipping_list,
                func.count(UnitInboundData.id).label('count')
            ).filter(
                and_(
                    UnitInboundData.dealer_id == dealer_id,
                    # Use regex to detect format and handle accordingly
                    or_(
                        # Handle YYYY-MM-DD format (contains 4 digits at start)
                        and_(
                            UnitInboundData.tanggal_terima.op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                            UnitInboundData.tanggal_terima >= date_from,
                            UnitInboundData.tanggal_terima <= date_to
                        ),
                        # Handle DD/MM/YYYY format (contains / separators)
                        and_(
                            UnitInboundData.tanggal_terima.op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                            func.to_date(UnitInboundData.tanggal_terima, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(UnitInboundData.tanggal_terima, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(UnitInboundData.status_shipping_list)

            # Execute query
            results = query.all()
            logger.info(f"Found {len(results)} different statuses")

            # Convert to schema objects with status mapping
            status_items = []
            for status, count in results:
                status_items.append(UnitInboundStatusItem(
                    status_shipping_list=status,
                    status_label=UnitInboundStatusMapper.get_mapped_status(status),
                    count=count
                ))

            return status_items
            
        except Exception as e:
            raise Exception(f"Error getting unit inbound status counts: {str(e)}")
    
    def get_total_unit_inbound_records(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> int:
        """
        Get total count of unit inbound records for the given filters
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of records
        """
        try:
            total = self.db.query(func.count(UnitInboundData.id)).filter(
                and_(
                    UnitInboundData.dealer_id == dealer_id,
                    # Use regex to detect format and handle accordingly
                    or_(
                        # Handle YYYY-MM-DD format (contains 4 digits at start)
                        and_(
                            UnitInboundData.tanggal_terima.op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                            UnitInboundData.tanggal_terima >= date_from,
                            UnitInboundData.tanggal_terima <= date_to
                        ),
                        # Handle DD/MM/YYYY format (contains / separators)
                        and_(
                            UnitInboundData.tanggal_terima.op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                            func.to_date(UnitInboundData.tanggal_terima, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(UnitInboundData.tanggal_terima, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total unit inbound records: {str(e)}")

    def get_payment_type_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[PaymentTypeItem]:
        """
        Get count and sum of billing process data grouped by tipe_pembayaran

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            List of PaymentTypeItem with payment type, count, and total amount
        """
        try:
            logger.info(f"Querying billing process data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build the query with flexible date filtering to handle both formats
            # Format 1: YYYY-MM-DD (test data)
            # Format 2: DD/MM/YYYY (real API data)
            query = self.db.query(
                BillingProcessData.tipe_pembayaran,
                func.count(BillingProcessData.id).label('count'),
                func.sum(BillingProcessData.amount).label('total_amount')
            ).filter(
                and_(
                    BillingProcessData.dealer_id == dealer_id,
                    # Use regex to detect format and handle accordingly
                    or_(
                        # Handle YYYY-MM-DD format (contains 4 digits at start)
                        and_(
                            BillingProcessData.created_time.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            BillingProcessData.created_time >= date_from,
                            BillingProcessData.created_time <= date_to + ' 23:59:59'
                        ),
                        # Handle DD/MM/YYYY format (contains / separators)
                        and_(
                            BillingProcessData.created_time.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(BillingProcessData.created_time, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(BillingProcessData.created_time, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(BillingProcessData.tipe_pembayaran)

            # Execute query
            results = query.all()
            logger.info(f"Found {len(results)} different payment types")

            # Convert to schema objects
            payment_items = []
            for tipe_pembayaran, count, total_amount in results:
                payment_items.append(PaymentTypeItem(
                    tipe_pembayaran=tipe_pembayaran,
                    count=count,
                    total_amount=total_amount
                ))

            return payment_items

        except Exception as e:
            raise Exception(f"Error getting payment type statistics: {str(e)}")

    def get_total_billing_process_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of billing process records for the given filters

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Total number of records
        """
        try:
            total = self.db.query(func.count(BillingProcessData.id)).filter(
                and_(
                    BillingProcessData.dealer_id == dealer_id,
                    # Use regex to detect format and handle accordingly
                    or_(
                        # Handle YYYY-MM-DD format (contains 4 digits at start)
                        and_(
                            BillingProcessData.created_time.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            BillingProcessData.created_time >= date_from,
                            BillingProcessData.created_time <= date_to + ' 23:59:59'
                        ),
                        # Handle DD/MM/YYYY format (contains / separators)
                        and_(
                            BillingProcessData.created_time.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(BillingProcessData.created_time, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(BillingProcessData.created_time, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total billing process records: {str(e)}")

    def get_total_billing_amount(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ):
        """
        Get total amount of billing process records for the given filters

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Total amount across all records
        """
        try:
            total = self.db.query(func.sum(BillingProcessData.amount)).filter(
                and_(
                    BillingProcessData.dealer_id == dealer_id,
                    # Use regex to detect format and handle accordingly
                    or_(
                        # Handle YYYY-MM-DD format (contains 4 digits at start)
                        and_(
                            BillingProcessData.created_time.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            BillingProcessData.created_time >= date_from,
                            BillingProcessData.created_time <= date_to + ' 23:59:59'
                        ),
                        # Handle DD/MM/YYYY format (contains / separators)
                        and_(
                            BillingProcessData.created_time.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(BillingProcessData.created_time, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(BillingProcessData.created_time, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total billing amount: {str(e)}")

    def get_delivery_process_status_counts(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[DeliveryProcessStatusItem]:
        """
        Get count of delivery process data grouped by status_delivery_document

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            List of DeliveryProcessStatusItem with status and count
        """
        try:
            logger.info(f"Querying delivery process data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Status mapping for delivery process
            status_mapping = {
                '1': 'Ready',
                '2': 'In Progress',
                '3': 'Back to Dealer',
                '4': 'Completed'
            }

            # Query to get counts grouped by status_delivery_document
            query = self.db.query(
                DeliveryProcessData.status_delivery_document,
                func.count(DeliveryProcessData.id).label('count')
            ).filter(
                DeliveryProcessData.dealer_id == dealer_id,
                func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= date_from,
                func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= date_to
            ).group_by(DeliveryProcessData.status_delivery_document)

            result = query.all()

            logger.info(f"Found {len(result)} different delivery statuses")

            # Convert to schema objects with status labels
            status_items = []
            for row in result:
                print(row)
                status_label = status_mapping.get(row.status_delivery_document, row.status_delivery_document or 'Unknown')

                status_items.append(DeliveryProcessStatusItem(
                    status_delivery_document=row.status_delivery_document,
                    status_label=status_label,
                    count=row.count
                ))

            return status_items

        except Exception as e:
            logger.error(f"Error in get_delivery_process_status_counts: {str(e)}")
            raise

    def get_total_delivery_process_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of delivery process records for the given criteria

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Total number of delivery process records
        """
        try:
            total = self.db.query(func.count(DeliveryProcessData.id)).filter(
                DeliveryProcessData.dealer_id == dealer_id,
                func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= date_from,
                func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= date_to
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total delivery process records: {str(e)}")

    def get_prospect_followup_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[ProspectFollowUpItem]:
        """
        Get count of prospect data grouped by status_follow_up_prospecting
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of ProspectFollowUpItem with status and count
        """
        try:
            logger.info(f"Querying prospect data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Status mapping for prospect follow-up
            status_mapping = {
                '1': 'Low',
                '2': 'Medium', 
                '3': 'Hot',
                '4': 'Deal',
                '5': 'Not Deal'
            }

            # Query to get counts grouped by status_follow_up_prospecting
            # Filter by tanggal_appointment which is already a Date type
            query = self.db.query(
                ProspectData.status_follow_up_prospecting,
                func.count(ProspectData.id).label('count')
            ).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).group_by(ProspectData.status_follow_up_prospecting)

            results = query.all()
            logger.info(f"Found {len(results)} different prospect follow-up statuses")

            # Convert to schema objects with status mapping
            followup_items = []
            for status, count in results:
                status_label = status_mapping.get(status, status or 'Unknown')
                
                followup_items.append(ProspectFollowUpItem(
                    status_follow_up_prospecting=status,
                    status_label=status_label,
                    count=count
                ))

            return followup_items

        except Exception as e:
            logger.error(f"Error in get_prospect_followup_statistics: {str(e)}")
            raise Exception(f"Error getting prospect follow-up statistics: {str(e)}")

    def get_total_prospect_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of prospect records for the given criteria
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of prospect records
        """
        try:
            total = self.db.query(func.count(ProspectData.id)).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total prospect records: {str(e)}")

    def get_spk_status_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[SPKStatusItem]:
        """
        Get count of SPK dealing process data grouped by status_spk
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of SPKStatusItem with status and count
        """
        try:
            logger.info(f"Querying SPK dealing process data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Status mapping for SPK status
            status_mapping = {
                '1': 'Open',
                '2': 'Indent', 
                '3': 'Complete',
                '4': 'Cancelled'
            }

            # Query to get counts grouped by status_spk
            # Filter by tanggal_pesanan which is a string field that needs conversion
            # Handle various date formats that might be in the string field
            query = self.db.query(
                SPKDealingProcessData.status_spk,
                func.count(SPKDealingProcessData.id).label('count')
            ).filter(
                and_(
                    SPKDealingProcessData.dealer_id == dealer_id,
                    # Use regex to detect format and handle date conversion accordingly
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            SPKDealingProcessData.tanggal_pesanan.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            SPKDealingProcessData.tanggal_pesanan >= date_from,
                            SPKDealingProcessData.tanggal_pesanan <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            SPKDealingProcessData.tanggal_pesanan.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(SPKDealingProcessData.tanggal_pesanan, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessData.tanggal_pesanan, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (with time)
                        and_(
                            SPKDealingProcessData.tanggal_pesanan.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(SPKDealingProcessData.tanggal_pesanan, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(SPKDealingProcessData.tanggal_pesanan, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(SPKDealingProcessData.status_spk)

            results = query.all()
            logger.info(f"Found {len(results)} different SPK statuses")

            # Convert to schema objects with status mapping
            spk_items = []
            for status, count in results:
                status_label = status_mapping.get(status, status or 'Unknown')
                
                spk_items.append(SPKStatusItem(
                    status_spk=status,
                    status_label=status_label,
                    count=count
                ))

            return spk_items

        except Exception as e:
            logger.error(f"Error in get_spk_status_statistics: {str(e)}")
            raise Exception(f"Error getting SPK status statistics: {str(e)}")

    def get_total_spk_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of SPK dealing process records for the given criteria
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of SPK records
        """
        try:
            total = self.db.query(func.count(SPKDealingProcessData.id)).filter(
                and_(
                    SPKDealingProcessData.dealer_id == dealer_id,
                    # Use regex to detect format and handle date conversion accordingly
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            SPKDealingProcessData.tanggal_pesanan.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            SPKDealingProcessData.tanggal_pesanan >= date_from,
                            SPKDealingProcessData.tanggal_pesanan <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            SPKDealingProcessData.tanggal_pesanan.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(SPKDealingProcessData.tanggal_pesanan, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessData.tanggal_pesanan, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (with time)
                        and_(
                            SPKDealingProcessData.tanggal_pesanan.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(SPKDealingProcessData.tanggal_pesanan, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(SPKDealingProcessData.tanggal_pesanan, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total SPK records: {str(e)}")

    def get_top_leasing_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[TopLeasingItem]:
        """
        Get count of leasing data grouped by nama_finance_company, ordered by count descending, limited to top 5
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of TopLeasingItem with finance company name and count
        """
        try:
            logger.info(f"Querying leasing data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Query to get counts grouped by nama_finance_company (top 5)
            # Filter by tanggal_pengajuan which is a varchar field that needs conversion
            # Handle various date formats that might be in the string field
            query = self.db.query(
                LeasingData.nama_finance_company,
                func.count(LeasingData.id_po_finance_company).label('count')
            ).filter(
                and_(
                    LeasingData.dealer_id == dealer_id,
                    LeasingData.nama_finance_company.isnot(None),  # Exclude null company names
                    LeasingData.id_po_finance_company.isnot(None),  # Exclude null PO finance company IDs
                    # Use regex to detect format and handle date conversion accordingly
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            LeasingData.tanggal_pengajuan.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            LeasingData.tanggal_pengajuan >= date_from,
                            LeasingData.tanggal_pengajuan <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            LeasingData.tanggal_pengajuan.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(LeasingData.tanggal_pengajuan, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(LeasingData.tanggal_pengajuan, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (with time)
                        and_(
                            LeasingData.tanggal_pengajuan.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(LeasingData.tanggal_pengajuan, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(LeasingData.tanggal_pengajuan, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(LeasingData.nama_finance_company).order_by(func.count(LeasingData.id_po_finance_company).desc()).limit(5)

            results = query.all()
            logger.info(f"Found {len(results)} top leasing companies")

            # Convert to schema objects
            leasing_items = []
            for nama_finance_company, count in results:
                leasing_items.append(TopLeasingItem(
                    nama_finance_company=nama_finance_company,
                    count=count
                ))

            return leasing_items

        except Exception as e:
            logger.error(f"Error in get_top_leasing_statistics: {str(e)}")
            raise Exception(f"Error getting top leasing statistics: {str(e)}")

    def get_total_leasing_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of leasing records for the given criteria
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of leasing records
        """
        try:
            total = self.db.query(func.count(LeasingData.id)).filter(
                and_(
                    LeasingData.dealer_id == dealer_id,
                    LeasingData.nama_finance_company.isnot(None),  # Exclude null company names
                    LeasingData.id_po_finance_company.isnot(None),  # Exclude null PO finance company IDs
                    # Use regex to detect format and handle date conversion accordingly
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            LeasingData.tanggal_pengajuan.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            LeasingData.tanggal_pengajuan >= date_from,
                            LeasingData.tanggal_pengajuan <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            LeasingData.tanggal_pengajuan.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(LeasingData.tanggal_pengajuan, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(LeasingData.tanggal_pengajuan, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (with time)
                        and_(
                            LeasingData.tanggal_pengajuan.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(LeasingData.tanggal_pengajuan, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(LeasingData.tanggal_pengajuan, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total leasing records: {str(e)}")

    def get_document_handling_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get count of document handling data where status_faktur_stnk == 1
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Count of SPK records matching criteria
        """
        try:
            logger.info(f"Querying document handling data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Query to count id_spk from document_handling_data through units
            # Filter by dealer_id, date range on tanggal_pengajuan_stnk_ke_biro, and status_faktur_stnk == 1
            # Handle various date formats that might be in the string field
            query = self.db.query(func.count(DocumentHandlingData.id_spk)).join(
                DocumentHandlingUnit, DocumentHandlingData.id == DocumentHandlingUnit.document_handling_data_id
            ).filter(
                and_(
                    DocumentHandlingData.dealer_id == dealer_id,
                    DocumentHandlingData.id_spk.isnot(None),  # Ensure id_spk is not null
                    DocumentHandlingUnit.status_faktur_stnk == '1',  # Filter by status_faktur_stnk == 1
                    DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.isnot(None),  # Ensure date field is not null
                    # Use regex to detect format and handle date conversion accordingly
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro >= date_from,
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (with time)
                        and_(
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            )

            result = query.scalar()
            count = result or 0
            
            logger.info(f"Found {count} document handling records matching criteria")
            return count

        except Exception as e:
            logger.error(f"Error in get_document_handling_statistics: {str(e)}")
            raise Exception(f"Error getting document handling statistics: {str(e)}")

    def get_total_document_handling_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of document handling records for the given criteria (without status filter)
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of document handling records
        """
        try:
            total = self.db.query(func.count(DocumentHandlingData.id)).join(
                DocumentHandlingUnit, DocumentHandlingData.id == DocumentHandlingUnit.document_handling_data_id
            ).filter(
                and_(
                    DocumentHandlingData.dealer_id == dealer_id,
                    DocumentHandlingData.id_spk.isnot(None),  # Ensure id_spk is not null
                    DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.isnot(None),  # Ensure date field is not null
                    # Use regex to detect format and handle date conversion accordingly
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro >= date_from,
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (with time)
                        and_(
                            DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(DocumentHandlingUnit.tanggal_pengajuan_stnk_ke_biro, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total document handling records: {str(e)}")

    def get_status_prospect_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[StatusProspectItem]:
        """
        Get count of prospect data grouped by status_prospect
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of StatusProspectItem with status and count
        """
        try:
            logger.info(f"Querying prospect data for status_prospect statistics dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Status mapping for status_prospect
            status_mapping = {
                '1': 'Low',
                '2': 'Medium', 
                '3': 'Hot',
                '4': 'Deal',
                '5': 'Not Deal'
            }

            # Query to get counts grouped by status_prospect
            # Filter by tanggal_appointment which is a Date type
            query = self.db.query(
                ProspectData.status_prospect,
                func.count(ProspectData.id).label('count')
            ).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).group_by(ProspectData.status_prospect)

            results = query.all()
            logger.info(f"Found {len(results)} different status_prospect values")

            # Convert to schema objects with status mapping
            status_items = []
            for status, count in results:
                status_label = status_mapping.get(status, status or 'Unknown')
                
                status_items.append(StatusProspectItem(
                    status_prospect=status,
                    status_label=status_label,
                    count=count
                ))

            return status_items

        except Exception as e:
            logger.error(f"Error in get_status_prospect_statistics: {str(e)}")
            raise Exception(f"Error getting status prospect statistics: {str(e)}")

    def get_metode_follow_up_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[MetodeFollowUpItem]:
        """
        Get count of prospect data grouped by metode_follow_up
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of MetodeFollowUpItem with metode and count
        """
        try:
            logger.info(f"Querying prospect data for metode_follow_up statistics dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Metode mapping for metode_follow_up
            metode_mapping = {
                '1': 'SMS (WA/Line)',
                '2': 'Call', 
                '3': 'Visit',
                '4': 'Direct Touch'
            }

            # Query to get counts grouped by metode_follow_up
            # Filter by tanggal_appointment which is a Date type
            query = self.db.query(
                ProspectData.metode_follow_up,
                func.count(ProspectData.id).label('count')
            ).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).group_by(ProspectData.metode_follow_up)

            results = query.all()
            logger.info(f"Found {len(results)} different metode_follow_up values")

            # Convert to schema objects with metode mapping
            metode_items = []
            for metode, count in results:
                metode_label = metode_mapping.get(metode, metode or 'Unknown')
                
                metode_items.append(MetodeFollowUpItem(
                    metode_follow_up=metode,
                    metode_label=metode_label,
                    count=count
                ))

            return metode_items

        except Exception as e:
            logger.error(f"Error in get_metode_follow_up_statistics: {str(e)}")
            raise Exception(f"Error getting metode follow up statistics: {str(e)}")

    def get_sumber_prospect_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[SumberProspectItem]:
        """
        Get count of prospect data grouped by sumber_prospect (top 5)
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of SumberProspectItem with sumber and count (top 5)
        """
        try:
            logger.info(f"Querying prospect data for sumber_prospect statistics dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Sumber mapping for sumber_prospect
            sumber_mapping = {
                '0001': 'Pameran (Joint Promo, Grebek Pasar, Alfamart, Indomart, Mall dll)',
                '0002': 'Showroom Event',
                '0003': 'Roadshow',
                '0004': 'Walk in',
                '0005': 'Customer RO H1',
                '0006': 'Customer RO H23',
                '0007': 'Website',
                '0008': 'Social media',
                '0009': 'External parties (leasing, insurance)',
                '0010': 'Mobile Apps MD/Dealer',
                '0011': 'Refferal',
                '0012': 'Contact Center',
                '9999': 'Others'
            }

            # Query to get counts grouped by sumber_prospect (top 5)
            # Filter by tanggal_prospect which is a Date type
            query = self.db.query(
                ProspectData.sumber_prospect,
                func.count(ProspectData.id).label('count')
            ).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_prospect >= date_from,
                    ProspectData.tanggal_prospect <= date_to
                )
            ).group_by(ProspectData.sumber_prospect).order_by(func.count(ProspectData.id).desc()).limit(5)

            results = query.all()
            logger.info(f"Found {len(results)} different sumber_prospect values (top 5)")

            # Convert to schema objects with sumber mapping
            sumber_items = []
            for sumber, count in results:
                sumber_label = sumber_mapping.get(sumber, sumber or 'Unknown')
                
                sumber_items.append(SumberProspectItem(
                    sumber_prospect=sumber,
                    sumber_label=sumber_label,
                    count=count
                ))

            return sumber_items

        except Exception as e:
            logger.error(f"Error in get_sumber_prospect_statistics: {str(e)}")
            raise Exception(f"Error getting sumber prospect statistics: {str(e)}")

    def get_total_status_prospect_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of prospect records for status_prospect criteria
        """
        try:
            total = self.db.query(func.count(ProspectData.id)).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total status prospect records: {str(e)}")

    def get_total_metode_follow_up_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of prospect records for metode_follow_up criteria
        """
        try:
            total = self.db.query(func.count(ProspectData.id)).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total metode follow up records: {str(e)}")

    def get_total_sumber_prospect_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of prospect records for sumber_prospect criteria
        """
        try:
            total = self.db.query(func.count(ProspectData.id)).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_prospect >= date_from,
                    ProspectData.tanggal_prospect <= date_to
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total sumber prospect records: {str(e)}")

    def get_sebaran_prospect_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[SebaranProspectItem]:
        """
        Get count of prospect data grouped by kode_kecamatan, ordered by count descending, limited to top 5
        Also retrieves latitude/longitude coordinates for mapping
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of SebaranProspectItem with kecamatan code, count, and coordinates
        """
        try:
            logger.info(f"Querying sebaran prospect data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Query to get counts grouped by kode_kecamatan (top 5)
            # Filter by tanggal_appointment date field
            query = self.db.query(
                ProspectData.kode_kecamatan,
                func.count(ProspectData.id).label('count'),
                # Get any latitude/longitude for mapping (use first available)
                func.min(ProspectData.latitude).label('latitude'),
                func.min(ProspectData.longitude).label('longitude')
            ).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to,
                    ProspectData.kode_kecamatan.isnot(None)  # Exclude null kecamatan codes
                )
            ).group_by(
                ProspectData.kode_kecamatan
            ).order_by(
                func.count(ProspectData.id).desc()
            ).limit(5)

            results = query.all()
            
            # Simple kecamatan name mapping for common codes
            kecamatan_mapping = {
                "3273010": "Bandung Wetan",
                "3273020": "Sumur Bandung", 
                "3273030": "Bandung Kulon",
                "3273040": "Bandung Kidul",
                "3273050": "Arcamanik",
                "3273060": "Antapani",
                "3273070": "Mandalajati",
                "3273080": "Kiaracondong",
                "3273090": "Astanaanyar",
                "3273100": "Cicendo",
                "3273110": "Sukajadi",
                "3273120": "Cidadap",
                "3273130": "Coblong",
                "3273140": "Andir",
                "3273150": "Lengkong",
                "3273160": "Regol",
                "3273170": "Batununggal",
                "3273180": "Buahbatu",
                "3273190": "Rancasari",
                "3273200": "Cibiru",
                "3273210": "Ujungberung",
                "3273220": "Cinambo",
                "3273230": "Panyileukan",
                "3273240": "Cibeunying Kidul",
                "3273250": "Cibeunying Kaler",
                "3273260": "Sukasari",
                "3273270": "Cicaheum",
                "3273280": "Babakan Ciparay",
                "3273290": "Bojongloa Kaler",
                "3273300": "Bojongloa Kidul"
            }
            
            return [
                SebaranProspectItem(
                    kode_kecamatan=result.kode_kecamatan,
                    nama_kecamatan=kecamatan_mapping.get(result.kode_kecamatan, f"Kecamatan {result.kode_kecamatan}"),
                    count=result.count,
                    latitude=result.latitude,
                    longitude=result.longitude
                )
                for result in results
            ]

        except Exception as e:
            logger.error(f"Error getting sebaran prospect statistics: {str(e)}")
            raise Exception(f"Error getting sebaran prospect statistics: {str(e)}")

    def get_total_sebaran_prospect_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of prospect records for sebaran prospect criteria
        """
        try:
            total = self.db.query(func.count(ProspectData.id)).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total sebaran prospect records: {str(e)}")

    def get_prospect_data_table(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str,
        page: int = 1,
        per_page: int = 20,
        id_prospect: str = None,
        nama_lengkap: str = None,
        alamat: str = None,
        no_kontak: str = None,
        tanggal_prospect: str = None,
        status_prospect: str = None
    ) -> tuple[List[ProspectDataTableItem], int]:
        """
        Get prospect data for table display with pagination and filters
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page
            id_prospect: Filter by prospect ID (exact match)
            nama_lengkap: Filter by name (partial match)
            alamat: Filter by address (partial match)
            no_kontak: Filter by contact number (exact match)
            tanggal_prospect: Filter by prospect date (exact match)
            status_prospect: Filter by status (exact match)
            
        Returns:
            Tuple of (List of ProspectDataTableItem, total_count)
        """
        try:
            logger.info(f"Querying prospect data table for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}, page={page}, per_page={per_page}")

            # Build base query
            query = self.db.query(ProspectData).filter(
                and_(
                    ProspectData.dealer_id == dealer_id,
                    ProspectData.tanggal_appointment >= date_from,
                    ProspectData.tanggal_appointment <= date_to
                )
            )
            
            # Apply filters if provided
            if id_prospect:
                query = query.filter(ProspectData.id_prospect.ilike(f"%{id_prospect}%"))
                
            if nama_lengkap:
                query = query.filter(ProspectData.nama_lengkap.ilike(f"%{nama_lengkap}%"))
                
            if alamat:
                query = query.filter(ProspectData.alamat.ilike(f"%{alamat}%"))
                
            if no_kontak:
                query = query.filter(ProspectData.no_kontak.ilike(f"%{no_kontak}%"))
                
            if tanggal_prospect:
                query = query.filter(ProspectData.tanggal_prospect == tanggal_prospect)
                
            if status_prospect:
                query = query.filter(ProspectData.status_prospect == status_prospect)

            # Get total count for pagination
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            results = query.order_by(ProspectData.tanggal_prospect.desc()).offset(offset).limit(per_page).all()
            
            # Convert to response items
            prospect_items = []
            for prospect in results:
                prospect_items.append(
                    ProspectDataTableItem(
                        id_prospect=prospect.id_prospect,
                        nama_lengkap=prospect.nama_lengkap,
                        alamat=prospect.alamat,
                        no_kontak=prospect.no_kontak,
                        tanggal_prospect=prospect.tanggal_prospect.strftime('%Y-%m-%d') if prospect.tanggal_prospect else None,
                        status_prospect=prospect.status_prospect,
                        sumber_prospect=prospect.sumber_prospect,
                        tanggal_appointment=prospect.tanggal_appointment.strftime('%Y-%m-%d') if prospect.tanggal_appointment else None,
                        no_ktp=prospect.no_ktp,
                        kode_kecamatan=prospect.kode_kecamatan,
                        metode_follow_up=prospect.metode_follow_up
                    )
                )
            
            logger.info(f"Found {len(prospect_items)} prospect records (page {page}/{(total_count + per_page - 1) // per_page})")
            
            return prospect_items, total_count

        except Exception as e:
            logger.error(f"Error getting prospect data table: {str(e)}")
            raise Exception(f"Error getting prospect data table: {str(e)}")

    def get_top_dealing_units_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[TopDealingUnitItem]:
        """
        Get top dealing units statistics by summing quantity grouped by kode_tipe_unit
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of TopDealingUnitItem with top 3 unit types by quantity
        """
        try:
            logger.info(f"Querying top dealing units for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Query to get quantity sum grouped by kode_tipe_unit (top 3)
            # Join with SPKDealingProcessData to filter by dealer_id
            # Filter by tanggal_pengiriman (string format, need conversion)
            query = self.db.query(
                SPKDealingProcessUnit.kode_tipe_unit,
                func.sum(SPKDealingProcessUnit.quantity).label('total_quantity')
            ).join(
                SPKDealingProcessData,
                SPKDealingProcessUnit.spk_dealing_process_data_id == SPKDealingProcessData.id
            ).filter(
                and_(
                    SPKDealingProcessData.dealer_id == dealer_id,
                    SPKDealingProcessUnit.kode_tipe_unit.isnot(None),  # Exclude null unit codes
                    SPKDealingProcessUnit.quantity.isnot(None),  # Exclude null quantities
                    # Handle string date conversion for tanggal_pengiriman
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH24:MI:SS format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(
                SPKDealingProcessUnit.kode_tipe_unit
            ).order_by(
                func.sum(SPKDealingProcessUnit.quantity).desc()
            ).limit(3)

            results = query.all()
            
            # Simple unit type name mapping for common Honda codes
            unit_mapping = {
                "SCOOPY": "Honda Scoopy",
                "VARIO": "Honda Vario",
                "BEAT": "Honda Beat",
                "PCX": "Honda PCX",
                "GENIO": "Honda Genio",
                "CB150R": "Honda CB150R",
                "CBR150R": "Honda CBR150R",
                "CRF150L": "Honda CRF150L",
                "FORZA": "Honda Forza",
                "ADV": "Honda ADV"
            }
            
            return [
                TopDealingUnitItem(
                    kode_tipe_unit=result.kode_tipe_unit,
                    nama_unit=unit_mapping.get(result.kode_tipe_unit, result.kode_tipe_unit),
                    total_quantity=result.total_quantity or 0
                )
                for result in results if result.total_quantity and result.total_quantity > 0
            ]

        except Exception as e:
            logger.error(f"Error getting top dealing units statistics: {str(e)}")
            raise Exception(f"Error getting top dealing units statistics: {str(e)}")

    def get_total_dealing_units_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of SPK unit records for dealing units criteria
        """
        try:
            total = self.db.query(func.count(SPKDealingProcessUnit.id)).join(
                SPKDealingProcessData,
                SPKDealingProcessUnit.spk_dealing_process_data_id == SPKDealingProcessData.id
            ).filter(
                and_(
                    SPKDealingProcessData.dealer_id == dealer_id,
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH24:MI:SS format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total dealing units records: {str(e)}")

    def get_revenue_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> tuple[float, int]:
        """
        Get revenue statistics by summing harga_jual from SPK dealing process units
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Tuple of (total_revenue, total_records)
        """
        try:
            logger.info(f"Querying revenue statistics for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Query to get revenue sum from harga_jual
            # Join with SPKDealingProcessData to filter by dealer_id
            # Filter by tanggal_pengiriman (string format, need conversion)
            query = self.db.query(
                func.sum(SPKDealingProcessUnit.harga_jual).label('total_revenue'),
                func.count(SPKDealingProcessUnit.id).label('total_records')
            ).join(
                SPKDealingProcessData,
                SPKDealingProcessUnit.spk_dealing_process_data_id == SPKDealingProcessData.id
            ).filter(
                and_(
                    SPKDealingProcessData.dealer_id == dealer_id,
                    SPKDealingProcessUnit.harga_jual.isnot(None),  # Exclude null prices
                    # Handle string date conversion for tanggal_pengiriman
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle YYYY-MM-DD HH24:MI:SS format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.date(func.to_timestamp(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD HH24:MI:SS')) >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.date(func.to_timestamp(SPKDealingProcessUnit.tanggal_pengiriman, 'YYYY-MM-DD HH24:MI:SS')) <= func.to_date(date_to, 'YYYY-MM-DD')
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            SPKDealingProcessUnit.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(SPKDealingProcessUnit.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            )

            result = query.first()
            
            total_revenue = float(result.total_revenue) if result.total_revenue else 0.0
            total_records = result.total_records or 0
            
            logger.info(f"Found total revenue: {total_revenue} from {total_records} records")
            
            return total_revenue, total_records

        except Exception as e:
            logger.error(f"Error getting revenue statistics: {str(e)}")
            raise Exception(f"Error getting revenue statistics: {str(e)}")

    def get_top_driver_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> List[TopDriverItem]:
        """
        Get top 5 drivers by delivery count from delivery process data joined with details
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of TopDriverItem with top 5 drivers by delivery count
        """
        try:
            logger.info(f"Querying top driver data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build the query with join and date filtering
            # Join DeliveryProcessData with DeliveryProcessDetail to count id_spk per driver
            query = self.db.query(
                DeliveryProcessData.id_driver,
                func.count(DeliveryProcessDetail.id_spk).label('total_deliveries')
            ).join(
                DeliveryProcessDetail, 
                DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id
            ).filter(
                and_(
                    DeliveryProcessData.dealer_id == dealer_id,
                    DeliveryProcessData.id_driver.isnot(None),  # Exclude null drivers
                    DeliveryProcessData.id_driver != '',  # Exclude empty drivers
                    DeliveryProcessDetail.id_spk.isnot(None),  # Only count valid SPK IDs
                    # Handle string date conversion for tanggal_pengiriman
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DeliveryProcessData.tanggal_pengiriman >= date_from,
                            DeliveryProcessData.tanggal_pengiriman <= date_to
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (extract date part)
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) >= date_from,
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(
                DeliveryProcessData.id_driver
            ).order_by(
                func.count(DeliveryProcessDetail.id_spk).desc()
            ).limit(5)  # Top 5 drivers

            # Execute query
            results = query.all()
            logger.info(f"Found {len(results)} drivers with delivery data")

            # Convert to schema objects
            driver_items = []
            for id_driver, total_deliveries in results:
                driver_items.append(TopDriverItem(
                    id_driver=id_driver,
                    nama_driver=id_driver,  # Use ID as name since we don't have driver names
                    total_deliveries=total_deliveries
                ))

            return driver_items
            
        except Exception as e:
            logger.error(f"Error getting top driver statistics: {str(e)}")
            raise Exception(f"Error getting top driver statistics: {str(e)}")

    def get_total_driver_records(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> int:
        """
        Get total count of delivery records for drivers within date range
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of delivery records
        """
        try:
            # Count total delivery records with valid drivers
            query = self.db.query(
                func.count(DeliveryProcessDetail.id_spk)
            ).join(
                DeliveryProcessDetail, 
                DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id
            ).filter(
                and_(
                    DeliveryProcessData.dealer_id == dealer_id,
                    DeliveryProcessData.id_driver.isnot(None),
                    DeliveryProcessData.id_driver != '',
                    DeliveryProcessDetail.id_spk.isnot(None),
                    # Handle string date conversion for tanggal_pengiriman
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DeliveryProcessData.tanggal_pengiriman >= date_from,
                            DeliveryProcessData.tanggal_pengiriman <= date_to
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (extract date part)
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) >= date_from,
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            )
            
            total_count = query.scalar() or 0
            logger.info(f"Found {total_count} total delivery records")
            
            return total_count
            
        except Exception as e:
            logger.error(f"Error getting total driver records: {str(e)}")
            raise Exception(f"Error getting total driver records: {str(e)}")

    def get_delivery_location_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> List[DeliveryLocationItem]:
        """
        Get top 5 delivery locations by count from delivery process data joined with details
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            List of DeliveryLocationItem with top 5 delivery locations by count
        """
        try:
            logger.info(f"Querying delivery location data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build the query with join and date filtering
            # Join DeliveryProcessData with DeliveryProcessDetail to count locations
            query = self.db.query(
                DeliveryProcessDetail.lokasi_pengiriman,
                func.count(DeliveryProcessDetail.lokasi_pengiriman).label('delivery_count')
            ).join(
                DeliveryProcessData, 
                DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id
            ).filter(
                and_(
                    DeliveryProcessData.dealer_id == dealer_id,
                    DeliveryProcessDetail.lokasi_pengiriman.isnot(None),  # Exclude null locations
                    DeliveryProcessDetail.lokasi_pengiriman != '',  # Exclude empty locations
                    # Handle string date conversion for tanggal_pengiriman
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DeliveryProcessData.tanggal_pengiriman >= date_from,
                            DeliveryProcessData.tanggal_pengiriman <= date_to
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (extract date part)
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) >= date_from,
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            ).group_by(
                DeliveryProcessDetail.lokasi_pengiriman
            ).order_by(
                func.count(DeliveryProcessDetail.lokasi_pengiriman).desc()
            ).limit(5)  # Top 5 locations

            # Execute query
            results = query.all()
            logger.info(f"Found {len(results)} delivery locations with data")

            # Get total count for percentage calculation
            total_count_query = self.db.query(
                func.count(DeliveryProcessDetail.lokasi_pengiriman)
            ).join(
                DeliveryProcessData, 
                DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id
            ).filter(
                and_(
                    DeliveryProcessData.dealer_id == dealer_id,
                    DeliveryProcessDetail.lokasi_pengiriman.isnot(None),
                    DeliveryProcessDetail.lokasi_pengiriman != '',
                    # Same date filtering logic
                    or_(
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DeliveryProcessData.tanggal_pengiriman >= date_from,
                            DeliveryProcessData.tanggal_pengiriman <= date_to
                        ),
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) >= date_from,
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) <= date_to
                        ),
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            )

            total_count = total_count_query.scalar() or 0
            logger.info(f"Total delivery location records: {total_count}")

            # Convert to schema objects with percentage calculation
            location_items = []
            for lokasi_pengiriman, delivery_count in results:
                # Calculate percentage
                percentage = (delivery_count / total_count * 100) if total_count > 0 else 0
                
                # Clean location name (remove extra spaces, capitalize)
                location_name = lokasi_pengiriman.strip().title() if lokasi_pengiriman else "Unknown"
                
                location_items.append(DeliveryLocationItem(
                    lokasi_pengiriman=lokasi_pengiriman,
                    location_name=location_name,
                    delivery_count=delivery_count,
                    percentage=round(percentage, 1)
                ))

            return location_items
            
        except Exception as e:
            logger.error(f"Error getting delivery location statistics: {str(e)}")
            raise Exception(f"Error getting delivery location statistics: {str(e)}")

    def get_total_delivery_location_records(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> int:
        """
        Get total count of delivery location records within date range
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Total number of delivery location records
        """
        try:
            # Count total delivery location records
            query = self.db.query(
                func.count(DeliveryProcessDetail.lokasi_pengiriman)
            ).join(
                DeliveryProcessData, 
                DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id
            ).filter(
                and_(
                    DeliveryProcessData.dealer_id == dealer_id,
                    DeliveryProcessDetail.lokasi_pengiriman.isnot(None),
                    DeliveryProcessDetail.lokasi_pengiriman != '',
                    # Handle string date conversion for tanggal_pengiriman
                    or_(
                        # Handle YYYY-MM-DD format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                            DeliveryProcessData.tanggal_pengiriman >= date_from,
                            DeliveryProcessData.tanggal_pengiriman <= date_to
                        ),
                        # Handle YYYY-MM-DD HH:MI:SS format (extract date part)
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) >= date_from,
                            func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) <= date_to
                        ),
                        # Handle DD/MM/YYYY format
                        and_(
                            DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                        )
                    )
                )
            )
            
            total_count = query.scalar() or 0
            logger.info(f"Found {total_count} total delivery location records")
            
            return total_count
            
        except Exception as e:
            logger.error(f"Error getting total delivery location records: {str(e)}")
            raise Exception(f"Error getting total delivery location records: {str(e)}")

    def get_delivery_data_history(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str,
        page: int = 1,
        per_page: int = 20,
        delivery_document_id: str = None,
        tanggal_pengiriman: str = None,
        status_delivery_document: str = None,
        id_driver: str = None,
        id_spk: str = None,
        nama_penerima: str = None,
        no_kontak_penerima: str = None,
        lokasi_pengiriman: str = None,
        waktu_pengiriman: str = None
    ) -> tuple[List[DeliveryDataHistoryItem], int]:
        """
        Get delivery data history with pagination and filters
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page (default 20)
            delivery_document_id: Filter by delivery document ID
            tanggal_pengiriman: Filter by delivery date
            status_delivery_document: Filter by delivery status
            id_driver: Filter by driver ID
            id_spk: Filter by SPK ID
            nama_penerima: Filter by recipient name
            no_kontak_penerima: Filter by recipient contact
            lokasi_pengiriman: Filter by delivery location
            waktu_pengiriman: Filter by delivery time
            
        Returns:
            Tuple of (List of DeliveryDataHistoryItem, total_count)
        """
        try:
            logger.info(f"Querying delivery data history for dealer_id={dealer_id}, page={page}, per_page={per_page}")

            # Build base query with join
            query = self.db.query(
                DeliveryProcessData.delivery_document_id,
                DeliveryProcessData.tanggal_pengiriman,
                DeliveryProcessData.status_delivery_document,
                DeliveryProcessData.id_driver,
                DeliveryProcessDetail.id_spk,
                DeliveryProcessDetail.nama_penerima,
                DeliveryProcessDetail.no_kontak_penerima,
                DeliveryProcessDetail.lokasi_pengiriman,
                DeliveryProcessDetail.waktu_pengiriman
            ).join(
                DeliveryProcessDetail, 
                DeliveryProcessData.id == DeliveryProcessDetail.delivery_process_data_id
            )

            # Build filter conditions
            filter_conditions = [
                DeliveryProcessData.dealer_id == dealer_id,
                # Handle string date conversion for tanggal_pengiriman date range
                or_(
                    # Handle YYYY-MM-DD format
                    and_(
                        DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2}'),
                        DeliveryProcessData.tanggal_pengiriman >= date_from,
                        DeliveryProcessData.tanggal_pengiriman <= date_to
                    ),
                    # Handle YYYY-MM-DD HH:MI:SS format (extract date part)
                    and_(
                        DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),
                        func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) >= date_from,
                        func.substring(DeliveryProcessData.tanggal_pengiriman, 1, 10) <= date_to
                    ),
                    # Handle DD/MM/YYYY format
                    and_(
                        DeliveryProcessData.tanggal_pengiriman.op('~')(r'^\d{2}/\d{2}/\d{4}'),
                        func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                        func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                    )
                )
            ]

            # Add optional filters
            if delivery_document_id:
                filter_conditions.append(DeliveryProcessData.delivery_document_id.ilike(f'%{delivery_document_id}%'))
            
            if tanggal_pengiriman:
                filter_conditions.append(DeliveryProcessData.tanggal_pengiriman.ilike(f'%{tanggal_pengiriman}%'))
            
            if status_delivery_document:
                filter_conditions.append(DeliveryProcessData.status_delivery_document.ilike(f'%{status_delivery_document}%'))
            
            if id_driver:
                filter_conditions.append(DeliveryProcessData.id_driver.ilike(f'%{id_driver}%'))
            
            if id_spk:
                filter_conditions.append(DeliveryProcessDetail.id_spk.ilike(f'%{id_spk}%'))
            
            if nama_penerima:
                filter_conditions.append(DeliveryProcessDetail.nama_penerima.ilike(f'%{nama_penerima}%'))
            
            if no_kontak_penerima:
                filter_conditions.append(DeliveryProcessDetail.no_kontak_penerima.ilike(f'%{no_kontak_penerima}%'))
            
            if lokasi_pengiriman:
                filter_conditions.append(DeliveryProcessDetail.lokasi_pengiriman.ilike(f'%{lokasi_pengiriman}%'))
            
            if waktu_pengiriman:
                filter_conditions.append(DeliveryProcessDetail.waktu_pengiriman.ilike(f'%{waktu_pengiriman}%'))

            # Apply filters
            query = query.filter(and_(*filter_conditions))

            # Get total count
            count_query = query.statement.alias()
            total_count = self.db.query(func.count()).select_from(count_query).scalar()

            # Apply pagination and ordering
            offset = (page - 1) * per_page
            results = query.order_by(
                DeliveryProcessData.tanggal_pengiriman.desc(),
                DeliveryProcessData.delivery_document_id
            ).offset(offset).limit(per_page).all()

            logger.info(f"Found {len(results)} delivery records on page {page} (total: {total_count})")

            # Convert to schema objects
            history_items = []
            for result in results:
                history_items.append(DeliveryDataHistoryItem(
                    delivery_document_id=result.delivery_document_id,
                    tanggal_pengiriman=result.tanggal_pengiriman,
                    status_delivery_document=result.status_delivery_document,
                    id_driver=result.id_driver,
                    id_spk=result.id_spk,
                    nama_penerima=result.nama_penerima,
                    no_kontak_penerima=result.no_kontak_penerima,
                    lokasi_pengiriman=result.lokasi_pengiriman,
                    waktu_pengiriman=result.waktu_pengiriman
                ))

            return history_items, total_count
            
        except Exception as e:
            logger.error(f"Error getting delivery data history: {str(e)}")
            raise Exception(f"Error getting delivery data history: {str(e)}")

    def get_spk_dealing_process_data(
        self, 
        dealer_id: str, 
        page: int = 1,
        per_page: int = 20,
        id_spk: str = None,
        nama_customer: str = None,
        alamat: str = None,
        no_kontak: str = None,
        email: str = None,
        status_spk: str = None,
        nama_bpkb: str = None
    ) -> tuple[List[SPKDealingProcessDataItem], int]:
        """
        Get SPK dealing process data with pagination and filters
        
        Args:
            dealer_id: Dealer ID to filter by
            page: Page number (1-based)
            per_page: Records per page (default 20)
            id_spk: Filter by SPK ID
            nama_customer: Filter by customer name
            alamat: Filter by address
            no_kontak: Filter by contact number
            email: Filter by email
            status_spk: Filter by SPK status
            nama_bpkb: Filter by BPKB name
            
        Returns:
            Tuple of (List of SPKDealingProcessDataItem, total_count)
        """
        try:
            logger.info(f"Querying SPK dealing process data for dealer_id={dealer_id}, page={page}, per_page={per_page}")

            # Build base query
            query = self.db.query(SPKDealingProcessData)

            # Build filter conditions
            filter_conditions = [
                SPKDealingProcessData.dealer_id == dealer_id
            ]

            # Add optional filters
            if id_spk:
                filter_conditions.append(SPKDealingProcessData.id_spk.ilike(f'%{id_spk}%'))
            
            if nama_customer:
                filter_conditions.append(SPKDealingProcessData.nama_customer.ilike(f'%{nama_customer}%'))
            
            if alamat:
                filter_conditions.append(SPKDealingProcessData.alamat.ilike(f'%{alamat}%'))
            
            if no_kontak:
                filter_conditions.append(SPKDealingProcessData.no_kontak.ilike(f'%{no_kontak}%'))
            
            if email:
                filter_conditions.append(SPKDealingProcessData.email.ilike(f'%{email}%'))
            
            if status_spk:
                filter_conditions.append(SPKDealingProcessData.status_spk.ilike(f'%{status_spk}%'))
            
            if nama_bpkb:
                filter_conditions.append(SPKDealingProcessData.nama_bpkb.ilike(f'%{nama_bpkb}%'))

            # Apply filters
            query = query.filter(and_(*filter_conditions))

            # Get total count
            total_count = query.count()

            # Apply pagination and ordering
            offset = (page - 1) * per_page
            results = query.order_by(
                SPKDealingProcessData.tanggal_pesanan.desc(),
                SPKDealingProcessData.id_spk
            ).offset(offset).limit(per_page).all()

            logger.info(f"Found {len(results)} SPK records on page {page} (total: {total_count})")

            # Convert to schema objects
            spk_items = []
            for result in results:
                spk_items.append(SPKDealingProcessDataItem(
                    id_spk=result.id_spk,
                    nama_customer=result.nama_customer,
                    alamat=result.alamat,
                    no_kontak=result.no_kontak,
                    email=result.email,
                    status_spk=result.status_spk,
                    nama_bpkb=result.nama_bpkb,
                    id_prospect=result.id_prospect,
                    no_ktp=result.no_ktp,
                    kode_propinsi=result.kode_propinsi,
                    kode_kota=result.kode_kota,
                    kode_kecamatan=result.kode_kecamatan,
                    kode_kelurahan=result.kode_kelurahan,
                    kode_pos=result.kode_pos,
                    no_ktp_bpkb=result.no_ktp_bpkb,
                    alamat_bpkb=result.alamat_bpkb,
                    latitude=result.latitude,
                    longitude=result.longitude,
                    npwp=result.npwp,
                    no_kk=result.no_kk,
                    alamat_kk=result.alamat_kk,
                    fax=result.fax,
                    id_sales_people=result.id_sales_people,
                    id_event=result.id_event,
                    tanggal_pesanan=result.tanggal_pesanan,
                    created_time=result.created_time,
                    modified_time=result.modified_time
                ))

            return spk_items, total_count
            
        except Exception as e:
            logger.error(f"Error getting SPK dealing process data: {str(e)}")
            raise Exception(f"Error getting SPK dealing process data: {str(e)}")
