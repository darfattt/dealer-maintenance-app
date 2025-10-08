"""
Google Review Scrape Tracker repository for database operations
"""

import logging
from typing import List, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from sqlalchemy.exc import SQLAlchemyError

from app.models.google_review_scrape_tracker import GoogleReviewScrapeTracker

logger = logging.getLogger(__name__)


class GoogleReviewScrapeTrackerRepository:
    """Repository for Google Review Scrape Tracker operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_today_scrape_activities(self) -> List[GoogleReviewScrapeTracker]:
        """
        Get all Google Review scrape activities from today (no pagination)

        Returns:
            List of GoogleReviewScrapeTracker objects from today
        """
        try:
            # Get today's date range (00:00:00 to 23:59:59)
            today_start = datetime.combine(date.today(), datetime.min.time())
            today_end = datetime.combine(date.today(), datetime.max.time())

            return (
                self.db.query(GoogleReviewScrapeTracker)
                .filter(
                    GoogleReviewScrapeTracker.scrape_date >= today_start,
                    GoogleReviewScrapeTracker.scrape_date <= today_end
                )
                .order_by(GoogleReviewScrapeTracker.scrape_date.desc())
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting today's scrape activities: {str(e)}")
            return []

    def get_today_summary_by_dealer(self) -> List[Dict[str, Any]]:
        """
        Get aggregated summary of today's scrape activities grouped by dealer_id

        Returns:
            List of dictionaries containing dealer scrape summaries:
            - dealer_id
            - dealer_name
            - total_scrapes
            - completed_scrapes
            - failed_scrapes
            - processing_scrapes
            - partial_scrapes
            - total_reviews_scraped
            - total_new_reviews
            - total_duplicate_reviews
            - avg_scrape_duration_seconds
            - sentiment_analysis_enabled_count
            - sentiment_completed_count
        """
        try:
            # Get today's date range
            today_start = datetime.combine(date.today(), datetime.min.time())
            today_end = datetime.combine(date.today(), datetime.max.time())

            # Query aggregated data grouped by dealer_id
            results = (
                self.db.query(
                    GoogleReviewScrapeTracker.dealer_id,
                    func.max(GoogleReviewScrapeTracker.dealer_name).label('dealer_name'),
                    func.count(GoogleReviewScrapeTracker.id).label('total_scrapes'),
                    func.sum(
                        case(
                            (GoogleReviewScrapeTracker.scrape_status == 'COMPLETED', 1),
                            else_=0
                        )
                    ).label('completed_scrapes'),
                    func.sum(
                        case(
                            (GoogleReviewScrapeTracker.scrape_status == 'FAILED', 1),
                            else_=0
                        )
                    ).label('failed_scrapes'),
                    func.sum(
                        case(
                            (GoogleReviewScrapeTracker.scrape_status == 'PROCESSING', 1),
                            else_=0
                        )
                    ).label('processing_scrapes'),
                    func.sum(
                        case(
                            (GoogleReviewScrapeTracker.scrape_status == 'PARTIAL', 1),
                            else_=0
                        )
                    ).label('partial_scrapes'),
                    func.sum(GoogleReviewScrapeTracker.scraped_reviews).label('total_reviews_scraped'),
                    func.sum(GoogleReviewScrapeTracker.new_reviews).label('total_new_reviews'),
                    func.sum(GoogleReviewScrapeTracker.duplicate_reviews).label('total_duplicate_reviews'),
                    func.avg(GoogleReviewScrapeTracker.scrape_duration_seconds).label('avg_scrape_duration_seconds'),
                    func.sum(
                        case(
                            (GoogleReviewScrapeTracker.analyze_sentiment_enabled == True, 1),
                            else_=0
                        )
                    ).label('sentiment_analysis_enabled_count'),
                    func.sum(
                        case(
                            (GoogleReviewScrapeTracker.sentiment_analysis_status == 'COMPLETED', 1),
                            else_=0
                        )
                    ).label('sentiment_completed_count')
                )
                .filter(
                    GoogleReviewScrapeTracker.scrape_date >= today_start,
                    GoogleReviewScrapeTracker.scrape_date <= today_end,
                    GoogleReviewScrapeTracker.dealer_id.isnot(None)  # Only include records with dealer_id
                )
                .group_by(GoogleReviewScrapeTracker.dealer_id)
                .order_by(GoogleReviewScrapeTracker.dealer_id)
                .all()
            )

            # Format results
            summaries = []
            for row in results:
                summaries.append({
                    'dealer_id': row.dealer_id,
                    'dealer_name': row.dealer_name,
                    'total_scrapes': row.total_scrapes or 0,
                    'completed_scrapes': row.completed_scrapes or 0,
                    'failed_scrapes': row.failed_scrapes or 0,
                    'processing_scrapes': row.processing_scrapes or 0,
                    'partial_scrapes': row.partial_scrapes or 0,
                    'total_reviews_scraped': row.total_reviews_scraped or 0,
                    'total_new_reviews': row.total_new_reviews or 0,
                    'total_duplicate_reviews': row.total_duplicate_reviews or 0,
                    'avg_scrape_duration_seconds': float(row.avg_scrape_duration_seconds) if row.avg_scrape_duration_seconds else 0.0,
                    'sentiment_analysis_enabled_count': row.sentiment_analysis_enabled_count or 0,
                    'sentiment_completed_count': row.sentiment_completed_count or 0
                })

            return summaries

        except SQLAlchemyError as e:
            logger.error(f"Database error getting today's dealer scrape summary: {str(e)}")
            return []
