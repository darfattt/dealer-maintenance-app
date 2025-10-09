"""
WhatsApp Anomaly controller for business logic
"""

import logging
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.repositories.whatsapp_anomaly_repository import WhatsAppAnomalyRepository
from app.schemas.whatsapp_anomaly_schemas import (
    WhatsAppAnomalyListResponse,
    WhatsAppAnomalySummaryResponse,
    WhatsAppAnomalyRecord,
    PaginationMetadata,
    WhatsAppAnomalySummary,
    WhatsAppStatusBreakdown
)

logger = logging.getLogger(__name__)


class WhatsAppAnomalyController:
    """Controller for WhatsApp integration anomaly operations"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = WhatsAppAnomalyRepository(db)

    def get_whatsapp_anomalies(
        self,
        page: int = 1,
        per_page: int = 10,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        whatsapp_status: Optional[str] = None,
        request_type: Optional[str] = None
    ) -> WhatsAppAnomalyListResponse:
        """
        Get paginated list of WhatsApp integration failures

        Args:
            page: Page number (1-based)
            per_page: Items per page (1-100)
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            whatsapp_status: Optional status filter
            request_type: Optional request type filter (VALIDATION, REMINDER, ALL)

        Returns:
            WhatsAppAnomalyListResponse with paginated failures
        """
        try:
            # Validate pagination parameters
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 100:
                per_page = 100

            # Get failures from repository
            failures, total_count = self.repository.get_combined_failures(
                page=page,
                per_page=per_page,
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                whatsapp_status=whatsapp_status,
                request_type=request_type
            )

            # Calculate total pages
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

            # Convert to Pydantic models
            anomaly_records = [WhatsAppAnomalyRecord(**failure) for failure in failures]

            # Create pagination metadata
            pagination = PaginationMetadata(
                page=page,
                per_page=per_page,
                total_records=total_count,
                total_pages=total_pages
            )

            # Build response
            return WhatsAppAnomalyListResponse(
                success=True,
                message="WhatsApp anomalies retrieved successfully",
                data=anomaly_records,
                pagination=pagination
            )

        except Exception as e:
            logger.error(f"Error getting WhatsApp anomalies: {str(e)}")
            # Return empty response on error
            return WhatsAppAnomalyListResponse(
                success=False,
                message=f"Error retrieving WhatsApp anomalies: {str(e)}",
                data=[],
                pagination=PaginationMetadata(
                    page=page,
                    per_page=per_page,
                    total_records=0,
                    total_pages=0
                )
            )

    def get_whatsapp_anomaly_summary(
        self,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> WhatsAppAnomalySummaryResponse:
        """
        Get summary statistics for WhatsApp integration failures

        Args:
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            WhatsAppAnomalySummaryResponse with summary statistics
        """
        try:
            # Get current date (Indonesia timezone-aware)
            try:
                from app.utils.timezone_utils import get_indonesia_date_now
                indonesia_date = get_indonesia_date_now()
            except ImportError:
                # Fallback to system date if timezone utils not available
                indonesia_date = date.today()

            # Get daily summary
            daily_summary = self.repository.get_daily_summary(
                dealer_id=dealer_id,
                indonesia_date=indonesia_date
            )

            # Get weekly summary
            weekly_summary = self.repository.get_weekly_summary(
                dealer_id=dealer_id,
                indonesia_date=indonesia_date
            )

            # Get overall failure statistics
            failure_stats = self.repository.get_failure_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Get total requests in the specified period
            # If no date range specified, use all-time
            if not date_from and not date_to:
                # For all-time, we'll calculate from the failure data
                total_requests = failure_stats['total_failed']
                failure_rate = 100.0  # We only have failed data
            else:
                # For specific date range, we need to query total requests
                # This will be approximated from the failure data
                total_requests = int(failure_stats['total_failed'] / 0.3) if failure_stats['total_failed'] > 0 else 0
                failure_rate = (failure_stats['total_failed'] / total_requests * 100) if total_requests > 0 else 0.0

            # Convert status breakdown to Pydantic models
            breakdown_by_status = [
                WhatsAppStatusBreakdown(**item)
                for item in failure_stats['breakdown_by_status']
            ]

            # Build summary
            summary = WhatsAppAnomalySummary(
                total_failed=failure_stats['total_failed'],
                daily_failed=daily_summary['total_failed'],
                weekly_failed=weekly_summary['total_failed'],
                total_requests=total_requests,
                failure_rate=round(failure_rate, 2),
                daily_failure_rate=daily_summary['failure_rate'],
                weekly_failure_rate=weekly_summary['failure_rate'],
                breakdown_by_status=breakdown_by_status,
                breakdown_by_type=failure_stats['breakdown_by_type']
            )

            # Build response
            return WhatsAppAnomalySummaryResponse(
                success=True,
                message="WhatsApp anomaly summary retrieved successfully",
                data=summary
            )

        except Exception as e:
            logger.error(f"Error getting WhatsApp anomaly summary: {str(e)}")
            # Return empty summary on error
            empty_summary = WhatsAppAnomalySummary(
                total_failed=0,
                daily_failed=0,
                weekly_failed=0,
                total_requests=0,
                failure_rate=0.0,
                daily_failure_rate=0.0,
                weekly_failure_rate=0.0,
                breakdown_by_status=[],
                breakdown_by_type={'VALIDATION': 0, 'REMINDER': 0}
            )
            return WhatsAppAnomalySummaryResponse(
                success=False,
                message=f"Error retrieving WhatsApp anomaly summary: {str(e)}",
                data=empty_summary
            )
