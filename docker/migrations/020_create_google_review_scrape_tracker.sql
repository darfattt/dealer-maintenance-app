-- Migration: Create Google Review Scrape Tracker table
-- Version: 020
-- Date: 2025-01-20
-- Description: Creates customer_google_review_scrape_tracker table for tracking Google Reviews scraping operations

-- Create Google Review Scrape Tracker table
CREATE TABLE IF NOT EXISTS customer.customer_google_review_scrape_tracker (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Dealer information
    dealer_id VARCHAR(10) NOT NULL,
    dealer_name VARCHAR(255),

    -- Scraping configuration
    scrape_type VARCHAR(20) NOT NULL DEFAULT 'MANUAL',
    max_reviews_requested INTEGER NOT NULL DEFAULT 10,
    language VARCHAR(5) NOT NULL DEFAULT 'id',

    -- Scraping results
    scrape_status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING',
    total_reviews_available INTEGER,
    scraped_reviews INTEGER NOT NULL DEFAULT 0,
    failed_reviews INTEGER NOT NULL DEFAULT 0,
    new_reviews INTEGER NOT NULL DEFAULT 0,
    duplicate_reviews INTEGER NOT NULL DEFAULT 0,

    -- Sentiment analysis tracking
    analyze_sentiment_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    sentiment_analysis_status VARCHAR(20),
    sentiment_analyzed_count INTEGER NOT NULL DEFAULT 0,
    sentiment_failed_count INTEGER NOT NULL DEFAULT 0,
    sentiment_batch_id UUID,

    -- API response tracking
    api_response_id VARCHAR(100),
    google_business_id VARCHAR(100),
    business_name VARCHAR(255),
    business_rating VARCHAR(10),

    -- Error handling
    error_message TEXT,
    warning_message TEXT,

    -- Processing times
    scrape_duration_seconds INTEGER,
    sentiment_duration_seconds INTEGER,

    -- Audit fields
    scraped_by VARCHAR(100),
    scrape_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_date TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_scrape_type CHECK (scrape_type IN ('MANUAL', 'SCHEDULED')),
    CONSTRAINT chk_scrape_status CHECK (scrape_status IN ('PROCESSING', 'COMPLETED', 'FAILED', 'PARTIAL')),
    CONSTRAINT chk_sentiment_status CHECK (sentiment_analysis_status IS NULL OR sentiment_analysis_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    CONSTRAINT chk_max_reviews CHECK (max_reviews_requested >= 1 AND max_reviews_requested <= 50),
    CONSTRAINT chk_review_counts CHECK (
        scraped_reviews >= 0 AND
        failed_reviews >= 0 AND
        new_reviews >= 0 AND
        duplicate_reviews >= 0 AND
        new_reviews + duplicate_reviews <= scraped_reviews
    ),
    CONSTRAINT chk_sentiment_counts CHECK (
        sentiment_analyzed_count >= 0 AND
        sentiment_failed_count >= 0 AND
        sentiment_analyzed_count + sentiment_failed_count <= scraped_reviews
    )
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_google_review_scrape_tracker_dealer_id
ON customer.customer_google_review_scrape_tracker(dealer_id);

CREATE INDEX IF NOT EXISTS idx_google_review_scrape_tracker_status
ON customer.customer_google_review_scrape_tracker(scrape_status);

CREATE INDEX IF NOT EXISTS idx_google_review_scrape_tracker_date
ON customer.customer_google_review_scrape_tracker(scrape_date DESC);

CREATE INDEX IF NOT EXISTS idx_google_review_scrape_tracker_sentiment_batch
ON customer.customer_google_review_scrape_tracker(sentiment_batch_id)
WHERE sentiment_batch_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_google_review_scrape_tracker_processing
ON customer.customer_google_review_scrape_tracker(scrape_status, scrape_date)
WHERE scrape_status IN ('PROCESSING', 'PENDING');

-- Create composite index for dealer history queries
CREATE INDEX IF NOT EXISTS idx_google_review_scrape_tracker_dealer_history
ON customer.customer_google_review_scrape_tracker(dealer_id, scrape_date DESC, scrape_status);

-- Add comments to document the table and columns
COMMENT ON TABLE customer.customer_google_review_scrape_tracker IS 'Tracks Google Reviews scraping operations with sentiment analysis integration';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.dealer_id IS 'Dealer ID that reviews were scraped for';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.scrape_type IS 'Type of scraping: MANUAL (user-initiated) or SCHEDULED (automated)';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.max_reviews_requested IS 'Maximum number of reviews requested from API (1-50)';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.language IS 'Language code for review scraping (e.g., id, en)';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.scrape_status IS 'Overall scraping status: PROCESSING, COMPLETED, FAILED, PARTIAL';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.total_reviews_available IS 'Total reviews available on Google Business Profile';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.scraped_reviews IS 'Number of reviews successfully scraped';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.failed_reviews IS 'Number of reviews that failed to scrape';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.new_reviews IS 'Number of new reviews added to database';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.duplicate_reviews IS 'Number of reviews that already existed';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.analyze_sentiment_enabled IS 'Whether sentiment analysis was enabled for this scrape';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.sentiment_analysis_status IS 'Status of sentiment analysis: PENDING, PROCESSING, COMPLETED, FAILED';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.sentiment_analyzed_count IS 'Number of reviews successfully analyzed for sentiment';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.sentiment_failed_count IS 'Number of reviews that failed sentiment analysis';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.sentiment_batch_id IS 'UUID linking to sentiment analysis batch';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.api_response_id IS 'Apify API response ID for tracking';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.google_business_id IS 'Google Business Profile ID';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.business_name IS 'Business name from Google';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.business_rating IS 'Business rating from Google';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.error_message IS 'Error message if scraping failed';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.warning_message IS 'Warning messages during scraping';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.scrape_duration_seconds IS 'Time taken for scraping operation in seconds';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.sentiment_duration_seconds IS 'Time taken for sentiment analysis in seconds';

COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.scraped_by IS 'User who initiated the scraping';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.scrape_date IS 'When scraping was started';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.completed_date IS 'When scraping was completed';
COMMENT ON COLUMN customer.customer_google_review_scrape_tracker.last_updated IS 'Last update timestamp';

-- Create trigger to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_google_review_scrape_tracker_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_google_review_scrape_tracker_timestamp
    BEFORE UPDATE ON customer.customer_google_review_scrape_tracker
    FOR EACH ROW
    EXECUTE FUNCTION update_google_review_scrape_tracker_timestamp();

-- Verify the table creation
DO $$
DECLARE
    table_exists BOOLEAN;
    index_count INTEGER;
    constraint_count INTEGER;
BEGIN
    -- Check if table exists
    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'customer'
        AND table_name = 'customer_google_review_scrape_tracker'
    ) INTO table_exists;

    -- Count indexes
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'customer'
    AND tablename = 'customer_google_review_scrape_tracker';

    -- Count constraints
    SELECT COUNT(*) INTO constraint_count
    FROM information_schema.table_constraints
    WHERE table_schema = 'customer'
    AND table_name = 'customer_google_review_scrape_tracker'
    AND constraint_type = 'CHECK';

    RAISE NOTICE 'Migration 020 completed successfully:';
    RAISE NOTICE '- Table exists: %', table_exists;
    RAISE NOTICE '- Created % indexes for performance optimization', index_count;
    RAISE NOTICE '- Added % check constraints for data integrity', constraint_count;
    RAISE NOTICE '- Google Review scrape tracking system ready';

    IF table_exists THEN
        RAISE NOTICE '- ✅ customer_google_review_scrape_tracker table created successfully';
    ELSE
        RAISE WARNING '- ❌ Failed to create customer_google_review_scrape_tracker table';
    END IF;
END $$;