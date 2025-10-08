"""
API request log routes
"""

import sys
import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Add utils and parent paths
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if parent_path not in sys.path:
    sys.path.append(parent_path)

from app.schemas.api_request_log import (
    ApiRequestLogResponse,
    ApiRequestLogListResponse,
    DealerSummaryResponse,
    DealerSummaryListResponse
)
from app.repositories.api_request_log_repository import ApiRequestLogRepository
from utils.database import DatabaseManager
from utils.logger import setup_logger
from app.dependencies import get_current_user

logger = setup_logger(__name__)

# Import settings
from app.config import settings

# Create database manager
db_manager = DatabaseManager(settings.db_schema)

router = APIRouter(prefix="/api-logs", tags=["API Request Logs"])


def get_db():
    """Get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()


@router.get("/today", response_model=ApiRequestLogListResponse)
def get_today_api_logs(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all API request logs from today (no pagination, no filters)

    Only admins can access this endpoint.
    Returns all API logs from 00:00:00 today to current time in Indonesia timezone (WIB/UTC+7).
    """
    # Check if user has admin permissions
    # Assuming user has a 'role' attribute with values like 'SUPER_ADMIN', 'SYSTEM_ADMIN'
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for admin roles
    admin_roles = ['SUPER_ADMIN', 'SYSTEM_ADMIN']
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if user_role not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access API request logs"
        )

    logger.info(f"Admin {current_user.email} accessing today's API logs")

    from app.utils.timezone_utils import get_indonesia_datetime

    # Get today's logs using Indonesia timezone
    api_log_repo = ApiRequestLogRepository(db)
    indonesia_now = get_indonesia_datetime()
    logs = api_log_repo.get_today_request_logs(indonesia_date=indonesia_now.date())

    # Convert to response models
    log_responses = [
        ApiRequestLogResponse(
            id=str(log.id),
            request_name=log.request_name,
            dealer_id=log.dealer_id,
            request_method=log.request_method,
            endpoint=log.endpoint,
            request_payload=log.request_payload,
            request_headers=log.request_headers,
            request_ip=log.request_ip,
            user_email=log.user_email,
            response_status=log.response_status,
            response_code=log.response_code,
            response_data=log.response_data,
            error_message=log.error_message,
            processing_time_ms=log.processing_time_ms,
            request_timestamp=log.request_timestamp,
            response_timestamp=log.response_timestamp,
            created_date=log.created_date
        )
        for log in logs
    ]

    return ApiRequestLogListResponse(
        date=indonesia_now.date().isoformat(),
        total=len(log_responses),
        logs=log_responses
    )


@router.get("/today/summary-by-dealer", response_model=DealerSummaryListResponse)
def get_today_summary_by_dealer(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of today's API requests grouped by dealer_id

    Only admins can access this endpoint.
    Returns aggregated statistics per dealer for today.
    """
    # Check if user has admin permissions
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for admin roles
    admin_roles = ['SUPER_ADMIN', 'SYSTEM_ADMIN']
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if user_role not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access API request summaries"
        )

    logger.info(f"Admin {current_user.email} accessing today's dealer summary")

    from app.utils.timezone_utils import get_indonesia_datetime

    # Get today's summary using Indonesia timezone
    api_log_repo = ApiRequestLogRepository(db)
    indonesia_now = get_indonesia_datetime()
    summaries = api_log_repo.get_today_summary_by_dealer(indonesia_date=indonesia_now.date())

    # Convert to response models
    summary_responses = [
        DealerSummaryResponse(
            dealer_id=summary['dealer_id'],
            total_requests=summary['total_requests'],
            successful_requests=summary['successful_requests'],
            failed_requests=summary['failed_requests'],
            avg_processing_time_ms=summary['avg_processing_time_ms'],
            request_count_by_type=summary['request_count_by_type']
        )
        for summary in summaries
    ]

    return DealerSummaryListResponse(
        date=indonesia_now.date().isoformat(),
        total_dealers=len(summary_responses),
        summaries=summary_responses
    )


@router.get("/weekly/summary-by-dealer", response_model=DealerSummaryListResponse)
def get_weekly_summary_by_dealer(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of this week's API requests grouped by dealer_id

    Only admins can access this endpoint.
    Returns aggregated statistics per dealer for the current week (Monday to Sunday) in Indonesia timezone (WIB/UTC+7).
    """
    # Check if user has admin permissions
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for admin roles
    admin_roles = ['SUPER_ADMIN', 'SYSTEM_ADMIN']
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if user_role not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access API request summaries"
        )

    logger.info(f"Admin {current_user.email} accessing weekly dealer summary")

    from app.utils.timezone_utils import get_indonesia_datetime
    from datetime import timedelta

    # Get this week's summary using Indonesia timezone
    api_log_repo = ApiRequestLogRepository(db)
    indonesia_now = get_indonesia_datetime()
    summaries = api_log_repo.get_weekly_summary_by_dealer(indonesia_date=indonesia_now.date())

    # Calculate week start and end dates for display
    days_since_monday = indonesia_now.date().weekday()
    week_start_date = indonesia_now.date() - timedelta(days=days_since_monday)
    week_end_date = week_start_date + timedelta(days=6)
    week_range = f"{week_start_date.isoformat()} to {week_end_date.isoformat()}"

    # Convert to response models
    summary_responses = [
        DealerSummaryResponse(
            dealer_id=summary['dealer_id'],
            total_requests=summary['total_requests'],
            successful_requests=summary['successful_requests'],
            failed_requests=summary['failed_requests'],
            avg_processing_time_ms=summary['avg_processing_time_ms'],
            request_count_by_type=summary['request_count_by_type']
        )
        for summary in summaries
    ]

    return DealerSummaryListResponse(
        date=week_range,
        total_dealers=len(summary_responses),
        summaries=summary_responses
    )
