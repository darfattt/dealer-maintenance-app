# Google Reviews Scraping Flow - End-to-End Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Frontend Flow](#frontend-flow)
4. [API Service Layer](#api-service-layer)
5. [Backend API Routes](#backend-api-routes)
6. [Controller Layer](#controller-layer)
7. [Service Layer](#service-layer)
8. [External API Integration](#external-api-integration)
9. [Database Storage](#database-storage)
10. [Background Processing](#background-processing)
11. [Sequence Diagram](#sequence-diagram)
12. [Data Models](#data-models)
13. [Error Handling](#error-handling)
14. [Key Features](#key-features)

---

## Overview

The Google Reviews Scraping system allows administrators to scrape Google Maps reviews for dealers and optionally perform sentiment analysis on the reviews. The system follows a layered architecture pattern:

- **Frontend**: Vue.js 3 components for user interaction
- **API Gateway**: Routes authenticated requests to microservices
- **Backend Service**: FastAPI microservice for Google Reviews operations
- **External API**: Apify API for Google Maps data scraping
- **Database**: PostgreSQL with `customer` schema for data persistence
- **Background Workers**: Thread pool for asynchronous sentiment analysis

### Key Components
- **Frontend**: `GoogleReviews.vue`, `GoogleReviewScrapingSidebar.vue`
- **Service**: `GoogleReviewService.js` (HTTP client)
- **Routes**: `google_review_routes.py` (FastAPI endpoints)
- **Controller**: `CustomerGoogleReviewController` (business logic)
- **Service**: `GoogleReviewService` (Apify API integration)
- **Models**: `GoogleReview`, `GoogleReviewDetail`, `GoogleReviewScrapeTracker`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                               │
│  ┌──────────────────────┐      ┌───────────────────────────────┐   │
│  │ GoogleReviews.vue    │      │GoogleReviewScrapingSidebar.vue│   │
│  │ (Main Dashboard)     │◄────►│ (Scraping UI)                 │   │
│  └──────────┬───────────┘      └──────────┬────────────────────┘   │
│             │                               │                        │
│             └───────────────┬───────────────┘                        │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API SERVICE LAYER                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │          GoogleReviewService.js (HTTP Client)               │   │
│  │  • scrapeReviews()                                          │   │
│  │  • getReviewsForDealer()                                    │   │
│  │  • getLatestScrapeInfo()                                    │   │
│  └────────────────────────┬────────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼ POST /v1/google-reviews/scrape-reviews
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND API LAYER                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │   google_review_routes.py (FastAPI Routes)                  │   │
│  │   @router.post("/scrape-reviews")                           │   │
│  └────────────────────────┬────────────────────────────────────┘   │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  CustomerGoogleReviewController                             │   │
│  │  • scrape_reviews_for_dealer()                              │   │
│  │  • Create GoogleReviewScrapeTracker                         │   │
│  │  • Validate dealer and configuration                        │   │
│  └────────────────────────┬────────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │        GoogleReviewService (Apify Integration)              │   │
│  │  • scrape_reviews_for_dealer()                              │   │
│  │  • _call_apify_api()                                        │   │
│  │  • _create_google_review_record()                           │   │
│  │  • _create_review_detail_record()                           │   │
│  └────────────────────────┬────────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼ POST {apify_api_url}?token={token}
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL API LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Apify Google Maps Scraper API                  │   │
│  │  • Scrapes Google Maps business data                        │   │
│  │  • Returns business info + individual reviews               │   │
│  └────────────────────────┬────────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼ JSON Response
┌─────────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │        PostgreSQL (customer schema)                         │   │
│  │  • google_reviews (Business data)                           │   │
│  │  • google_review_details (Individual reviews)               │   │
│  │  • google_review_scrape_tracker (Audit trail)               │   │
│  │  • dealer_config (Dealer configuration)                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Optional)
┌─────────────────────────────────────────────────────────────────────┐
│                  BACKGROUND PROCESSING                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │        Thread Pool Executor (Sentiment Analysis)            │   │
│  │  • _run_sentiment_analysis_background()                     │   │
│  │  • SentimentAnalysisService (OpenAI integration)            │   │
│  │  • Updates GoogleReviewDetail with sentiment data           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Flow

### 1. User Interface - GoogleReviewScrapingSidebar.vue

**File**: `web/src/components/GoogleReviewScrapingSidebar.vue`

#### Component Responsibilities:
- Displays scraping configuration form in a sidebar
- Allows dealer selection, max reviews configuration
- Triggers scraping operation
- Shows scraping history

#### Key Methods:

```javascript
// Load dealer options from API
const loadDealerOptions = async () => {
    const result = await CustomerService.getActiveDealers();
    // Map dealers to dropdown options
    dealerOptions.value = result.data.map(dealer => ({
        label: dealer.dealer_name || dealer.dealer_id,
        value: dealer.dealer_id
    }));
};

// Main scraping function
const scrapeReviews = async () => {
    const result = await GoogleReviewService.scrapeReviews({
        dealer_id: selectedDealer.value,
        max_reviews: maxReviews.value,
        language: language.value,
        auto_analyze_sentiment: analyzeSentiment.value
    });

    if (result.success) {
        // Show success toast
        // Refresh history
        await refreshHistory();
        emit('scrape-success');
    }
};
```

#### User Interaction Flow:
1. User clicks **"Manage Scraping"** button in `GoogleReviews.vue`
2. Sidebar opens showing dealer selection dropdown
3. User selects:
   - Dealer (required)
   - Max Reviews (1-50, default: 10)
   - Language (default: 'id' for Indonesian)
4. User clicks **"Scrape Reviews"** button
5. Loading spinner shown during API call
6. Success/error toast notification displayed
7. Scraping history refreshed automatically

---

## API Service Layer

### GoogleReviewService.js

**File**: `web/src/service/GoogleReviewService.js`

#### Scraping Method:

```javascript
async scrapeReviews(options = {}) {
    const {
        dealer_id,
        max_reviews = 10,
        language = 'id',
        auto_analyze_sentiment = true
    } = options;

    const requestData = {
        dealer_id,
        max_reviews,
        language,
        auto_analyze_sentiment
    };

    // POST /v1/google-reviews/scrape-reviews
    const response = await api.post(
        '/v1/google-reviews/scrape-reviews',
        requestData
    );
    return response.data;
}
```

#### Request Format:
```json
{
    "dealer_id": "12284",
    "max_reviews": 10,
    "language": "id",
    "auto_analyze_sentiment": false
}
```

#### Response Format:
```json
{
    "success": true,
    "message": "Successfully processed 10 reviews (5 new, 5 existing)",
    "data": {
        "dealer_id": "12284",
        "api_response_id": "12284_abc12345_1234567890",
        "business_name": "AHASS Honda Dealer XYZ",
        "total_score": 4.5,
        "reviews_count": 150,
        "scraped_reviews_count": 10,
        "new_reviews_count": 5,
        "scraping_status": "success",
        "scraped_at": "2025-10-02T10:30:00+07:00",
        "tracker_id": "uuid-tracker-id",
        "auto_analyze_sentiment": false,
        "sentiment_status": null
    }
}
```

---

## Backend API Routes

### google_review_routes.py

**File**: `backend-microservices/services/customer/app/routes/google_review_routes.py`

#### Endpoint Definition:

```python
@router.post(
    "/scrape-reviews",
    response_model=ScrapeReviewsResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape Google Reviews for Dealer"
)
async def scrape_reviews_for_dealer(
    request: ScrapeReviewsRequest,
    controller: CustomerGoogleReviewController = Depends(get_google_review_controller)
) -> ScrapeReviewsResponse:
    """
    Scrape Google Maps reviews for a specific dealer using the Apify API.

    Process:
    1. Validates dealer exists and has google_location_url configured
    2. Calls Apify API to scrape Google Maps data
    3. Stores business information and individual reviews in database
    4. Returns scraping summary with audit information
    """
    return await controller.scrape_reviews_for_dealer(request)
```

#### Request Schema (Pydantic):

```python
class ScrapeReviewsRequest(BaseModel):
    dealer_id: str = Field(..., description="Dealer ID to scrape reviews for")
    max_reviews: int = Field(10, ge=1, le=50, description="Maximum reviews to fetch")
    language: str = Field("id", description="Language code for reviews")
    auto_analyze_sentiment: bool = Field(False, description="Auto-analyze sentiment")
```

---

## Controller Layer

### CustomerGoogleReviewController

**File**: `backend-microservices/services/customer/app/controllers/customer_google_review_controller.py`

#### Main Scraping Method:

```python
async def scrape_reviews_for_dealer(
    self,
    request: ScrapeReviewsRequest,
    scraped_by: str = None
) -> ScrapeReviewsResponse:
    """
    Orchestrates the entire scraping process with tracking and error handling
    """

    # STEP 1: Create scrape tracker for audit trail
    tracker = GoogleReviewScrapeTracker(
        dealer_id=request.dealer_id,
        scrape_type='MANUAL',
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
        # STEP 2: Validate dealer exists
        dealer = self.db.query(DealerConfig).filter(
            DealerConfig.dealer_id == request.dealer_id
        ).first()

        if not dealer:
            tracker.scrape_status = 'FAILED'
            tracker.error_message = f"Dealer with ID {request.dealer_id} not found"
            tracker.completed_date = datetime.now()
            self.db.commit()
            raise HTTPException(status_code=404, detail="Dealer not found")

        # STEP 3: Validate Google location URL is configured
        if not dealer.google_location_url:
            tracker.scrape_status = 'FAILED'
            tracker.error_message = "Google location URL not configured"
            tracker.completed_date = datetime.now()
            self.db.commit()
            raise HTTPException(status_code=400, detail="Google URL not configured")

        # STEP 4: Perform scraping via GoogleReviewService
        success, message, google_review = self.google_review_service.scrape_reviews_for_dealer(
            dealer_id=request.dealer_id,
            max_reviews=request.max_reviews,
            language=request.language
        )

        scrape_duration = int((datetime.now() - scrape_start_time).total_seconds())

        if not success:
            tracker.scrape_status = 'FAILED'
            tracker.error_message = message
            tracker.scrape_duration_seconds = scrape_duration
            self.db.commit()
            raise HTTPException(status_code=500, detail=f"Scraping failed: {message}")

        # STEP 5: Count scraped reviews
        scraped_reviews_count = self.db.query(GoogleReviewDetail).filter(
            GoogleReviewDetail.google_review_id == google_review.id
        ).count()

        new_reviews_count = self.db.query(GoogleReviewDetail).filter(
            GoogleReviewDetail.google_review_id == google_review.id,
            GoogleReviewDetail.created_at >= scrape_start_time
        ).count()

        # STEP 6: Update tracker with success results
        tracker.api_response_id = google_review.api_response_id
        tracker.google_business_id = google_review.place_id
        tracker.business_name = google_review.title
        tracker.business_rating = str(google_review.total_score)
        tracker.total_reviews_available = google_review.reviews_count
        tracker.scraped_reviews = scraped_reviews_count
        tracker.new_reviews = new_reviews_count
        tracker.duplicate_reviews = scraped_reviews_count - new_reviews_count
        tracker.scrape_status = 'COMPLETED'
        tracker.completed_date = datetime.now()
        tracker.scrape_duration_seconds = scrape_duration

        # STEP 7: Optional background sentiment analysis
        if request.auto_analyze_sentiment and new_reviews_count > 0:
            tracker.sentiment_analysis_status = 'PROCESSING'
            self.db.commit()

            # Start background thread for sentiment analysis
            loop = asyncio.get_event_loop()
            loop.run_in_executor(
                self.thread_pool,
                self._run_sentiment_analysis_background,
                request.dealer_id,
                new_reviews_count,
                str(tracker.id)
            )

        self.db.commit()

        # STEP 8: Return response
        return ScrapeReviewsResponse(
            success=True,
            message=message,
            data={
                "dealer_id": request.dealer_id,
                "api_response_id": google_review.api_response_id,
                "business_name": google_review.title,
                "total_score": google_review.total_score,
                "reviews_count": google_review.reviews_count,
                "scraped_reviews_count": scraped_reviews_count,
                "new_reviews_count": new_reviews_count,
                "scraping_status": "success",
                "scraped_at": google_review.scraped_at.isoformat(),
                "tracker_id": str(tracker.id),
                "auto_analyze_sentiment": request.auto_analyze_sentiment,
                "sentiment_status": tracker.sentiment_analysis_status
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        # Update tracker with unexpected error
        tracker.scrape_status = 'FAILED'
        tracker.error_message = f"Unexpected error: {str(e)}"
        tracker.completed_date = datetime.now()
        tracker.scrape_duration_seconds = int((datetime.now() - scrape_start_time).total_seconds())
        self.db.commit()
        raise HTTPException(status_code=500, detail=str(e))
```

#### Key Responsibilities:
1. **Audit Tracking**: Create and update `GoogleReviewScrapeTracker` for every scraping attempt
2. **Validation**: Ensure dealer exists and has Google location URL configured
3. **Error Handling**: Comprehensive error handling with tracker updates
4. **Performance Tracking**: Record scrape duration and success rates
5. **Background Processing**: Optional sentiment analysis in separate thread
6. **Database Transactions**: Proper commit/rollback handling

---

## Service Layer

### GoogleReviewService

**File**: `backend-microservices/services/customer/app/services/google_review_service.py`

#### Main Scraping Method:

```python
def scrape_reviews_for_dealer(
    self,
    dealer_id: str,
    max_reviews: int = 10,
    language: str = "id"
) -> Tuple[bool, str, Optional[GoogleReview]]:
    """
    Scrape Google Reviews for a specific dealer

    Returns:
        Tuple of (success, message, google_review_record)
    """
    try:
        # STEP 1: Get dealer configuration
        dealer = self.db.query(DealerConfig).filter(
            DealerConfig.dealer_id == dealer_id
        ).first()

        if not dealer or not dealer.google_location_url:
            return False, "Dealer not found or no Google URL", None

        # STEP 2: Generate unique API response ID
        api_response_id = f"{dealer_id}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

        # STEP 3: Prepare Apify API request
        request_body = {
            "startUrls": [{"url": dealer.google_location_url}],
            "maxReviews": max_reviews,
            "language": language,
            "includeReviewerName": True,
            "includeReviewId": True,
            "includeOwnerResponse": True,
            "includeReviewerProfile": True
        }

        # STEP 4: Call Apify API
        success, api_response = self._call_apify_api(request_body)

        if not success:
            # Create failed record for audit
            failed_record = self._create_failed_record(
                dealer_id, api_response_id, api_response
            )
            self.db.add(failed_record)
            self.db.commit()
            return False, f"API request failed: {api_response}", failed_record

        if not api_response or len(api_response) == 0:
            return False, "No data returned from API", None

        # STEP 5: Process API response
        business_data = api_response[0]
        place_id = business_data.get("placeId")

        # STEP 6: Upsert GoogleReview record
        if place_id:
            existing_review = self.db.query(GoogleReview).filter(
                GoogleReview.place_id == place_id
            ).first()

            if existing_review:
                google_review = self._update_google_review_record(
                    existing_review, dealer_id, api_response_id, business_data
                )
            else:
                google_review = self._create_google_review_record(
                    dealer_id, api_response_id, business_data
                )
                self.db.add(google_review)
        else:
            google_review = self._create_google_review_record(
                dealer_id, api_response_id, business_data
            )
            self.db.add(google_review)

        self.db.flush()  # Get the ID

        # STEP 7: Process individual reviews (upsert logic)
        new_reviews_count = 0
        if "reviews" in business_data and business_data["reviews"]:
            for review_data in business_data["reviews"]:
                review_id = review_data.get("reviewId")

                if review_id:
                    existing_review_detail = self.db.query(GoogleReviewDetail).filter(
                        GoogleReviewDetail.review_id == review_id
                    ).first()

                    if existing_review_detail:
                        self._update_review_detail_record(
                            existing_review_detail, google_review.id, dealer_id, review_data
                        )
                    else:
                        review_detail = self._create_review_detail_record(
                            google_review.id, dealer_id, review_data
                        )
                        self.db.add(review_detail)
                        new_reviews_count += 1
                else:
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
```

#### Helper Methods:

```python
def _call_apify_api(self, request_body: Dict[str, Any]) -> Tuple[bool, Any]:
    """Call the Apify API with timeout and error handling"""
    try:
        headers = {"Content-Type": "application/json"}
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
```

---

## External API Integration

### Apify Google Maps Scraper API

#### API Configuration:
```python
# From app/config.py settings
apify_api_url: str = "https://api.apify.com/v2/acts/ACTOR_ID/runs/last/dataset/items"
apify_api_token: str = "YOUR_API_TOKEN"
apify_timeout: int = 300  # 5 minutes
```

#### Request Format:
```json
{
    "startUrls": [
        {
            "url": "https://www.google.com/maps/place/AHASS+Honda+XYZ/@-6.123,106.456,17z/..."
        }
    ],
    "maxReviews": 10,
    "language": "id",
    "includeReviewerName": true,
    "includeReviewId": true,
    "includeOwnerResponse": true,
    "includeReviewerProfile": true
}
```

#### Response Format (Business Data):
```json
[
    {
        "placeId": "ChIJXXXXXXXXXXXXXXXXXXXX",
        "title": "AHASS Honda Dealer XYZ",
        "subTitle": "Motorcycle repair shop",
        "description": "Official Honda service center...",
        "categoryName": "Motorcycle repair shop",
        "address": "Jl. Raya Utama No. 123, Jakarta",
        "city": "Jakarta",
        "state": "DKI Jakarta",
        "countryCode": "ID",
        "postalCode": "12345",
        "location": {
            "lat": -6.123456,
            "lng": 106.789012
        },
        "website": "https://dealer.example.com",
        "phone": "+62 21 1234567",
        "phoneUnformatted": "+622112345678",
        "totalScore": 4.5,
        "reviewsCount": 150,
        "imagesCount": 45,
        "categories": ["Motorcycle repair shop", "Honda dealer"],
        "openingHours": [
            {"day": "Monday", "hours": "08:00-17:00"},
            {"day": "Tuesday", "hours": "08:00-17:00"}
        ],
        "reviewsDistribution": {
            "oneStar": 5,
            "twoStars": 8,
            "threeStars": 12,
            "fourStars": 35,
            "fiveStars": 90
        },
        "scrapedAt": "2025-10-02T10:30:00Z",
        "reviews": [
            {
                "reviewId": "ChgKD...",
                "reviewerId": "123456789",
                "name": "John Doe",
                "reviewerNumberOfReviews": 25,
                "isLocalGuide": true,
                "text": "Pelayanan sangat baik dan cepat!",
                "textTranslated": "Very good and fast service!",
                "stars": 5,
                "likesCount": 3,
                "publishAt": "3 months ago",
                "publishedAtDate": "2025-07-01T00:00:00Z",
                "reviewUrl": "https://www.google.com/maps/reviews/...",
                "responseFromOwnerText": "Terima kasih atas review-nya!",
                "responseFromOwnerDate": "2025-07-02T00:00:00Z",
                "reviewImageUrls": [],
                "visitedIn": "July 2025"
            }
        ]
    }
]
```

---

## Database Storage

### Database Schema (PostgreSQL - customer schema)

#### 1. google_reviews Table

**Purpose**: Stores business-level information from Google Maps

```sql
CREATE TABLE customer.google_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    scraping_status VARCHAR(50) DEFAULT 'success',
    scraping_error_message TEXT,
    api_response_id VARCHAR(100),

    -- Business information
    title VARCHAR(500),
    subtitle VARCHAR(500),
    description TEXT,
    category_name VARCHAR(255),

    -- Location
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(100),
    country_code VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,

    -- Contact
    website VARCHAR(500),
    phone VARCHAR(50),

    -- Metrics
    total_score FLOAT,
    reviews_count INTEGER,
    images_count INTEGER,

    -- Google IDs
    place_id VARCHAR(255) UNIQUE,
    google_cid VARCHAR(50),
    google_fid VARCHAR(100),

    -- JSON fields
    location_data JSON,
    reviews_distribution JSON,
    categories JSON,
    opening_hours JSON,
    popular_times_histogram JSON,
    additional_info JSON,
    reviews_tags JSON,
    owner_updates JSON,
    raw_api_response JSON,

    -- Timestamps
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_google_reviews_dealer_id ON customer.google_reviews(dealer_id);
CREATE INDEX idx_google_reviews_place_id ON customer.google_reviews(place_id);
```

#### 2. google_review_details Table

**Purpose**: Stores individual review records

```sql
CREATE TABLE customer.google_review_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    google_review_id UUID NOT NULL,
    dealer_id VARCHAR(10) NOT NULL,

    -- Review identification
    review_id VARCHAR(255) UNIQUE,
    reviewer_id VARCHAR(100),
    reviewer_url VARCHAR(500),

    -- Reviewer info
    reviewer_name VARCHAR(255),
    reviewer_number_of_reviews INTEGER,
    is_local_guide BOOLEAN DEFAULT FALSE,
    reviewer_photo_url VARCHAR(500),

    -- Review content
    review_text TEXT,
    review_text_translated TEXT,
    stars INTEGER,
    likes_count INTEGER,

    -- Review metadata
    published_at VARCHAR(100),
    published_at_date TIMESTAMP,
    review_url VARCHAR(1000),
    original_language VARCHAR(10),

    -- Owner response
    response_from_owner_date TIMESTAMP,
    response_from_owner_text TEXT,

    -- Additional data
    review_image_urls JSON,
    visited_in VARCHAR(50),

    -- Sentiment analysis
    sentiment VARCHAR(20),
    sentiment_score NUMERIC(4, 2),
    sentiment_reasons TEXT,
    sentiment_suggestion TEXT,
    sentiment_themes TEXT,
    sentiment_analyzed_at TIMESTAMP,
    sentiment_batch_id UUID,

    -- Raw data
    raw_review_data JSON,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_google_review_details_google_review_id
    ON customer.google_review_details(google_review_id);
CREATE INDEX idx_google_review_details_dealer_id
    ON customer.google_review_details(dealer_id);
CREATE INDEX idx_google_review_details_review_id
    ON customer.google_review_details(review_id);
CREATE INDEX idx_google_review_details_sentiment_batch_id
    ON customer.google_review_details(sentiment_batch_id);
```

#### 3. google_review_scrape_tracker Table

**Purpose**: Audit trail for all scraping operations

```sql
CREATE TABLE customer.google_review_scrape_tracker (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    dealer_name VARCHAR(500),

    -- Scraping configuration
    scrape_type VARCHAR(20) CHECK (scrape_type IN ('MANUAL', 'SCHEDULED')),
    max_reviews_requested INTEGER,
    language VARCHAR(10),

    -- Scraping status
    scrape_status VARCHAR(20) CHECK (scrape_status IN ('PROCESSING', 'COMPLETED', 'FAILED', 'PARTIAL')),
    scrape_date TIMESTAMP DEFAULT NOW(),
    completed_date TIMESTAMP,
    scrape_duration_seconds INTEGER,

    -- Scraping results
    api_response_id VARCHAR(100),
    google_business_id VARCHAR(255),
    business_name VARCHAR(500),
    business_rating VARCHAR(10),
    total_reviews_available INTEGER,
    scraped_reviews INTEGER,
    new_reviews INTEGER,
    duplicate_reviews INTEGER,
    failed_reviews INTEGER,
    success_rate NUMERIC(5, 2) GENERATED ALWAYS AS (
        CASE WHEN scraped_reviews > 0
        THEN (scraped_reviews::NUMERIC / NULLIF(max_reviews_requested, 0) * 100)
        ELSE 0 END
    ) STORED,

    -- Sentiment analysis tracking
    analyze_sentiment_enabled BOOLEAN DEFAULT FALSE,
    sentiment_analysis_status VARCHAR(20),
    sentiment_analyzed_count INTEGER,
    sentiment_failed_count INTEGER,
    sentiment_completion_rate NUMERIC(5, 2) GENERATED ALWAYS AS (
        CASE WHEN scraped_reviews > 0
        THEN (sentiment_analyzed_count::NUMERIC / NULLIF(scraped_reviews, 0) * 100)
        ELSE 0 END
    ) STORED,
    sentiment_duration_seconds INTEGER,

    -- Error tracking
    error_message TEXT,
    warning_message TEXT,

    -- Audit
    scraped_by VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_google_review_scrape_tracker_dealer_id
    ON customer.google_review_scrape_tracker(dealer_id);
CREATE INDEX idx_google_review_scrape_tracker_scrape_date
    ON customer.google_review_scrape_tracker(scrape_date DESC);
```

---

## Background Processing

### Optional Sentiment Analysis

#### Thread Pool Execution:

```python
# In CustomerGoogleReviewController.__init__
self.thread_pool = ThreadPoolExecutor(
    max_workers=2,
    thread_name_prefix="sentiment_analysis"
)

# Trigger background sentiment analysis
if request.auto_analyze_sentiment and new_reviews_count > 0:
    tracker.sentiment_analysis_status = 'PROCESSING'
    self.db.commit()

    # Start background thread
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        self.thread_pool,
        self._run_sentiment_analysis_background,
        request.dealer_id,
        new_reviews_count,
        str(tracker.id)
    )
```

#### Background Worker Method:

```python
def _run_sentiment_analysis_background(
    self,
    dealer_id: str,
    limit: int,
    tracker_id: str
) -> None:
    """
    Run sentiment analysis in background thread
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        sentiment_start_time = datetime.now()

        # Create new database session for background thread
        from app.dependencies import db_manager
        background_db = next(db_manager.get_session())

        try:
            # Get tracker record
            tracker = background_db.query(GoogleReviewScrapeTracker).filter(
                GoogleReviewScrapeTracker.id == tracker_id
            ).first()

            if not tracker:
                logger.error(f"Tracker {tracker_id} not found")
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

                # Run sentiment analysis
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
                        logger.info(f"Background sentiment analysis completed: {tracker.sentiment_analyzed_count} analyzed")
                    else:
                        tracker.sentiment_analysis_status = 'FAILED'
                        tracker.warning_message = f"Sentiment analysis failed: {sentiment_result.message}"

                    tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())
                    background_db.commit()

                finally:
                    loop.close()

            except Exception as sentiment_error:
                logger.error(f"Error during background sentiment analysis: {str(sentiment_error)}")
                background_db.rollback()

                # Re-fetch tracker and update with error
                tracker = background_db.query(GoogleReviewScrapeTracker).filter(
                    GoogleReviewScrapeTracker.id == tracker_id
                ).first()

                if tracker:
                    tracker.sentiment_analysis_status = 'FAILED'
                    tracker.warning_message = f"Background sentiment analysis error: {str(sentiment_error)}"
                    tracker.sentiment_duration_seconds = int((datetime.now() - sentiment_start_time).total_seconds())
                    background_db.commit()

        finally:
            background_db.close()

    except Exception as e:
        logger.error(f"Critical error in background sentiment analysis: {str(e)}", exc_info=True)
```

---

## Sequence Diagram

### Complete Scraping Flow

```mermaid
sequenceDiagram
    participant User
    participant Sidebar as GoogleReviewScrapingSidebar
    participant Service as GoogleReviewService.js
    participant API as FastAPI Route
    participant Controller as CustomerGoogleReviewController
    participant GoogleService as GoogleReviewService
    participant Apify as Apify API
    participant DB as PostgreSQL
    participant Background as Thread Pool

    User->>Sidebar: Click "Scrape Reviews"
    Sidebar->>Sidebar: Validate inputs (dealer, max_reviews)
    Sidebar->>Service: scrapeReviews({dealer_id, max_reviews, language})

    Service->>API: POST /v1/google-reviews/scrape-reviews
    API->>Controller: scrape_reviews_for_dealer(request)

    Controller->>DB: Create GoogleReviewScrapeTracker (PROCESSING)
    DB-->>Controller: tracker_id

    Controller->>DB: Query DealerConfig (validate dealer)
    DB-->>Controller: dealer record

    Controller->>Controller: Validate google_location_url exists

    Controller->>GoogleService: scrape_reviews_for_dealer(dealer_id, max_reviews, language)

    GoogleService->>GoogleService: Generate api_response_id
    GoogleService->>Apify: POST /runs?token=xxx (request_body)

    Apify-->>GoogleService: JSON response (business + reviews)

    GoogleService->>DB: Upsert GoogleReview (by place_id)
    DB-->>GoogleService: google_review record

    loop For each review in response
        GoogleService->>DB: Upsert GoogleReviewDetail (by review_id)
        DB-->>GoogleService: review_detail record
    end

    GoogleService->>DB: Commit transaction
    GoogleService-->>Controller: (success, message, google_review)

    Controller->>DB: Count scraped_reviews and new_reviews
    DB-->>Controller: counts

    Controller->>DB: Update tracker (COMPLETED, results, metrics)

    alt auto_analyze_sentiment = true AND new_reviews > 0
        Controller->>DB: Update tracker.sentiment_analysis_status = 'PROCESSING'
        Controller->>Background: run_in_executor(_run_sentiment_analysis_background)
        Background-->>Controller: (async, non-blocking)
    end

    Controller->>DB: Commit tracker updates
    Controller-->>API: ScrapeReviewsResponse
    API-->>Service: JSON response
    Service-->>Sidebar: result object

    Sidebar->>Sidebar: Show success toast
    Sidebar->>Service: refreshHistory()
    Sidebar->>User: Display scraping results

    opt Background Sentiment Analysis
        Background->>Background: Create new DB session
        Background->>DB: Get unanalyzed reviews
        DB-->>Background: review records

        loop Process in batches
            Background->>Background: Call SentimentAnalysisService
            Background->>DB: Update GoogleReviewDetail with sentiment
        end

        Background->>DB: Update tracker (sentiment_analysis_status = 'COMPLETED')
        Background->>Background: Close DB session
    end
```

---

## Data Models

### 1. GoogleReview Model

**File**: `backend-microservices/services/customer/app/models/google_review.py`

```python
class GoogleReview(Base):
    """Google Review model - stores scraped Google Maps data"""

    __tablename__ = "google_reviews"
    __table_args__ = {"schema": "customer"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), nullable=False, index=True)
    scraping_status = Column(String(50), default='success')
    api_response_id = Column(String(100), nullable=True)

    # Business information
    title = Column(String(500), nullable=True)
    category_name = Column(String(255), nullable=True)

    # Location
    address = Column(Text, nullable=True)
    city = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Contact
    website = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)

    # Metrics
    total_score = Column(Float, nullable=True)
    reviews_count = Column(Integer, nullable=True)

    # Google identifiers
    place_id = Column(String(255), nullable=True, unique=True)

    # JSON fields
    opening_hours = Column(JSON, nullable=True)
    reviews_distribution = Column(JSON, nullable=True)
    categories = Column(JSON, nullable=True)
    raw_api_response = Column(JSON, nullable=True)

    # Timestamps
    scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. GoogleReviewDetail Model

```python
class GoogleReviewDetail(Base):
    """Individual review details from Google Maps"""

    __tablename__ = "google_review_details"
    __table_args__ = {"schema": "customer"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_review_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    dealer_id = Column(String(10), nullable=False, index=True)

    # Review identification
    review_id = Column(String(255), nullable=True, unique=True)

    # Reviewer information
    reviewer_name = Column(String(255), nullable=True)
    reviewer_number_of_reviews = Column(Integer, nullable=True)
    is_local_guide = Column(Boolean, default=False)

    # Review content
    review_text = Column(Text, nullable=True)
    stars = Column(Integer, nullable=True)

    # Review metadata
    published_at_date = Column(DateTime, nullable=True)

    # Owner response
    response_from_owner_text = Column(Text, nullable=True)
    response_from_owner_date = Column(DateTime, nullable=True)

    # Sentiment analysis fields
    sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Numeric(4, 2), nullable=True)
    sentiment_reasons = Column(Text, nullable=True)
    sentiment_suggestion = Column(Text, nullable=True)
    sentiment_themes = Column(Text, nullable=True)
    sentiment_analyzed_at = Column(DateTime, nullable=True)
    sentiment_batch_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

### 3. GoogleReviewScrapeTracker Model

```python
class GoogleReviewScrapeTracker(Base):
    """Audit trail for Google Reviews scraping operations"""

    __tablename__ = "google_review_scrape_tracker"
    __table_args__ = {"schema": "customer"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), nullable=False, index=True)
    dealer_name = Column(String(500))

    # Scraping configuration
    scrape_type = Column(String(20))  # MANUAL, SCHEDULED
    max_reviews_requested = Column(Integer)
    language = Column(String(10))

    # Scraping status
    scrape_status = Column(String(20))  # PROCESSING, COMPLETED, FAILED
    scrape_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime)
    scrape_duration_seconds = Column(Integer)

    # Scraping results
    api_response_id = Column(String(100))
    business_name = Column(String(500))
    scraped_reviews = Column(Integer)
    new_reviews = Column(Integer)
    duplicate_reviews = Column(Integer)
    success_rate = Column(Numeric(5, 2))  # Computed column

    # Sentiment analysis tracking
    analyze_sentiment_enabled = Column(Boolean, default=False)
    sentiment_analysis_status = Column(String(20))
    sentiment_analyzed_count = Column(Integer)
    sentiment_failed_count = Column(Integer)
    sentiment_completion_rate = Column(Numeric(5, 2))  # Computed column
    sentiment_duration_seconds = Column(Integer)

    # Error tracking
    error_message = Column(Text)
    warning_message = Column(Text)

    # Audit
    scraped_by = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

---

## Error Handling

### 1. Frontend Error Handling

```javascript
// In GoogleReviewScrapingSidebar.vue
const scrapeReviews = async () => {
    try {
        const result = await GoogleReviewService.scrapeReviews({...});

        if (result.success) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: result.message
            });
        } else {
            toast.add({
                severity: 'error',
                summary: 'Scraping Failed',
                detail: result.message
            });
        }
    } catch (error) {
        console.error('Scraping error:', error);
        toast.add({
            severity: 'error',
            summary: 'Scraping Error',
            detail: error.response?.data?.detail || 'An error occurred during scraping'
        });
    } finally {
        scraping.value = false;
    }
};
```

### 2. Backend Error Handling

```python
# In CustomerGoogleReviewController.scrape_reviews_for_dealer

try:
    # Scraping logic...

except HTTPException:
    # Re-raise HTTP exceptions (already handled)
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
```

### 3. Database Transaction Handling

```python
# In GoogleReviewService.scrape_reviews_for_dealer

try:
    # Process business data...
    google_review = self._create_google_review_record(...)
    self.db.add(google_review)
    self.db.flush()  # Get ID without committing

    # Process reviews...
    for review_data in business_data["reviews"]:
        review_detail = self._create_review_detail_record(...)
        self.db.add(review_detail)

    self.db.commit()  # Commit all changes together
    return True, message, google_review

except Exception as e:
    self.db.rollback()  # Rollback on any error
    return False, f"Unexpected error: {str(e)}", None
```

### 4. Common Error Scenarios

| Error Scenario | HTTP Status | Handler | Recovery |
|---------------|-------------|---------|----------|
| Dealer not found | 404 | Controller | Update tracker, return error |
| No Google URL configured | 400 | Controller | Update tracker, return error |
| Apify API timeout | 500 | Service | Create failed record, return error |
| Invalid API response | 500 | Service | Create failed record, return error |
| Database constraint violation | 500 | Service | Rollback transaction, return error |
| Background sentiment failure | N/A | Background | Update tracker, log error |

---

## Key Features

### 1. Upsert Logic (Deduplication)

**Business Records**:
- Uses `place_id` as unique identifier
- Updates existing record if `place_id` already exists
- Creates new record if `place_id` is new

**Review Records**:
- Uses `review_id` as unique identifier
- Updates existing review if `review_id` already exists
- Creates new review if `review_id` is new
- Prevents duplicate reviews across multiple scrapes

### 2. Comprehensive Audit Trail

Every scraping operation is tracked in `google_review_scrape_tracker`:
- **Configuration**: max_reviews, language, scrape_type
- **Status**: PROCESSING → COMPLETED/FAILED
- **Metrics**: scraped_reviews, new_reviews, duplicate_reviews, success_rate
- **Timing**: scrape_date, completed_date, scrape_duration_seconds
- **Errors**: error_message, warning_message
- **Sentiment**: sentiment_analysis_status, sentiment_analyzed_count, sentiment_completion_rate

### 3. Performance Tracking

- **Scrape Duration**: Measured in seconds from start to completion
- **Success Rate**: Percentage of successfully scraped reviews vs requested
- **Sentiment Completion Rate**: Percentage of reviews analyzed for sentiment
- **Deduplication Metrics**: New vs duplicate reviews tracked

### 4. Background Sentiment Analysis

- **Non-blocking**: Runs in separate thread pool
- **Independent DB Session**: Prevents blocking main scraping transaction
- **Automatic Tracking**: Updates tracker with progress and results
- **Error Resilient**: Failures don't affect main scraping operation

### 5. Flexible Configuration

- **Max Reviews**: 1-50 reviews per scrape (Apify API limit)
- **Language**: Supports multiple languages (default: Indonesian)
- **Auto Sentiment**: Optional automatic sentiment analysis
- **Scrape Type**: MANUAL or SCHEDULED (for future automation)

---

## Configuration

### Environment Variables

```bash
# Apify API Configuration
APIFY_API_URL=https://api.apify.com/v2/acts/YOUR_ACTOR_ID/runs/last/dataset/items
APIFY_API_TOKEN=your_apify_token_here
APIFY_TIMEOUT=300  # 5 minutes

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Settings File

**File**: `backend-microservices/services/customer/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Apify API settings
    apify_api_url: str
    apify_api_token: str
    apify_timeout: int = 300

    # Database settings
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Testing

### Manual Testing Steps

1. **Setup**:
   ```bash
   # Start backend services
   docker-compose up -d postgres redis
   cd backend-microservices/services/customer
   python -m uvicorn app.main:app --reload --port 8300

   # Start frontend
   cd web
   npm run dev
   ```

2. **Test Scraping**:
   - Login as SUPER_ADMIN
   - Navigate to Google Reviews page
   - Click "Manage Scraping"
   - Select dealer from dropdown
   - Set max_reviews = 10
   - Click "Scrape Reviews"
   - Verify success toast
   - Check scraping history

3. **Verify Database**:
   ```sql
   -- Check scrape tracker
   SELECT * FROM customer.google_review_scrape_tracker
   ORDER BY scrape_date DESC LIMIT 5;

   -- Check business record
   SELECT * FROM customer.google_reviews
   WHERE dealer_id = '12284'
   ORDER BY created_at DESC LIMIT 1;

   -- Check individual reviews
   SELECT * FROM customer.google_review_details
   WHERE dealer_id = '12284'
   ORDER BY created_at DESC LIMIT 10;
   ```

### API Testing with cURL

```bash
# Scrape reviews for dealer
curl -X POST "http://localhost:8300/v1/google-reviews/scrape-reviews" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "dealer_id": "12284",
    "max_reviews": 10,
    "language": "id",
    "auto_analyze_sentiment": false
  }'

# Get latest scrape info
curl -X GET "http://localhost:8300/v1/google-reviews/dealers/12284/latest-scrape-info" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get scrape history
curl -X GET "http://localhost:8300/v1/google-reviews/scrape-history?dealer_id=12284&page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Performance Considerations

### 1. API Rate Limiting
- Apify API has rate limits based on subscription tier
- Recommended: Max 50 reviews per scrape
- Add delays between multiple consecutive scrapes

### 2. Database Optimization
- Indexes on `dealer_id`, `place_id`, `review_id`
- Batch inserts for review details
- Connection pooling for background threads

### 3. Background Processing
- Thread pool size: 2 workers (configurable)
- Separate DB sessions for each background task
- Async event loop for sentiment analysis

### 4. Frontend Optimization
- Lazy loading of scraping history
- Debounced search inputs
- Optimistic UI updates

---

## Future Enhancements

1. **Scheduled Scraping**: Automatic periodic scraping via cron jobs
2. **Webhook Support**: Real-time notifications on scrape completion
3. **Bulk Operations**: Scrape multiple dealers in one request
4. **Advanced Filtering**: Filter reviews by sentiment, rating range, date
5. **Export Functionality**: CSV/Excel export of reviews and statistics
6. **Review Response Management**: Interface for responding to reviews
7. **Analytics Dashboard**: Trends, charts, and insights from reviews
8. **Multi-language Support**: Automatic translation of reviews

---

## Troubleshooting

### Common Issues

**Issue**: Scraping fails with "Google location URL not configured"
- **Solution**: Ensure dealer has `google_location_url` set in `dealer_config` table

**Issue**: Apify API timeout
- **Solution**: Increase `APIFY_TIMEOUT` setting or reduce `max_reviews`

**Issue**: Duplicate reviews still appearing
- **Solution**: Check if `review_id` is being returned by Apify API

**Issue**: Sentiment analysis not starting
- **Solution**: Verify `auto_analyze_sentiment=true` and new reviews exist

**Issue**: Background thread not updating tracker
- **Solution**: Check application logs for thread pool errors

---

## References

- **Apify Documentation**: https://docs.apify.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Vue.js 3 Documentation**: https://vuejs.org/
- **PrimeVue Documentation**: https://primevue.org/

---

## Changelog

### Version 1.0.0 (2025-10-02)
- Initial implementation of Google Reviews scraping
- Apify API integration
- Upsert logic for deduplication
- Background sentiment analysis
- Comprehensive audit trail
- Frontend UI components

---

## License

Internal use only - AHM Dealer Management System

---

**Document Version**: 1.0
**Last Updated**: October 2, 2025
**Author**: Development Team
**Status**: Production
