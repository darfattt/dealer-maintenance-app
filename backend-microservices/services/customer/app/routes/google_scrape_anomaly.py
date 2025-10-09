"""
FastAPI routes for Google scrape anomaly logging
"""

import logging
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.controllers.google_scrape_anomaly_controller import GoogleScrapeAnomalyController
from app.schemas.google_scrape_anomaly_schemas import (
    GoogleScrapeAnomalyListResponse,
    GoogleScrapeAnomalySummaryResponse
)
from app.dependencies import get_db, get_current_user, UserContext

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/google-scrape-anomalies",
    tags=["Google Scrape Anomalies"],
    responses={
        500: {"description": "Internal server error"}
    }
)


def get_google_scrape_anomaly_controller(db: Session = Depends(get_db)) -> GoogleScrapeAnomalyController:
    """
    Dependency to get Google Scrape Anomaly controller instance

    Args:
        db: Database session

    Returns:
        GoogleScrapeAnomalyController instance
    """
    return GoogleScrapeAnomalyController(db)


@router.get(
    "",
    response_model=GoogleScrapeAnomalyListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google Review Scrape Failures",
    description="""
    Retrieve paginated list of failed and partially failed Google Review scraping operations.

    **Features:**
    - **Pagination**: Configurable page size (1-100 items per page)
    - **Date Filtering**: Filter by scrape date range
    - **Dealer Filtering**: Filter by specific dealer ID
    - **Status Filtering**: Filter by scrape status (FAILED, PARTIAL, or both)
    - **Detailed Error Info**: Complete error messages and warning messages
    - **Performance Metrics**: Scrape duration and success rates

    **Scrape Status Values:**
    - **FAILED**: Scraping operation completely failed (0 reviews scraped)
    - **PARTIAL**: Some reviews scraped but operation didn't complete fully

    **Response Includes:**
    - Scrape tracker ID and dealer information
    - Scrape date/time and type (MANUAL/SCHEDULED)
    - Scraping results (requested, scraped, failed, new, duplicate reviews)
    - Success rate percentage
    - Complete error and warning messages
    - Scrape duration in seconds
    - API response IDs for debugging
    - Google Business information
    - Sentiment analysis status
    - User who initiated the scrape

    **Use Cases:**
    - Monitor and troubleshoot Google scraping failures
    - Identify patterns in scraping errors
    - Track API issues and rate limiting problems
    - Generate failure reports for specific date ranges
    - Admin dashboard for scraping health monitoring
    - Debug Apify API integration issues

    **Common Error Scenarios:**
    - Apify API connection timeout
    - Invalid Google location URL
    - Rate limiting exceeded
    - Google Business not found
    - Parsing errors from Google Maps data

    **Permissions:**
    - Requires valid JWT authentication
    - SUPER_ADMIN: Can view all anomalies across all dealers
    - DEALER_USER: Can view anomalies for their assigned dealer only
    """
)
async def get_google_scrape_anomalies(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD format)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD format)"),
    scrape_status: Optional[str] = Query(None, description="Filter by scrape status (FAILED, PARTIAL)"),
    current_user: UserContext = Depends(get_current_user),
    controller: GoogleScrapeAnomalyController = Depends(get_google_scrape_anomaly_controller)
) -> GoogleScrapeAnomalyListResponse:
    """
    Get paginated list of Google scrape failures

    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        dealer_id: Optional dealer ID filter
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)
        scrape_status: Optional status filter (FAILED, PARTIAL)
        current_user: Current authenticated user
        controller: Google Scrape Anomaly controller instance

    Returns:
        GoogleScrapeAnomalyListResponse with paginated failure records

    Raises:
        HTTPException: If unauthorized or query fails
    """
    try:
        # Apply dealer_id filter based on user role
        effective_dealer_id = dealer_id
        if current_user.role == "DEALER_USER" and current_user.dealer_id:
            # Dealer users can only see their own dealer's data
            effective_dealer_id = current_user.dealer_id
            logger.info(f"Dealer user {current_user.email} accessing scrape anomalies for dealer {effective_dealer_id}")

        # Get anomalies
        result = controller.get_scrape_anomalies(
            page=page,
            per_page=per_page,
            dealer_id=effective_dealer_id,
            date_from=date_from,
            date_to=date_to,
            scrape_status=scrape_status
        )

        return result

    except Exception as e:
        logger.error(f"Error in get_google_scrape_anomalies endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Google scrape anomalies: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=GoogleScrapeAnomalySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google Scrape Anomaly Summary Statistics",
    description="""
    Get comprehensive summary statistics for Google Review scraping failures including
    daily, weekly, and overall metrics.

    **Summary Statistics Include:**

    **Daily Metrics (Today):**
    - Total failed scrapes today
    - Daily failure rate percentage

    **Weekly Metrics (Past 7 Days):**
    - Total failed scrapes in past week
    - Weekly failure rate percentage

    **Overall Metrics:**
    - Total failed scrapes (in specified period or all-time)
    - Overall failure rate percentage
    - Total scrape attempts

    **Breakdown Analysis:**
    - **By Status**: Count and percentage for each failure status (FAILED, PARTIAL)
    - **By Type**: Count split between MANUAL and SCHEDULED scrapes
    - **Common Errors**: Top 10 most frequent error messages with occurrence counts

    **Use Cases:**
    - Dashboard KPI display and health monitoring
    - Trend analysis for scraping reliability
    - Identify most common failure reasons
    - Compare manual vs scheduled scrape failure rates
    - Generate executive summary reports
    - Set up alerting thresholds based on failure rates
    - API health monitoring and SLA tracking
    - Capacity planning for scraping operations

    **Filtering Options:**
    - **dealer_id**: Get summary for specific dealer
    - **date_from/date_to**: Calculate metrics for custom date range
    - No filters: Get all-time statistics across all dealers (SUPER_ADMIN only)

    **Response Format:**
    ```json
    {
        "success": true,
        "message": "Google scrape anomaly summary retrieved successfully",
        "data": {
            "total_failed": 45,
            "daily_failed": 5,
            "weekly_failed": 28,
            "total_scrapes": 150,
            "failure_rate": 30.0,
            "daily_failure_rate": 41.7,
            "weekly_failure_rate": 35.0,
            "breakdown_by_status": [
                {"status": "FAILED", "count": 30, "percentage": 66.7},
                {"status": "PARTIAL", "count": 15, "percentage": 33.3}
            ],
            "breakdown_by_type": {
                "MANUAL": 35,
                "SCHEDULED": 10
            },
            "common_errors": [
                {"error": "Apify API connection timeout", "count": 15},
                {"error": "Invalid Google location URL", "count": 10}
            ]
        }
    }
    ```

    **Insights from Common Errors:**
    - **API Timeout**: Network or Apify service issues
    - **Invalid URL**: Dealer configuration problems
    - **Rate Limiting**: Too many requests to Google Maps API
    - **Business Not Found**: Incorrect or outdated Google Business IDs
    - **Parsing Errors**: Changes in Google Maps HTML structure

    **Permissions:**
    - Requires valid JWT authentication
    - SUPER_ADMIN: Can view summary across all dealers
    - DEALER_USER: Can view summary for their assigned dealer only
    """
)
async def get_google_scrape_anomaly_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD format)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD format)"),
    current_user: UserContext = Depends(get_current_user),
    controller: GoogleScrapeAnomalyController = Depends(get_google_scrape_anomaly_controller)
) -> GoogleScrapeAnomalySummaryResponse:
    """
    Get summary statistics for Google scrape failures

    Args:
        dealer_id: Optional dealer ID filter
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)
        current_user: Current authenticated user
        controller: Google Scrape Anomaly controller instance

    Returns:
        GoogleScrapeAnomalySummaryResponse with summary statistics

    Raises:
        HTTPException: If unauthorized or query fails
    """
    try:
        # Apply dealer_id filter based on user role
        effective_dealer_id = dealer_id
        if current_user.role == "DEALER_USER" and current_user.dealer_id:
            # Dealer users can only see their own dealer's data
            effective_dealer_id = current_user.dealer_id
            logger.info(f"Dealer user {current_user.email} accessing scrape anomaly summary for dealer {effective_dealer_id}")

        # Get summary
        result = controller.get_scrape_anomaly_summary(
            dealer_id=effective_dealer_id,
            date_from=date_from,
            date_to=date_to
        )

        return result

    except Exception as e:
        logger.error(f"Error in get_google_scrape_anomaly_summary endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Google scrape anomaly summary: {str(e)}"
        )
