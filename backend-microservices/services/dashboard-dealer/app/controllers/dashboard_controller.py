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
from app.schemas.dashboard import UnitInboundStatusResponse, UnitInboundStatusItem

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
