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
from app.schemas.dashboard import UnitInboundStatusResponse, UnitInboundStatusItem, PaymentTypeResponse, PaymentTypeItem, PaymentMethodResponse, PaymentStatusResponse, PaymentRevenueResponse, PaymentDataHistoryResponse, LeasingDataHistoryResponse, DocumentHandlingDataHistoryResponse, UnitInboundDataHistoryResponse, DeliveryProcessStatusResponse, DeliveryProcessStatusItem, ProspectFollowUpResponse, ProspectFollowUpItem, SPKStatusResponse, SPKStatusItem, TopLeasingResponse, TopLeasingItem, DocumentHandlingCountResponse, StatusProspectResponse, MetodeFollowUpResponse, SumberProspectResponse, SebaranProspectResponse, ProspectDataTableResponse, TopDealingUnitsResponse, RevenueResponse, TopDriverResponse, DeliveryLocationResponse, DeliveryDataHistoryResponse, SPKDealingProcessDataResponse

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

    async def get_payment_method_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> PaymentMethodResponse:
        """
        Get payment method statistics for billing process data

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            PaymentMethodResponse with payment method counts
        """
        try:
            logger.info(f"Getting payment method statistics for dealer {dealer_id} from {date_from} to {date_to}")

            # Get payment method statistics
            payment_method_items = self.repository.get_payment_method_statistics(
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

            logger.info(f"Found {len(payment_method_items)} different payment methods with total {total_records} records")

            return PaymentMethodResponse(
                success=True,
                message="Payment method statistics retrieved successfully",
                data=payment_method_items,
                total_records=total_records
            )

        except Exception as e:
            logger.error(f"Error getting payment method statistics: {str(e)}")
            return PaymentMethodResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_payment_status_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> PaymentStatusResponse:
        """
        Get payment status statistics for billing process data

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            PaymentStatusResponse with payment status counts
        """
        try:
            logger.info(f"Getting payment status statistics for dealer {dealer_id} from {date_from} to {date_to}")

            # Get payment status statistics
            payment_status_items = self.repository.get_payment_status_statistics(
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

            logger.info(f"Found {len(payment_status_items)} different payment statuses with total {total_records} records")

            return PaymentStatusResponse(
                success=True,
                message="Payment status statistics retrieved successfully",
                data=payment_status_items,
                total_records=total_records
            )

        except Exception as e:
            logger.error(f"Error getting payment status statistics: {str(e)}")
            return PaymentStatusResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_payment_revenue_total(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> PaymentRevenueResponse:
        """
        Get total payment revenue from billing process data

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            PaymentRevenueResponse with total revenue amount
        """
        try:
            logger.info(f"Getting payment revenue total for dealer {dealer_id} from {date_from} to {date_to}")

            # Get revenue total and record count
            revenue_data = self.repository.get_payment_revenue_total(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            total_revenue = revenue_data.get('total_revenue', 0.0)
            total_records = revenue_data.get('total_records', 0)

            logger.info(f"Total revenue: {total_revenue}, Total records: {total_records}")

            return PaymentRevenueResponse(
                success=True,
                message="Payment revenue total retrieved successfully",
                total_revenue=total_revenue,
                total_records=total_records
            )

        except Exception as e:
            logger.error(f"Error getting payment revenue total: {str(e)}")
            return PaymentRevenueResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                total_revenue=0.0,
                total_records=0
            )

    async def get_payment_data_history(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str,
        page: int = 1,
        per_page: int = 20
    ) -> PaymentDataHistoryResponse:
        """
        Get payment data history with pagination

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page (default 20)

        Returns:
            PaymentDataHistoryResponse with paginated payment data
        """
        try:
            logger.info(f"Getting payment data history for dealer {dealer_id} from {date_from} to {date_to}, page {page}")

            # Get payment data history from repository
            history_data = self.repository.get_payment_data_history(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page
            )

            data = history_data.get('data', [])
            total_records = history_data.get('total_records', 0)
            total_pages = history_data.get('total_pages', 0)

            logger.info(f"Found {len(data)} payment records on page {page} (total: {total_records})")

            return PaymentDataHistoryResponse(
                success=True,
                message="Payment data history retrieved successfully",
                data=data,
                total_records=total_records,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error getting payment data history: {str(e)}")
            return PaymentDataHistoryResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )

    async def get_leasing_data_history(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str,
        page: int = 1,
        per_page: int = 20
    ) -> LeasingDataHistoryResponse:
        """
        Get leasing data history with pagination

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page (default 20)

        Returns:
            LeasingDataHistoryResponse with paginated leasing data
        """
        try:
            logger.info(f"Getting leasing data history for dealer {dealer_id} from {date_from} to {date_to}, page {page}")

            # Get leasing data history from repository
            history_data = self.repository.get_leasing_data_history(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page
            )

            data = history_data.get('data', [])
            total_records = history_data.get('total_records', 0)
            total_pages = history_data.get('total_pages', 0)

            logger.info(f"Found {len(data)} leasing records on page {page} (total: {total_records})")

            return LeasingDataHistoryResponse(
                success=True,
                message="Leasing data history retrieved successfully",
                data=data,
                total_records=total_records,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error getting leasing data history: {str(e)}")
            return LeasingDataHistoryResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )

    async def get_document_handling_data_history(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str,
        page: int = 1,
        per_page: int = 20
    ) -> DocumentHandlingDataHistoryResponse:
        """
        Get document handling data history with pagination

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page (default 20)

        Returns:
            DocumentHandlingDataHistoryResponse with paginated document handling data
        """
        try:
            logger.info(f"Getting document handling data history for dealer {dealer_id} from {date_from} to {date_to}, page {page}")

            # Get document handling data history from repository
            history_data = self.repository.get_document_handling_data_history(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page
            )

            data = history_data.get('data', [])
            total_records = history_data.get('total_records', 0)
            total_pages = history_data.get('total_pages', 0)

            logger.info(f"Found {len(data)} document handling records on page {page} (total: {total_records})")

            return DocumentHandlingDataHistoryResponse(
                success=True,
                message="Document handling data history retrieved successfully",
                data=data,
                total_records=total_records,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error getting document handling data history: {str(e)}")
            return DocumentHandlingDataHistoryResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )

    async def get_unit_inbound_data_history(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str,
        page: int = 1,
        per_page: int = 20
    ) -> UnitInboundDataHistoryResponse:
        """
        Get unit inbound data history with pagination

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page (default 20)

        Returns:
            UnitInboundDataHistoryResponse with paginated unit inbound data
        """
        try:
            logger.info(f"Getting unit inbound data history for dealer {dealer_id} from {date_from} to {date_to}, page {page}")

            # Get unit inbound data history from repository
            history_data = self.repository.get_unit_inbound_data_history(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page
            )

            data = history_data.get('data', [])
            total_records = history_data.get('total_records', 0)
            total_pages = history_data.get('total_pages', 0)

            logger.info(f"Found {len(data)} unit inbound records on page {page} (total: {total_records})")

            return UnitInboundDataHistoryResponse(
                success=True,
                message="Unit inbound data history retrieved successfully",
                data=data,
                total_records=total_records,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error getting unit inbound data history: {str(e)}")
            return UnitInboundDataHistoryResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                page=page,
                per_page=per_page,
                total_pages=0
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

    async def get_sebaran_prospect_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> SebaranProspectResponse:
        """
        Get sebaran prospect statistics by kecamatan for map visualization
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            SebaranProspectResponse with kecamatan distribution counts and coordinates
        """
        try:
            logger.info(f"Getting sebaran prospect statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get sebaran prospect data
            sebaran_items = self.repository.get_sebaran_prospect_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_sebaran_prospect_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(sebaran_items)} top kecamatan distributions with total {total_records} records")
            
            return SebaranProspectResponse(
                success=True,
                message="Sebaran prospect statistics retrieved successfully",
                data=sebaran_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting sebaran prospect statistics: {str(e)}")
            return SebaranProspectResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_prospect_data_table(
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
    ) -> ProspectDataTableResponse:
        """
        Get prospect data for table display with pagination and filters
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based)
            per_page: Records per page (default 20)
            id_prospect: Filter by prospect ID
            nama_lengkap: Filter by name (partial match)
            alamat: Filter by address (partial match)
            no_kontak: Filter by contact number
            tanggal_prospect: Filter by prospect date
            status_prospect: Filter by status
            
        Returns:
            ProspectDataTableResponse with paginated prospect data
        """
        try:
            logger.info(f"Getting prospect data table for dealer {dealer_id} from {date_from} to {date_to} (page {page}, per_page {per_page})")
            
            # Get prospect data with pagination
            prospect_items, total_count = self.repository.get_prospect_data_table(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page,
                id_prospect=id_prospect,
                nama_lengkap=nama_lengkap,
                alamat=alamat,
                no_kontak=no_kontak,
                tanggal_prospect=tanggal_prospect,
                status_prospect=status_prospect
            )
            
            # Calculate total pages
            total_pages = (total_count + per_page - 1) // per_page
            
            logger.info(f"Found {len(prospect_items)} prospect records on page {page} of {total_pages} (total: {total_count})")
            
            return ProspectDataTableResponse(
                success=True,
                message="Prospect data retrieved successfully",
                data=prospect_items,
                total_records=total_count,
                total_pages=total_pages,
                current_page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Error getting prospect data table: {str(e)}")
            return ProspectDataTableResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                total_pages=0,
                current_page=page,
                per_page=per_page
            )

    async def get_top_dealing_units_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> TopDealingUnitsResponse:
        """
        Get top dealing units statistics by quantity for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            TopDealingUnitsResponse with top 3 dealing units by quantity
        """
        try:
            logger.info(f"Getting top dealing units statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get top dealing units data
            dealing_items = self.repository.get_top_dealing_units_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_dealing_units_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(dealing_items)} top dealing units with total {total_records} records")
            
            return TopDealingUnitsResponse(
                success=True,
                message="Top dealing units statistics retrieved successfully",
                data=dealing_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting top dealing units statistics: {str(e)}")
            return TopDealingUnitsResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_revenue_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> RevenueResponse:
        """
        Get revenue statistics by summing harga_jual for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            RevenueResponse with total revenue and record count
        """
        try:
            logger.info(f"Getting revenue statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get revenue data
            total_revenue, total_records = self.repository.get_revenue_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found total revenue: {total_revenue} from {total_records} records")
            
            return RevenueResponse(
                success=True,
                message="Revenue statistics retrieved successfully",
                total_revenue=total_revenue,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting revenue statistics: {str(e)}")
            return RevenueResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                total_revenue=0.0,
                total_records=0
            )

    async def get_top_driver_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> TopDriverResponse:
        """
        Get top driver statistics by delivery count for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            TopDriverResponse with top 5 drivers by delivery count
        """
        try:
            logger.info(f"Getting top driver statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get top driver data
            driver_items = self.repository.get_top_driver_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_driver_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(driver_items)} top drivers with total {total_records} delivery records")
            
            return TopDriverResponse(
                success=True,
                message="Top driver statistics retrieved successfully",
                data=driver_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting top driver statistics: {str(e)}")
            return TopDriverResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_delivery_location_statistics(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> DeliveryLocationResponse:
        """
        Get delivery location statistics by count for dashboard widget
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            DeliveryLocationResponse with top 5 delivery locations by count
        """
        try:
            logger.info(f"Getting delivery location statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get delivery location data
            location_items = self.repository.get_delivery_location_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_delivery_location_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(location_items)} top delivery locations with total {total_records} delivery records")
            
            return DeliveryLocationResponse(
                success=True,
                message="Delivery location statistics retrieved successfully",
                data=location_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting delivery location statistics: {str(e)}")
            return DeliveryLocationResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    async def get_delivery_data_history(
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
    ) -> DeliveryDataHistoryResponse:
        """
        Get delivery data history for table display with pagination and filters
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            page: Page number (1-based, default 1)
            per_page: Records per page (default 20)
            delivery_document_id: Optional filter by delivery document ID
            tanggal_pengiriman: Optional filter by delivery date
            status_delivery_document: Optional filter by delivery status
            id_driver: Optional filter by driver ID
            id_spk: Optional filter by SPK ID
            nama_penerima: Optional filter by recipient name
            no_kontak_penerima: Optional filter by recipient contact
            lokasi_pengiriman: Optional filter by delivery location
            waktu_pengiriman: Optional filter by delivery time
            
        Returns:
            DeliveryDataHistoryResponse with paginated delivery data and metadata
        """
        try:
            logger.info(f"Getting delivery data history for dealer {dealer_id} from {date_from} to {date_to} (page {page}, per_page {per_page})")
            
            # Get delivery data with pagination
            history_items, total_count = self.repository.get_delivery_data_history(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page,
                delivery_document_id=delivery_document_id,
                tanggal_pengiriman=tanggal_pengiriman,
                status_delivery_document=status_delivery_document,
                id_driver=id_driver,
                id_spk=id_spk,
                nama_penerima=nama_penerima,
                no_kontak_penerima=no_kontak_penerima,
                lokasi_pengiriman=lokasi_pengiriman,
                waktu_pengiriman=waktu_pengiriman
            )
            
            # Calculate total pages
            total_pages = (total_count + per_page - 1) // per_page
            
            logger.info(f"Found {len(history_items)} delivery records on page {page} of {total_pages} (total: {total_count})")
            
            return DeliveryDataHistoryResponse(
                success=True,
                message="Delivery data history retrieved successfully",
                data=history_items,
                total_records=total_count,
                total_pages=total_pages,
                current_page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Error getting delivery data history: {str(e)}")
            return DeliveryDataHistoryResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                total_pages=0,
                current_page=page,
                per_page=per_page
            )

    async def get_spk_dealing_process_data(
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
    ) -> SPKDealingProcessDataResponse:
        """
        Get SPK dealing process data for table display with pagination and filters
        
        Args:
            dealer_id: Dealer ID to filter by
            page: Page number (1-based, default 1)
            per_page: Records per page (default 20)
            id_spk: Optional filter by SPK ID
            nama_customer: Optional filter by customer name
            alamat: Optional filter by address
            no_kontak: Optional filter by contact number
            email: Optional filter by email
            status_spk: Optional filter by SPK status
            nama_bpkb: Optional filter by BPKB name
            
        Returns:
            SPKDealingProcessDataResponse with paginated SPK data and metadata
        """
        try:
            logger.info(f"Getting SPK dealing process data for dealer {dealer_id} (page {page}, per_page {per_page})")
            
            # Get SPK data with pagination
            spk_items, total_count = self.repository.get_spk_dealing_process_data(
                dealer_id=dealer_id,
                page=page,
                per_page=per_page,
                id_spk=id_spk,
                nama_customer=nama_customer,
                alamat=alamat,
                no_kontak=no_kontak,
                email=email,
                status_spk=status_spk,
                nama_bpkb=nama_bpkb
            )
            
            # Calculate total pages
            total_pages = (total_count + per_page - 1) // per_page
            
            logger.info(f"Found {len(spk_items)} SPK records on page {page} of {total_pages} (total: {total_count})")
            
            return SPKDealingProcessDataResponse(
                success=True,
                message="SPK dealing process data retrieved successfully",
                data=spk_items,
                total_records=total_count,
                total_pages=total_pages,
                current_page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Error getting SPK dealing process data: {str(e)}")
            return SPKDealingProcessDataResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0,
                total_pages=0,
                current_page=page,
                per_page=per_page
            )
