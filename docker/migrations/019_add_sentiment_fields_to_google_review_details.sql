-- Migration: Add sentiment analysis fields to google_review_details table
-- Version: 019
-- Date: 2025-01-20
-- Description: Adds sentiment analysis fields to google_review_details table for Google Reviews sentiment analysis

-- Add sentiment analysis fields to google_review_details table
DO $$
BEGIN
    -- Add sentiment field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment VARCHAR(20);
        RAISE NOTICE 'Added sentiment column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment column already exists in google_review_details table';
    END IF;

    -- Add sentiment_score field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment_score'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment_score DECIMAL(4,2);
        RAISE NOTICE 'Added sentiment_score column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment_score column already exists in google_review_details table';
    END IF;

    -- Add sentiment_reasons field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment_reasons'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment_reasons TEXT;
        RAISE NOTICE 'Added sentiment_reasons column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment_reasons column already exists in google_review_details table';
    END IF;

    -- Add sentiment_suggestion field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment_suggestion'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment_suggestion TEXT;
        RAISE NOTICE 'Added sentiment_suggestion column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment_suggestion column already exists in google_review_details table';
    END IF;

    -- Add sentiment_themes field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment_themes'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment_themes TEXT;
        RAISE NOTICE 'Added sentiment_themes column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment_themes column already exists in google_review_details table';
    END IF;

    -- Add sentiment_analyzed_at field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment_analyzed_at'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment_analyzed_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Added sentiment_analyzed_at column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment_analyzed_at column already exists in google_review_details table';
    END IF;

    -- Add sentiment_batch_id field
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'customer'
        AND table_name = 'google_review_details'
        AND column_name = 'sentiment_batch_id'
    ) THEN
        ALTER TABLE customer.google_review_details
        ADD COLUMN sentiment_batch_id UUID;
        RAISE NOTICE 'Added sentiment_batch_id column to google_review_details table';
    ELSE
        RAISE NOTICE 'sentiment_batch_id column already exists in google_review_details table';
    END IF;
END $$;

-- Create indexes for sentiment analysis fields
CREATE INDEX IF NOT EXISTS idx_google_review_details_sentiment
ON customer.google_review_details(sentiment);

CREATE INDEX IF NOT EXISTS idx_google_review_details_sentiment_score
ON customer.google_review_details(sentiment_score);

CREATE INDEX IF NOT EXISTS idx_google_review_details_sentiment_analyzed_at
ON customer.google_review_details(sentiment_analyzed_at);

CREATE INDEX IF NOT EXISTS idx_google_review_details_sentiment_batch_id
ON customer.google_review_details(sentiment_batch_id);

-- Add constraints for sentiment analysis fields
ALTER TABLE customer.google_review_details
ADD CONSTRAINT chk_google_review_details_sentiment
CHECK (sentiment IS NULL OR sentiment IN ('Positive', 'Negative', 'Neutral'));

ALTER TABLE customer.google_review_details
ADD CONSTRAINT chk_google_review_details_sentiment_score
CHECK (sentiment_score IS NULL OR (sentiment_score >= -5.00 AND sentiment_score <= 5.00));

-- Add comments to document the sentiment analysis fields
COMMENT ON COLUMN customer.google_review_details.sentiment IS 'Sentiment classification: Positive, Negative, or Neutral';
COMMENT ON COLUMN customer.google_review_details.sentiment_score IS 'Sentiment score from -5.00 (very negative) to 5.00 (very positive)';
COMMENT ON COLUMN customer.google_review_details.sentiment_reasons IS 'AI-generated reasons for the sentiment classification';
COMMENT ON COLUMN customer.google_review_details.sentiment_suggestion IS 'AI-generated suggestions for addressing the review';
COMMENT ON COLUMN customer.google_review_details.sentiment_themes IS 'JSON array of themes identified in the review text';
COMMENT ON COLUMN customer.google_review_details.sentiment_analyzed_at IS 'Timestamp when sentiment analysis was performed';
COMMENT ON COLUMN customer.google_review_details.sentiment_batch_id IS 'UUID of the sentiment analysis batch for tracking';

-- Verify the changes
DO $$
DECLARE
    sentiment_field_count INTEGER;
    index_count INTEGER;
    constraint_count INTEGER;
BEGIN
    -- Count sentiment analysis fields
    SELECT COUNT(*) INTO sentiment_field_count
    FROM information_schema.columns
    WHERE table_schema = 'customer'
    AND table_name = 'google_review_details'
    AND column_name IN (
        'sentiment', 'sentiment_score', 'sentiment_reasons',
        'sentiment_suggestion', 'sentiment_themes',
        'sentiment_analyzed_at', 'sentiment_batch_id'
    );

    -- Count sentiment-related indexes
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'customer'
    AND tablename = 'google_review_details'
    AND indexname LIKE '%sentiment%';

    -- Count sentiment-related constraints
    SELECT COUNT(*) INTO constraint_count
    FROM information_schema.table_constraints
    WHERE table_schema = 'customer'
    AND table_name = 'google_review_details'
    AND constraint_name LIKE '%sentiment%';

    RAISE NOTICE 'Migration 019 completed successfully:';
    RAISE NOTICE '- Added % sentiment analysis fields to google_review_details table', sentiment_field_count;
    RAISE NOTICE '- Created % sentiment-related indexes', index_count;
    RAISE NOTICE '- Added % sentiment-related constraints', constraint_count;
    RAISE NOTICE '- Sentiment analysis ready for Google Reviews';

    IF sentiment_field_count = 7 THEN
        RAISE NOTICE '- All 7 sentiment fields successfully added';
    ELSE
        RAISE WARNING '- Expected 7 sentiment fields, found %', sentiment_field_count;
    END IF;
END $$;