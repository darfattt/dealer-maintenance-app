"""
Customer Google Review Controller
Handles Google Reviews scraping and retrieval operations
"""

import math
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract

from app.services.google_review_service import GoogleReviewService
from app.models.google_review import GoogleReview, GoogleReviewDetail
from app.models.dealer_config import DealerConfig
from app.models.google_review_scrape_tracker import GoogleReviewScrapeTracker
from app.schemas.google_review_schemas import (
    ScrapeReviewsRequest,
    ScrapeReviewsResponse,
    GetReviewsRequest,
    GetReviewsResponse,
    ReviewDetailResponse,
    PaginationInfo,
    ReviewFilters,
    ErrorResponse,
    ReviewSortBy,
    SortOrder,
    AnalyzeSentimentRequest,
    AnalyzeSentimentResponse,
    DealerProfileResponse,
    DealerProfile,
    BusinessInfo,
    ReviewSummary,
    StarDistribution,
    ReviewTag,
    ScrapeTracker,
    ScrapeTrackerSummary,
    ScrapeHistoryResponse,
    DealerOptionsResponse,
    DealerOption,
    OwnerUpdate
)


class CustomerGoogleReviewController:
    """Controller for Google Review operations"""

    def __init__(self, db: Session):
        """
        Initialize controller with database session

        Args:
            db: Database session
        """
        self.db = db
        self.google_review_service = GoogleReviewService(db)
        # Thread pool for background sentiment analysis
        self.thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="sentiment_analysis")
        # Valid scrape types as per database constraint
        self._valid_scrape_types = {'MANUAL', 'SCHEDULED'}

    def _validate_scrape_type(self, scrape_type: str) -> str:
        """
        Validate and sanitize scrape_type value

        Args:
            scrape_type: The scrape type to validate

        Returns:
            Valid scrape_type value

        Raises:
            ValueError: If scrape_type is invalid
        """
        if scrape_type not in self._valid_scrape_types:
            # Log the invalid value and default to MANUAL
            print(f"Warning: Invalid scrape_type '{scrape_type}', defaulting to 'MANUAL'")
            return 'MANUAL'
        return scrape_type

    async def scrape_reviews_for_dealer(self, request: ScrapeReviewsRequest, scraped_by: str = None) -> ScrapeReviewsResponse:
        """
        Scrape Google Reviews for a specific dealer

        Args:
            request: Scrape reviews request data
            scraped_by: User who initiated the scraping

        Returns:
            ScrapeReviewsResponse with scraping results

        Raises:
            HTTPException: If dealer not found or scraping fails
        """
        # Create scrape tracker entry
        tracker = GoogleReviewScrapeTracker(
            dealer_id=request.dealer_id,
            dealer_name=None,  # Will be updated after dealer validation
            scrape_type=self._validate_scrape_type('MANUAL'),
            max_reviews_requested=request.max_reviews,
            language=request.language,
            scrape_status='PROCESSING',
            analyze_sentiment_enabled=request.auto_analyze_sentiment,
            sentiment_analysis_status='PENDING' if request.auto_analyze_sentiment else None,
            scraped_by=scraped_by
        )
        self.db.add(tracker)
        self.db.commit()
        self.db.refresh(tracker)

        scrape_start_time = datetime.now()

        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == request.dealer_id
            ).first()

            if not dealer:
                # Update tracker with error
                tracker.scrape_status = 'FAILED'
                tracker.error_message = f"Dealer with ID {request.dealer_id} not found"
                tracker.completed_date = datetime.now()
                tracker.scrape_duration_seconds = int((datetime.now() - scrape_start_time).total_seconds())
                self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {request.dealer_id} not found"
                )

            # Update tracker with dealer info
            tracker.dealer_name = dealer.dealer_name

            if not dealer.google_location_url:
                # Update tracker with error
                tracker.scrape_status = 'FAILED'
                tracker.error_message = f"Google location URL not configured for dealer {request.dealer_id}"
                tracker.completed_date = datetime.now()
                tracker.scrape_duration_seconds = int((datetime.now() - scrape_start_time).total_seconds())
                self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google location URL not configured for dealer {request.dealer_id}"
                )

            # Perform scraping
            success, message, google_review = self.google_review_service.scrape_reviews_for_dealer(
                dealer_id=request.dealer_id,
                max_reviews=request.max_reviews,
                language=request.language
            )

            # Calculate scrape duration
            scrape_duration = int((datetime.now() - scrape_start_time).total_seconds())

            if not success:
                # Update tracker with failure
                tracker.scrape_status = 'FAILED'
                tracker.error_message = message
                tracker.completed_date = datetime.now()
                tracker.scrape_duration_seconds = scrape_duration
                self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Scraping failed: {message}"
                )

            # Get scraped reviews count and update tracker
            scraped_reviews_count = 0
            new_reviews_count = 0

            if google_review:
                scraped_reviews_count = self.db.query(GoogleReviewDetail).filter(
                    GoogleReviewDetail.google_review_id == google_review.id
                ).count()

                # Count new reviews (those created in this scrape session)
                new_reviews_count = self.db.query(GoogleReviewDetail).filter(
                    GoogleReviewDetail.google_review_id == google_review.id,
                    GoogleReviewDetail.created_at >= scrape_start_time
                ).count()

                # Update tracker with scraping results
                tracker.api_response_id = google_review.api_response_id
                tracker.google_business_id = google_review.place_id
                tracker.business_name = google_review.title
                tracker.business_rating = str(google_review.total_score) if google_review.total_score else None
                tracker.total_reviews_available = google_review.reviews_count
                tracker.scraped_reviews = scraped_reviews_count
                tracker.new_reviews = new_reviews_count
                tracker.duplicate_reviews = scraped_reviews_count - new_reviews_count
                tracker.scrape_status = 'COMPLETED'
                tracker.completed_date = datetime.now()
                tracker.scrape_duration_seconds = scrape_duration

                # If auto sentiment analysis is enabled, trigger it in background
                if request.auto_analyze_sentiment and new_reviews_count > 0:
                    try:
                        tracker.sentiment_analysis_status = 'PROCESSING'
                        self.db.commit()

                        # Start background sentiment analysis using thread pool
                        loop = asyncio.get_event_loop()
                        loop.run_in_executor(
                            self.thread_pool,
                            self._run_sentiment_analysis_background,
                            request.dealer_id,
                            new_reviews_count,
                            str(tracker.id)
                        )

                    except Exception as e:
                        tracker.sentiment_analysis_status = 'FAILED'
                        tracker.warning_message = f"Error starting background sentiment analysis: {str(e)}"
                elif request.auto_analyze_sentiment and new_reviews_count == 0:
                    tracker.sentiment_analysis_status = 'COMPLETED'
                    tracker.warning_message = "No new reviews to analyze for sentiment"
            else:
                # Update tracker for failed scraping
                tracker.scrape_status = 'FAILED'
                tracker.completed_date = datetime.now()
                tracker.scrape_duration_seconds = scrape_duration

            self.db.commit()

            # Prepare response data
            response_data = {
                "dealer_id": request.dealer_id,
                "api_response_id": google_review.api_response_id if google_review else None,
                "business_name": google_review.title if google_review else None,
                "total_score": google_review.total_score if google_review else None,
                "reviews_count": google_review.reviews_count if google_review else None,
                "scraped_reviews_count": scraped_reviews_count,
                "new_reviews_count": new_reviews_count,
                "scraping_status": google_review.scraping_status if google_review else "failed",
                "scraped_at": google_review.scraped_at.isoformat() if google_review and google_review.scraped_at else None,
                "tracker_id": str(tracker.id),
                "auto_analyze_sentiment": request.auto_analyze_sentiment,
                "sentiment_status": tracker.sentiment_analysis_status
            }

            # Enhance message based on sentiment analysis status
            if request.auto_analyze_sentiment and new_reviews_count > 0:
                if tracker.sentiment_analysis_status == 'PROCESSING':
                    message += f". Sentiment analysis is running in background."
                elif tracker.sentiment_analysis_status == 'COMPLETED':
                    message += f". Sentiment analysis completed."
                elif tracker.sentiment_analysis_status == 'FAILED':
                    message += f". Sentiment analysis failed."

            return ScrapeReviewsResponse(
                success=True,
                message=message,
                data=response_data
            )

        except HTTPException:
            raise
        except Exception as e:
            # Update tracker with unexpected error
            try:
                tracker.scrape_status = 'FAILED'
                tracker.error_message = f"Unexpected error: {str(e)}"
                tracker.completed_date = datetime.now()
                tracker.scrape_duration_seconds = int((datetime.now() - scrape_start_time).total_seconds())
                self.db.commit()
            except:
                pass  # Ignore any errors during error logging

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during scraping: {str(e)}"
            )

    def get_reviews_for_dealer(
        self,
        dealer_id: str,
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
        published_from: Optional[date] = Query(None, description="Filter reviews published from this date"),
        published_to: Optional[date] = Query(None, description="Filter reviews published until this date"),
        reviewer_name: Optional[str] = Query(None, description="Filter by reviewer name (partial match)"),
        text_search: Optional[str] = Query(None, description="Search in review text"),
        stars: Optional[int] = Query(None, ge=1, le=5, description="Filter by star rating (1-5)"),
        sort_by: ReviewSortBy = Query(ReviewSortBy.PUBLISHED_DATE, description="Field to sort by"),
        sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order")
    ) -> GetReviewsResponse:
        """
        Get Google Review details for a dealer with filtering and pagination

        Args:
            dealer_id: Dealer ID to get reviews for
            page: Page number for pagination
            per_page: Number of items per page
            published_from: Filter reviews from this date
            published_to: Filter reviews until this date
            reviewer_name: Filter by reviewer name
            text_search: Search in review text
            stars: Filter by star rating
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            GetReviewsResponse with paginated review details

        Raises:
            HTTPException: If dealer not found or query fails
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Validate date range
            if published_from and published_to and published_to < published_from:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="published_to must be after published_from"
                )

            # Build base query
            query = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id
            )

            # Apply filters
            filters = []

            if published_from:
                filters.append(GoogleReviewDetail.published_at_date >= published_from)

            if published_to:
                filters.append(GoogleReviewDetail.published_at_date <= published_to)

            if reviewer_name:
                filters.append(GoogleReviewDetail.reviewer_name.ilike(f"%{reviewer_name}%"))

            if text_search:
                text_filter = or_(
                    GoogleReviewDetail.review_text.ilike(f"%{text_search}%"),
                    GoogleReviewDetail.review_text_translated.ilike(f"%{text_search}%")
                )
                filters.append(text_filter)

            if stars:
                filters.append(GoogleReviewDetail.stars == stars)

            if filters:
                query = query.filter(and_(*filters))

            # Apply sorting
            sort_column = self._get_sort_column(sort_by)
            if sort_order == SortOrder.DESC:
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

            # Add secondary sort by created_at for consistency
            query = query.order_by(GoogleReviewDetail.created_at.desc())

            # Get total count before pagination
            total_items = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            paginated_query = query.offset(offset).limit(per_page)

            # Execute query
            review_details = paginated_query.all()

            # Calculate pagination info
            total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
            has_next = page < total_pages
            has_prev = page > 1

            pagination = PaginationInfo(
                page=page,
                per_page=per_page,
                total_items=total_items,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )

            # Get latest Google Review for business info
            latest_google_review = self.db.query(GoogleReview).filter(
                GoogleReview.dealer_id == dealer_id,
                GoogleReview.scraping_status == "success"
            ).order_by(GoogleReview.created_at.desc()).first()

            # Prepare filters info
            filters_info = ReviewFilters(
                dealer_id=dealer_id,
                published_from=published_from,
                published_to=published_to,
                reviewer_name=reviewer_name,
                text_search=text_search,
                stars=stars,
                sort_by=sort_by.value,
                sort_order=sort_order.value
            )

            # Prepare response data
            response_data = {
                "dealer_id": dealer_id,
                "business_name": latest_google_review.title if latest_google_review else None,
                "last_scraped": latest_google_review.scraped_at.isoformat() if latest_google_review and latest_google_review.scraped_at else None
            }

            # Convert review details to response format
            reviews = [ReviewDetailResponse.from_model(detail) for detail in review_details]

            return GetReviewsResponse(
                success=True,
                message=f"Retrieved {len(reviews)} reviews for dealer {dealer_id}",
                data=response_data,
                pagination=pagination,
                filters=filters_info,
                reviews=reviews
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving reviews: {str(e)}"
            )

    def _get_sort_column(self, sort_by: ReviewSortBy):
        """
        Get SQLAlchemy column for sorting

        Args:
            sort_by: Sort field enum

        Returns:
            SQLAlchemy column object
        """
        sort_mapping = {
            ReviewSortBy.PUBLISHED_DATE: GoogleReviewDetail.published_at_date,
            ReviewSortBy.STARS: GoogleReviewDetail.stars,
            ReviewSortBy.REVIEWER_NAME: GoogleReviewDetail.reviewer_name,
            ReviewSortBy.CREATED_DATE: GoogleReviewDetail.created_at
        }

        return sort_mapping.get(sort_by, GoogleReviewDetail.published_at_date)

    def get_review_statistics(self, dealer_id: str) -> Dict[str, Any]:
        """
        Get review statistics for a dealer

        Args:
            dealer_id: Dealer ID

        Returns:
            Dictionary with statistics

        Raises:
            HTTPException: If dealer not found
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Get statistics from service
            stats = self.google_review_service.get_review_statistics_for_dealer(dealer_id)

            return {
                "success": True,
                "message": f"Statistics for dealer {dealer_id}",
                "data": stats
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving statistics: {str(e)}"
            )

    def get_recent_reviews(self, dealer_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get recent reviews for a dealer

        Args:
            dealer_id: Dealer ID
            limit: Number of recent reviews to return

        Returns:
            Dictionary with recent reviews

        Raises:
            HTTPException: If dealer not found
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Get recent reviews from service
            recent_reviews = self.google_review_service.get_recent_reviews_for_dealer(
                dealer_id, limit
            )

            return {
                "success": True,
                "message": f"Recent reviews for dealer {dealer_id}",
                "data": {
                    "dealer_id": dealer_id,
                    "reviews_count": len(recent_reviews),
                    "reviews": recent_reviews
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving recent reviews: {str(e)}"
            )

    async def analyze_reviews_sentiment(self, request: AnalyzeSentimentRequest) -> AnalyzeSentimentResponse:
        """
        Analyze sentiment for Google Reviews of a specific dealer using background processing

        Args:
            request: Sentiment analysis request data

        Returns:
            AnalyzeSentimentResponse with background processing status

        Raises:
            HTTPException: If dealer not found or no reviews available
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == request.dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {request.dealer_id} not found"
                )

            # Check if dealer has any Google Reviews data that need sentiment analysis
            # Use same query as sync method for consistency
            unanalyzed_reviews_count = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == request.dealer_id,
                GoogleReviewDetail.review_text.isnot(None),
                GoogleReviewDetail.review_text != "",
                GoogleReviewDetail.sentiment_analyzed_at.is_(None)  # Changed from sentiment.is_(None)
            ).count()

            if unanalyzed_reviews_count == 0:
                return AnalyzeSentimentResponse(
                    success=True,
                    message=f"No unanalyzed Google Reviews found for dealer {request.dealer_id}",
                    data={
                        "dealer_id": request.dealer_id,
                        "batch_id": None,
                        "total_reviews": 0,
                        "analyzed_reviews": 0,
                        "failed_reviews": 0,
                        "status": "COMPLETED",
                        "tracker_id": None,
                        "started_at": datetime.now().isoformat(),
                        "completed_at": datetime.now().isoformat()
                    }
                )

            # Create tracker for manual sentiment analysis
            tracker = GoogleReviewScrapeTracker(
                dealer_id=request.dealer_id,
                dealer_name=dealer.dealer_name,
                scrape_type=self._validate_scrape_type('MANUAL'),  # Validate scrape type
                max_reviews_requested=unanalyzed_reviews_count,
                language='id',  # Default language
                scrape_status='COMPLETED',  # Scraping is not needed, only sentiment
                scraped_reviews=unanalyzed_reviews_count,
                new_reviews=0,
                duplicate_reviews=0,
                analyze_sentiment_enabled=True,
                sentiment_analysis_status='PROCESSING',
                scraped_by='manual_sentiment_analysis'
            )
            self.db.add(tracker)
            self.db.commit()
            self.db.refresh(tracker)

            try:
                # Start background sentiment analysis using thread pool for manual analysis
                loop = asyncio.get_event_loop()
                loop.run_in_executor(
                    self.thread_pool,
                    self._run_manual_sentiment_analysis_background,
                    request.dealer_id,
                    request.limit,
                    str(tracker.id)
                )

                # Return immediately with processing status
                return AnalyzeSentimentResponse(
                    success=True,
                    message=f"Sentiment analysis started in background for {unanalyzed_reviews_count} reviews",
                    data={
                        "dealer_id": request.dealer_id,
                        "batch_id": None,  # Will be set by background process
                        "total_reviews": unanalyzed_reviews_count,
                        "analyzed_reviews": 0,  # Will be updated by background process
                        "failed_reviews": 0,  # Will be updated by background process
                        "status": "PROCESSING",
                        "tracker_id": str(tracker.id),
                        "started_at": datetime.now().isoformat(),
                        "completed_at": None  # Will be set by background process
                    }
                )

            except Exception as e:
                # Update tracker with error if background processing fails to start
                try:
                    tracker.sentiment_analysis_status = 'FAILED'
                    tracker.warning_message = f"Failed to start background sentiment analysis: {str(e)}"
                    self.db.commit()
                except Exception as db_error:
                    # If we can't update tracker, rollback and log error
                    try:
                        self.db.rollback()
                    except:
                        pass
                    print(f"Database error when updating tracker: {str(db_error)}")

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to start background sentiment analysis: {str(e)}"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during sentiment analysis setup: {str(e)}"
            )

    def get_sentiment_statistics(self, dealer_id: str) -> Dict[str, Any]:
        """
        Get sentiment analysis statistics for a dealer

        Args:
            dealer_id: Dealer ID

        Returns:
            Dictionary with sentiment statistics

        Raises:
            HTTPException: If dealer not found
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Get sentiment statistics from service
            stats = self.google_review_service.get_review_sentiment_statistics(dealer_id)

            return {
                "success": True,
                "message": f"Sentiment statistics for dealer {dealer_id}",
                "data": stats
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving sentiment statistics: {str(e)}"
            )

    def get_monthly_review_totals(self, dealer_id: str, year: int = None) -> Dict[str, Any]:
        """
        Get monthly review totals for a dealer for a specific year

        Args:
            dealer_id: Dealer ID to get monthly totals for
            year: Year to filter by (default: current year)

        Returns:
            Dictionary with monthly totals data

        Raises:
            HTTPException: If dealer not found or query fails
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Use current year if not specified
            if year is None:
                from datetime import datetime
                year = datetime.now().year

            # Query monthly totals using optimized SQL GROUP BY
            monthly_query = self.db.query(
                extract('month', GoogleReviewDetail.published_at_date).label('month'),
                func.count(GoogleReviewDetail.id).label('total_reviews')
            ).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                extract('year', GoogleReviewDetail.published_at_date) == year,
                GoogleReviewDetail.published_at_date.isnot(None)
            ).group_by(
                extract('month', GoogleReviewDetail.published_at_date)
            ).all()

            # Convert to dictionary for easy lookup
            month_data = {int(month): int(total) for month, total in monthly_query}

            # Generate all 12 months with proper names and zero counts for missing months
            monthly_totals = []
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            for month in range(1, 13):
                monthly_totals.append({
                    "month": month,
                    "month_name": month_names[month - 1],
                    "total_reviews": month_data.get(month, 0)
                })

            # Calculate total year reviews
            total_year_reviews = sum(month_data.values())

            return {
                "success": True,
                "data": {
                    "dealer_id": dealer_id,
                    "year": year,
                    "monthly_totals": monthly_totals,
                    "total_year_reviews": total_year_reviews
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving monthly review totals: {str(e)}"
            )

    def get_dealer_profile(self, dealer_id: str) -> DealerProfileResponse:
        """
        Get complete Google Business Profile for a dealer

        Args:
            dealer_id: Dealer ID

        Returns:
            DealerProfileResponse with complete profile data

        Raises:
            HTTPException: If dealer not found
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Get latest Google Review data
            latest_google_review = self.db.query(GoogleReview).filter(
                GoogleReview.dealer_id == dealer_id,
                GoogleReview.scraping_status == "success"
            ).order_by(GoogleReview.created_at.desc()).first()

            if not latest_google_review:
                # Return empty profile if no data
                profile_data = DealerProfile(
                    business_info=BusinessInfo(),
                    review_summary=ReviewSummary(),
                    review_tags=[],
                    has_data=False,
                    scraping_status="no_data"
                )

                return DealerProfileResponse(
                    success=True,
                    message=f"No Google Reviews data found for dealer {dealer_id}",
                    data=profile_data
                )

            # Parse additional business information from JSON fields
            opening_hours_raw = latest_google_review.opening_hours
            additional_info = latest_google_review.additional_info
            categories = latest_google_review.categories

            # Transform opening_hours from list to dictionary format if needed
            opening_hours = None
            if opening_hours_raw:
                if isinstance(opening_hours_raw, list):
                    # Convert list format [{'day': 'Selasa', 'hours': '07.30 to 16.30'}] to dict format
                    opening_hours = {}
                    for hour_entry in opening_hours_raw:
                        if isinstance(hour_entry, dict) and 'day' in hour_entry:
                            day_key = hour_entry['day'].lower()
                            # Use 'hours' field if available, otherwise use 'time' or the whole entry
                            if 'hours' in hour_entry:
                                opening_hours[day_key] = hour_entry['hours']
                            elif 'time' in hour_entry:
                                opening_hours[day_key] = hour_entry['time']
                            else:
                                # Fallback: convert dict to string representation
                                hour_info = {k: v for k, v in hour_entry.items() if k != 'day'}
                                opening_hours[day_key] = str(hour_info) if hour_info else 'N/A'
                elif isinstance(opening_hours_raw, dict):
                    # Already in dictionary format
                    opening_hours = opening_hours_raw
                else:
                    # Handle string or other formats
                    opening_hours = {'general': str(opening_hours_raw)}

            # Extract services from categories or additional info
            services = []
            if categories:
                if isinstance(categories, list):
                    services.extend(categories)
                elif isinstance(categories, str):
                    services.append(categories)

            # Extract appointment info from additional info
            appointments = None
            if additional_info and isinstance(additional_info, dict):
                # Look for appointment-related keys
                appointment_keys = ['appointments', 'booking', 'reservations', 'online_booking']
                for key in appointment_keys:
                    if key in additional_info:
                        appointments = {
                            'available': True,
                            'info': additional_info[key]
                        }
                        break

                # Check for service offerings in additional info
                if 'service_options' in additional_info:
                    if isinstance(additional_info['service_options'], list):
                        services.extend(additional_info['service_options'])

            # Extract owner updates from latest_google_review
            owner_updates_data = []
            if latest_google_review.owner_updates:
                try:
                    import json
                    if isinstance(latest_google_review.owner_updates, str):
                        owner_updates_raw = json.loads(latest_google_review.owner_updates)
                    else:
                        owner_updates_raw = latest_google_review.owner_updates

                    # Process owner updates into OwnerUpdate schema format
                    if isinstance(owner_updates_raw, list):
                        for update in owner_updates_raw:
                            if isinstance(update, dict):
                                owner_update = OwnerUpdate(
                                    title=update.get('title'),
                                    description=update.get('description'),
                                    imageUrl=update.get('imageUrl') or update.get('image_url'),
                                    date=update.get('date'),
                                    url=update.get('url')
                                )
                                owner_updates_data.append(owner_update)
                except Exception as e:
                    # Log error and continue with empty owner updates
                    print(f"Error processing owner updates for dealer {dealer_id}: {e}")
                    owner_updates_data = []

            # Build business info with enhanced data
            business_info = BusinessInfo(
                name=latest_google_review.title,
                rating=float(latest_google_review.total_score) if latest_google_review.total_score else None,
                total_reviews=latest_google_review.reviews_count or 0,
                category=latest_google_review.category_name or "Motorcycle repair shop",
                location=f"{latest_google_review.city}, {latest_google_review.state}" if latest_google_review.city and latest_google_review.state else None,
                photos_count=latest_google_review.images_count or 0,
                description=latest_google_review.description,
                website=latest_google_review.website,
                phone=latest_google_review.phone,
                address=latest_google_review.address,
                hours=opening_hours,
                services=services if services else None,
                appointments=appointments,
                ownerUpdates=owner_updates_data
            )

            # Get review statistics for star distribution
            review_details = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id
            ).all()

            # Calculate star distribution
            star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            total_scraped = len(review_details)

            for review in review_details:
                if review.stars and 1 <= review.stars <= 5:
                    star_counts[review.stars] += 1

            # Build star distribution - ALWAYS show all 5 stars (1-5) even if count is 0
            star_distribution = []
            for stars in range(1, 6):
                count = star_counts[stars]
                percentage = (count / total_scraped * 100) if total_scraped > 0 else 0
                star_distribution.append(StarDistribution(
                    stars=stars,
                    count=count,
                    percentage=round(percentage, 1)
                ))

            # Calculate precise average rating from scraped reviews (no rounding)
            if total_scraped > 0:
                # Get all valid ratings from reviews
                valid_ratings = [review.stars for review in review_details if review.stars]
                scraped_average = sum(valid_ratings) / len(valid_ratings) if valid_ratings else None
                # Keep precise value, don't round
                if scraped_average is not None:
                    scraped_average = round(scraped_average, 2)  # Only round to 2 decimal places for precision
            else:
                scraped_average = None

            # Get recent reviews count (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_count = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.published_at_date >= thirty_days_ago
            ).count()

            # Build review summary
            review_summary = ReviewSummary(
                total_reviews=total_scraped,
                average_rating=scraped_average,
                star_distribution=star_distribution,
                recent_review_count=recent_count
            )

            # Get review tags from sentiment themes
            review_tags = []
            sentiment_themes = self.db.query(GoogleReviewDetail.sentiment_themes).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.sentiment_themes.isnot(None),
                GoogleReviewDetail.sentiment_themes != ""
            ).all()

            # Parse themes and count them
            theme_counts = {}
            for theme_result in sentiment_themes:
                if theme_result.sentiment_themes:
                    try:
                        import json
                        themes = json.loads(theme_result.sentiment_themes)
                        if isinstance(themes, list):
                            for theme in themes:
                                theme = str(theme).strip().lower()
                                if theme:
                                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
                    except:
                        # If not JSON, try splitting by comma
                        themes = theme_result.sentiment_themes.split(',')
                        for theme in themes:
                            theme = theme.strip().lower()
                            if theme:
                                theme_counts[theme] = theme_counts.get(theme, 0) + 1

            # Create review tags from most common themes
            sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]  # Top 10
            for theme, count in sorted_themes:
                review_tags.append(ReviewTag(
                    tag=theme,
                    count=count,
                    category="experience",  # Default category
                    sentiment="positive"  # Default sentiment, can be enhanced
                ))

            # Build complete profile
            profile_data = DealerProfile(
                business_info=business_info,
                review_summary=review_summary,
                review_tags=review_tags,
                last_updated=latest_google_review.scraped_at,
                has_data=True,
                scraping_status=latest_google_review.scraping_status
            )

            return DealerProfileResponse(
                success=True,
                message=f"Profile retrieved for dealer {dealer_id}",
                data=profile_data
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving dealer profile: {str(e)}"
            )

    def get_scrape_history(self, dealer_id: str = None, page: int = 1, per_page: int = 20) -> ScrapeHistoryResponse:
        """
        Get scraping history for dealers

        Args:
            dealer_id: Optional dealer ID to filter by
            page: Page number for pagination
            per_page: Items per page

        Returns:
            ScrapeHistoryResponse with history data
        """
        try:
            # Build query
            query = self.db.query(GoogleReviewScrapeTracker)

            if dealer_id:
                query = query.filter(GoogleReviewScrapeTracker.dealer_id == dealer_id)

            # Order by scrape date descending
            query = query.order_by(GoogleReviewScrapeTracker.scrape_date.desc())

            # Get total count
            total_items = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            paginated_query = query.offset(offset).limit(per_page)

            # Execute query
            trackers = paginated_query.all()

            # Calculate pagination info
            total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
            has_next = page < total_pages
            has_prev = page > 1

            pagination = PaginationInfo(
                page=page,
                per_page=per_page,
                total_items=total_items,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )

            # Calculate summary statistics
            successful_scrapes = len([t for t in trackers if t.scrape_status == 'COMPLETED'])
            failed_scrapes = len([t for t in trackers if t.scrape_status == 'FAILED'])
            processing_scrapes = len([t for t in trackers if t.scrape_status == 'PROCESSING'])

            # Prepare summary data
            summary_data = {
                "total_scrapes": total_items,
                "successful_scrapes": successful_scrapes,
                "failed_scrapes": failed_scrapes,
                "processing_scrapes": processing_scrapes,
                "current_page_items": len(trackers)
            }

            if dealer_id:
                summary_data["dealer_id"] = dealer_id

            # Convert to response format using ScrapeTrackerSummary
            history_items = [ScrapeTrackerSummary.from_model(tracker) for tracker in trackers]

            return ScrapeHistoryResponse(
                success=True,
                message=f"Retrieved {len(history_items)} scrape history items",
                data=summary_data,
                trackers=history_items,
                pagination=pagination.dict()
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving scrape history: {str(e)}"
            )

    def get_dealer_options(self) -> DealerOptionsResponse:
        """
        Get list of dealers available for scraping

        Returns:
            DealerOptionsResponse with dealer options
        """
        try:
            # Get dealers with Google location URL configured
            dealers = self.db.query(DealerConfig).filter(
                DealerConfig.google_location_url.isnot(None),
                DealerConfig.google_location_url != ""
            ).order_by(DealerConfig.dealer_name).all()

            # Convert to options format
            dealer_options = [
                DealerOption(
                    dealer_id=dealer.dealer_id,
                    dealer_name=dealer.dealer_name or dealer.dealer_id,
                    has_google_url=bool(dealer.google_location_url)
                )
                for dealer in dealers
            ]

            return DealerOptionsResponse(
                success=True,
                message=f"Retrieved {len(dealer_options)} dealer options",
                data=dealer_options
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving dealer options: {str(e)}"
            )

    def get_latest_scrape_info(self, dealer_id: str) -> Dict[str, Any]:
        """
        Get latest scrape information for a specific dealer

        Args:
            dealer_id: Dealer ID to get latest scrape info for

        Returns:
            Dictionary with latest scrape information including sentiment analysis status

        Raises:
            HTTPException: If dealer not found or query fails
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Get the latest scrape tracker for the dealer
            latest_tracker = self.db.query(GoogleReviewScrapeTracker).filter(
                GoogleReviewScrapeTracker.dealer_id == dealer_id
            ).order_by(GoogleReviewScrapeTracker.scrape_date.desc()).first()

            if not latest_tracker:
                return {
                    "success": True,
                    "message": "No scraping information found for this dealer",
                    "data": None
                }

            # Return the tracker data using the built-in to_dict method
            tracker_data = latest_tracker.to_dict()

            return {
                "success": True,
                "message": "Latest scrape information retrieved successfully",
                "data": tracker_data
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving latest scrape information: {str(e)}"
            )

    def _run_sentiment_analysis_background(self, dealer_id: str, limit: int, tracker_id: str) -> None:
        """
        Run sentiment analysis in background thread

        Args:
            dealer_id: Dealer ID to analyze reviews for
            limit: Maximum number of reviews to analyze
            tracker_id: Tracker ID to update status
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            sentiment_start_time = datetime.now()
            print(f"Starting background sentiment analysis for dealer {dealer_id} (tracker: {tracker_id})")

            # Create new database session for background thread
            from app.dependencies import db_manager
            background_db = next(db_manager.get_session())
            try:
                # Get tracker record
                tracker = background_db.query(GoogleReviewScrapeTracker).filter(
                    GoogleReviewScrapeTracker.id == tracker_id
                ).first()

                if not tracker:
                    logger.error(f"Tracker {tracker_id} not found for background sentiment analysis")
                    return

                try:
                    # Create sentiment request
                    sentiment_request = AnalyzeSentimentRequest(
                        dealer_id=dealer_id,
                        limit=limit,
                        batch_size=10
                    )

                    # Initialize controller with background db session
                    background_controller = CustomerGoogleReviewController(background_db)

                    # Run sentiment analysis synchronously in background thread
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        sentiment_result = loop.run_until_complete(
                            background_controller.analyze_reviews_sentiment(sentiment_request)
                        )

                        # Update tracker with results
                        if sentiment_result.success:
                            tracker.sentiment_analysis_status = 'COMPLETED'
                            tracker.sentiment_analyzed_count = sentiment_result.data.get('analyzed_reviews', 0)
                            tracker.sentiment_failed_count = sentiment_result.data.get('failed_reviews', 0)
                            logger.info(f"Background sentiment analysis completed for dealer {dealer_id}: "
                                      f"{tracker.sentiment_analyzed_count} analyzed, {tracker.sentiment_failed_count} failed")
                        else:
                            tracker.sentiment_analysis_status = 'FAILED'
                            tracker.warning_message = f"Sentiment analysis failed: {sentiment_result.message}"
                            logger.error(f"Background sentiment analysis failed for dealer {dealer_id}: {sentiment_result.message}")

                        tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())
                        background_db.commit()

                    finally:
                        loop.close()

                except Exception as sentiment_error:
                    logger.error(f"Error during background sentiment analysis for dealer {dealer_id}: {str(sentiment_error)}")
                    try:
                        # Rollback any failed transaction before updating tracker
                        background_db.rollback()

                        # Re-fetch tracker to ensure we have a clean state
                        tracker = background_db.query(GoogleReviewScrapeTracker).filter(
                            GoogleReviewScrapeTracker.id == tracker_id
                        ).first()

                        if tracker:
                            tracker.sentiment_analysis_status = 'FAILED'
                            tracker.warning_message = f"Background sentiment analysis error: {str(sentiment_error)}"
                            tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())
                            background_db.commit()
                    except Exception as update_error:
                        logger.error(f"Failed to update tracker after error: {str(update_error)}")
                        try:
                            background_db.rollback()
                        except:
                            pass  # Ignore rollback errors

            finally:
                background_db.close()

        except Exception as e:
            logger.error(f"Critical error in background sentiment analysis for dealer {dealer_id}: {str(e)}", exc_info=True)

    def _run_manual_sentiment_analysis_background(self, dealer_id: str, limit: int, tracker_id: str) -> None:
        """
        Run manual sentiment analysis for unanalyzed reviews in background thread

        Args:
            dealer_id: Dealer ID to analyze reviews for
            limit: Maximum number of reviews to analyze
            tracker_id: Tracker ID to update status
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            sentiment_start_time = datetime.now()
            print(f"Starting background manual sentiment analysis for dealer {dealer_id} (tracker: {tracker_id})")

            # Create new database session for background thread
            from app.dependencies import db_manager
            background_db = next(db_manager.get_session())
            try:
                # Get tracker record
                tracker = background_db.query(GoogleReviewScrapeTracker).filter(
                    GoogleReviewScrapeTracker.id == tracker_id
                ).first()

                if not tracker:
                    logger.error(f"Tracker {tracker_id} not found for background manual sentiment analysis")
                    return

                try:
                    # Import sentiment service
                    from app.services.sentiment_analysis_service import SentimentAnalysisService
                    sentiment_service = SentimentAnalysisService()

                    # Get unanalyzed Google Review Details where review_text is not null and sentiment_analyzed_at is null
                    unanalyzed_reviews = background_db.query(GoogleReviewDetail).filter(
                        GoogleReviewDetail.dealer_id == dealer_id,
                        GoogleReviewDetail.review_text.isnot(None),
                        GoogleReviewDetail.review_text != "",
                        GoogleReviewDetail.sentiment_analyzed_at.is_(None)
                    ).limit(limit).all()

                    if not unanalyzed_reviews:
                        logger.info(f"No unanalyzed reviews found for dealer {dealer_id}")
                        tracker.sentiment_analysis_status = 'COMPLETED'
                        tracker.sentiment_analyzed_count = 0
                        tracker.sentiment_failed_count = 0
                        tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())
                        background_db.commit()
                        return

                    # Prepare records for sentiment analysis (same format as customer satisfaction)
                    formatted_records = []
                    for review in unanalyzed_reviews:
                        formatted_records.append({
                            "id": str(review.id),
                            "no_tiket": review.review_id or "",  # Add null handling like Customer Satisfaction
                            "review": review.review_text or ""
                        })

                    print(f"📊 Processing {len(formatted_records)} records for sentiment analysis")
                    print(f"📝 Sample record: {formatted_records[0] if formatted_records else 'None'}")

                    # Run sentiment analysis asynchronously in background thread
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        # Process sentiment analysis
                        sentiment_results, errors = loop.run_until_complete(
                            sentiment_service.analyze_sentiments(formatted_records)
                        )

                        print(f"✅ Sentiment Results Count: {len(sentiment_results) if sentiment_results else 0}")
                        print(f"❌ Errors Count: {len(errors) if errors else 0}")
                        if errors:
                            print(f"🚨 First error: {errors[0] if errors else 'None'}")
                        if sentiment_results:
                            print(f"📄 Sample result: {sentiment_results[0] if sentiment_results else 'None'}")

                        # Update GoogleReviewDetail records with sentiment results
                        successful_count = 0
                        failed_count = 0

                        for result in sentiment_results:
                            try:
                                record_id = result.get('id')
                                review_record = background_db.query(GoogleReviewDetail).filter(
                                    GoogleReviewDetail.id == record_id
                                ).first()

                                if review_record:
                                    # Update sentiment fields - Fixed to match sentiment analysis service output
                                    review_record.sentiment = result.get('sentiment')
                                    review_record.sentiment_score = result.get('sentiment_score')
                                    review_record.sentiment_reasons = result.get('sentiment_reasons')
                                    review_record.sentiment_suggestion = result.get('sentiment_suggestion')
                                    review_record.sentiment_themes = result.get('sentiment_themes')
                                    review_record.sentiment_analyzed_at = result.get('sentiment_analyzed_at')
                                    review_record.sentiment_batch_id = result.get('sentiment_batch_id')

                                    successful_count += 1

                            except Exception as e:
                                failed_count += 1
                                errors.append(f"Failed to update record {record_id}: {str(e)}")

                        # Handle failed sentiment analysis errors
                        for error in errors:
                            failed_count += 1

                        # Commit all changes
                        background_db.commit()

                        # Update tracker with results
                        tracker.sentiment_analysis_status = 'COMPLETED'
                        tracker.sentiment_analyzed_count = successful_count
                        tracker.sentiment_failed_count = failed_count
                        tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())

                        if failed_count > 0:
                            tracker.warning_message = f"Sentiment analysis completed with {failed_count} failures"

                        background_db.commit()

                        logger.info(f"Background manual sentiment analysis completed for dealer {dealer_id}: "
                                  f"{successful_count} analyzed, {failed_count} failed")

                    finally:
                        loop.close()

                except Exception as sentiment_error:
                    logger.error(f"Error during background manual sentiment analysis for dealer {dealer_id}: {str(sentiment_error)}")
                    try:
                        # Rollback any failed transaction before updating tracker
                        background_db.rollback()

                        # Re-fetch tracker to ensure we have a clean state
                        tracker = background_db.query(GoogleReviewScrapeTracker).filter(
                            GoogleReviewScrapeTracker.id == tracker_id
                        ).first()

                        if tracker:
                            tracker.sentiment_analysis_status = 'FAILED'
                            tracker.warning_message = f"Background manual sentiment analysis error: {str(sentiment_error)}"
                            tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())
                            background_db.commit()
                    except Exception as update_error:
                        logger.error(f"Failed to update tracker after error: {str(update_error)}")
                        try:
                            background_db.rollback()
                        except:
                            pass  # Ignore rollback errors

            finally:
                background_db.close()

        except Exception as e:
            logger.error(f"Critical error in background manual sentiment analysis for dealer {dealer_id}: {str(e)}", exc_info=True)

    async def sync_process_google_review_sentiment_analysis(
        self,
        dealer_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Process sentiment analysis for Google Reviews synchronously

        Args:
            dealer_id: Dealer ID to process reviews for
            limit: Maximum number of reviews to process

        Returns:
            Dictionary containing processing results

        Raises:
            HTTPException: If dealer not found or processing fails
        """
        try:
            # Validate dealer exists
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dealer with ID {dealer_id} not found"
                )

            # Import sentiment service
            from app.services.sentiment_analysis_service import SentimentAnalysisService
            sentiment_service = SentimentAnalysisService()

            # Get unanalyzed Google Review Details where review_text is not null and sentiment_analyzed_at is null
            unanalyzed_reviews = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.review_text.isnot(None),
                GoogleReviewDetail.review_text != "",
                GoogleReviewDetail.sentiment_analyzed_at.is_(None)
            )

            if not unanalyzed_reviews:
                return {
                    "success": True,
                    "message": f"No unanalyzed Google Reviews found for dealer {dealer_id}",
                    "data": {
                        "dealer_id": dealer_id,
                        "total_records": 0,
                        "processed_records": 0,
                        "successful_records": 0,
                        "failed_records": 0,
                        "errors": []
                    }
                }

            # Prepare records for sentiment analysis (same format as customer satisfaction)
            formatted_records = []
            for review in unanalyzed_reviews:
                formatted_records.append({
                    "id": str(review.id),
                    "no_tiket": review.review_id or "",  # Add null handling like Customer Satisfaction
                    "review": review.review_text or ""
                })

            print(f"📊 Processing {len(formatted_records)} records for sentiment analysis")
            print(f"📝 Sample record: {formatted_records[0] if formatted_records else 'None'}")

            # Process sentiment analysis
            sentiment_results, errors = await sentiment_service.analyze_sentiments(formatted_records)
            print(f"✅ Sentiment Results Count: {len(sentiment_results) if sentiment_results else 0}")
            print(f"❌ Errors Count: {len(errors) if errors else 0}")
            if errors:
                print(f"🚨 First error: {errors[0] if errors else 'None'}")
            if sentiment_results:
                print(f"📄 Sample result: {sentiment_results[0] if sentiment_results else 'None'}")
            # Update GoogleReviewDetail records with sentiment results
            successful_count = 0
            failed_count = 0

            for result in sentiment_results:
                try:
                    record_id = result.get('id')
                    review_record = self.db.query(GoogleReviewDetail).filter(
                        GoogleReviewDetail.id == record_id
                    ).first()

                    if review_record:
                        # Update sentiment fields - Fixed to match sentiment analysis service output
                        review_record.sentiment = result.get('sentiment')
                        review_record.sentiment_score = result.get('sentiment_score')
                        review_record.sentiment_reasons = result.get('sentiment_reasons')
                        review_record.sentiment_suggestion = result.get('sentiment_suggestion')
                        review_record.sentiment_themes = result.get('sentiment_themes')
                        review_record.sentiment_analyzed_at = result.get('sentiment_analyzed_at')
                        review_record.sentiment_batch_id = result.get('sentiment_batch_id')

                        successful_count += 1

                except Exception as e:
                    failed_count += 1
                    errors.append(f"Failed to update record {record_id}: {str(e)}")

            # Handle failed sentiment analysis errors
            for error in errors:
                failed_count += 1

            # Commit all changes
            self.db.commit()

            return {
                "success": True,
                "message": f"Processed {len(formatted_records)} Google Reviews for sentiment analysis",
                "data": {
                    "dealer_id": dealer_id,
                    "total_records": len(formatted_records),
                    "processed_records": len(sentiment_results),
                    "successful_records": successful_count,
                    "failed_records": failed_count,
                    "errors": errors[:10]  # Limit to first 10 errors
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            # Rollback in case of unexpected error
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing Google Review sentiment analysis: {str(e)}"
            )

    def __del__(self):
        """Cleanup thread pool executor on object deletion"""
        if hasattr(self, 'thread_pool') and self.thread_pool:
            self.thread_pool.shutdown(wait=False)