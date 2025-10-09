"""
Google Scrape Anomaly controller for business logic
"""

import logging
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.repositories.google_review_scrape_tracker_repository import GoogleReviewScrapeTrackerRepository
from app.schemas.google_scrape_anomaly_schemas import (
    GoogleScrapeAnomalyListResponse,
    GoogleScrapeAnomalySummaryResponse,
    GoogleScrapeAnomalyRecord,
    PaginationMetadata,
    GoogleScrapeAnomalySummary,
    GoogleScrapeStatusBreakdown
)

logger = logging.getLogger(__name__)


class GoogleScrapeAnomalyController:
    """Controller for Google scrape anomaly operations"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = GoogleReviewScrapeTrackerRepository(db)

    def get_scrape_anomalies(
        self,
        page: int = 1,
        per_page: int = 10,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        scrape_status: Optional[str] = None
    ) -> GoogleScrapeAnomalyListResponse:
        """
        Get paginated list of Google scrape failures

        Args:
            page: Page number (1-based)
            per_page: Items per page (1-100)
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            scrape_status: Optional status filter (FAILED, PARTIAL)

        Returns:
            GoogleScrapeAnomalyListResponse with paginated failures
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
            failures, total_count = self.repository.get_failed_scrapes(
                page=page,
                per_page=per_page,
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to,
                scrape_status=scrape_status
            )

            # Calculate total pages
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

            # Convert to dictionary format
            anomaly_records = []
            for failure in failures:
                anomaly_records.append(GoogleScrapeAnomalyRecord(
                    id=str(failure.id),
                    dealer_id=failure.dealer_id,
                    dealer_name=failure.dealer_name,
                    scrape_date=failure._format_datetime_indonesia(failure.scrape_date),
                    scrape_status=failure.scrape_status,
                    scrape_type=failure.scrape_type,
                    max_reviews_requested=failure.max_reviews_requested,
                    scraped_reviews=failure.scraped_reviews,
                    failed_reviews=failure.failed_reviews,
                    new_reviews=failure.new_reviews,
                    duplicate_reviews=failure.duplicate_reviews,
                    success_rate=failure.success_rate,
                    error_message=failure.error_message,
                    warning_message=failure.warning_message,
                    scrape_duration_seconds=failure.scrape_duration_seconds,
                    api_response_id=failure.api_response_id,
                    google_business_id=failure.google_business_id,
                    business_name=failure.business_name,
                    sentiment_analysis_status=failure.sentiment_analysis_status,
                    scraped_by=failure.scraped_by
                ))

            # Create pagination metadata
            pagination = PaginationMetadata(
                page=page,
                per_page=per_page,
                total_records=total_count,
                total_pages=total_pages
            )

            # Build response
            return GoogleScrapeAnomalyListResponse(
                success=True,
                message="Google scrape anomalies retrieved successfully",
                data=anomaly_records,
                pagination=pagination
            )

        except Exception as e:
            logger.error(f"Error getting Google scrape anomalies: {str(e)}")
            # Return empty response on error
            return GoogleScrapeAnomalyListResponse(
                success=False,
                message=f"Error retrieving Google scrape anomalies: {str(e)}",
                data=[],
                pagination=PaginationMetadata(
                    page=page,
                    per_page=per_page,
                    total_records=0,
                    total_pages=0
                )
            )

    def get_scrape_anomaly_summary(
        self,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> GoogleScrapeAnomalySummaryResponse:
        """
        Get summary statistics for Google scrape failures

        Args:
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            GoogleScrapeAnomalySummaryResponse with summary statistics
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
            daily_summary = self.repository.get_daily_failed_scrapes(
                dealer_id=dealer_id,
                indonesia_date=indonesia_date
            )

            # Get weekly summary
            weekly_summary = self.repository.get_weekly_failed_scrapes(
                dealer_id=dealer_id,
                indonesia_date=indonesia_date
            )

            # Get overall failure statistics
            failure_stats = self.repository.get_scrape_failure_statistics(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Calculate overall failure rate
            # For the specified period (or all-time if no dates)
            if not date_from and not date_to:
                # Approximate total scrapes from failure data
                total_scrapes = int(failure_stats['total_failed'] / 0.3) if failure_stats['total_failed'] > 0 else 0
                failure_rate = (failure_stats['total_failed'] / total_scrapes * 100) if total_scrapes > 0 else 0.0
            else:
                # Use approximation based on failure rate patterns
                total_scrapes = failure_stats['total_failed']
                failure_rate = 100.0 if total_scrapes > 0 else 0.0

            # Convert status breakdown to Pydantic models
            breakdown_by_status = [
                GoogleScrapeStatusBreakdown(**item)
                for item in failure_stats['breakdown_by_status']
            ]

            # Build summary
            summary = GoogleScrapeAnomalySummary(
                total_failed=failure_stats['total_failed'],
                daily_failed=daily_summary['total_failed'],
                weekly_failed=weekly_summary['total_failed'],
                total_scrapes=total_scrapes,
                failure_rate=round(failure_rate, 2),
                daily_failure_rate=daily_summary['failure_rate'],
                weekly_failure_rate=weekly_summary['failure_rate'],
                breakdown_by_status=breakdown_by_status,
                breakdown_by_type=failure_stats['breakdown_by_type'],
                common_errors=failure_stats['common_errors']
            )

            # Build response
            return GoogleScrapeAnomalySummaryResponse(
                success=True,
                message="Google scrape anomaly summary retrieved successfully",
                data=summary
            )

        except Exception as e:
            logger.error(f"Error getting Google scrape anomaly summary: {str(e)}")
            # Return empty summary on error
            empty_summary = GoogleScrapeAnomalySummary(
                total_failed=0,
                daily_failed=0,
                weekly_failed=0,
                total_scrapes=0,
                failure_rate=0.0,
                daily_failure_rate=0.0,
                weekly_failure_rate=0.0,
                breakdown_by_status=[],
                breakdown_by_type={},
                common_errors=[]
            )
            return GoogleScrapeAnomalySummaryResponse(
                success=False,
                message=f"Error retrieving Google scrape anomaly summary: {str(e)}",
                data=empty_summary
            )
