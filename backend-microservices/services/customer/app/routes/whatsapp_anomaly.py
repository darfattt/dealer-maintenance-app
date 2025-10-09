"""
FastAPI routes for WhatsApp integration anomaly logging
"""

import logging
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.controllers.whatsapp_anomaly_controller import WhatsAppAnomalyController
from app.schemas.whatsapp_anomaly_schemas import (
    WhatsAppAnomalyListResponse,
    WhatsAppAnomalySummaryResponse,
    RequestType
)
from app.dependencies import get_db, get_current_user, UserContext

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/whatsapp-anomalies",
    tags=["WhatsApp Anomalies"],
    responses={
        500: {"description": "Internal server error"}
    }
)


def get_whatsapp_anomaly_controller(db: Session = Depends(get_db)) -> WhatsAppAnomalyController:
    """
    Dependency to get WhatsApp Anomaly controller instance

    Args:
        db: Database session

    Returns:
        WhatsAppAnomalyController instance
    """
    return WhatsAppAnomalyController(db)


@router.get(
    "",
    response_model=WhatsAppAnomalyListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get WhatsApp Integration Failures",
    description="""
    Retrieve paginated list of failed WhatsApp integration attempts from both customer validation
    and customer reminder requests.

    **Features:**
    - **Pagination**: Configurable page size (1-100 items per page)
    - **Date Filtering**: Filter by request date range
    - **Dealer Filtering**: Filter by specific dealer ID
    - **Status Filtering**: Filter by WhatsApp status (FAILED, ERROR, REJECTED, NOT_SENT)
    - **Type Filtering**: Filter by request type (VALIDATION, REMINDER, or ALL)
    - **Phone Masking**: Customer phone numbers are masked for privacy
    - **Error Details**: Includes Fonnte API response and extracted error messages

    **Failed Status Values:**
    - **FAILED**: WhatsApp message delivery failed
    - **ERROR**: Error occurred during message sending
    - **REJECTED**: Message rejected by Fonnte API
    - **NOT_SENT**: Message was not sent

    **Response Includes:**
    - Request ID and dealer information
    - Request date and time
    - Customer name and masked phone number
    - WhatsApp status and message content
    - Complete Fonnte API response
    - Extracted error details
    - Pagination metadata (page, per_page, total_records, total_pages)

    **Use Cases:**
    - Monitor and troubleshoot WhatsApp integration failures
    - Identify patterns in failed message deliveries
    - Track customer communication issues
    - Generate failure reports for specific date ranges
    - Admin dashboard for integration health monitoring

    **Permissions:**
    - Requires valid JWT authentication
    - SUPER_ADMIN: Can view all anomalies across all dealers
    - DEALER_USER: Can view anomalies for their assigned dealer only
    """
)
async def get_whatsapp_anomalies(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD format)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD format)"),
    whatsapp_status: Optional[str] = Query(None, description="Filter by WhatsApp status (FAILED, ERROR, REJECTED, NOT_SENT)"),
    request_type: Optional[RequestType] = Query(RequestType.ALL, description="Filter by request type (VALIDATION, REMINDER, ALL)"),
    current_user: UserContext = Depends(get_current_user),
    controller: WhatsAppAnomalyController = Depends(get_whatsapp_anomaly_controller)
) -> WhatsAppAnomalyListResponse:
    """
    Get paginated list of WhatsApp integration failures

    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        dealer_id: Optional dealer ID filter
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)
        whatsapp_status: Optional status filter
        request_type: Optional request type filter (default: ALL)
        current_user: Current authenticated user
        controller: WhatsApp Anomaly controller instance

    Returns:
        WhatsAppAnomalyListResponse with paginated failure records

    Raises:
        HTTPException: If unauthorized or query fails
    """
    try:
        # Apply dealer_id filter based on user role
        effective_dealer_id = dealer_id
        if current_user.role == "DEALER_USER" and current_user.dealer_id:
            # Dealer users can only see their own dealer's data
            effective_dealer_id = current_user.dealer_id
            logger.info(f"Dealer user {current_user.email} accessing anomalies for dealer {effective_dealer_id}")

        # Get anomalies
        result = controller.get_whatsapp_anomalies(
            page=page,
            per_page=per_page,
            dealer_id=effective_dealer_id,
            date_from=date_from,
            date_to=date_to,
            whatsapp_status=whatsapp_status,
            request_type=request_type.value if request_type else None
        )

        return result

    except Exception as e:
        logger.error(f"Error in get_whatsapp_anomalies endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving WhatsApp anomalies: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=WhatsAppAnomalySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get WhatsApp Anomaly Summary Statistics",
    description="""
    Get comprehensive summary statistics for WhatsApp integration failures including
    daily, weekly, and overall metrics.

    **Summary Statistics Include:**

    **Daily Metrics (Today):**
    - Total failed integrations today
    - Daily failure rate percentage

    **Weekly Metrics (Past 7 Days):**
    - Total failed integrations in past week
    - Weekly failure rate percentage

    **Overall Metrics:**
    - Total failed integrations (in specified period or all-time)
    - Overall failure rate percentage
    - Total requests processed

    **Breakdown Analysis:**
    - **By Status**: Count and percentage for each failure status (FAILED, ERROR, REJECTED, NOT_SENT)
    - **By Type**: Count split between VALIDATION and REMINDER requests

    **Use Cases:**
    - Dashboard KPI display and health monitoring
    - Trend analysis for integration reliability
    - Identify most common failure reasons
    - Compare validation vs reminder failure rates
    - Generate executive summary reports
    - Set up alerting thresholds based on failure rates

    **Filtering Options:**
    - **dealer_id**: Get summary for specific dealer
    - **date_from/date_to**: Calculate metrics for custom date range
    - No filters: Get all-time statistics across all dealers (SUPER_ADMIN only)

    **Response Format:**
    ```json
    {
        "success": true,
        "message": "WhatsApp anomaly summary retrieved successfully",
        "data": {
            "total_failed": 150,
            "daily_failed": 12,
            "weekly_failed": 85,
            "total_requests": 500,
            "failure_rate": 30.0,
            "daily_failure_rate": 25.0,
            "weekly_failure_rate": 28.0,
            "breakdown_by_status": [
                {"status": "FAILED", "count": 90, "percentage": 60.0},
                {"status": "ERROR", "count": 45, "percentage": 30.0}
            ],
            "breakdown_by_type": {
                "VALIDATION": 80,
                "REMINDER": 70
            }
        }
    }
    ```

    **Permissions:**
    - Requires valid JWT authentication
    - SUPER_ADMIN: Can view summary across all dealers
    - DEALER_USER: Can view summary for their assigned dealer only
    """
)
async def get_whatsapp_anomaly_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD format)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD format)"),
    current_user: UserContext = Depends(get_current_user),
    controller: WhatsAppAnomalyController = Depends(get_whatsapp_anomaly_controller)
) -> WhatsAppAnomalySummaryResponse:
    """
    Get summary statistics for WhatsApp integration failures

    Args:
        dealer_id: Optional dealer ID filter
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)
        current_user: Current authenticated user
        controller: WhatsApp Anomaly controller instance

    Returns:
        WhatsAppAnomalySummaryResponse with summary statistics

    Raises:
        HTTPException: If unauthorized or query fails
    """
    try:
        # Apply dealer_id filter based on user role
        effective_dealer_id = dealer_id
        if current_user.role == "DEALER_USER" and current_user.dealer_id:
            # Dealer users can only see their own dealer's data
            effective_dealer_id = current_user.dealer_id
            logger.info(f"Dealer user {current_user.email} accessing anomaly summary for dealer {effective_dealer_id}")

        # Get summary
        result = controller.get_whatsapp_anomaly_summary(
            dealer_id=effective_dealer_id,
            date_from=date_from,
            date_to=date_to
        )

        return result

    except Exception as e:
        logger.error(f"Error in get_whatsapp_anomaly_summary endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving WhatsApp anomaly summary: {str(e)}"
        )
