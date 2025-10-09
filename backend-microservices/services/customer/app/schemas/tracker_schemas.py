"""
Pydantic schemas for tracker operations
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


# Google Review Scrape Tracker Schemas

class GoogleReviewScrapeTrackerResponse(BaseModel):
    """Schema for Google Review Scrape Tracker response"""
    id: str
    dealer_id: str
    dealer_name: Optional[str]
    scrape_type: str
    max_reviews_requested: int
    language: str
    scrape_status: str
    total_reviews_available: Optional[int]
    scraped_reviews: int
    failed_reviews: int
    new_reviews: int
    duplicate_reviews: int
    analyze_sentiment_enabled: bool
    sentiment_analysis_status: Optional[str]
    sentiment_analyzed_count: int
    sentiment_failed_count: int
    sentiment_batch_id: Optional[str]
    api_response_id: Optional[str]
    google_business_id: Optional[str]
    business_name: Optional[str]
    business_rating: Optional[str]
    error_message: Optional[str]
    warning_message: Optional[str]
    scrape_duration_seconds: Optional[int]
    sentiment_duration_seconds: Optional[int]
    scraped_by: Optional[str]
    scrape_date: str  # ISO format datetime string
    completed_date: Optional[str]  # ISO format datetime string
    last_updated: str  # ISO format datetime string

    class Config:
        from_attributes = True


class GoogleReviewScrapeTrackerListResponse(BaseModel):
    """Schema for Google Review Scrape Tracker list response"""
    date: str
    total: int
    activities: list[GoogleReviewScrapeTrackerResponse]


class DealerScrapeStatsResponse(BaseModel):
    """Schema for dealer scrape statistics response"""
    dealer_id: str
    dealer_name: Optional[str]
    total_scrapes: int
    completed_scrapes: int
    failed_scrapes: int
    processing_scrapes: int
    partial_scrapes: int
    total_reviews_scraped: int
    total_new_reviews: int
    total_duplicate_reviews: int
    avg_scrape_duration_seconds: float
    sentiment_analysis_enabled_count: int
    sentiment_completed_count: int


class DealerScrapeStatsListResponse(BaseModel):
    """Schema for dealer scrape statistics list response"""
    date: str
    total_dealers: int
    summaries: list[DealerScrapeStatsResponse]


class WeeklyDealerScrapeStatsResponse(BaseModel):
    """Schema for weekly dealer scrape statistics response with week range"""
    week_start_date: str  # ISO format date string (Monday)
    week_end_date: str    # ISO format date string (Sunday)
    dealer_id: str
    dealer_name: Optional[str]
    total_scrapes: int
    completed_scrapes: int
    failed_scrapes: int
    processing_scrapes: int
    partial_scrapes: int
    total_reviews_scraped: int
    total_new_reviews: int
    total_duplicate_reviews: int
    avg_scrape_duration_seconds: float
    sentiment_analysis_enabled_count: int
    sentiment_completed_count: int


class WeeklyDealerScrapeStatsListResponse(BaseModel):
    """Schema for weekly dealer scrape statistics list response"""
    total_weeks: int
    total_dealers: int
    summaries: list[WeeklyDealerScrapeStatsResponse]


# Customer Satisfaction Upload Tracker Schemas

class CustomerSatisfactionUploadTrackerResponse(BaseModel):
    """Schema for Customer Satisfaction Upload Tracker response"""
    id: str
    file_name: str
    file_size: Optional[int]
    total_records: int
    successful_records: int
    failed_records: int
    upload_status: str
    error_message: Optional[str]
    uploaded_by: Optional[str]
    upload_date: str  # ISO format datetime string
    completed_date: Optional[str]  # ISO format datetime string

    class Config:
        from_attributes = True


class CustomerSatisfactionUploadTrackerListResponse(BaseModel):
    """Schema for Customer Satisfaction Upload Tracker list response"""
    date: str
    total: int
    uploads: list[CustomerSatisfactionUploadTrackerResponse]
