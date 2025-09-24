-- Migration: Create Google Reviews tables for storing scraped Google Maps data
-- Version: 018
-- Date: 2025-01-20
-- Description: Creates google_reviews and google_review_details tables to store Google Maps scraping data

-- Create google_reviews table (main business information)
CREATE TABLE IF NOT EXISTS customer.google_reviews (
    -- Primary key and audit fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dealer_id VARCHAR(10) NOT NULL,
    scraping_status VARCHAR(50) DEFAULT 'success',
    scraping_error_message TEXT,
    api_response_id VARCHAR(100),

    -- Business information
    title VARCHAR(500),
    subtitle VARCHAR(500),
    description TEXT,
    category_name VARCHAR(255),

    -- Location information
    address TEXT,
    neighborhood VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(255),
    postal_code VARCHAR(20),
    state VARCHAR(100),
    country_code VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    plus_code VARCHAR(100),

    -- Contact information
    website VARCHAR(500),
    phone VARCHAR(50),
    phone_unformatted VARCHAR(50),

    -- Business metrics
    total_score DECIMAL(2, 1),
    reviews_count INTEGER,
    images_count INTEGER,

    -- Business status
    permanently_closed BOOLEAN DEFAULT FALSE,
    temporarily_closed BOOLEAN DEFAULT FALSE,
    claim_this_business BOOLEAN DEFAULT FALSE,

    -- Google-specific identifiers
    place_id VARCHAR(255) UNIQUE,
    google_cid VARCHAR(50),
    google_fid VARCHAR(100),

    -- JSON fields for complex data
    location_data JSONB,
    reviews_distribution JSONB,
    categories JSONB,
    opening_hours JSONB,
    additional_opening_hours JSONB,
    popular_times_histogram JSONB,
    popular_times_live JSONB,
    additional_info JSONB,
    reviews_tags JSONB,
    people_also_search JSONB,
    owner_updates JSONB,
    booking_links JSONB,
    image_categories JSONB,
    raw_api_response JSONB,

    -- Timestamps
    scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create google_review_details table (individual reviews)
CREATE TABLE IF NOT EXISTS customer.google_review_details (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key relationships
    google_review_id UUID NOT NULL,
    dealer_id VARCHAR(10) NOT NULL,

    -- Review identification
    review_id VARCHAR(255) UNIQUE,
    reviewer_id VARCHAR(100),
    reviewer_url VARCHAR(500),

    -- Reviewer information
    reviewer_name VARCHAR(255),
    reviewer_number_of_reviews INTEGER,
    is_local_guide BOOLEAN DEFAULT FALSE,
    reviewer_photo_url VARCHAR(500),

    -- Review content
    review_text TEXT,
    review_text_translated TEXT,
    stars INTEGER CHECK (stars >= 1 AND stars <= 5),
    likes_count INTEGER DEFAULT 0,

    -- Review metadata
    published_at VARCHAR(100),
    published_at_date TIMESTAMP WITH TIME ZONE,
    review_url VARCHAR(1000),
    review_origin VARCHAR(50),
    original_language VARCHAR(10),
    translated_language VARCHAR(10),

    -- Owner response
    response_from_owner_date TIMESTAMP WITH TIME ZONE,
    response_from_owner_text TEXT,

    -- Additional data
    review_image_urls JSONB,
    review_context JSONB,
    review_detailed_rating JSONB,
    visited_in VARCHAR(50),
    raw_review_data JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_google_reviews_dealer_id ON customer.google_reviews(dealer_id);
CREATE INDEX IF NOT EXISTS idx_google_reviews_place_id ON customer.google_reviews(place_id);
CREATE INDEX IF NOT EXISTS idx_google_reviews_scraping_status ON customer.google_reviews(scraping_status);
CREATE INDEX IF NOT EXISTS idx_google_reviews_created_at ON customer.google_reviews(created_at);
CREATE INDEX IF NOT EXISTS idx_google_reviews_scraped_at ON customer.google_reviews(scraped_at);

CREATE INDEX IF NOT EXISTS idx_google_review_details_google_review_id ON customer.google_review_details(google_review_id);
CREATE INDEX IF NOT EXISTS idx_google_review_details_dealer_id ON customer.google_review_details(dealer_id);
CREATE INDEX IF NOT EXISTS idx_google_review_details_review_id ON customer.google_review_details(review_id);
CREATE INDEX IF NOT EXISTS idx_google_review_details_reviewer_id ON customer.google_review_details(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_google_review_details_stars ON customer.google_review_details(stars);
CREATE INDEX IF NOT EXISTS idx_google_review_details_published_at_date ON customer.google_review_details(published_at_date);

-- Add foreign key constraint
ALTER TABLE customer.google_review_details
ADD CONSTRAINT fk_google_review_details_google_review_id
FOREIGN KEY (google_review_id) REFERENCES customer.google_reviews(id) ON DELETE CASCADE;

-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_google_reviews_updated_at
    BEFORE UPDATE ON customer.google_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_google_review_details_updated_at
    BEFORE UPDATE ON customer.google_review_details
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments to document tables
COMMENT ON TABLE customer.google_reviews IS 'Stores Google Maps business information scraped from Apify API';
COMMENT ON TABLE customer.google_review_details IS 'Stores individual Google Maps reviews for businesses';

COMMENT ON COLUMN customer.google_reviews.dealer_id IS 'Reference to dealer who owns this Google Maps location';
COMMENT ON COLUMN customer.google_reviews.place_id IS 'Google Maps unique place identifier';
COMMENT ON COLUMN customer.google_reviews.scraping_status IS 'Status of the scraping operation (success, failed, partial)';
COMMENT ON COLUMN customer.google_reviews.api_response_id IS 'Unique identifier for the API scraping session';
COMMENT ON COLUMN customer.google_reviews.raw_api_response IS 'Complete API response for debugging and data recovery';

COMMENT ON COLUMN customer.google_review_details.google_review_id IS 'Foreign key to parent google_reviews record';
COMMENT ON COLUMN customer.google_review_details.review_id IS 'Google unique review identifier';
COMMENT ON COLUMN customer.google_review_details.stars IS 'Review rating from 1-5 stars';

-- Verify the tables were created successfully
DO $$
DECLARE
    google_reviews_count INTEGER;
    google_review_details_count INTEGER;
    index_count INTEGER;
BEGIN
    -- Check if tables exist
    SELECT COUNT(*) INTO google_reviews_count
    FROM information_schema.tables
    WHERE table_schema = 'customer' AND table_name = 'google_reviews';

    SELECT COUNT(*) INTO google_review_details_count
    FROM information_schema.tables
    WHERE table_schema = 'customer' AND table_name = 'google_review_details';

    -- Check if indexes were created
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'customer'
    AND tablename IN ('google_reviews', 'google_review_details');

    RAISE NOTICE 'Migration 018 completed successfully:';

    IF google_reviews_count > 0 THEN
        RAISE NOTICE '- google_reviews table created';
    ELSE
        RAISE WARNING '- google_reviews table was not created';
    END IF;

    IF google_review_details_count > 0 THEN
        RAISE NOTICE '- google_review_details table created';
    ELSE
        RAISE WARNING '- google_review_details table was not created';
    END IF;

    RAISE NOTICE '- Created % indexes for performance optimization', index_count;
    RAISE NOTICE '- Added foreign key constraints and triggers';
    RAISE NOTICE '- Tables ready to store Google Maps scraping data';
END $$;