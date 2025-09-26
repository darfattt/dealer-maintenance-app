"""
FastAPI routes for Google Review operations
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.controllers.customer_google_review_controller import CustomerGoogleReviewController
from app.schemas.google_review_schemas import (
    ScrapeReviewsRequest,
    ScrapeReviewsResponse,
    GetReviewsResponse,
    ErrorResponse,
    ReviewSortBy,
    SortOrder,
    AnalyzeSentimentRequest,
    AnalyzeSentimentResponse,
    DealerProfileResponse,
    ScrapeHistoryResponse,
    DealerOptionsResponse
)
from app.dependencies import get_db, get_current_user, UserContext
from datetime import datetime, date
from typing import Optional

# Create router
router = APIRouter(
    prefix="/google-reviews",
    tags=["Google Reviews"],
    responses={
        404: {"model": ErrorResponse, "description": "Dealer not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


def get_google_review_controller(db: Session = Depends(get_db)) -> CustomerGoogleReviewController:
    """
    Dependency to get Google Review controller instance

    Args:
        db: Database session

    Returns:
        CustomerGoogleReviewController instance
    """
    return CustomerGoogleReviewController(db)


@router.post(
    "/scrape-reviews",
    response_model=ScrapeReviewsResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape Google Reviews for Dealer",
    description="""
    Scrape Google Maps reviews for a specific dealer using the Apify API.

    **Process:**
    1. Validates dealer exists and has google_location_url configured
    2. Calls Apify API to scrape Google Maps data
    3. Stores business information and individual reviews in database
    4. Returns scraping summary with audit information

    **Features:**
    - Configurable max_reviews (1-50)
    - Language selection for reviews
    - Complete audit trail with unique api_response_id
    - Error handling for failed scraping attempts

    **Rate Limiting:**
    - Respects Apify API rate limits
    - Stores failed attempts for debugging
    """
)
async def scrape_reviews_for_dealer(
    request: ScrapeReviewsRequest,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> ScrapeReviewsResponse:
    """
    Scrape Google Reviews for a dealer

    Args:
        request: Scraping request with dealer_id, max_reviews, and language
        controller: Google Review controller instance

    Returns:
        ScrapeReviewsResponse with scraping results

    Raises:
        HTTPException: If dealer not found, no google_location_url, or scraping fails
    """
    return await controller.scrape_reviews_for_dealer(request)


@router.get(
    "/reviews/{dealer_id}",
    response_model=GetReviewsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google Review Details with Filtering",
    description="""
    Retrieve Google review details for a dealer with advanced filtering and pagination.

    **Filtering Options:**
    - **Date Range:** Filter by review publication date
    - **Reviewer Name:** Partial match on reviewer name
    - **Text Search:** Search within review text (original or translated)
    - **Star Rating:** Filter by specific star rating (1-5)

    **Sorting Options:**
    - published_date, stars, reviewer_name, created_date
    - Ascending or descending order

    **Pagination:**
    - Configurable page size (1-100 items)
    - Complete pagination metadata
    - Consistent ordering for stable pagination

    **Response Includes:**
    - Paginated review details with reviewer information
    - Owner responses to reviews
    - Review metadata (images, language, etc.)
    - Business information and last scraping date
    """
)
async def get_reviews_for_dealer(
    dealer_id: str,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    published_from: Optional[date] = Query(None, description="Filter reviews published from this date (YYYY-MM-DD format)"),
    published_to: Optional[date] = Query(None, description="Filter reviews published until this date (YYYY-MM-DD format)"),
    reviewer_name: Optional[str] = Query(None, description="Filter by reviewer name (partial match, case-insensitive)"),
    text_search: Optional[str] = Query(None, description="Search in review text (original or translated, case-insensitive)"),
    stars: Optional[int] = Query(None, ge=1, le=5, description="Filter by star rating (1-5)"),
    sort_by: ReviewSortBy = Query(ReviewSortBy.PUBLISHED_DATE, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order (asc/desc)"),
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> GetReviewsResponse:
    """
    Get Google review details for a dealer with filtering and pagination

    Args:
        dealer_id: Dealer ID to get reviews for (required path parameter)
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        published_from: Filter reviews from this date (YYYY-MM-DD format)
        published_to: Filter reviews until this date (YYYY-MM-DD format)
        reviewer_name: Filter by reviewer name (partial match)
        text_search: Search in review text (original or translated)
        stars: Filter by star rating (1-5)
        sort_by: Field to sort by (default: published_date)
        sort_order: Sort order (default: desc)
        controller: Google Review controller instance

    Returns:
        GetReviewsResponse with paginated and filtered review details

    Raises:
        HTTPException: If dealer not found or invalid parameters
    """
    return controller.get_reviews_for_dealer(
        dealer_id=dealer_id,
        page=page,
        per_page=per_page,
        published_from=published_from,
        published_to=published_to,
        reviewer_name=reviewer_name,
        text_search=text_search,
        stars=stars,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get(
    "/statistics/{dealer_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Review Statistics for Dealer",
    description="""
    Get comprehensive statistics for a dealer's Google Reviews.

    **Statistics Include:**
    - Business name and total score from Google
    - Total reviews count vs scraped reviews count
    - Average rating from scraped reviews
    - Last scraping date and status
    - Business contact information
    - Categories and location data

    **Use Cases:**
    - Dashboard overview
    - Monitoring scraping status
    - Business performance metrics
    """
)
async def get_review_statistics(
    dealer_id: str,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> Dict[str, Any]:
    """
    Get review statistics for a dealer

    Args:
        dealer_id: Dealer ID to get statistics for
        controller: Google Review controller instance

    Returns:
        Dictionary with comprehensive review statistics

    Raises:
        HTTPException: If dealer not found
    """
    return controller.get_review_statistics(dealer_id)


@router.get(
    "/recent/{dealer_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Recent Reviews for Dealer",
    description="""
    Get the most recent Google reviews for a dealer.

    **Features:**
    - Returns latest reviews sorted by publication date
    - Configurable limit (default: 5)
    - Simplified response format for quick display
    - Includes reviewer name, rating, text, and owner response

    **Use Cases:**
    - Homepage review showcase
    - Recent activity monitoring
    - Quick customer feedback overview
    """
)
async def get_recent_reviews(
    dealer_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of recent reviews to return (1-20)"),
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> Dict[str, Any]:
    """
    Get recent reviews for a dealer

    Args:
        dealer_id: Dealer ID to get recent reviews for
        limit: Number of recent reviews to return (default: 5, max: 20)
        controller: Google Review controller instance

    Returns:
        Dictionary with recent reviews data

    Raises:
        HTTPException: If dealer not found
    """
    return controller.get_recent_reviews(dealer_id, limit)


# Additional utility endpoints
@router.get(
    "/health",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Health Check for Google Review Service",
    description="Simple health check endpoint to verify the Google Review service is operational."
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "google-review-service",
        "timestamp": datetime.now().isoformat()
    }


@router.get(
    "/dealers/{dealer_id}/has-reviews",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Check if Dealer has Google Reviews Data",
    description="""
    Quick check to see if a dealer has any Google Reviews data in the system.

    **Response:**
    - has_reviews: Boolean indicating if reviews exist
    - last_scraped: Timestamp of last successful scraping
    - reviews_count: Total number of scraped reviews
    - scraping_status: Status of last scraping attempt

    **Use Cases:**
    - UI conditional rendering
    - Data availability checks
    - Integration status monitoring
    """
)
async def check_dealer_has_reviews(
    dealer_id: str,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> Dict[str, Any]:
    """
    Check if dealer has Google Reviews data

    Args:
        dealer_id: Dealer ID to check
        controller: Google Review controller instance

    Returns:
        Dictionary with data availability status

    Raises:
        HTTPException: If dealer not found
    """
    try:
        stats = controller.get_review_statistics(dealer_id)

        has_reviews = stats.get("data", {}).get("has_data", False)

        return {
            "success": True,
            "dealer_id": dealer_id,
            "has_reviews": has_reviews,
            "last_scraped": stats.get("data", {}).get("last_scraped"),
            "reviews_count": stats.get("data", {}).get("scraped_reviews_count", 0),
            "scraping_status": stats.get("data", {}).get("scraping_status"),
            "business_name": stats.get("data", {}).get("business_name")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking review data: {str(e)}"
        )


@router.post(
    "/analyze-sentiment",
    response_model=AnalyzeSentimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Sentiment for Google Reviews",
    description="""
    Perform sentiment analysis on Google Reviews for a specific dealer.

    **Process:**
    1. Validates dealer exists and has Google Reviews data
    2. Retrieves unanalyzed reviews (those without sentiment data)
    3. Calls sentiment analysis service to analyze review text
    4. Stores sentiment results in database with batch tracking
    5. Returns analysis summary with statistics

    **Sentiment Analysis Results:**
    - **Sentiment**: Positive, Negative, or Neutral classification
    - **Sentiment Score**: Numeric score from -5.00 (very negative) to 5.00 (very positive)
    - **Sentiment Reasons**: AI-generated explanation for the classification
    - **Sentiment Suggestion**: AI-generated suggestions for addressing the review
    - **Sentiment Themes**: JSON array of themes identified in the review

    **Features:**
    - Batch processing for performance optimization
    - Configurable processing limits and batch sizes
    - Complete audit trail with batch IDs and timestamps
    - Error handling for individual review analysis failures
    - Integration with existing sentiment analysis service

    **Use Cases:**
    - Bulk analysis of newly scraped reviews
    - Periodic sentiment analysis updates
    - Customer feedback insights and trend analysis
    - Business intelligence and reputation management
    """
)
async def analyze_reviews_sentiment(
    request: AnalyzeSentimentRequest,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> AnalyzeSentimentResponse:
    """
    Analyze sentiment for Google Reviews of a dealer

    Args:
        request: Sentiment analysis request with dealer_id, limit, and batch_size
        controller: Google Review controller instance

    Returns:
        AnalyzeSentimentResponse with analysis results and statistics

    Raises:
        HTTPException: If dealer not found, no reviews available, or analysis fails
    """
    return await controller.analyze_reviews_sentiment(request)


@router.get(
    "/sentiment-statistics/{dealer_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Sentiment Analysis Statistics for Dealer",
    description="""
    Get comprehensive sentiment analysis statistics for a dealer's Google Reviews.

    **Statistics Include:**
    - Total reviews count (with review text)
    - Analyzed vs unanalyzed reviews breakdown
    - Analysis completion rate percentage
    - Sentiment distribution (Positive, Negative, Neutral counts)
    - Average sentiment score across all analyzed reviews

    **Use Cases:**
    - Dashboard overview of sentiment analysis status
    - Business intelligence and reputation monitoring
    - Progress tracking for sentiment analysis completion
    - Performance metrics for customer satisfaction analysis

    **Response Format:**
    ```json
    {
        "dealer_id": "12284",
        "total_reviews": 150,
        "analyzed_reviews": 120,
        "unanalyzed_reviews": 30,
        "analysis_completion_rate": 80.0,
        "sentiment_distribution": {
            "Positive": 85,
            "Neutral": 25,
            "Negative": 10
        },
        "average_sentiment_score": 3.2
    }
    ```
    """
)
async def get_sentiment_statistics(
    dealer_id: str,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> Dict[str, Any]:
    """
    Get sentiment analysis statistics for a dealer

    Args:
        dealer_id: Dealer ID to get sentiment statistics for
        controller: Google Review controller instance

    Returns:
        Dictionary with comprehensive sentiment analysis statistics

    Raises:
        HTTPException: If dealer not found
    """
    return controller.get_sentiment_statistics(dealer_id)


@router.get(
    "/monthly-totals/{dealer_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Monthly Review Totals for Dealer",
    description="""
    Get monthly review totals for a dealer for a specific year using optimized database aggregation.

    **Features:**
    - **Optimized Performance**: Single SQL query with GROUP BY instead of multiple API calls
    - **Complete Data**: Returns all 12 months with zero counts for months without reviews
    - **Year Filtering**: Specify year or defaults to current year
    - **Aggregated Statistics**: Total year reviews and monthly breakdown

    **Response Includes:**
    - Monthly totals array with month names and review counts
    - Total reviews for the entire year
    - Year and dealer information
    - Zero counts for months without any reviews

    **Performance Benefits:**
    - Replaces 12 separate API calls with 1 optimized database query
    - Much faster response time for dashboard charts
    - Reduced network traffic and database load

    **Use Cases:**
    - Monthly review trend charts and analytics
    - Year-over-year comparison data
    - Business performance dashboards
    - Review activity pattern analysis

    **Response Format:**
    ```json
    {
        "success": true,
        "data": {
            "dealer_id": "12284",
            "year": 2025,
            "monthly_totals": [
                {"month": 1, "month_name": "Jan", "total_reviews": 5},
                {"month": 2, "month_name": "Feb", "total_reviews": 8},
                ...
            ],
            "total_year_reviews": 67
        }
    }
    ```
    """
)
async def get_monthly_review_totals(
    dealer_id: str,
    year: int = Query(None, description="Year to get monthly totals for (default: current year)"),
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> Dict[str, Any]:
    """
    Get monthly review totals for a dealer

    Args:
        dealer_id: Dealer ID to get monthly totals for
        year: Optional year to filter by (default: current year)
        controller: Google Review controller instance

    Returns:
        Dictionary with monthly totals and year summary

    Raises:
        HTTPException: If dealer not found
    """
    return controller.get_monthly_review_totals(dealer_id, year)


@router.get(
    "/profile/{dealer_id}",
    response_model=DealerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google Business Profile for Dealer",
    description="""
    Get complete Google Business Profile information for a specific dealer.

    **Profile Information Includes:**
    - **Business Details**: Name, rating, total reviews, category, location
    - **Photo Count**: Number of photos available on Google Business
    - **Contact Information**: Website, phone number, description
    - **Review Summary**: Star distribution, average rating, recent activity
    - **Review Tags**: Popular themes and categories from customer reviews
    - **Data Status**: Last update timestamp and scraping status

    **Use Cases:**
    - Display Google Business Profile replica in frontend
    - Business overview for dealer dashboard
    - Review summary and statistics visualization
    - Customer-facing business information display

    **Response Format:**
    - Complete business profile data in Google-style format
    - Star distribution chart data (1-5 stars with counts and percentages)
    - Review tags with counts (e.g., "quality service 122", "consumer 48")
    - Meta information about data freshness and availability

    **Data Sources:**
    - Latest successful Google Maps scraping results
    - Aggregated review statistics from scraped data
    - Sentiment analysis themes for review tags
    - Business contact information from Google Business listings
    """
)
async def get_dealer_profile(
    dealer_id: str,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> DealerProfileResponse:
    """
    Get Google Business Profile for a dealer

    Args:
        dealer_id: Dealer ID to get profile for
        controller: Google Review controller instance

    Returns:
        DealerProfileResponse with complete business profile data

    Raises:
        HTTPException: If dealer not found
    """
    return controller.get_dealer_profile(dealer_id)


@router.get(
    "/scrape-history",
    response_model=ScrapeHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google Review Scraping History",
    description="""
    Get history of Google Review scraping operations with optional dealer filtering.

    **Features:**
    - **Complete History**: All scraping attempts with status and results
    - **Dealer Filtering**: Filter by specific dealer (optional)
    - **Pagination**: Configurable page size and navigation
    - **Status Tracking**: Processing, completed, failed, and partial statuses
    - **Sentiment Integration**: Shows sentiment analysis progress and results
    - **Performance Metrics**: Success rates, duration, and error details

    **Response Includes:**
    - Scraping operation details (reviews scraped, failures, duration)
    - Sentiment analysis status and completion rates
    - Business information discovered during scraping
    - Error messages and warnings for failed operations
    - User tracking (who initiated the scraping)

    **Use Cases:**
    - Admin dashboard for monitoring scraping operations
    - Troubleshooting failed scraping attempts
    - Performance analysis and optimization
    - User activity tracking and auditing

    **Permissions:**
    - SUPER_ADMIN: Can view all scraping history across dealers
    - DEALER_USER: Can only view history for their assigned dealer
    """
)
async def get_scrape_history(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID (optional)"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=50, description="Items per page (1-50)"),
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> ScrapeHistoryResponse:
    """
    Get Google Review scraping history

    Args:
        dealer_id: Optional dealer ID filter
        page: Page number for pagination
        per_page: Number of items per page
        controller: Google Review controller instance

    Returns:
        ScrapeHistoryResponse with scraping history data

    Raises:
        HTTPException: If access denied or query fails
    """
    return controller.get_scrape_history(dealer_id, page, per_page)


@router.get(
    "/dealer-options",
    response_model=DealerOptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Dealer Options for Scraping",
    description="""
    Get list of dealers available for Google Review scraping with their configuration status.

    **Dealer Information Includes:**
    - **Basic Info**: Dealer ID, name, and location
    - **Configuration Status**: Whether Google location URL is configured
    - **Scraping Readiness**: Indicates if dealer is ready for review scraping

    **Use Cases:**
    - Populate dealer selection dropdown in scraping interface
    - Admin interface for dealer management
    - Configuration status checking
    - Bulk operations planning

    **Permissions:**
    - SUPER_ADMIN: Can see all dealers in the system
    - DEALER_USER: Can only see their assigned dealer

    **Response Format:**
    - List of dealers with scraping configuration status
    - Filtered based on user permissions
    - Sorted by dealer name for easy selection
    """
)
async def get_dealer_options(
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> DealerOptionsResponse:
    """
    Get dealer options for scraping

    Args:
        controller: Google Review controller instance

    Returns:
        DealerOptionsResponse with available dealers

    Raises:
        HTTPException: If access denied
    """
    return controller.get_dealer_options()


@router.get(
    "/dealers/{dealer_id}/latest-scrape-info",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Latest Scrape Information for Dealer",
    description="""
    Get the latest Google Review scraping information for a specific dealer.

    **Information Includes:**
    - **Scrape Details**: Date, status, reviews scraped, success rate
    - **Business Info**: Business name, rating, total reviews available
    - **Sentiment Analysis**: Status, progress, completion rate
    - **Processing Status**: Real-time indicators for ongoing operations
    - **Performance Metrics**: Scrape duration, error messages, warnings

    **Scrape Status Values:**
    - **PROCESSING**: Scraping operation is currently running
    - **COMPLETED**: Scraping completed successfully
    - **FAILED**: Scraping failed with error details
    - **PARTIAL**: Scraping completed with some failures

    **Sentiment Analysis Status:**
    - **PENDING**: Sentiment analysis queued but not started
    - **PROCESSING**: Sentiment analysis currently running
    - **COMPLETED**: Sentiment analysis finished successfully
    - **FAILED**: Sentiment analysis failed

    **Use Cases:**
    - Dashboard progress tracking and status display
    - Real-time scraping and analysis monitoring
    - Latest operation summary for user interface
    - Progress indicators for background operations

    **Response Examples:**

    **Active Processing:**
    ```json
    {
        "success": true,
        "message": "Latest scrape information retrieved successfully",
        "data": {
            "dealer_id": "12345",
            "scrape_date": "2025-09-26T15:30:00+07:00",
            "scrape_status": "PROCESSING",
            "scraped_reviews": 15,
            "max_reviews_requested": 30,
            "is_processing": true,
            "sentiment_analysis_status": "PENDING"
        }
    }
    ```

    **Completed with Sentiment Analysis:**
    ```json
    {
        "success": true,
        "message": "Latest scrape information retrieved successfully",
        "data": {
            "dealer_id": "12345",
            "scrape_date": "2025-09-26T15:30:00+07:00",
            "scrape_status": "COMPLETED",
            "scraped_reviews": 28,
            "max_reviews_requested": 30,
            "success_rate": 93.3,
            "sentiment_analysis_status": "COMPLETED",
            "sentiment_analyzed_count": 28,
            "sentiment_completion_rate": 100.0,
            "is_completed": true,
            "completed_date": "2025-09-26T15:35:00+07:00"
        }
    }
    ```

    **No Scrape Data:**
    ```json
    {
        "success": true,
        "message": "No scraping information found for this dealer",
        "data": null
    }
    ```
    """
)
async def get_latest_scrape_info(
    dealer_id: str,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> Dict[str, Any]:
    """
    Get latest scrape information for a specific dealer

    Args:
        dealer_id: Dealer ID to get latest scrape info for
        controller: Google Review controller instance

    Returns:
        Dictionary with latest scrape information including sentiment analysis status

    Raises:
        HTTPException: If dealer not found or access denied
    """
    return controller.get_latest_scrape_info(dealer_id)