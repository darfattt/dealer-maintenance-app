"""
Pydantic schemas for Google scrape anomaly logging
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GoogleScrapeAnomalyRecord(BaseModel):
    """Schema for individual Google scrape failure record"""

    id: str = Field(..., description="Tracker UUID")
    dealer_id: str = Field(..., description="Dealer ID")
    dealer_name: Optional[str] = Field(None, description="Dealer name")
    scrape_date: str = Field(..., description="Scrape timestamp")
    scrape_status: str = Field(..., description="Scrape status (FAILED/PARTIAL)")
    scrape_type: str = Field(..., description="Scrape type (MANUAL/SCHEDULED)")
    max_reviews_requested: int = Field(..., description="Maximum reviews requested")
    scraped_reviews: int = Field(..., description="Number of reviews successfully scraped")
    failed_reviews: int = Field(..., description="Number of reviews failed to scrape")
    new_reviews: int = Field(..., description="Number of new reviews added")
    duplicate_reviews: int = Field(..., description="Number of duplicate reviews skipped")
    success_rate: float = Field(..., description="Success rate percentage")
    error_message: Optional[str] = Field(None, description="Error message")
    warning_message: Optional[str] = Field(None, description="Warning message")
    scrape_duration_seconds: Optional[int] = Field(None, description="Scrape duration in seconds")
    api_response_id: Optional[str] = Field(None, description="Apify response ID")
    google_business_id: Optional[str] = Field(None, description="Google Business ID")
    business_name: Optional[str] = Field(None, description="Business name")
    sentiment_analysis_status: Optional[str] = Field(None, description="Sentiment analysis status")
    scraped_by: Optional[str] = Field(None, description="User who initiated scrape")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "dealer_id": "12284",
                "dealer_name": "Honda Main Dealer",
                "scrape_date": "2025-01-10T10:30:00+07:00",
                "scrape_status": "FAILED",
                "scrape_type": "MANUAL",
                "max_reviews_requested": 50,
                "scraped_reviews": 0,
                "failed_reviews": 50,
                "new_reviews": 0,
                "duplicate_reviews": 0,
                "success_rate": 0.0,
                "error_message": "Apify API connection timeout",
                "warning_message": None,
                "scrape_duration_seconds": 30,
                "api_response_id": "apify_123456",
                "google_business_id": "ChIJ123abc",
                "business_name": "Honda Main Dealer",
                "sentiment_analysis_status": None,
                "scraped_by": "admin@example.com"
            }
        }


class PaginationMetadata(BaseModel):
    """Schema for pagination metadata"""

    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_records: int = Field(..., description="Total number of records")
    total_pages: int = Field(..., description="Total number of pages")


class GoogleScrapeAnomalyListResponse(BaseModel):
    """Schema for paginated Google scrape anomaly list response"""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: List[GoogleScrapeAnomalyRecord] = Field(..., description="List of anomaly records")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Google scrape anomalies retrieved successfully",
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "dealer_id": "12284",
                        "dealer_name": "Honda Main Dealer",
                        "scrape_date": "2025-01-10T10:30:00+07:00",
                        "scrape_status": "FAILED",
                        "scrape_type": "MANUAL",
                        "max_reviews_requested": 50,
                        "scraped_reviews": 0,
                        "failed_reviews": 50,
                        "new_reviews": 0,
                        "duplicate_reviews": 0,
                        "success_rate": 0.0,
                        "error_message": "API timeout",
                        "scraped_by": "admin@example.com"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_records": 45,
                    "total_pages": 5
                }
            }
        }


class GoogleScrapeStatusBreakdown(BaseModel):
    """Schema for Google scrape status breakdown"""

    status: str = Field(..., description="Status name")
    count: int = Field(..., description="Number of occurrences")
    percentage: float = Field(..., description="Percentage of total")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "FAILED",
                "count": 30,
                "percentage": 66.7
            }
        }


class GoogleScrapeAnomalySummary(BaseModel):
    """Schema for Google scrape anomaly summary statistics"""

    total_failed: int = Field(..., description="Total failed scrape operations")
    daily_failed: int = Field(..., description="Failed scrapes today")
    weekly_failed: int = Field(..., description="Failed scrapes in past 7 days")
    total_scrapes: int = Field(..., description="Total scrape attempts in period")
    failure_rate: float = Field(..., description="Failure rate percentage")
    daily_failure_rate: float = Field(..., description="Daily failure rate percentage")
    weekly_failure_rate: float = Field(..., description="Weekly failure rate percentage")
    breakdown_by_status: List[GoogleScrapeStatusBreakdown] = Field(..., description="Breakdown by status")
    breakdown_by_type: Dict[str, int] = Field(..., description="Breakdown by scrape type (MANUAL/SCHEDULED)")
    common_errors: List[Dict[str, Any]] = Field(..., description="Most common error messages")

    class Config:
        json_schema_extra = {
            "example": {
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
                    {"error": "API timeout", "count": 15},
                    {"error": "Invalid location URL", "count": 10}
                ]
            }
        }


class GoogleScrapeAnomalySummaryResponse(BaseModel):
    """Schema for Google scrape anomaly summary response"""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: GoogleScrapeAnomalySummary = Field(..., description="Summary statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
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
                        {"status": "FAILED", "count": 30, "percentage": 66.7}
                    ],
                    "breakdown_by_type": {
                        "MANUAL": 35,
                        "SCHEDULED": 10
                    },
                    "common_errors": [
                        {"error": "API timeout", "count": 15}
                    ]
                }
            }
        }
