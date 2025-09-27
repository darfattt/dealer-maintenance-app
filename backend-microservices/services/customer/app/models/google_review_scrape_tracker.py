"""
Google Review Scrape Tracker model for customer service
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import timezone utilities for proper Indonesian timezone formatting
try:
    from app.utils.timezone_utils import convert_utc_to_indonesia_for_display
except ImportError:
    # Fallback if timezone utils not available
    convert_utc_to_indonesia_for_display = None

# Import Indonesian timezone utility function
def _get_indonesia_timezone_utc():
    """Get current Indonesian time as UTC for database storage"""
    try:
        from app.utils.timezone_utils import get_indonesia_utc_now
        return get_indonesia_utc_now()
    except ImportError:
        # Fallback to standard UTC if timezone utils not available
        return datetime.utcnow()


class GoogleReviewScrapeTracker(Base):
    """Tracker for Google Review scraping operations"""

    __tablename__ = "customer_google_review_scrape_tracker"
    __table_args__ = {"schema": "customer"}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Dealer information
    dealer_id = Column(String(10), nullable=False, index=True)
    dealer_name = Column(String(255), nullable=True)

    # Scraping configuration
    scrape_type = Column(String(20), nullable=False, default='MANUAL')  # MANUAL, SCHEDULED
    max_reviews_requested = Column(Integer, nullable=False, default=10)
    language = Column(String(5), nullable=False, default='id')

    # Scraping results
    scrape_status = Column(String(20), nullable=False, default='PROCESSING')  # PROCESSING, COMPLETED, FAILED, PARTIAL
    total_reviews_available = Column(Integer, nullable=True)  # Total reviews on Google
    scraped_reviews = Column(Integer, nullable=False, default=0)
    failed_reviews = Column(Integer, nullable=False, default=0)
    new_reviews = Column(Integer, nullable=False, default=0)  # Actually new reviews added
    duplicate_reviews = Column(Integer, nullable=False, default=0)  # Reviews already existed

    # Sentiment analysis tracking
    analyze_sentiment_enabled = Column(Boolean, nullable=False, default=False)
    sentiment_analysis_status = Column(String(20), nullable=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    sentiment_analyzed_count = Column(Integer, nullable=False, default=0)
    sentiment_failed_count = Column(Integer, nullable=False, default=0)
    sentiment_batch_id = Column(UUID(as_uuid=True), nullable=True)

    # API response tracking
    api_response_id = Column(String(100), nullable=True)  # Apify response ID
    google_business_id = Column(String(100), nullable=True)  # Google Business ID
    business_name = Column(String(255), nullable=True)
    business_rating = Column(String(10), nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    warning_message = Column(Text, nullable=True)

    # Processing times
    scrape_duration_seconds = Column(Integer, nullable=True)
    sentiment_duration_seconds = Column(Integer, nullable=True)

    # Audit fields - using Indonesian timezone
    scraped_by = Column(String(100), nullable=True)
    scrape_date = Column(DateTime, default=_get_indonesia_timezone_utc, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=_get_indonesia_timezone_utc, onupdate=_get_indonesia_timezone_utc, nullable=False)

    def __repr__(self):
        return f"<GoogleReviewScrapeTracker(id={self.id}, dealer_id={self.dealer_id}, status={self.scrape_status})>"

    def _format_datetime_indonesia(self, dt):
        """Format datetime field with Indonesian timezone conversion"""
        if dt is None:
            return None

        # Convert UTC datetime to Indonesian timezone for display
        if convert_utc_to_indonesia_for_display:
            indonesia_dt = convert_utc_to_indonesia_for_display(dt)
            return indonesia_dt.isoformat() if indonesia_dt else None
        else:
            # Fallback to original format if timezone utils not available
            return dt.isoformat()

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        total_attempted = self.scraped_reviews + self.failed_reviews
        if total_attempted == 0:
            return 0.0
        return round((self.scraped_reviews / total_attempted) * 100, 1)

    @property
    def sentiment_completion_rate(self):
        """Calculate sentiment analysis completion rate"""
        if not self.analyze_sentiment_enabled or self.scraped_reviews == 0:
            return 0.0
        return round((self.sentiment_analyzed_count / self.scraped_reviews) * 100, 1)

    @property
    def is_processing(self):
        """Check if scraping is still in progress"""
        return self.scrape_status == 'PROCESSING'

    @property
    def is_completed(self):
        """Check if scraping completed successfully"""
        return self.scrape_status == 'COMPLETED'

    @property
    def is_failed(self):
        """Check if scraping failed"""
        return self.scrape_status == 'FAILED'

    @property
    def has_sentiment_pending(self):
        """Check if sentiment analysis is pending"""
        return (self.analyze_sentiment_enabled and
                self.sentiment_analysis_status in ['PENDING', 'PROCESSING'])

    def to_dict(self):
        """Convert scrape tracker to dictionary"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "dealer_name": self.dealer_name,
            "scrape_type": self.scrape_type,
            "max_reviews_requested": self.max_reviews_requested,
            "language": self.language,
            "scrape_status": self.scrape_status,
            "total_reviews_available": self.total_reviews_available,
            "scraped_reviews": self.scraped_reviews,
            "failed_reviews": self.failed_reviews,
            "new_reviews": self.new_reviews,
            "duplicate_reviews": self.duplicate_reviews,
            "success_rate": self.success_rate,
            # Sentiment analysis
            "analyze_sentiment_enabled": self.analyze_sentiment_enabled,
            "sentiment_analysis_status": self.sentiment_analysis_status,
            "sentiment_analyzed_count": self.sentiment_analyzed_count,
            "sentiment_failed_count": self.sentiment_failed_count,
            "sentiment_completion_rate": self.sentiment_completion_rate,
            "sentiment_batch_id": str(self.sentiment_batch_id) if self.sentiment_batch_id else None,
            # API response
            "api_response_id": self.api_response_id,
            "google_business_id": self.google_business_id,
            "business_name": self.business_name,
            "business_rating": self.business_rating,
            # Error handling
            "error_message": self.error_message,
            "warning_message": self.warning_message,
            # Performance
            "scrape_duration_seconds": self.scrape_duration_seconds,
            "sentiment_duration_seconds": self.sentiment_duration_seconds,
            # Status flags
            "is_processing": self.is_processing,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "has_sentiment_pending": self.has_sentiment_pending,
            # Audit fields
            "scraped_by": self.scraped_by,
            "scrape_date": self._format_datetime_indonesia(self.scrape_date),
            "completed_date": self._format_datetime_indonesia(self.completed_date),
            "last_updated": self._format_datetime_indonesia(self.last_updated),
        }

    def to_summary_dict(self):
        """Convert to summary dictionary for history lists"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "dealer_name": self.dealer_name,
            "scrape_status": self.scrape_status,
            "scraped_reviews": self.scraped_reviews,
            "total_reviews_available": self.total_reviews_available,
            "success_rate": self.success_rate,
            "business_name": self.business_name,
            "analyze_sentiment_enabled": self.analyze_sentiment_enabled,
            "sentiment_analysis_status": self.sentiment_analysis_status,
            "sentiment_completion_rate": self.sentiment_completion_rate,
            "scrape_date": self._format_datetime_indonesia(self.scrape_date),
            "completed_date": self._format_datetime_indonesia(self.completed_date),
            "is_processing": self.is_processing,
            "has_sentiment_pending": self.has_sentiment_pending,
        }