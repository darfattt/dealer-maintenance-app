"""
Controller for H23 dashboard operations
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
from app.repositories.h23_dashboard_repository import H23DashboardRepository
from app.schemas.h23_dashboard import (
    TotalUnitEntryResponse, 
    WorkOrderRevenueResponse,
    WorkOrderStatusResponse,
    NJBStatisticsResponse,
    NSCStatisticsResponse,
    HLOStatisticsResponse
)

logger = setup_logger(__name__)


class H23DashboardController:
    """Controller for H23 dashboard analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = H23DashboardRepository(db)
    
    # Work Order Section Methods
    
    async def get_total_unit_entry(
        self, 
        dealer_id: str, 
        date_from: str, 
        date_to: str
    ) -> TotalUnitEntryResponse:
        """
        Get total unit entry count with trend indicator
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            TotalUnitEntryResponse with count, trend, and percentage
        """
        try:
            logger.info(f"Getting total unit entry for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get unit entry data with trend from repository
            result = self.repository.get_total_unit_entry_with_trend(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            count = result.get('count', 0)
            previous_count = result.get('previous_count', 0)
            trend = result.get('trend', 'stable')
            percentage = result.get('percentage', 0.0)
            
            logger.info(f"Retrieved total unit entry: count={count}, trend={trend}, percentage={percentage}")
            
            return TotalUnitEntryResponse(
                success=True,
                message="Total unit entry data retrieved successfully",
                count=count,
                previous_count=previous_count,
                trend=trend,
                percentage=percentage
            )
            
        except Exception as e:
            logger.error(f"Error getting total unit entry: {str(e)}")
            return TotalUnitEntryResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                count=0,
                previous_count=0,
                trend='stable',
                percentage=0.0
            )

    async def get_work_order_revenue(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> WorkOrderRevenueResponse:
        """
        Get work order revenue statistics
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            WorkOrderRevenueResponse with total revenue and record count
        """
        try:
            logger.info(f"Getting work order revenue for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get revenue data from repository
            revenue_data = self.repository.get_work_order_revenue(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            total_revenue = revenue_data.get('total_revenue', 0.0)
            total_records = revenue_data.get('total_records', 0)
            
            logger.info(f"Total revenue: {total_revenue}, Total records: {total_records}")
            
            return WorkOrderRevenueResponse(
                success=True,
                message="Work order revenue data retrieved successfully",
                total_revenue=total_revenue,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting work order revenue: {str(e)}")
            return WorkOrderRevenueResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                total_revenue=0.0,
                total_records=0
            )

    async def get_work_order_status_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> WorkOrderStatusResponse:
        """
        Get work order status statistics
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            WorkOrderStatusResponse with status distribution
        """
        try:
            logger.info(f"Getting work order status statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get status counts
            status_items = self.repository.get_work_order_status_counts(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get total records
            total_records = self.repository.get_total_work_order_records(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Found {len(status_items)} different work order statuses with total {total_records} records")
            
            return WorkOrderStatusResponse(
                success=True,
                message="Work order status statistics retrieved successfully",
                data=status_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting work order status statistics: {str(e)}")
            return WorkOrderStatusResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )

    # Pembayaran Section Methods
    
    async def get_njb_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> NJBStatisticsResponse:
        """
        Get NJB (Nota Jasa Bengkel) statistics
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            NJBStatisticsResponse with total amount and record count
        """
        try:
            logger.info(f"Getting NJB statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get NJB statistics from repository
            njb_data = self.repository.get_njb_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            total_amount = njb_data.get('total_amount', 0.0)
            total_records = njb_data.get('total_records', 0)
            
            logger.info(f"NJB statistics: total_amount={total_amount}, total_records={total_records}")
            
            return NJBStatisticsResponse(
                success=True,
                message="NJB statistics retrieved successfully",
                total_amount=total_amount,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting NJB statistics: {str(e)}")
            return NJBStatisticsResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                total_amount=0.0,
                total_records=0
            )

    async def get_nsc_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> NSCStatisticsResponse:
        """
        Get NSC (Nota Suku Cadang) statistics
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            NSCStatisticsResponse with total amount and record count
        """
        try:
            logger.info(f"Getting NSC statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get NSC statistics from repository
            nsc_data = self.repository.get_nsc_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            total_amount = nsc_data.get('total_amount', 0.0)
            total_records = nsc_data.get('total_records', 0)
            
            logger.info(f"NSC statistics: total_amount={total_amount}, total_records={total_records}")
            
            return NSCStatisticsResponse(
                success=True,
                message="NSC statistics retrieved successfully",
                total_amount=total_amount,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting NSC statistics: {str(e)}")
            return NSCStatisticsResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                total_amount=0.0,
                total_records=0
            )

    async def get_hlo_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> HLOStatisticsResponse:
        """
        Get HLO (Honda Layanan Otomotif) statistics
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            HLOStatisticsResponse with HLO document count, parts count, and total records
        """
        try:
            logger.info(f"Getting HLO statistics for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get HLO statistics from repository
            hlo_data = self.repository.get_hlo_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            total_hlo_documents = hlo_data.get('total_hlo_documents', 0)
            total_parts = hlo_data.get('total_parts', 0)
            total_records = hlo_data.get('total_records', 0)
            
            logger.info(f"HLO statistics: total_hlo_documents={total_hlo_documents}, total_parts={total_parts}, total_records={total_records}")
            
            return HLOStatisticsResponse(
                success=True,
                message="HLO statistics retrieved successfully",
                total_hlo_documents=total_hlo_documents,
                total_parts=total_parts,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting HLO statistics: {str(e)}")
            return HLOStatisticsResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                total_hlo_documents=0,
                total_parts=0,
                total_records=0
            )