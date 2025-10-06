"""
Controller for admin dealer management operations (SYSTEM_ADMIN only)
"""

import os
import sys
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.logger import setup_logger
from app.models.dealer import Dealer
from app.schemas.dealer import (
    DealerListResponse,
    DealerListItem,
    DealerResponse,
    DealerUpdateRequest,
    DealerUpdateResponse,
    DealerStatusResponse
)

logger = setup_logger(__name__)


class AdminDealerController:
    """Controller for admin dealer management operations"""

    def __init__(self, db: Session):
        self.db = db

    async def get_all_dealers(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> DealerListResponse:
        """
        Get all dealers with pagination and filtering

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Search term for dealer_id or dealer_name
            is_active: Filter by active status

        Returns:
            DealerListResponse with paginated dealer list
        """
        try:
            logger.info(f"Getting all dealers - page: {page}, page_size: {page_size}, search: {search}, is_active: {is_active}")

            # Build query
            query = self.db.query(Dealer)

            # Apply filters
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (Dealer.dealer_id.ilike(search_filter)) |
                    (Dealer.dealer_name.ilike(search_filter))
                )

            if is_active is not None:
                query = query.filter(Dealer.is_active == is_active)

            # Get total count
            total_records = query.count()

            # Calculate pagination
            total_pages = (total_records + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # Execute query with pagination
            dealers = query.order_by(Dealer.dealer_name).offset(offset).limit(page_size).all()

            # Convert to response items
            dealer_items = []
            for dealer in dealers:
                # Check DGI API configuration (both api_key AND secret_key required)
                dgi_api_configured = bool(dealer.api_key and dealer.secret_key)

                # Check Google location configuration
                google_location_configured = bool(dealer.google_location_url)

                # Check WhatsApp/Fonnte API configuration (all 3 fields required)
                whatsapp_api_configured = bool(
                    dealer.phone_number and
                    dealer.fonnte_api_key and
                    dealer.fonnte_api_url
                )

                dealer_items.append(DealerListItem(
                    id=str(dealer.id),
                    dealer_id=dealer.dealer_id,
                    dealer_name=dealer.dealer_name,
                    is_active=dealer.is_active,
                    dgi_api_configured=dgi_api_configured,
                    google_location_configured=google_location_configured,
                    whatsapp_api_configured=whatsapp_api_configured,
                    created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                    updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
                ))

            logger.info(f"Found {total_records} dealers, returning page {page}/{total_pages}")

            return DealerListResponse(
                success=True,
                message="Dealers retrieved successfully",
                data=dealer_items,
                total_records=total_records,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error getting dealers: {str(e)}")
            return DealerListResponse(
                success=False,
                message=f"Error retrieving dealers: {str(e)}",
                data=[],
                total_records=0,
                page=page,
                page_size=page_size,
                total_pages=0
            )

    async def get_dealer_by_id(self, dealer_id: str) -> DealerResponse:
        """
        Get single dealer by ID

        Args:
            dealer_id: Dealer ID to retrieve

        Returns:
            DealerResponse with dealer details
        """
        try:
            logger.info(f"Getting dealer by ID: {dealer_id}")

            dealer = self.db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()

            if not dealer:
                logger.warning(f"Dealer not found: {dealer_id}")
                return None

            return DealerResponse(
                id=str(dealer.id),
                dealer_id=dealer.dealer_id,
                dealer_name=dealer.dealer_name,
                api_key=dealer.api_key,
                api_token=dealer.api_token,
                secret_key=dealer.secret_key,
                fonnte_api_key=dealer.fonnte_api_key,
                fonnte_api_url=dealer.fonnte_api_url,
                phone_number=dealer.phone_number,
                google_location_url=dealer.google_location_url,
                is_active=dealer.is_active,
                created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
            )

        except Exception as e:
            logger.error(f"Error getting dealer by ID: {str(e)}")
            return None

    async def update_dealer(
        self,
        dealer_id: str,
        update_data: DealerUpdateRequest
    ) -> DealerUpdateResponse:
        """
        Update dealer information

        Args:
            dealer_id: Dealer ID to update
            update_data: Update data

        Returns:
            DealerUpdateResponse with updated dealer
        """
        try:
            logger.info(f"Updating dealer: {dealer_id}")

            dealer = self.db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()

            if not dealer:
                logger.warning(f"Dealer not found: {dealer_id}")
                return DealerUpdateResponse(
                    success=False,
                    message=f"Dealer not found: {dealer_id}",
                    data=None
                )

            # Update fields if provided
            if update_data.dealer_name is not None:
                dealer.dealer_name = update_data.dealer_name

            if update_data.api_key is not None:
                dealer.api_key = update_data.api_key

            if update_data.api_token is not None:
                dealer.api_token = update_data.api_token

            if update_data.secret_key is not None:
                dealer.secret_key = update_data.secret_key

            if update_data.fonnte_api_key is not None:
                dealer.fonnte_api_key = update_data.fonnte_api_key

            if update_data.fonnte_api_url is not None:
                dealer.fonnte_api_url = update_data.fonnte_api_url

            if update_data.phone_number is not None:
                dealer.phone_number = update_data.phone_number

            if update_data.google_location_url is not None:
                dealer.google_location_url = update_data.google_location_url

            if update_data.is_active is not None:
                dealer.is_active = update_data.is_active

            # Update timestamp
            dealer.updated_at = datetime.utcnow()

            # Commit changes
            self.db.commit()
            self.db.refresh(dealer)

            logger.info(f"Dealer updated successfully: {dealer_id}")

            # Return updated dealer
            dealer_response = DealerResponse(
                id=str(dealer.id),
                dealer_id=dealer.dealer_id,
                dealer_name=dealer.dealer_name,
                api_key=dealer.api_key,
                api_token=dealer.api_token,
                secret_key=dealer.secret_key,
                fonnte_api_key=dealer.fonnte_api_key,
                fonnte_api_url=dealer.fonnte_api_url,
                phone_number=dealer.phone_number,
                google_location_url=dealer.google_location_url,
                is_active=dealer.is_active,
                created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
            )

            return DealerUpdateResponse(
                success=True,
                message="Dealer updated successfully",
                data=dealer_response
            )

        except Exception as e:
            logger.error(f"Error updating dealer: {str(e)}")
            self.db.rollback()
            return DealerUpdateResponse(
                success=False,
                message=f"Error updating dealer: {str(e)}",
                data=None
            )

    async def toggle_dealer_status(
        self,
        dealer_id: str,
        is_active: bool
    ) -> DealerStatusResponse:
        """
        Toggle dealer active/inactive status

        Args:
            dealer_id: Dealer ID to update
            is_active: New active status

        Returns:
            DealerStatusResponse with updated dealer
        """
        try:
            logger.info(f"Toggling dealer status: {dealer_id} -> {is_active}")

            dealer = self.db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()

            if not dealer:
                logger.warning(f"Dealer not found: {dealer_id}")
                return DealerStatusResponse(
                    success=False,
                    message=f"Dealer not found: {dealer_id}",
                    data=None
                )

            # Update status
            dealer.is_active = is_active
            dealer.updated_at = datetime.utcnow()

            # Commit changes
            self.db.commit()
            self.db.refresh(dealer)

            status_text = "activated" if is_active else "deactivated"
            logger.info(f"Dealer {status_text} successfully: {dealer_id}")

            # Return updated dealer
            dealer_response = DealerResponse(
                id=str(dealer.id),
                dealer_id=dealer.dealer_id,
                dealer_name=dealer.dealer_name,
                api_key=dealer.api_key,
                api_token=dealer.api_token,
                secret_key=dealer.secret_key,
                fonnte_api_key=dealer.fonnte_api_key,
                fonnte_api_url=dealer.fonnte_api_url,
                phone_number=dealer.phone_number,
                google_location_url=dealer.google_location_url,
                is_active=dealer.is_active,
                created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
            )

            return DealerStatusResponse(
                success=True,
                message=f"Dealer {status_text} successfully",
                data=dealer_response
            )

        except Exception as e:
            logger.error(f"Error toggling dealer status: {str(e)}")
            self.db.rollback()
            return DealerStatusResponse(
                success=False,
                message=f"Error updating dealer status: {str(e)}",
                data=None
            )
