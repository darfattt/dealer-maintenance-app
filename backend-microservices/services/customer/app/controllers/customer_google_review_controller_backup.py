"""
Customer Google Review Controller
Handles Google Reviews scraping and retrieval operations
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.services.google_review_service import GoogleReviewService
from app.models.google_review import GoogleReview, GoogleReviewDetail
from app.models.dealer_config import DealerConfig
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
    ReviewTag
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

    def scrape_reviews_for_dealer(self, request: ScrapeReviewsRequest) -> ScrapeReviewsResponse:
        """
        Scrape Google Reviews for a specific dealer

        Args:
            request: Scrape reviews request data

        Returns:
            ScrapeReviewsResponse with scraping results

        Raises:
            HTTPException: If dealer not found or scraping fails
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

            if not dealer.google_location_url:
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

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Scraping failed: {message}"
                )

            # Get scraped reviews count
            scraped_reviews_count = 0
            if google_review:
                scraped_reviews_count = self.db.query(GoogleReviewDetail).filter(
                    GoogleReviewDetail.google_review_id == google_review.id
                ).count()

            # Prepare response data
            response_data = {
                "dealer_id": request.dealer_id,
                "api_response_id": google_review.api_response_id if google_review else None,
                "business_name": google_review.title if google_review else None,
                "total_score": google_review.total_score if google_review else None,
                "reviews_count": google_review.reviews_count if google_review else None,
                "scraped_reviews_count": scraped_reviews_count,
                "scraping_status": google_review.scraping_status if google_review else "failed",
                "scraped_at": google_review.scraped_at.isoformat() if google_review and google_review.scraped_at else None
            }

            return ScrapeReviewsResponse(
                success=True,
                message=message,
                data=response_data
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during scraping: {str(e)}"
            )

    def get_reviews_for_dealer(
        self,
        dealer_id: str,
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
        published_from: Optional[datetime] = Query(None, description="Filter reviews published from this date"),
        published_to: Optional[datetime] = Query(None, description="Filter reviews published until this date"),
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
        Analyze sentiment for Google Reviews of a specific dealer

        Args:
            request: Sentiment analysis request data

        Returns:
            AnalyzeSentimentResponse with analysis results

        Raises:
            HTTPException: If dealer not found or analysis fails
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

            # Check if dealer has any Google Reviews data
            reviews_count = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == request.dealer_id,
                GoogleReviewDetail.review_text.isnot(None),
                GoogleReviewDetail.review_text != ""
            ).count()

            if reviews_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No Google Reviews found for dealer {request.dealer_id}"
                )

            # Perform sentiment analysis
            result = await self.google_review_service.analyze_reviews_sentiment(
                dealer_id=request.dealer_id,
                limit=request.limit,
                batch_size=request.batch_size
            )

            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Sentiment analysis failed: {result['message']}"
                )

            return AnalyzeSentimentResponse(
                success=True,
                message=result["message"],
                data=result["data"]
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during sentiment analysis: {str(e)}"
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

            # Build business info
            business_info = BusinessInfo(
                name=latest_google_review.title,
                rating=float(latest_google_review.total_score) if latest_google_review.total_score else None,
                total_reviews=latest_google_review.reviews_count or 0,
                category="Motorcycle repair shop",  # Default category, can be enhanced
                location=f"{latest_google_review.city}, {latest_google_review.state}" if latest_google_review.city and latest_google_review.state else None,
                photos_count=latest_google_review.photos_count or 0,
                description=latest_google_review.description,
                website=latest_google_review.website,
                phone=latest_google_review.phone
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

            # Build star distribution
            star_distribution = []
            for stars in range(1, 6):
                count = star_counts[stars]
                percentage = (count / total_scraped * 100) if total_scraped > 0 else 0
                star_distribution.append(StarDistribution(
                    stars=stars,
                    count=count,
                    percentage=round(percentage, 1)
                ))

            # Calculate average rating from scraped reviews
            if total_scraped > 0:
                total_stars = sum(review.stars * star_counts[review.stars] for review in [1, 2, 3, 4, 5] for review_stars in [review] if review in star_counts)
                scraped_average = sum(review.stars for review in review_details if review.stars) / len([r for r in review_details if r.stars]) if len([r for r in review_details if r.stars]) > 0 else None
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