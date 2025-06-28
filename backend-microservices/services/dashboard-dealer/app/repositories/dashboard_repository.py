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
from app.schemas.dashboard import UnitInboundStatusItem, PaymentTypeItem, DeliveryProcessStatusItem
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
