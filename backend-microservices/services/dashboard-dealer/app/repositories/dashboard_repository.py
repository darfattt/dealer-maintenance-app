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
from app.schemas.dashboard import UnitInboundStatusItem
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
