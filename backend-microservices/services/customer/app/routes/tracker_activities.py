"""
Tracker activities routes for Google Review Scrape Tracker and Customer Satisfaction Upload Tracker
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

from app.schemas.tracker_schemas import (
    GoogleReviewScrapeTrackerResponse,
    GoogleReviewScrapeTrackerListResponse,
    DealerScrapeStatsResponse,
    DealerScrapeStatsListResponse,
    CustomerSatisfactionUploadTrackerResponse,
    CustomerSatisfactionUploadTrackerListResponse
)
from app.repositories.google_review_scrape_tracker_repository import GoogleReviewScrapeTrackerRepository
from app.repositories.customer_satisfaction_repository import CustomerSatisfactionRepository
from utils.database import DatabaseManager
from utils.logger import setup_logger
from app.dependencies import get_current_user

logger = setup_logger(__name__)

# Import settings
from app.config import settings

# Create database manager
db_manager = DatabaseManager(settings.db_schema)

router = APIRouter(prefix="/trackers", tags=["Tracker Activities"])


def get_db():
    """Get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()


@router.get("/google-reviews/today", response_model=GoogleReviewScrapeTrackerListResponse)
def get_today_google_review_scrapes(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all Google Review scrape activities from today (no pagination, no filters)

    Only admins can access this endpoint.
    Returns all scrape activities from 00:00:00 today to current time.
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
            detail="Only administrators can access Google Review scrape activities"
        )

    logger.info(f"Admin {current_user.email} accessing today's Google Review scrape activities")

    # Get today's scrape activities
    scrape_tracker_repo = GoogleReviewScrapeTrackerRepository(db)
    activities = scrape_tracker_repo.get_today_scrape_activities()

    # Convert to response models
    activity_responses = [
        GoogleReviewScrapeTrackerResponse(
            id=str(activity.id),
            dealer_id=activity.dealer_id,
            dealer_name=activity.dealer_name,
            scrape_type=activity.scrape_type,
            max_reviews_requested=activity.max_reviews_requested,
            language=activity.language,
            scrape_status=activity.scrape_status,
            total_reviews_available=activity.total_reviews_available,
            scraped_reviews=activity.scraped_reviews,
            failed_reviews=activity.failed_reviews,
            new_reviews=activity.new_reviews,
            duplicate_reviews=activity.duplicate_reviews,
            analyze_sentiment_enabled=activity.analyze_sentiment_enabled,
            sentiment_analysis_status=activity.sentiment_analysis_status,
            sentiment_analyzed_count=activity.sentiment_analyzed_count,
            sentiment_failed_count=activity.sentiment_failed_count,
            sentiment_batch_id=str(activity.sentiment_batch_id) if activity.sentiment_batch_id else None,
            api_response_id=activity.api_response_id,
            google_business_id=activity.google_business_id,
            business_name=activity.business_name,
            business_rating=activity.business_rating,
            error_message=activity.error_message,
            warning_message=activity.warning_message,
            scrape_duration_seconds=activity.scrape_duration_seconds,
            sentiment_duration_seconds=activity.sentiment_duration_seconds,
            scraped_by=activity.scraped_by,
            scrape_date=activity.scrape_date.isoformat() if activity.scrape_date else None,
            completed_date=activity.completed_date.isoformat() if activity.completed_date else None,
            last_updated=activity.last_updated.isoformat() if activity.last_updated else None
        )
        for activity in activities
    ]

    return GoogleReviewScrapeTrackerListResponse(
        date=date.today().isoformat(),
        total=len(activity_responses),
        activities=activity_responses
    )


@router.get("/google-reviews/today/summary-by-dealer", response_model=DealerScrapeStatsListResponse)
def get_today_google_review_summary_by_dealer(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of today's Google Review scrape activities grouped by dealer_id

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
            detail="Only administrators can access Google Review scrape summaries"
        )

    logger.info(f"Admin {current_user.email} accessing today's Google Review dealer summary")

    # Get today's dealer summary
    scrape_tracker_repo = GoogleReviewScrapeTrackerRepository(db)
    summaries = scrape_tracker_repo.get_today_summary_by_dealer()

    # Convert to response models
    summary_responses = [
        DealerScrapeStatsResponse(
            dealer_id=summary['dealer_id'],
            dealer_name=summary['dealer_name'],
            total_scrapes=summary['total_scrapes'],
            completed_scrapes=summary['completed_scrapes'],
            failed_scrapes=summary['failed_scrapes'],
            processing_scrapes=summary['processing_scrapes'],
            partial_scrapes=summary['partial_scrapes'],
            total_reviews_scraped=summary['total_reviews_scraped'],
            total_new_reviews=summary['total_new_reviews'],
            total_duplicate_reviews=summary['total_duplicate_reviews'],
            avg_scrape_duration_seconds=summary['avg_scrape_duration_seconds'],
            sentiment_analysis_enabled_count=summary['sentiment_analysis_enabled_count'],
            sentiment_completed_count=summary['sentiment_completed_count']
        )
        for summary in summaries
    ]

    return DealerScrapeStatsListResponse(
        date=date.today().isoformat(),
        total_dealers=len(summary_responses),
        summaries=summary_responses
    )


@router.get("/customer-satisfaction/today", response_model=CustomerSatisfactionUploadTrackerListResponse)
def get_today_customer_satisfaction_uploads(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all Customer Satisfaction upload trackers from today (no pagination, no filters)

    Only admins can access this endpoint.
    Returns all upload activities from 00:00:00 today to current time.
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
            detail="Only administrators can access Customer Satisfaction upload trackers"
        )

    logger.info(f"Admin {current_user.email} accessing today's Customer Satisfaction upload trackers")

    # Get today's upload trackers
    satisfaction_repo = CustomerSatisfactionRepository(db)
    uploads = satisfaction_repo.get_today_upload_trackers()

    # Convert to response models
    upload_responses = [
        CustomerSatisfactionUploadTrackerResponse(
            id=str(upload.id),
            file_name=upload.file_name,
            file_size=upload.file_size,
            total_records=upload.total_records,
            successful_records=upload.successful_records,
            failed_records=upload.failed_records,
            upload_status=upload.upload_status,
            error_message=upload.error_message,
            uploaded_by=upload.uploaded_by,
            upload_date=upload.upload_date.isoformat() if upload.upload_date else None,
            completed_date=upload.completed_date.isoformat() if upload.completed_date else None
        )
        for upload in uploads
    ]

    return CustomerSatisfactionUploadTrackerListResponse(
        date=date.today().isoformat(),
        total=len(upload_responses),
        uploads=upload_responses
    )
