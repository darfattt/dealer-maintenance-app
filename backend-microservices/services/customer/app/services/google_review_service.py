"""
Google Review Service for scraping Google Maps data via Apify API
"""

import uuid
import requests
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.google_review import GoogleReview, GoogleReviewDetail
from app.models.dealer_config import DealerConfig
from app.config import settings

logger = logging.getLogger(__name__)


class GoogleReviewService:
    """Service for scraping and storing Google Maps review data"""

    def __init__(self, db: Session):
        """
        Initialize Google Review Service

        Args:
            db: Database session
        """
        self.db = db

        # Load Apify API configuration from settings
        self.apify_api_url = settings.apify_api_url
        self.apify_api_token = settings.apify_api_token
        self.apify_timeout = settings.apify_timeout

        # Import sentiment service here to avoid circular imports
        try:
            from app.services.sentiment_analysis_service import SentimentAnalysisService
            self.sentiment_service = SentimentAnalysisService()
        except ImportError:
            logger.warning("SentimentAnalysisService not available")
            self.sentiment_service = None

    def scrape_reviews_for_dealer(
        self,
        dealer_id: str,
        max_reviews: int = 10,
        language: str = "id"
    ) -> Tuple[bool, str, Optional[GoogleReview]]:
        """
        Scrape Google Reviews for a specific dealer

        Args:
            dealer_id: Dealer ID to scrape reviews for
            max_reviews: Maximum number of reviews to fetch
            language: Language for reviews

        Returns:
            Tuple of (success, message, google_review_record)
        """
        try:
            # Get dealer configuration
            dealer = self.db.query(DealerConfig).filter(
                DealerConfig.dealer_id == dealer_id
            ).first()

            if not dealer:
                return False, f"Dealer with ID {dealer_id} not found", None

            if not dealer.google_location_url:
                return False, f"Google location URL not configured for dealer {dealer_id}", None

            # Generate unique API response ID for this scraping session
            api_response_id = f"{dealer_id}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

            # Prepare API request
            request_body = {
                "startUrls": [
                    {"url": dealer.google_location_url}
                ],
                "maxReviews": max_reviews,
                "language": language,
                "includeReviewerName": True,
                "includeReviewId": True,
                "includeOwnerResponse": True,
                "includeReviewerProfile": True
            }
            print(f"Request body :{request_body}")
            # Make API request
            success, api_response = self._call_apify_api(request_body)
        
            if not success:
                # Create failed record for audit
                failed_record = self._create_failed_record(
                    dealer_id, api_response_id, api_response
                )
                self.db.add(failed_record)
                self.db.commit()
                return False, f"API request failed: {api_response}", failed_record

            # Process API response
            if not api_response or len(api_response) == 0:
                return False, "No data returned from API", None

            # Take the first business result (should only be one)
            business_data = api_response[0]

            # Get or create Google Review record (upsert logic)
            place_id = business_data.get("placeId")
            google_review = None

            if place_id:
                # Check if a record already exists for this place_id
                existing_review = self.db.query(GoogleReview).filter(
                    GoogleReview.place_id == place_id
                ).first()

                if existing_review:
                    # Update existing record
                    google_review = self._update_google_review_record(
                        existing_review, dealer_id, api_response_id, business_data
                    )
                    logger.info(f"Updated existing GoogleReview record for place_id: {place_id}")
                else:
                    # Create new record
                    google_review = self._create_google_review_record(
                        dealer_id, api_response_id, business_data
                    )
                    self.db.add(google_review)
                    logger.info(f"Created new GoogleReview record for place_id: {place_id}")
            else:
                # No place_id available, create new record (shouldn't happen but handle gracefully)
                google_review = self._create_google_review_record(
                    dealer_id, api_response_id, business_data
                )
                self.db.add(google_review)
                logger.warning(f"Created GoogleReview record without place_id for dealer: {dealer_id}")

            self.db.flush()  # Get the ID

            # Process individual reviews (upsert logic for review details)
            new_reviews_count = 0
            if "reviews" in business_data and business_data["reviews"]:
                for review_data in business_data["reviews"]:
                    review_id = review_data.get("reviewId")

                    if review_id:
                        # Check if review already exists
                        existing_review_detail = self.db.query(GoogleReviewDetail).filter(
                            GoogleReviewDetail.review_id == review_id
                        ).first()

                        if existing_review_detail:
                            # Update existing review detail
                            self._update_review_detail_record(
                                existing_review_detail, google_review.id, dealer_id, review_data
                            )
                        else:
                            # Create new review detail
                            review_detail = self._create_review_detail_record(
                                google_review.id, dealer_id, review_data
                            )
                            self.db.add(review_detail)
                            new_reviews_count += 1
                    else:
                        # No review_id, create new record (might be duplicate but handle gracefully)
                        review_detail = self._create_review_detail_record(
                            google_review.id, dealer_id, review_data
                        )
                        self.db.add(review_detail)
                        new_reviews_count += 1

            self.db.commit()

            total_reviews = len(business_data.get('reviews', []))
            return True, f"Successfully processed {total_reviews} reviews ({new_reviews_count} new, {total_reviews - new_reviews_count} existing)", google_review

        except Exception as e:
            self.db.rollback()
            return False, f"Unexpected error: {str(e)}", None

    def _call_apify_api(self, request_body: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Call the Apify API

        Args:
            request_body: Request payload

        Returns:
            Tuple of (success, response_data_or_error_message)
        """
        try:
            headers = {
                "Content-Type": "application/json",
                #"Authorization": f"Bearer {self.APIFY_TOKEN}"
            }
            print(f"URL : {self.apify_api_url}?token={self.apify_api_token}")
            response = requests.post(
                f"{self.apify_api_url}?token={self.apify_api_token}",
                headers=headers,
                json=request_body,
                timeout=self.apify_timeout
            )

            response.raise_for_status()

            return True, response.json()

        except requests.exceptions.Timeout:
            return False, "API request timed out"
        except requests.exceptions.RequestException as e:
            return False, f"HTTP request error: {str(e)}"
        except json.JSONDecodeError:
            return False, "Invalid JSON response from API"
        except Exception as e:
            return False, f"Unexpected API error: {str(e)}"

    def _create_google_review_record(
        self,
        dealer_id: str,
        api_response_id: str,
        business_data: Dict[str, Any]
    ) -> GoogleReview:
        """
        Create GoogleReview record from API response

        Args:
            dealer_id: Dealer ID
            api_response_id: Unique API response identifier
            business_data: Business data from API

        Returns:
            GoogleReview instance
        """
        # Parse location data
        location = business_data.get("location", {})
        latitude = location.get("lat") if location else None
        longitude = location.get("lng") if location else None

        # Parse scraped_at timestamp
        scraped_at = None
        if "scrapedAt" in business_data and business_data["scrapedAt"]:
            try:
                scraped_at_str = business_data["scrapedAt"]
                if isinstance(scraped_at_str, str):
                    scraped_at = datetime.fromisoformat(
                        scraped_at_str.replace("Z", "+00:00")
                    )
                else:
                    scraped_at = datetime.now(timezone.utc)
            except (ValueError, TypeError):
                scraped_at = datetime.now(timezone.utc)

        # Parse popular times live data
        popular_times_live = None
        if "popularTimesLiveText" in business_data and "popularTimesLivePercent" in business_data:
            popular_times_live = {
                "text": business_data.get("popularTimesLiveText"),
                "percent": business_data.get("popularTimesLivePercent")
            }

        return GoogleReview(
            dealer_id=dealer_id,
            scraping_status="success",
            api_response_id=api_response_id,

            # Business information
            title=business_data.get("title"),
            subtitle=business_data.get("subTitle"),
            description=business_data.get("description"),
            category_name=business_data.get("categoryName"),

            # Location information
            address=business_data.get("address"),
            neighborhood=business_data.get("neighborhood"),
            street=business_data.get("street"),
            city=business_data.get("city"),
            postal_code=business_data.get("postalCode"),
            state=business_data.get("state"),
            country_code=business_data.get("countryCode"),
            latitude=latitude,
            longitude=longitude,
            plus_code=business_data.get("plusCode"),

            # Contact information
            website=business_data.get("website"),
            phone=business_data.get("phone"),
            phone_unformatted=business_data.get("phoneUnformatted"),

            # Business metrics
            total_score=business_data.get("totalScore"),
            reviews_count=business_data.get("reviewsCount"),
            images_count=business_data.get("imagesCount"),

            # Business status
            permanently_closed=business_data.get("permanentlyClosed", False),
            temporarily_closed=business_data.get("temporarilyClosed", False),
            claim_this_business=business_data.get("claimThisBusiness", False),

            # Google identifiers
            place_id=business_data.get("placeId"),
            google_cid=business_data.get("cid"),
            google_fid=business_data.get("fid"),

            # JSON fields
            location_data=location,
            reviews_distribution=business_data.get("reviewsDistribution"),
            categories=business_data.get("categories"),
            opening_hours=business_data.get("openingHours"),
            additional_opening_hours=business_data.get("additionalOpeningHours"),
            popular_times_histogram=business_data.get("popularTimesHistogram"),
            popular_times_live=popular_times_live,
            additional_info=business_data.get("additionalInfo"),
            reviews_tags=business_data.get("reviewsTags"),
            people_also_search=business_data.get("peopleAlsoSearch"),
            owner_updates=business_data.get("ownerUpdates"),
            booking_links=business_data.get("bookingLinks"),
            image_categories=business_data.get("imageCategories"),
            raw_api_response=business_data,

            # Timestamps
            scraped_at=scraped_at
        )

    def _update_google_review_record(
        self,
        existing_review: GoogleReview,
        dealer_id: str,
        api_response_id: str,
        business_data: Dict[str, Any]
    ) -> GoogleReview:
        """
        Update existing GoogleReview record with new data from API response

        Args:
            existing_review: Existing GoogleReview instance
            dealer_id: Dealer ID
            api_response_id: Unique API response identifier
            business_data: Business data from API

        Returns:
            Updated GoogleReview instance
        """
        # Parse location data
        location = business_data.get("location", {})
        latitude = location.get("lat") if location else None
        longitude = location.get("lng") if location else None

        # Parse scraped_at timestamp
        scraped_at = None
        if "scrapedAt" in business_data and business_data["scrapedAt"]:
            try:
                scraped_at_str = business_data["scrapedAt"]
                if isinstance(scraped_at_str, str):
                    scraped_at = datetime.fromisoformat(
                        scraped_at_str.replace("Z", "+00:00")
                    )
                else:
                    scraped_at = datetime.now(timezone.utc)
            except (ValueError, TypeError):
                scraped_at = datetime.now(timezone.utc)

        # Parse popular times live data
        popular_times_live = None
        if "popularTimesLiveText" in business_data and "popularTimesLivePercent" in business_data:
            popular_times_live = {
                "text": business_data.get("popularTimesLiveText"),
                "percent": business_data.get("popularTimesLivePercent")
            }

        # Update existing record with new data
        existing_review.dealer_id = dealer_id  # Update dealer_id in case it changed
        existing_review.scraping_status = "success"
        existing_review.api_response_id = api_response_id
        existing_review.scraping_error_message = None  # Clear any previous errors

        # Update business information
        existing_review.title = business_data.get("title")
        existing_review.subtitle = business_data.get("subTitle")
        existing_review.description = business_data.get("description")
        existing_review.category_name = business_data.get("categoryName")

        # Update location information
        existing_review.address = business_data.get("address")
        existing_review.neighborhood = business_data.get("neighborhood")
        existing_review.street = business_data.get("street")
        existing_review.city = business_data.get("city")
        existing_review.postal_code = business_data.get("postalCode")
        existing_review.state = business_data.get("state")
        existing_review.country_code = business_data.get("countryCode")
        existing_review.latitude = latitude
        existing_review.longitude = longitude
        existing_review.plus_code = business_data.get("plusCode")

        # Update contact information
        existing_review.website = business_data.get("website")
        existing_review.phone = business_data.get("phone")
        existing_review.phone_unformatted = business_data.get("phoneUnformatted")

        # Update business metrics
        existing_review.total_score = business_data.get("totalScore")
        existing_review.reviews_count = business_data.get("reviewsCount")
        existing_review.images_count = business_data.get("imagesCount")

        # Update business status
        existing_review.permanently_closed = business_data.get("permanentlyClosed", False)
        existing_review.temporarily_closed = business_data.get("temporarilyClosed", False)
        existing_review.claim_this_business = business_data.get("claimThisBusiness", False)

        # Update Google identifiers (place_id should remain the same, but update others)
        existing_review.google_cid = business_data.get("cid")
        existing_review.google_fid = business_data.get("fid")

        # Update JSON fields
        existing_review.location_data = location
        existing_review.reviews_distribution = business_data.get("reviewsDistribution")
        existing_review.categories = business_data.get("categories")
        existing_review.opening_hours = business_data.get("openingHours")
        existing_review.additional_opening_hours = business_data.get("additionalOpeningHours")
        existing_review.popular_times_histogram = business_data.get("popularTimesHistogram")
        existing_review.popular_times_live = popular_times_live
        existing_review.additional_info = business_data.get("additionalInfo")
        existing_review.reviews_tags = business_data.get("reviewsTags")
        existing_review.people_also_search = business_data.get("peopleAlsoSearch")
        existing_review.owner_updates = business_data.get("ownerUpdates")
        existing_review.booking_links = business_data.get("bookingLinks")
        existing_review.image_categories = business_data.get("imageCategories")
        existing_review.raw_api_response = business_data

        # Update timestamps
        existing_review.scraped_at = scraped_at
        existing_review.updated_at = datetime.utcnow()

        return existing_review

    def _create_review_detail_record(
        self,
        google_review_id: uuid.UUID,
        dealer_id: str,
        review_data: Dict[str, Any]
    ) -> GoogleReviewDetail:
        """
        Create GoogleReviewDetail record from review data

        Args:
            google_review_id: Parent GoogleReview ID
            dealer_id: Dealer ID
            review_data: Individual review data

        Returns:
            GoogleReviewDetail instance
        """
        # Parse published date
        published_at_date = None
        if "publishedAtDate" in review_data and review_data["publishedAtDate"]:
            try:
                published_date_str = review_data["publishedAtDate"]
                if isinstance(published_date_str, str):
                    published_at_date = datetime.fromisoformat(
                        published_date_str.replace("Z", "+00:00")
                    )
            except (ValueError, TypeError):
                pass

        # Parse owner response date
        response_from_owner_date = None
        if "responseFromOwnerDate" in review_data and review_data["responseFromOwnerDate"]:
            try:
                response_date_str = review_data["responseFromOwnerDate"]
                if isinstance(response_date_str, str):
                    response_from_owner_date = datetime.fromisoformat(
                        response_date_str.replace("Z", "+00:00")
                    )
            except (ValueError, TypeError):
                pass

        return GoogleReviewDetail(
            google_review_id=google_review_id,
            dealer_id=dealer_id,

            # Review identification
            review_id=review_data.get("reviewId"),
            reviewer_id=review_data.get("reviewerId"),
            reviewer_url=review_data.get("reviewerUrl"),

            # Reviewer information
            reviewer_name=review_data.get("name"),
            reviewer_number_of_reviews=review_data.get("reviewerNumberOfReviews"),
            is_local_guide=review_data.get("isLocalGuide", False),
            reviewer_photo_url=review_data.get("reviewerPhotoUrl"),

            # Review content
            review_text=review_data.get("text"),
            review_text_translated=review_data.get("textTranslated"),
            stars=review_data.get("stars"),
            likes_count=review_data.get("likesCount", 0),

            # Review metadata
            published_at=review_data.get("publishAt"),
            published_at_date=published_at_date,
            review_url=review_data.get("reviewUrl"),
            review_origin=review_data.get("reviewOrigin"),
            original_language=review_data.get("originalLanguage"),
            translated_language=review_data.get("translatedLanguage"),

            # Owner response
            response_from_owner_date=response_from_owner_date,
            response_from_owner_text=review_data.get("responseFromOwnerText"),

            # Additional data
            review_image_urls=review_data.get("reviewImageUrls"),
            review_context=review_data.get("reviewContext"),
            review_detailed_rating=review_data.get("reviewDetailedRating"),
            visited_in=review_data.get("visitedIn"),
            raw_review_data=review_data
        )

    def _update_review_detail_record(
        self,
        existing_review_detail: GoogleReviewDetail,
        google_review_id: uuid.UUID,
        dealer_id: str,
        review_data: Dict[str, Any]
    ) -> GoogleReviewDetail:
        """
        Update existing GoogleReviewDetail record with new data

        Args:
            existing_review_detail: Existing GoogleReviewDetail instance
            google_review_id: Parent GoogleReview ID
            dealer_id: Dealer ID
            review_data: Individual review data

        Returns:
            Updated GoogleReviewDetail instance
        """
        # Parse published date
        published_at_date = None
        if "publishedAtDate" in review_data and review_data["publishedAtDate"]:
            try:
                published_date_str = review_data["publishedAtDate"]
                if isinstance(published_date_str, str):
                    published_at_date = datetime.fromisoformat(
                        published_date_str.replace("Z", "+00:00")
                    )
            except (ValueError, TypeError):
                pass

        # Parse owner response date
        response_from_owner_date = None
        if "responseFromOwnerDate" in review_data and review_data["responseFromOwnerDate"]:
            try:
                response_date_str = review_data["responseFromOwnerDate"]
                if isinstance(response_date_str, str):
                    response_from_owner_date = datetime.fromisoformat(
                        response_date_str.replace("Z", "+00:00")
                    )
            except (ValueError, TypeError):
                pass

        # Update existing record with new data
        existing_review_detail.google_review_id = google_review_id
        existing_review_detail.dealer_id = dealer_id

        # Update reviewer information
        existing_review_detail.reviewer_id = review_data.get("reviewerId")
        existing_review_detail.reviewer_url = review_data.get("reviewerUrl")
        existing_review_detail.reviewer_name = review_data.get("name")
        existing_review_detail.reviewer_number_of_reviews = review_data.get("reviewerNumberOfReviews")
        existing_review_detail.is_local_guide = review_data.get("isLocalGuide", False)
        existing_review_detail.reviewer_photo_url = review_data.get("reviewerPhotoUrl")

        # Update review content
        existing_review_detail.review_text = review_data.get("text")
        existing_review_detail.review_text_translated = review_data.get("textTranslated")
        existing_review_detail.stars = review_data.get("stars")
        existing_review_detail.likes_count = review_data.get("likesCount", 0)

        # Update review metadata
        existing_review_detail.published_at = review_data.get("publishAt")
        existing_review_detail.published_at_date = published_at_date
        existing_review_detail.review_url = review_data.get("reviewUrl")
        existing_review_detail.review_origin = review_data.get("reviewOrigin")
        existing_review_detail.original_language = review_data.get("originalLanguage")
        existing_review_detail.translated_language = review_data.get("translatedLanguage")

        # Update owner response
        existing_review_detail.response_from_owner_date = response_from_owner_date
        existing_review_detail.response_from_owner_text = review_data.get("responseFromOwnerText")

        # Update additional data
        existing_review_detail.review_image_urls = review_data.get("reviewImageUrls")
        existing_review_detail.review_context = review_data.get("reviewContext")
        existing_review_detail.review_detailed_rating = review_data.get("reviewDetailedRating")
        existing_review_detail.visited_in = review_data.get("visitedIn")
        existing_review_detail.raw_review_data = review_data

        # Update timestamp
        existing_review_detail.updated_at = datetime.utcnow()

        # Note: We preserve existing sentiment analysis data to avoid overwriting it
        # If sentiment data needs to be updated, it should be done separately

        return existing_review_detail

    def _create_failed_record(
        self,
        dealer_id: str,
        api_response_id: str,
        error_message: str
    ) -> GoogleReview:
        """
        Create a failed GoogleReview record for audit purposes

        Args:
            dealer_id: Dealer ID
            api_response_id: Unique API response identifier
            error_message: Error description

        Returns:
            GoogleReview instance with failed status
        """
        return GoogleReview(
            dealer_id=dealer_id,
            scraping_status="failed",
            scraping_error_message=error_message,
            api_response_id=api_response_id
        )

    def get_latest_reviews_for_dealer(
        self,
        dealer_id: str,
        limit: int = 10
    ) -> Optional[GoogleReview]:
        """
        Get the latest Google Review record for a dealer

        Args:
            dealer_id: Dealer ID
            limit: Maximum number of reviews to include

        Returns:
            Latest GoogleReview record or None
        """
        try:
            return self.db.query(GoogleReview).filter(
                GoogleReview.dealer_id == dealer_id,
                GoogleReview.scraping_status == "success"
            ).order_by(GoogleReview.created_at.desc()).first()

        except SQLAlchemyError as e:
            return None

    def get_review_statistics_for_dealer(self, dealer_id: str) -> Dict[str, Any]:
        """
        Get review statistics for a dealer

        Args:
            dealer_id: Dealer ID

        Returns:
            Dictionary with statistics
        """
        try:
            latest_review = self.get_latest_reviews_for_dealer(dealer_id)

            if not latest_review:
                return {
                    "has_data": False,
                    "message": "No review data available"
                }

            # Get review details count
            details_count = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.google_review_id == latest_review.id
            ).count()

            # Calculate average rating from stored reviews
            review_details = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.google_review_id == latest_review.id,
                GoogleReviewDetail.stars.isnot(None)
            ).all()

            avg_rating = None
            if review_details:
                total_stars = sum(detail.stars for detail in review_details if detail.stars)
                avg_rating = total_stars / len(review_details) if review_details else None

            return {
                "has_data": True,
                "business_name": latest_review.title,
                "total_score": latest_review.total_score,
                "reviews_count": latest_review.reviews_count,
                "scraped_reviews_count": details_count,
                "average_rating_scraped": round(avg_rating, 1) if avg_rating else None,
                "last_scraped": latest_review.scraped_at.isoformat() if latest_review.scraped_at else None,
                "scraping_status": latest_review.scraping_status,
                "address": latest_review.address,
                "phone": latest_review.phone,
                "categories": latest_review.categories
            }

        except SQLAlchemyError as e:
            return {
                "has_data": False,
                "error": f"Database error: {str(e)}"
            }

    def get_recent_reviews_for_dealer(
        self,
        dealer_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent individual reviews for a dealer

        Args:
            dealer_id: Dealer ID
            limit: Number of reviews to return

        Returns:
            List of recent reviews
        """
        try:
            recent_reviews = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id
            ).order_by(
                GoogleReviewDetail.published_at_date.desc().nullslast(),
                GoogleReviewDetail.created_at.desc()
            ).limit(limit).all()

            return [
                {
                    "reviewer_name": review.reviewer_name,
                    "stars": review.stars,
                    "review_text": review.review_text,
                    "published_at": review.published_at,
                    "response_from_owner": review.response_from_owner_text,
                    "review_url": review.review_url
                }
                for review in recent_reviews
            ]

        except SQLAlchemyError as e:
            return []

    # Sentiment Analysis Methods

    def get_unanalyzed_reviews(
        self,
        dealer_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get Google Review details that haven't been analyzed for sentiment

        Args:
            dealer_id: Optional filter by dealer ID
            limit: Maximum number of records to return

        Returns:
            List of unanalyzed review records formatted for sentiment analysis
        """
        try:
            query = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.sentiment.is_(None),
                GoogleReviewDetail.review_text.isnot(None),
                GoogleReviewDetail.review_text != ""
            )

            if dealer_id:
                query = query.filter(GoogleReviewDetail.dealer_id == dealer_id)

            unanalyzed_reviews = query.limit(limit).all()

            # Format for sentiment analysis service
            formatted_reviews = []
            for review in unanalyzed_reviews:
                if review.review_text and review.review_text.strip():
                    formatted_reviews.append({
                        "id": str(review.id),
                        "no_tiket": review.review_id,
                        "review": review.review_text
                    })

            return formatted_reviews

        except SQLAlchemyError as e:
            logger.error(f"Error getting unanalyzed reviews: {str(e)}")
            return []

    def update_review_sentiment(
        self,
        review_id: str,
        sentiment_data: Dict[str, Any]
    ) -> bool:
        """
        Update a single review with sentiment analysis results

        Args:
            review_id: UUID of the review to update
            sentiment_data: Dictionary containing sentiment analysis results

        Returns:
            Boolean indicating success
        """
        try:
            review = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.id == review_id
            ).first()

            if not review:
                logger.warning(f"Review {review_id} not found for sentiment update")
                return False

            # Update sentiment fields
            review.sentiment = sentiment_data.get("sentiment")
            review.sentiment_score = sentiment_data.get("sentiment_score")
            review.sentiment_reasons = sentiment_data.get("sentiment_reasons")
            review.sentiment_suggestion = sentiment_data.get("sentiment_suggestion")
            review.sentiment_themes = sentiment_data.get("sentiment_themes")
            review.sentiment_analyzed_at = sentiment_data.get("sentiment_analyzed_at", datetime.now(timezone.utc))
            review.sentiment_batch_id = sentiment_data.get("sentiment_batch_id")

            self.db.commit()
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating sentiment for review {review_id}: {str(e)}")
            return False

    def bulk_update_review_sentiments(
        self,
        sentiment_results: List[Dict[str, Any]],
        batch_id: str
    ) -> Dict[str, int]:
        """
        Bulk update multiple reviews with sentiment analysis results

        Args:
            sentiment_results: List of sentiment analysis results
            batch_id: UUID for tracking this batch

        Returns:
            Dictionary with update statistics
        """
        updated_count = 0
        failed_count = 0

        try:
            for result in sentiment_results:
                review_id = result.get("id")
                if not review_id:
                    failed_count += 1
                    continue

                # Add batch ID to result
                result["sentiment_batch_id"] = uuid.UUID(batch_id)
                result["sentiment_analyzed_at"] = datetime.now(timezone.utc)

                success = self.update_review_sentiment(review_id, result)
                if success:
                    updated_count += 1
                else:
                    failed_count += 1

            logger.info(f"Bulk sentiment update completed: {updated_count} updated, {failed_count} failed")

        except Exception as e:
            logger.error(f"Error in bulk sentiment update: {str(e)}")
            failed_count += len(sentiment_results) - updated_count

        return {
            "updated_count": updated_count,
            "failed_count": failed_count
        }

    async def analyze_reviews_sentiment(
        self,
        dealer_id: str,
        limit: int = 50,
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze sentiment for Google Reviews of a specific dealer

        Args:
            dealer_id: Dealer ID to analyze reviews for
            limit: Maximum number of reviews to analyze
            batch_size: Size of batches for processing

        Returns:
            Dictionary with analysis results
        """
        if not self.sentiment_service:
            return {
                "success": False,
                "message": "Sentiment analysis service not available",
                "data": None
            }

        try:
            started_at = datetime.now(timezone.utc)

            # Get unanalyzed reviews for this dealer
            unanalyzed_reviews = self.get_unanalyzed_reviews(
                dealer_id=dealer_id,
                limit=limit
            )

            if not unanalyzed_reviews:
                return {
                    "success": True,
                    "message": "No unanalyzed reviews found for sentiment analysis",
                    "data": {
                        "dealer_id": dealer_id,
                        "batch_id": None,
                        "total_reviews": 0,
                        "analyzed_reviews": 0,
                        "failed_reviews": 0,
                        "started_at": started_at.isoformat(),
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    }
                }

            batch_id = str(uuid.uuid4())
            logger.info(f"Starting sentiment analysis for {len(unanalyzed_reviews)} Google Reviews (batch {batch_id})")

            total_analyzed = 0
            total_failed = 0

            # Process in smaller batches
            for i in range(0, len(unanalyzed_reviews), batch_size):
                batch = unanalyzed_reviews[i:i + batch_size]

                logger.info(f"Processing sentiment analysis batch {i//batch_size + 1} with {len(batch)} reviews")

                try:
                    # Analyze sentiments for this batch
                    sentiment_results, errors = await self.sentiment_service.analyze_sentiments(batch)

                    if sentiment_results:
                        # Update database with results
                        update_stats = self.bulk_update_review_sentiments(
                            sentiment_results,
                            batch_id=batch_id
                        )

                        total_analyzed += update_stats["updated_count"]
                        total_failed += update_stats["failed_count"]

                        if errors:
                            logger.warning(f"Batch {i//batch_size + 1} had {len(errors)} errors")
                    else:
                        logger.warning(f"No sentiment results for batch {i//batch_size + 1}")
                        total_failed += len(batch)

                except Exception as batch_error:
                    logger.error(f"Error processing sentiment batch {i//batch_size + 1}: {str(batch_error)}")
                    total_failed += len(batch)

                # Small delay between batches
                if i + batch_size < len(unanalyzed_reviews):
                    await asyncio.sleep(1)

            completed_at = datetime.now(timezone.utc)

            return {
                "success": True,
                "message": f"Sentiment analysis completed: {total_analyzed} analyzed, {total_failed} failed",
                "data": {
                    "dealer_id": dealer_id,
                    "batch_id": batch_id,
                    "total_reviews": len(unanalyzed_reviews),
                    "analyzed_reviews": total_analyzed,
                    "failed_reviews": total_failed,
                    "started_at": started_at.isoformat(),
                    "completed_at": completed_at.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error in sentiment analysis for dealer {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error during sentiment analysis: {str(e)}",
                "data": None
            }

    async def _safe_background_sentiment_analysis(self, dealer_id: str, limit: int = 50) -> None:
        """
        Safe wrapper for background sentiment analysis that catches all exceptions

        Args:
            dealer_id: Dealer ID to analyze reviews for
            limit: Maximum number of reviews to analyze
        """
        try:
            await self._background_sentiment_analysis(dealer_id, limit)
        except Exception as e:
            logger.error(f"Safe wrapper caught error in background sentiment analysis for dealer {dealer_id}: {str(e)}", exc_info=True)

    async def _background_sentiment_analysis(self, dealer_id: str, limit: int = 50) -> None:
        """
        Background task to perform sentiment analysis on Google Reviews

        Args:
            dealer_id: Dealer ID to analyze reviews for
            limit: Maximum number of reviews to analyze
        """
        try:
            logger.info(f"Starting background sentiment analysis for dealer {dealer_id}")

            result = await self.analyze_reviews_sentiment(
                dealer_id=dealer_id,
                limit=limit,
                batch_size=10
            )

            if result["success"]:
                data = result["data"]
                logger.info(f"Background sentiment analysis completed for dealer {dealer_id}: "
                           f"{data['analyzed_reviews']} analyzed, {data['failed_reviews']} failed")
            else:
                logger.error(f"Background sentiment analysis failed for dealer {dealer_id}: {result['message']}")

        except Exception as e:
            logger.error(f"Error in background sentiment analysis for dealer {dealer_id}: {str(e)}", exc_info=True)

    def get_review_sentiment_statistics(self, dealer_id: str) -> Dict[str, Any]:
        """
        Get sentiment analysis statistics for a dealer's Google Reviews

        Args:
            dealer_id: Dealer ID

        Returns:
            Dictionary with sentiment statistics
        """
        try:
            # Get total reviews count
            total_reviews = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.review_text.isnot(None),
                GoogleReviewDetail.review_text != ""
            ).count()

            # Get analyzed reviews count
            analyzed_reviews = self.db.query(GoogleReviewDetail).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.sentiment.isnot(None)
            ).count()

            # Get sentiment distribution
            from sqlalchemy import func
            sentiment_dist = self.db.query(
                GoogleReviewDetail.sentiment,
                func.count(GoogleReviewDetail.id).label('count')
            ).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.sentiment.isnot(None)
            ).group_by(GoogleReviewDetail.sentiment).all()

            sentiment_distribution = {item.sentiment: item.count for item in sentiment_dist}

            # Get average sentiment score
            avg_score_result = self.db.query(
                func.avg(GoogleReviewDetail.sentiment_score)
            ).filter(
                GoogleReviewDetail.dealer_id == dealer_id,
                GoogleReviewDetail.sentiment_score.isnot(None)
            ).scalar()

            avg_sentiment_score = float(avg_score_result) if avg_score_result else None

            return {
                "dealer_id": dealer_id,
                "total_reviews": total_reviews,
                "analyzed_reviews": analyzed_reviews,
                "unanalyzed_reviews": total_reviews - analyzed_reviews,
                "analysis_completion_rate": round((analyzed_reviews / total_reviews * 100), 2) if total_reviews > 0 else 0,
                "sentiment_distribution": sentiment_distribution,
                "average_sentiment_score": round(avg_sentiment_score, 2) if avg_sentiment_score else None
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting sentiment statistics for dealer {dealer_id}: {str(e)}")
            return {
                "dealer_id": dealer_id,
                "error": str(e)
            }