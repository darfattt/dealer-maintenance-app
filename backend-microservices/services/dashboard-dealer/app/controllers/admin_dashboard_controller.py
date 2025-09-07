"""
Controller for admin dashboard operations
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
from app.models.unit_inbound import Dealer
from app.schemas.dashboard import ActiveDealersResponse, ActiveDealerItem

logger = setup_logger(__name__)


class AdminDashboardController:
    """Controller for admin dashboard operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_active_dealers(self) -> ActiveDealersResponse:
        """
        Get all active dealers without pagination
        
        Returns:
            ActiveDealersResponse with all active dealers
        """
        try:
            logger.info("Getting all active dealers")
            
            # Query all active dealers
            dealers = self.db.query(Dealer).filter(
                Dealer.is_active == True
            ).order_by(Dealer.dealer_name).all()
            
            # Convert to response items
            dealer_items = []
            for dealer in dealers:
                dealer_items.append(ActiveDealerItem(
                    dealer_id=dealer.dealer_id,
                    dealer_name=dealer.dealer_name,
                    is_active=dealer.is_active,
                    created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                    updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
                ))
            
            total_records = len(dealer_items)
            
            logger.info(f"Found {total_records} active dealers")
            
            return ActiveDealersResponse(
                success=True,
                message="Active dealers retrieved successfully",
                data=dealer_items,
                total_records=total_records
            )
            
        except Exception as e:
            logger.error(f"Error getting active dealers: {str(e)}")
            return ActiveDealersResponse(
                success=False,
                message=f"Error retrieving data: {str(e)}",
                data=[],
                total_records=0
            )