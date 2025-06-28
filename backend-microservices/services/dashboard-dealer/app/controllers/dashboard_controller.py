"""
Controller for dashboard operations
"""

import os
import sys
from typing import List
from sqlalchemy.orm import Session

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.logger import setup_logger
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import UnitInboundStatusResponse, UnitInboundStatusItem, PaymentTypeResponse, PaymentTypeItem, DeliveryProcessStatusResponse, DeliveryProcessStatusItem

logger = setup_logger(__name__)


class DashboardController:
    """Controller for dashboard analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = DashboardRepository(db)
    
    async def get_unit_inbound_status_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> UnitInboundStatusResponse:
        """
        Get unit inbound status statistics for pie chart
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            UnitInboundStatusResponse with status counts
        """
        try:
            logger.info(f"Getting unit inbound status statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get status counts
            status_items = self.repository.get_unit_inbound_status_counts(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_unit_inbound_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(status_items)} different statuses with total {total_records} records")
            
            return UnitInboundStatusResponse(
                success=True,
                message="Unit inbound status statistics retrieved successfully",
                data=status_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting unit inbound status statistics: {str(e)}")
            return UnitInboundStatusResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_payment_type_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> PaymentTypeResponse:
        """
        Get payment type statistics for billing process data

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            PaymentTypeResponse with payment type counts and amounts
        """
        try:
            logger.info(f"Getting payment type statistics for dealer {dealer_id} from {date_from} to {date_to}")

            # Get payment type statistics
            payment_items = self.repository.get_payment_type_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Get total records
            total_records = self.repository.get_total_billing_process_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Get total amount
            total_amount = self.repository.get_total_billing_amount(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            logger.info(f"Found {len(payment_items)} different payment types with total {total_records} records")

            return PaymentTypeResponse(
                success=True,
                message="Payment type statistics retrieved successfully",
                data=payment_items,
                total_records=total_records,
                total_amount=total_amount
            )

        except Exception as e:
            logger.error(f"Error getting payment type statistics: {str(e)}")
            return PaymentTypeResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                total_amount=0
            )

    async def get_delivery_process_status_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> DeliveryProcessStatusResponse:
        """
        Get delivery process status statistics for dashboard widget

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            DeliveryProcessStatusResponse with delivery status counts
        """
        try:
            logger.info(f"Getting delivery process status statistics for dealer {dealer_id} from {date_from} to {date_to}")

            # Get delivery status counts
            status_items = self.repository.get_delivery_process_status_counts(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Get total records
            total_records = self.repository.get_total_delivery_process_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            logger.info(f"Found {len(status_items)} different delivery statuses with total {total_records} records")

            return DeliveryProcessStatusResponse(
                success=True,
                message="Delivery process status statistics retrieved successfully",
                data=status_items,
                total_records=total_records
            )

        except Exception as e:
            logger.error(f"Error getting delivery process status statistics: {str(e)}")
            return DeliveryProcessStatusResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )
