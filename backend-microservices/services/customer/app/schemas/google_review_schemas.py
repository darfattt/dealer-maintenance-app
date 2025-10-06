"""
Pydantic schemas for Google Review API endpoints
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class ReviewSortBy(str, Enum):
    """Available sort fields for reviews"""
    PUBLISHED_DATE = "published_date"
    STARS = "stars"
    REVIEWER_NAME = "reviewer_name"
    CREATED_DATE = "created_date"


# Request Schemas
class ScrapeReviewsRequest(BaseModel):
    """Schema for scraping Google Reviews request"""
    dealer_id: str = Field(..., min_length=1, max_length=10, description="Dealer ID to scrape reviews for")
    max_reviews: int = Field(10, ge=1, le=50, description="Maximum number of reviews to fetch (1-50)")
    language: str = Field("id", min_length=2, max_length=5, description="Language code for reviews (e.g., 'id', 'en')")
    auto_analyze_sentiment: bool = Field(True, description="Automatically analyze sentiment after scraping")

    @validator('dealer_id')
    def validate_dealer_id(cls, v):
        """Validate dealer ID format"""
        if not v.strip():
            raise ValueError('Dealer ID cannot be empty')
        return v.strip()

    @validator('language')
    def validate_language(cls, v):
        """Validate language code"""
        valid_languages = ['id', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
        if v.lower() not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v.lower()


class AnalyzeSentimentRequest(BaseModel):
    """Schema for analyzing review sentiment request"""
    dealer_id: str = Field(..., min_length=1, max_length=10, description="Dealer ID to analyze reviews for")
    limit: int = Field(50, ge=1, le=200, description="Maximum number of reviews to analyze (1-200)")
    batch_size: int = Field(10, ge=1, le=50, description="Size of processing batches (1-50)")

    @validator('dealer_id')
    def validate_dealer_id(cls, v):
        """Validate dealer ID format"""
        if not v.strip():
            raise ValueError('Dealer ID cannot be empty')
        return v.strip()


class GetReviewsRequest(BaseModel):
    """Schema for getting reviews with filtering and pagination"""
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    per_page: int = Field(10, ge=1, le=100, description="Items per page (1-100)")

    # Date filtering
    published_from: Optional[date] = Field(None, description="Filter reviews published from this date")
    published_to: Optional[date] = Field(None, description="Filter reviews published until this date")

    # Content filtering
    reviewer_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Filter by reviewer name (partial match)")
    text_search: Optional[str] = Field(None, min_length=1, max_length=500, description="Search in review text")
    stars: Optional[int] = Field(None, ge=1, le=5, description="Filter by star rating (1-5)")

    # Sorting
    sort_by: ReviewSortBy = Field(ReviewSortBy.PUBLISHED_DATE, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")

    @validator('published_to')
    def validate_date_range(cls, v, values):
        """Validate that published_to is after published_from"""
        if v and 'published_from' in values and values['published_from']:
            if v < values['published_from']:
                raise ValueError('published_to must be after published_from')
        return v

    @validator('reviewer_name')
    def validate_reviewer_name(cls, v):
        """Validate reviewer name"""
        if v:
            v = v.strip()
            if not v:
                raise ValueError('Reviewer name cannot be empty')
        return v

    @validator('text_search')
    def validate_text_search(cls, v):
        """Validate text search"""
        if v:
            v = v.strip()
            if not v:
                raise ValueError('Text search cannot be empty')
        return v


# Response Schemas
class ScrapeReviewsResponse(BaseModel):
    """Schema for scrape reviews response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully scraped 10 reviews for dealer 12284",
                "data": {
                    "dealer_id": "12284",
                    "api_response_id": "12284_a1b2c3d4_1642687200",
                    "business_name": "Wijaya Abadi Motorindo",
                    "total_score": 4.5,
                    "reviews_count": 1046,
                    "scraped_reviews_count": 10,
                    "scraping_status": "success",
                    "scraped_at": "2025-01-20T10:30:00Z"
                }
            }
        }


class AnalyzeSentimentResponse(BaseModel):
    """Schema for analyze sentiment response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Sentiment analysis completed: 45 analyzed, 5 failed",
                "data": {
                    "dealer_id": "12284",
                    "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "total_reviews": 50,
                    "analyzed_reviews": 45,
                    "failed_reviews": 5,
                    "started_at": "2025-01-20T10:30:00Z",
                    "completed_at": "2025-01-20T10:32:15Z"
                }
            }
        }


class SentimentInfo(BaseModel):
    """Schema for sentiment analysis information"""
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_reasons: Optional[str] = None
    sentiment_suggestion: Optional[str] = None
    sentiment_themes: Optional[str] = None
    sentiment_analyzed_at: Optional[datetime] = None
    sentiment_batch_id: Optional[str] = None


class ReviewerInfo(BaseModel):
    """Schema for reviewer information"""
    name: Optional[str] = None
    number_of_reviews: Optional[int] = None
    is_local_guide: bool = False
    photo_url: Optional[str] = None
    profile_url: Optional[str] = None


class OwnerResponse(BaseModel):
    """Schema for owner response to review"""
    text: Optional[str] = None
    date: Optional[datetime] = None


class ReviewDetailResponse(BaseModel):
    """Schema for individual review detail response"""
    id: str
    review_id: Optional[str] = None

    # Reviewer information
    reviewer: ReviewerInfo

    # Review content
    stars: Optional[int] = None
    review_text: Optional[str] = None
    review_text_translated: Optional[str] = None
    likes_count: int = 0

    # Review metadata
    published_at: Optional[str] = None
    published_at_date: Optional[datetime] = None
    review_url: Optional[str] = None
    review_origin: Optional[str] = None
    original_language: Optional[str] = None

    # Owner response
    owner_response: Optional[OwnerResponse] = None

    # Additional data
    review_image_urls: Optional[List[str]] = None
    visited_in: Optional[str] = None

    # Sentiment analysis
    sentiment_info: Optional[SentimentInfo] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, review_detail):
        """Create response from GoogleReviewDetail model"""
        return cls(
            id=str(review_detail.id),
            review_id=review_detail.review_id,
            reviewer=ReviewerInfo(
                name=review_detail.reviewer_name,
                number_of_reviews=review_detail.reviewer_number_of_reviews,
                is_local_guide=review_detail.is_local_guide,
                photo_url=review_detail.reviewer_photo_url,
                profile_url=review_detail.reviewer_url
            ),
            stars=review_detail.stars,
            review_text=review_detail.review_text,
            review_text_translated=review_detail.review_text_translated,
            likes_count=review_detail.likes_count or 0,
            published_at=review_detail.published_at,
            published_at_date=review_detail.published_at_date,
            review_url=review_detail.review_url,
            review_origin=review_detail.review_origin,
            original_language=review_detail.original_language,
            owner_response=OwnerResponse(
                text=review_detail.response_from_owner_text,
                date=review_detail.response_from_owner_date
            ) if review_detail.response_from_owner_text else None,
            review_image_urls=review_detail.review_image_urls,
            visited_in=review_detail.visited_in,
            sentiment_info=SentimentInfo(
                sentiment=review_detail.sentiment,
                sentiment_score=float(review_detail.sentiment_score) if review_detail.sentiment_score else None,
                sentiment_reasons=review_detail.sentiment_reasons,
                sentiment_suggestion=review_detail.sentiment_suggestion,
                sentiment_themes=review_detail.sentiment_themes,
                sentiment_analyzed_at=review_detail.sentiment_analyzed_at,
                sentiment_batch_id=str(review_detail.sentiment_batch_id) if review_detail.sentiment_batch_id else None
            ) if review_detail.sentiment else None,
            created_at=review_detail.created_at,
            updated_at=review_detail.updated_at
        )


class PaginationInfo(BaseModel):
    """Schema for pagination information"""
    page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ReviewFilters(BaseModel):
    """Schema for applied filters information"""
    dealer_id: str
    published_from: Optional[date] = None
    published_to: Optional[date] = None
    reviewer_name: Optional[str] = None
    text_search: Optional[str] = None
    stars: Optional[int] = None
    sort_by: str
    sort_order: str


class GetReviewsResponse(BaseModel):
    """Schema for get reviews response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    pagination: Optional[PaginationInfo] = None
    filters: Optional[ReviewFilters] = None
    reviews: List[ReviewDetailResponse] = []

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Retrieved 10 reviews for dealer 12284",
                "data": {
                    "dealer_id": "12284",
                    "business_name": "Wijaya Abadi Motorindo",
                    "last_scraped": "2025-01-20T10:30:00Z"
                },
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 25,
                    "total_pages": 3,
                    "has_next": True,
                    "has_prev": False
                },
                "filters": {
                    "dealer_id": "12284",
                    "stars": 5,
                    "sort_by": "published_date",
                    "sort_order": "desc"
                },
                "reviews": [
                    {
                        "id": "uuid-here",
                        "reviewer": {
                            "name": "John Doe",
                            "number_of_reviews": 25,
                            "is_local_guide": True
                        },
                        "stars": 5,
                        "review_text": "Excellent service!",
                        "published_at_date": "2025-01-15T14:30:00Z"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "Dealer not found",
                "error_code": "DEALER_NOT_FOUND",
                "details": {
                    "dealer_id": "99999"
                }
            }
        }


# Google Profile Schemas
class OwnerUpdate(BaseModel):
    """Schema for owner updates/posts"""
    title: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    date: Optional[datetime] = None
    url: Optional[str] = None


class BusinessInfo(BaseModel):
    """Schema for business information"""
    name: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: int = 0
    category: Optional[str] = None
    location: Optional[str] = None
    photos_count: int = 0
    description: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    hours: Optional[Dict[str, Any]] = None
    services: Optional[List[str]] = None
    appointments: Optional[Dict[str, Any]] = None
    ownerUpdates: Optional[List[OwnerUpdate]] = []


class StarDistribution(BaseModel):
    """Schema for star rating distribution"""
    stars: int = Field(..., ge=1, le=5, description="Star rating (1-5)")
    count: int = Field(..., ge=0, description="Number of reviews with this rating")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total reviews")


class ReviewSummary(BaseModel):
    """Schema for review summary statistics"""
    total_reviews: int = 0
    average_rating: Optional[float] = None
    star_distribution: List[StarDistribution] = []
    recent_review_count: int = 0  # Reviews in last 30 days


class ReviewTag(BaseModel):
    """Schema for review tags/themes"""
    tag: str = Field(..., min_length=1, description="Tag name")
    count: int = Field(..., ge=0, description="Number of times this tag appears")
    category: Optional[str] = None  # e.g., 'service', 'product', 'experience'
    sentiment: Optional[str] = None  # 'positive', 'negative', 'neutral'


class DealerProfile(BaseModel):
    """Schema for complete dealer Google profile"""
    business_info: BusinessInfo
    review_summary: ReviewSummary
    review_tags: List[ReviewTag] = []
    last_updated: Optional[datetime] = None
    has_data: bool = False
    scraping_status: Optional[str] = None


class DealerProfileResponse(BaseModel):
    """Schema for dealer profile API response"""
    success: bool = True
    message: str
    data: Optional[DealerProfile] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Dealer profile retrieved successfully",
                "data": {
                    "business_info": {
                        "name": "PT Daya Adipta Motora",
                        "rating": 4.6,
                        "total_reviews": 4536,
                        "category": "Motorcycle repair shop",
                        "location": "Bandung, West Java",
                        "photos_count": 2970,
                        "description": "Honda authorized dealer and service center",
                        "website": "https://example.com",
                        "phone": "+62-22-1234567"
                    },
                    "review_summary": {
                        "total_reviews": 4536,
                        "average_rating": 4.6,
                        "star_distribution": [
                            {"stars": 5, "count": 3200, "percentage": 70.5},
                            {"stars": 4, "count": 900, "percentage": 19.8},
                            {"stars": 3, "count": 300, "percentage": 6.6},
                            {"stars": 2, "count": 100, "percentage": 2.2},
                            {"stars": 1, "count": 36, "percentage": 0.8}
                        ],
                        "recent_review_count": 45
                    },
                    "review_tags": [
                        {"tag": "quality service", "count": 122, "category": "service", "sentiment": "positive"},
                        {"tag": "consumer", "count": 48, "category": "experience", "sentiment": "neutral"},
                        {"tag": "dealer", "count": 47, "category": "business", "sentiment": "positive"},
                        {"tag": "snack", "count": 154, "category": "amenity", "sentiment": "positive"}
                    ],
                    "last_updated": "2025-01-20T10:30:00Z",
                    "has_data": True,
                    "scraping_status": "success"
                }
            }
        }


# Google Review Scrape Tracker Schemas
class ScrapeTracker(BaseModel):
    """Schema for Google Review scrape tracking data"""
    id: str
    dealer_id: str
    dealer_name: Optional[str] = None
    scrape_type: str = "MANUAL"
    max_reviews_requested: int
    language: str
    scrape_status: str
    total_reviews_available: Optional[int] = None
    scraped_reviews: int = 0
    failed_reviews: int = 0
    new_reviews: int = 0
    duplicate_reviews: int = 0
    success_rate: float = 0.0

    # Sentiment analysis
    analyze_sentiment_enabled: bool = False
    sentiment_analysis_status: Optional[str] = None
    sentiment_analyzed_count: int = 0
    sentiment_failed_count: int = 0
    sentiment_completion_rate: float = 0.0
    sentiment_batch_id: Optional[str] = None

    # API response
    api_response_id: Optional[str] = None
    google_business_id: Optional[str] = None
    business_name: Optional[str] = None
    business_rating: Optional[str] = None

    # Error handling
    error_message: Optional[str] = None
    warning_message: Optional[str] = None

    # Performance
    scrape_duration_seconds: Optional[int] = None
    sentiment_duration_seconds: Optional[int] = None

    # Status flags
    is_processing: bool = False
    is_completed: bool = False
    is_failed: bool = False
    has_sentiment_pending: bool = False

    # Audit fields
    scraped_by: Optional[str] = None
    scrape_date: datetime
    completed_date: Optional[datetime] = None
    last_updated: datetime


class ScrapeTrackerSummary(BaseModel):
    """Schema for scrape tracker summary in history lists"""
    id: str
    dealer_id: str
    dealer_name: Optional[str] = None
    scrape_status: str
    scraped_reviews: int
    total_reviews_available: Optional[int] = None
    success_rate: float
    business_name: Optional[str] = None
    analyze_sentiment_enabled: bool
    sentiment_analysis_status: Optional[str] = None
    sentiment_analyzed_count: int = 0
    sentiment_failed_count: int = 0
    sentiment_completion_rate: float
    scrape_date: datetime
    completed_date: Optional[datetime] = None
    is_processing: bool
    has_sentiment_pending: bool

    @classmethod
    def from_model(cls, tracker):
        """Create response from GoogleReviewScrapeTracker model"""
        # Calculate success rate
        success_rate = 0.0
        if tracker.scraped_reviews > 0 and tracker.scraped_reviews + tracker.failed_reviews > 0:
            success_rate = (tracker.scraped_reviews / (tracker.scraped_reviews + tracker.failed_reviews)) * 100.0

        # Calculate sentiment completion rate
        sentiment_completion_rate = 0.0
        if tracker.analyze_sentiment_enabled and tracker.scraped_reviews > 0:
            sentiment_completion_rate = (tracker.sentiment_analyzed_count / tracker.scraped_reviews) * 100.0

        # Determine status flags
        is_processing = tracker.scrape_status in ['PROCESSING']
        has_sentiment_pending = (
            tracker.analyze_sentiment_enabled and
            tracker.sentiment_analysis_status in ['PENDING', 'PROCESSING']
        )

        return cls(
            id=str(tracker.id),
            dealer_id=tracker.dealer_id,
            dealer_name=tracker.dealer_name,
            scrape_status=tracker.scrape_status,
            scraped_reviews=tracker.scraped_reviews or 0,
            total_reviews_available=tracker.total_reviews_available,
            success_rate=round(success_rate, 1),
            business_name=tracker.business_name,
            analyze_sentiment_enabled=tracker.analyze_sentiment_enabled,
            sentiment_analysis_status=tracker.sentiment_analysis_status,
            sentiment_analyzed_count=tracker.sentiment_analyzed_count or 0,
            sentiment_failed_count=tracker.sentiment_failed_count or 0,
            sentiment_completion_rate=round(sentiment_completion_rate, 1),
            scrape_date=tracker.scrape_date,
            completed_date=tracker.completed_date,
            is_processing=is_processing,
            has_sentiment_pending=has_sentiment_pending
        )


class ScrapeHistoryResponse(BaseModel):
    """Schema for scrape history API response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    trackers: List[ScrapeTrackerSummary] = []
    pagination: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Scrape history retrieved successfully",
                "data": {
                    "dealer_id": "12284",
                    "total_scrapes": 5,
                    "successful_scrapes": 4,
                    "failed_scrapes": 1
                },
                "trackers": [
                    {
                        "id": "uuid-here",
                        "dealer_id": "12284",
                        "dealer_name": "PT Daya Adipta Motora",
                        "scrape_status": "COMPLETED",
                        "scraped_reviews": 15,
                        "total_reviews_available": 4536,
                        "success_rate": 100.0,
                        "business_name": "PT Daya Adipta Motora",
                        "analyze_sentiment_enabled": True,
                        "sentiment_analysis_status": "COMPLETED",
                        "sentiment_completion_rate": 100.0,
                        "scrape_date": "2025-01-20T10:30:00Z",
                        "completed_date": "2025-01-20T10:32:15Z",
                        "is_processing": False,
                        "has_sentiment_pending": False
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 5,
                    "total_pages": 1
                }
            }
        }


class DealerOption(BaseModel):
    """Schema for dealer selection options"""
    dealer_id: str
    dealer_name: Optional[str] = None
    location: Optional[str] = None
    has_google_url: bool = False


class DealerOptionsResponse(BaseModel):
    """Schema for dealer options API response"""
    success: bool = True
    message: str
    dealers: List[DealerOption] = []

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Dealer options retrieved successfully",
                "dealers": [
                    {
                        "dealer_id": "12284",
                        "dealer_name": "PT Daya Adipta Motora",
                        "location": "Bandung, West Java",
                        "has_google_url": True
                    },
                    {
                        "dealer_id": "12285",
                        "dealer_name": "Honda Service Center",
                        "location": "Jakarta",
                        "has_google_url": False
                    }
                ]
            }
        }