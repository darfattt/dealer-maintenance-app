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
from app.schemas.dashboard import UnitInboundStatusResponse, UnitInboundStatusItem, PaymentTypeResponse, PaymentTypeItem, DeliveryProcessStatusResponse, DeliveryProcessStatusItem, ProspectFollowUpResponse, ProspectFollowUpItem, SPKStatusResponse, SPKStatusItem, TopLeasingResponse, TopLeasingItem, DocumentHandlingCountResponse, StatusProspectResponse, MetodeFollowUpResponse, SumberProspectResponse

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

    async def get_prospect_followup_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> ProspectFollowUpResponse:
        """
        Get prospect follow-up status statistics for dashboard widget

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            ProspectFollowUpResponse with follow-up status counts
        """
        try:
            logger.info(f"Getting prospect follow-up statistics for dealer {dealer_id} from {date_from} to {date_to}")

            # Get follow-up status counts
            followup_items = self.repository.get_prospect_followup_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Get total records
            total_records = self.repository.get_total_prospect_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            logger.info(f"Found {len(followup_items)} different follow-up statuses with total {total_records} records")

            return ProspectFollowUpResponse(
                success=True,
                message="Prospect follow-up statistics retrieved successfully",
                data=followup_items,
                total_records=total_records
            )

        except Exception as e:
            logger.error(f"Error getting prospect follow-up statistics: {str(e)}")
            return ProspectFollowUpResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_spk_status_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> SPKStatusResponse:
        """
        Get SPK status statistics for dashboard widget

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            SPKStatusResponse with SPK status counts
        """
        try:
            logger.info(f"Getting SPK status statistics for dealer {dealer_id} from {date_from} to {date_to}")

            # Get SPK status counts
            spk_items = self.repository.get_spk_status_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Get total records
            total_records = self.repository.get_total_spk_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            logger.info(f"Found {len(spk_items)} different SPK statuses with total {total_records} records")

            return SPKStatusResponse(
                success=True,
                message="SPK status statistics retrieved successfully",
                data=spk_items,
                total_records=total_records
            )

        except Exception as e:
            logger.error(f"Error getting SPK status statistics: {str(e)}")
            return SPKStatusResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_top_leasing_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> TopLeasingResponse:
        """
        Get top leasing companies statistics for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            TopLeasingResponse with top 5 leasing companies and their counts
        """
        try:
            logger.info(f"Getting top leasing statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get top leasing companies
            leasing_items = self.repository.get_top_leasing_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_leasing_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(leasing_items)} top leasing companies with total {total_records} records")
            
            return TopLeasingResponse(
                success=True,
                message="Top leasing companies statistics retrieved successfully",
                data=leasing_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting top leasing statistics: {str(e)}")
            return TopLeasingResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_document_handling_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> DocumentHandlingCountResponse:
        """
        Get document handling statistics for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            DocumentHandlingCountResponse with count and total records
        """
        try:
            logger.info(f"Getting document handling statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get document handling count (status_faktur_stnk == 1)
            count = self.repository.get_document_handling_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_document_handling_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {count} document handling records matching criteria out of {total_records} total records")
            
            return DocumentHandlingCountResponse(
                success=True,
                message="Document handling statistics retrieved successfully",
                count=count,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting document handling statistics: {str(e)}")
            return DocumentHandlingCountResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                count=0,
                total_records=0
            )

    async def get_status_prospect_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> StatusProspectResponse:
        """
        Get status prospect statistics for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            StatusProspectResponse with status prospect counts
        """
        try:
            logger.info(f"Getting status prospect statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get status prospect counts
            status_items = self.repository.get_status_prospect_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_status_prospect_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(status_items)} different status prospect values with total {total_records} records")
            
            return StatusProspectResponse(
                success=True,
                message="Status prospect statistics retrieved successfully",
                data=status_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting status prospect statistics: {str(e)}")
            return StatusProspectResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_metode_follow_up_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> MetodeFollowUpResponse:
        """
        Get metode follow up statistics for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            MetodeFollowUpResponse with metode follow up counts
        """
        try:
            logger.info(f"Getting metode follow up statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get metode follow up counts
            metode_items = self.repository.get_metode_follow_up_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_metode_follow_up_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(metode_items)} different metode follow up values with total {total_records} records")
            
            return MetodeFollowUpResponse(
                success=True,
                message="Metode follow up statistics retrieved successfully",
                data=metode_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting metode follow up statistics: {str(e)}")
            return MetodeFollowUpResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_sumber_prospect_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> SumberProspectResponse:
        """
        Get sumber prospect statistics for dashboard widget (top 5)
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            SumberProspectResponse with top 5 sumber prospect counts
        """
        try:
            logger.info(f"Getting sumber prospect statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get sumber prospect counts (top 5)
            sumber_items = self.repository.get_sumber_prospect_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_sumber_prospect_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(sumber_items)} top sumber prospect values with total {total_records} records")
            
            return SumberProspectResponse(
                success=True,
                message="Sumber prospect statistics retrieved successfully",
                data=sumber_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting sumber prospect statistics: {str(e)}")
            return SumberProspectResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )
