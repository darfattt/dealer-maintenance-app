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
from app.models.delivery_process import DeliveryProcessData
from app.models.prospect_data import ProspectData
from app.models.spk_dealing_process import SPKDealingProcessData
from app.models.leasing_data import LeasingData
from app.models.document_handling import DocumentHandlingData, DocumentHandlingUnit
from app.schemas.dashboard import UnitInboundStatusItem, PaymentTypeItem, DeliveryProcessStatusItem, ProspectFollowUpItem, SPKStatusItem, TopLeasingItem, StatusProspectItem, MetodeFollowUpItem, SumberProspectItem
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
