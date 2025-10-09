"""
Google Review Scrape Tracker repository for database operations
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from app.models.google_review_scrape_tracker import GoogleReviewScrapeTracker

logger = logging.getLogger(__name__)


class GoogleReviewScrapeTrackerRepository:
    """Repository for Google Review Scrape Tracker operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_today_scrape_activities(self, indonesia_date=None) -> List[GoogleReviewScrapeTracker]:
        """
        Get all Google Review scrape activities from today (no pagination)

        Args:
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            List of GoogleReviewScrapeTracker objects from today
        """
        try:
            # Get today's date range (00:00:00 to 23:59:59)
            # Use provided Indonesia date or fallback to system date
            today_date = indonesia_date if indonesia_date else date.today()
            today_start = datetime.combine(today_date, datetime.min.time())
            today_end = datetime.combine(today_date, datetime.max.time())

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

    def get_today_summary_by_dealer(self, indonesia_date=None) -> List[Dict[str, Any]]:
        """
        Get aggregated summary of today's scrape activities grouped by dealer_id

        Args:
            indonesia_date: Optional date object representing today in Indonesia timezone

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
            # Use provided Indonesia date or fallback to system date
            today_date = indonesia_date if indonesia_date else date.today()
            today_start = datetime.combine(today_date, datetime.min.time())
            today_end = datetime.combine(today_date, datetime.max.time())

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

    def get_weekly_summary_by_dealer(self, indonesia_date=None) -> List[Dict[str, Any]]:
        """
        Get aggregated summary of ALL weeks' scrape activities grouped by week and dealer_id

        Week is defined as Monday 00:00:00 to Sunday 23:59:59 in Indonesia timezone.

        Args:
            indonesia_date: Not used, kept for backward compatibility

        Returns:
            List of dictionaries containing weekly dealer scrape summaries:
            - week_start_date (ISO format)
            - week_end_date (ISO format)
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
            from datetime import timedelta

            # Query aggregated data grouped by week and dealer_id
            # Using date_trunc to group by week (Monday-based)
            results = (
                self.db.query(
                    func.date_trunc('week', GoogleReviewScrapeTracker.scrape_date).label('week_start'),
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
                    GoogleReviewScrapeTracker.dealer_id.isnot(None)  # Only include records with dealer_id
                )
                .group_by(func.date_trunc('week', GoogleReviewScrapeTracker.scrape_date), GoogleReviewScrapeTracker.dealer_id)
                .order_by(func.date_trunc('week', GoogleReviewScrapeTracker.scrape_date).desc(), GoogleReviewScrapeTracker.dealer_id)
                .all()
            )

            # Format results
            summaries = []
            for row in results:
                week_start_datetime = row.week_start

                # Calculate week end date (Sunday)
                week_start_date = week_start_datetime.date()
                week_end_date = week_start_date + timedelta(days=6)

                summaries.append({
                    'week_start_date': week_start_date.isoformat(),
                    'week_end_date': week_end_date.isoformat(),
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
            logger.error(f"Database error getting weekly dealer scrape summary: {str(e)}")
            return []

    # Anomaly tracking methods
    def get_failed_scrapes(
        self,
        page: int = 1,
        per_page: int = 10,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        scrape_status: Optional[str] = None
    ) -> Tuple[List[GoogleReviewScrapeTracker], int]:
        """
        Get failed and partial scrape operations with pagination

        Args:
            page: Page number (1-based)
            per_page: Items per page
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            scrape_status: Optional status filter (FAILED, PARTIAL)

        Returns:
            Tuple of (list of GoogleReviewScrapeTracker objects, total count)
        """
        try:
            # Failed statuses
            if scrape_status:
                status_filter = [scrape_status]
            else:
                status_filter = ['FAILED', 'PARTIAL']

            # Build base query
            query = self.db.query(GoogleReviewScrapeTracker).filter(
                GoogleReviewScrapeTracker.scrape_status.in_(status_filter)
            )

            # Apply filters
            if dealer_id:
                query = query.filter(GoogleReviewScrapeTracker.dealer_id == dealer_id)

            if date_from:
                date_from_start = datetime.combine(date_from, datetime.min.time())
                query = query.filter(GoogleReviewScrapeTracker.scrape_date >= date_from_start)

            if date_to:
                date_to_end = datetime.combine(date_to, datetime.max.time())
                query = query.filter(GoogleReviewScrapeTracker.scrape_date <= date_to_end)

            # Get total count
            total_count = query.count()

            # Apply ordering and pagination
            offset = (page - 1) * per_page
            results = query.order_by(GoogleReviewScrapeTracker.scrape_date.desc()).offset(offset).limit(per_page).all()

            return results, total_count

        except SQLAlchemyError as e:
            logger.error(f"Database error getting failed scrapes: {str(e)}")
            return [], 0

    def get_daily_failed_scrapes(self, dealer_id: Optional[str] = None, indonesia_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get daily summary of failed scrapes for today

        Args:
            dealer_id: Optional dealer ID filter
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            Dictionary with daily failure statistics
        """
        try:
            # Get today's date range
            today_date = indonesia_date if indonesia_date else date.today()
            today_start = datetime.combine(today_date, datetime.min.time())
            today_end = datetime.combine(today_date, datetime.max.time())

            # Failed statuses
            failed_statuses = ['FAILED', 'PARTIAL']

            # Count failures
            failed_query = self.db.query(func.count(GoogleReviewScrapeTracker.id)).filter(
                GoogleReviewScrapeTracker.scrape_date >= today_start,
                GoogleReviewScrapeTracker.scrape_date <= today_end,
                GoogleReviewScrapeTracker.scrape_status.in_(failed_statuses)
            )
            if dealer_id:
                failed_query = failed_query.filter(GoogleReviewScrapeTracker.dealer_id == dealer_id)
            failed_count = failed_query.scalar() or 0

            # Count total scrapes
            total_query = self.db.query(func.count(GoogleReviewScrapeTracker.id)).filter(
                GoogleReviewScrapeTracker.scrape_date >= today_start,
                GoogleReviewScrapeTracker.scrape_date <= today_end
            )
            if dealer_id:
                total_query = total_query.filter(GoogleReviewScrapeTracker.dealer_id == dealer_id)
            total_count = total_query.scalar() or 0

            # Calculate failure rate
            failure_rate = (failed_count / total_count * 100) if total_count > 0 else 0.0

            return {
                'date': today_date.isoformat(),
                'total_failed': failed_count,
                'total_scrapes': total_count,
                'failure_rate': round(failure_rate, 2)
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting daily failed scrapes: {str(e)}")
            return {
                'date': date.today().isoformat(),
                'total_failed': 0,
                'total_scrapes': 0,
                'failure_rate': 0.0
            }

    def get_weekly_failed_scrapes(self, dealer_id: Optional[str] = None, indonesia_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get weekly summary of failed scrapes for past 7 days

        Args:
            dealer_id: Optional dealer ID filter
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            Dictionary with weekly failure statistics
        """
        try:
            # Get date range for past 7 days
            today_date = indonesia_date if indonesia_date else date.today()
            week_ago = today_date - timedelta(days=7)
            week_ago_start = datetime.combine(week_ago, datetime.min.time())
            today_end = datetime.combine(today_date, datetime.max.time())

            # Failed statuses
            failed_statuses = ['FAILED', 'PARTIAL']

            # Count failures
            failed_query = self.db.query(func.count(GoogleReviewScrapeTracker.id)).filter(
                GoogleReviewScrapeTracker.scrape_date >= week_ago_start,
                GoogleReviewScrapeTracker.scrape_date <= today_end,
                GoogleReviewScrapeTracker.scrape_status.in_(failed_statuses)
            )
            if dealer_id:
                failed_query = failed_query.filter(GoogleReviewScrapeTracker.dealer_id == dealer_id)
            failed_count = failed_query.scalar() or 0

            # Count total scrapes
            total_query = self.db.query(func.count(GoogleReviewScrapeTracker.id)).filter(
                GoogleReviewScrapeTracker.scrape_date >= week_ago_start,
                GoogleReviewScrapeTracker.scrape_date <= today_end
            )
            if dealer_id:
                total_query = total_query.filter(GoogleReviewScrapeTracker.dealer_id == dealer_id)
            total_count = total_query.scalar() or 0

            # Calculate failure rate
            failure_rate = (failed_count / total_count * 100) if total_count > 0 else 0.0

            return {
                'date_from': week_ago.isoformat(),
                'date_to': today_date.isoformat(),
                'total_failed': failed_count,
                'total_scrapes': total_count,
                'failure_rate': round(failure_rate, 2)
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting weekly failed scrapes: {str(e)}")
            today_date = date.today()
            week_ago = today_date - timedelta(days=7)
            return {
                'date_from': week_ago.isoformat(),
                'date_to': today_date.isoformat(),
                'total_failed': 0,
                'total_scrapes': 0,
                'failure_rate': 0.0
            }

    def get_scrape_failure_statistics(
        self,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive scrape failure statistics with breakdowns

        Args:
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            Dictionary with failure statistics and breakdowns
        """
        try:
            # Failed statuses
            failed_statuses = ['FAILED', 'PARTIAL']

            # Build base filters
            filters = [GoogleReviewScrapeTracker.scrape_status.in_(failed_statuses)]

            if dealer_id:
                filters.append(GoogleReviewScrapeTracker.dealer_id == dealer_id)

            if date_from:
                date_from_start = datetime.combine(date_from, datetime.min.time())
                filters.append(GoogleReviewScrapeTracker.scrape_date >= date_from_start)

            if date_to:
                date_to_end = datetime.combine(date_to, datetime.max.time())
                filters.append(GoogleReviewScrapeTracker.scrape_date <= date_to_end)

            # Get status breakdown
            status_breakdown = (
                self.db.query(
                    GoogleReviewScrapeTracker.scrape_status,
                    func.count(GoogleReviewScrapeTracker.id).label('count')
                )
                .filter(and_(*filters))
                .group_by(GoogleReviewScrapeTracker.scrape_status)
                .all()
            )

            # Calculate total failed
            total_failed = sum(count for _, count in status_breakdown)

            # Format status breakdown with percentages
            breakdown_by_status = []
            for status, count in status_breakdown:
                percentage = (count / total_failed * 100) if total_failed > 0 else 0.0
                breakdown_by_status.append({
                    'status': status,
                    'count': count,
                    'percentage': round(percentage, 2)
                })

            # Get type breakdown
            type_breakdown = (
                self.db.query(
                    GoogleReviewScrapeTracker.scrape_type,
                    func.count(GoogleReviewScrapeTracker.id).label('count')
                )
                .filter(and_(*filters))
                .group_by(GoogleReviewScrapeTracker.scrape_type)
                .all()
            )

            breakdown_by_type = {scrape_type: count for scrape_type, count in type_breakdown}

            # Get common errors
            error_query = (
                self.db.query(
                    GoogleReviewScrapeTracker.error_message,
                    func.count(GoogleReviewScrapeTracker.id).label('count')
                )
                .filter(
                    and_(*filters),
                    GoogleReviewScrapeTracker.error_message.isnot(None),
                    GoogleReviewScrapeTracker.error_message != ''
                )
                .group_by(GoogleReviewScrapeTracker.error_message)
                .order_by(func.count(GoogleReviewScrapeTracker.id).desc())
                .limit(10)
                .all()
            )

            common_errors = [
                {'error': error[:100], 'count': count}  # Truncate long error messages
                for error, count in error_query
            ]

            return {
                'total_failed': total_failed,
                'breakdown_by_status': breakdown_by_status,
                'breakdown_by_type': breakdown_by_type,
                'common_errors': common_errors
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting scrape failure statistics: {str(e)}")
            return {
                'total_failed': 0,
                'breakdown_by_status': [],
                'breakdown_by_type': {},
                'common_errors': []
            }
