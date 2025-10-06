"""
Google Review model for storing scraped Google Maps review data
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GoogleReview(Base):
    """Google Review model - stores scraped Google Maps data"""

    __tablename__ = "google_reviews"
    __table_args__ = {"schema": "customer"}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Audit and tracking fields
    dealer_id = Column(String(10), nullable=False, index=True)
    scraping_status = Column(String(50), default='success')  # success, failed, partial
    scraping_error_message = Column(Text, nullable=True)
    api_response_id = Column(String(100), nullable=True)  # Unique identifier for this scraping session

    # Business information from API response
    title = Column(String(500), nullable=True)
    subtitle = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    category_name = Column(String(255), nullable=True)

    # Location information
    address = Column(Text, nullable=True)
    neighborhood = Column(String(255), nullable=True)
    street = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    postal_code = Column(String(20), nullable=True)
    state = Column(String(100), nullable=True)
    country_code = Column(String(10), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    plus_code = Column(String(100), nullable=True)

    # Contact information
    website = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    phone_unformatted = Column(String(50), nullable=True)

    # Business metrics
    total_score = Column(Float, nullable=True)
    reviews_count = Column(Integer, nullable=True)
    images_count = Column(Integer, nullable=True)

    # Business status
    permanently_closed = Column(Boolean, default=False)
    temporarily_closed = Column(Boolean, default=False)
    claim_this_business = Column(Boolean, default=False)

    # Google-specific identifiers
    place_id = Column(String(255), nullable=True, unique=True)
    google_cid = Column(String(50), nullable=True)
    google_fid = Column(String(100), nullable=True)

    # JSON fields for complex data
    location_data = Column(JSON, nullable=True)  # Full location object
    reviews_distribution = Column(JSON, nullable=True)  # Star rating distribution
    categories = Column(JSON, nullable=True)  # Array of categories
    opening_hours = Column(JSON, nullable=True)  # Opening hours data
    additional_opening_hours = Column(JSON, nullable=True)  # Special hours
    popular_times_histogram = Column(JSON, nullable=True)  # Weekly popular times
    popular_times_live = Column(JSON, nullable=True)  # Current popularity
    additional_info = Column(JSON, nullable=True)  # Facilities, payment options, etc.
    reviews_tags = Column(JSON, nullable=True)  # Common review themes
    people_also_search = Column(JSON, nullable=True)  # Related businesses
    owner_updates = Column(JSON, nullable=True)  # Updates from business owner
    booking_links = Column(JSON, nullable=True)  # Reservation/booking links
    image_categories = Column(JSON, nullable=True)  # Types of photos available

    # Raw API response
    raw_api_response = Column(JSON, nullable=True)  # Complete API response for debugging

    # Timestamps
    scraped_at = Column(DateTime, nullable=True)  # When Google data was scraped
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<GoogleReview(id={self.id}, dealer_id={self.dealer_id}, title={self.title}, total_score={self.total_score})>"

    def to_dict(self):
        """Convert Google Review to dictionary"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "scraping_status": self.scraping_status,
            "scraping_error_message": self.scraping_error_message,
            "api_response_id": self.api_response_id,

            # Business info
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "category_name": self.category_name,

            # Location
            "address": self.address,
            "neighborhood": self.neighborhood,
            "street": self.street,
            "city": self.city,
            "postal_code": self.postal_code,
            "state": self.state,
            "country_code": self.country_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "plus_code": self.plus_code,

            # Contact
            "website": self.website,
            "phone": self.phone,
            "phone_unformatted": self.phone_unformatted,

            # Metrics
            "total_score": self.total_score,
            "reviews_count": self.reviews_count,
            "images_count": self.images_count,

            # Status
            "permanently_closed": self.permanently_closed,
            "temporarily_closed": self.temporarily_closed,
            "claim_this_business": self.claim_this_business,

            # Google IDs
            "place_id": self.place_id,
            "google_cid": self.google_cid,
            "google_fid": self.google_fid,

            # JSON fields
            "location_data": self.location_data,
            "reviews_distribution": self.reviews_distribution,
            "categories": self.categories,
            "opening_hours": self.opening_hours,
            "additional_opening_hours": self.additional_opening_hours,
            "popular_times_histogram": self.popular_times_histogram,
            "popular_times_live": self.popular_times_live,
            "additional_info": self.additional_info,
            "reviews_tags": self.reviews_tags,
            "people_also_search": self.people_also_search,
            "owner_updates": self.owner_updates,
            "booking_links": self.booking_links,
            "image_categories": self.image_categories,

            # Timestamps
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_summary(self):
        """Get a summary of the Google Review data"""
        return {
            "id": str(self.id),
            "dealer_id": self.dealer_id,
            "title": self.title,
            "total_score": self.total_score,
            "reviews_count": self.reviews_count,
            "address": self.address,
            "phone": self.phone,
            "scraping_status": self.scraping_status,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }


class GoogleReviewDetail(Base):
    """Individual review details from Google Maps"""

    __tablename__ = "google_review_details"
    __table_args__ = {"schema": "customer"}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to main google_reviews table
    google_review_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    dealer_id = Column(String(10), nullable=False, index=True)

    # Review identification
    review_id = Column(String(255), nullable=True, unique=True)
    reviewer_id = Column(String(100), nullable=True)
    reviewer_url = Column(String(500), nullable=True)

    # Reviewer information
    reviewer_name = Column(String(255), nullable=True)
    reviewer_number_of_reviews = Column(Integer, nullable=True)
    is_local_guide = Column(Boolean, default=False)
    reviewer_photo_url = Column(String(500), nullable=True)

    # Review content
    review_text = Column(Text, nullable=True)
    review_text_translated = Column(Text, nullable=True)
    stars = Column(Integer, nullable=True)
    likes_count = Column(Integer, nullable=True)

    # Review metadata
    published_at = Column(String(100), nullable=True)  # Original format from API
    published_at_date = Column(DateTime, nullable=True)  # Parsed date
    review_url = Column(String(1000), nullable=True)
    review_origin = Column(String(50), nullable=True)
    original_language = Column(String(10), nullable=True)
    translated_language = Column(String(10), nullable=True)

    # Owner response
    response_from_owner_date = Column(DateTime, nullable=True)
    response_from_owner_text = Column(Text, nullable=True)

    # Additional data
    review_image_urls = Column(JSON, nullable=True)
    review_context = Column(JSON, nullable=True)
    review_detailed_rating = Column(JSON, nullable=True)
    visited_in = Column(String(50), nullable=True)

    # Sentiment analysis fields
    sentiment = Column(String(20), nullable=True)  # Positive, Negative, Neutral
    sentiment_score = Column(Numeric(4, 2), nullable=True)  # -5.00 to 5.00
    sentiment_reasons = Column(Text, nullable=True)
    sentiment_suggestion = Column(Text, nullable=True)
    sentiment_themes = Column(Text, nullable=True)  # JSON array as string
    sentiment_analyzed_at = Column(DateTime, nullable=True)
    sentiment_batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Raw review data
    raw_review_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<GoogleReviewDetail(id={self.id}, reviewer_name={self.reviewer_name}, stars={self.stars})>"

    def to_dict(self):
        """Convert Google Review Detail to dictionary"""
        return {
            "id": str(self.id),
            "google_review_id": str(self.google_review_id),
            "dealer_id": self.dealer_id,
            "review_id": self.review_id,
            "reviewer_id": self.reviewer_id,
            "reviewer_url": self.reviewer_url,
            "reviewer_name": self.reviewer_name,
            "reviewer_number_of_reviews": self.reviewer_number_of_reviews,
            "is_local_guide": self.is_local_guide,
            "reviewer_photo_url": self.reviewer_photo_url,
            "review_text": self.review_text,
            "review_text_translated": self.review_text_translated,
            "stars": self.stars,
            "likes_count": self.likes_count,
            "published_at": self.published_at,
            "published_at_date": self.published_at_date.isoformat() if self.published_at_date else None,
            "review_url": self.review_url,
            "review_origin": self.review_origin,
            "original_language": self.original_language,
            "translated_language": self.translated_language,
            "response_from_owner_date": self.response_from_owner_date.isoformat() if self.response_from_owner_date else None,
            "response_from_owner_text": self.response_from_owner_text,
            "review_image_urls": self.review_image_urls,
            "review_context": self.review_context,
            "review_detailed_rating": self.review_detailed_rating,
            "visited_in": self.visited_in,

            # Sentiment analysis fields
            "sentiment": self.sentiment,
            "sentiment_score": float(self.sentiment_score) if self.sentiment_score else None,
            "sentiment_reasons": self.sentiment_reasons,
            "sentiment_suggestion": self.sentiment_suggestion,
            "sentiment_themes": self.sentiment_themes,
            "sentiment_analyzed_at": self.sentiment_analyzed_at.isoformat() if self.sentiment_analyzed_at else None,
            "sentiment_batch_id": str(self.sentiment_batch_id) if self.sentiment_batch_id else None,

            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }