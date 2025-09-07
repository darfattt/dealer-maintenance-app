-- Migration 016: Add sentiment analysis fields to customer satisfaction
-- Date: 2025-08-31
-- Description: Add sentiment analysis fields to customer_satisfaction_raw table
-- This migration adds support for AI-powered sentiment analysis of customer reviews

-- Step 1: Add sentiment analysis columns to customer_satisfaction_raw table
DO $$ 
BEGIN 
    -- Check if the customer_satisfaction_raw table exists
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_raw'
    ) THEN
        -- Add sentiment analysis fields if they don't exist
        
        -- Add sentiment field (Positive/Negative/Neutral)
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment VARCHAR(20);
            RAISE NOTICE 'Added sentiment column';
        END IF;
        
        -- Add sentiment_score field (-5.00 to 5.00)
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment_score'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment_score DECIMAL(4,2);
            RAISE NOTICE 'Added sentiment_score column';
        END IF;
        
        -- Add sentiment_reasons field
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment_reasons'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment_reasons TEXT;
            RAISE NOTICE 'Added sentiment_reasons column';
        END IF;
        
        -- Add sentiment_suggestion field
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment_suggestion'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment_suggestion TEXT;
            RAISE NOTICE 'Added sentiment_suggestion column';
        END IF;
        
        -- Add sentiment_themes field (JSON array as string)
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment_themes'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment_themes TEXT;
            RAISE NOTICE 'Added sentiment_themes column';
        END IF;
        
        -- Add sentiment_analyzed_at timestamp
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment_analyzed_at'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment_analyzed_at TIMESTAMP;
            RAISE NOTICE 'Added sentiment_analyzed_at column';
        END IF;
        
        -- Add sentiment_batch_id for tracking bulk analysis
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'customer' 
            AND table_name = 'customer_satisfaction_raw' 
            AND column_name = 'sentiment_batch_id'
        ) THEN
            ALTER TABLE customer.customer_satisfaction_raw 
            ADD COLUMN sentiment_batch_id UUID;
            RAISE NOTICE 'Added sentiment_batch_id column';
        END IF;
        
        RAISE NOTICE 'Sentiment analysis columns added to customer_satisfaction_raw table';
    ELSE
        RAISE EXCEPTION 'customer_satisfaction_raw table does not exist';
    END IF;
END $$;

-- Step 2: Add constraints and checks for sentiment fields
DO $$
BEGIN
    -- Add constraint for sentiment values
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND constraint_name = 'chk_sentiment_values'
    ) THEN
        ALTER TABLE customer.customer_satisfaction_raw
        ADD CONSTRAINT chk_sentiment_values 
        CHECK (sentiment IS NULL OR sentiment IN ('Positive', 'Negative', 'Neutral'));
        RAISE NOTICE 'Added sentiment values constraint';
    END IF;
    
    -- Add constraint for sentiment_score range
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND constraint_name = 'chk_sentiment_score_range'
    ) THEN
        ALTER TABLE customer.customer_satisfaction_raw
        ADD CONSTRAINT chk_sentiment_score_range 
        CHECK (sentiment_score IS NULL OR (sentiment_score >= -5.00 AND sentiment_score <= 5.00));
        RAISE NOTICE 'Added sentiment score range constraint';
    END IF;
END $$;

-- Step 3: Create indexes for sentiment analysis fields
DO $$
BEGIN
    -- Index for sentiment filtering
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'customer' 
        AND tablename = 'customer_satisfaction_raw' 
        AND indexname = 'idx_customer_satisfaction_raw_sentiment'
    ) THEN
        CREATE INDEX idx_customer_satisfaction_raw_sentiment 
        ON customer.customer_satisfaction_raw(sentiment);
        RAISE NOTICE 'Created sentiment index';
    END IF;
    
    -- Index for sentiment_analyzed_at for tracking analysis progress
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'customer' 
        AND tablename = 'customer_satisfaction_raw' 
        AND indexname = 'idx_customer_satisfaction_raw_sentiment_analyzed'
    ) THEN
        CREATE INDEX idx_customer_satisfaction_raw_sentiment_analyzed 
        ON customer.customer_satisfaction_raw(sentiment_analyzed_at);
        RAISE NOTICE 'Created sentiment analyzed timestamp index';
    END IF;
    
    -- Index for sentiment_batch_id for tracking bulk operations
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'customer' 
        AND tablename = 'customer_satisfaction_raw' 
        AND indexname = 'idx_customer_satisfaction_raw_sentiment_batch'
    ) THEN
        CREATE INDEX idx_customer_satisfaction_raw_sentiment_batch 
        ON customer.customer_satisfaction_raw(sentiment_batch_id);
        RAISE NOTICE 'Created sentiment batch ID index';
    END IF;
    
    -- Partial index for unanalyzed records (where sentiment is null but inbox has content)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'customer' 
        AND tablename = 'customer_satisfaction_raw' 
        AND indexname = 'idx_customer_satisfaction_raw_unanalyzed'
    ) THEN
        CREATE INDEX idx_customer_satisfaction_raw_unanalyzed 
        ON customer.customer_satisfaction_raw(id) 
        WHERE sentiment IS NULL AND inbox IS NOT NULL AND TRIM(inbox) != '';
        RAISE NOTICE 'Created unanalyzed records partial index';
    END IF;
END $$;

-- Step 4: Add column comments for documentation
DO $$
BEGIN
    -- Add comments for new sentiment columns
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment 
    IS 'AI-analyzed sentiment: Positive, Negative, or Neutral';
    
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment_score 
    IS 'Sentiment score from -5.00 (very negative) to 5.00 (very positive)';
    
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment_reasons 
    IS 'AI-generated explanation for the sentiment classification';
    
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment_suggestion 
    IS 'AI-generated suggestion for improvement (null for positive sentiments)';
    
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment_themes 
    IS 'JSON array of themes identified in the review (e.g., ["Service", "Staff"])';
    
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment_analyzed_at 
    IS 'Timestamp when sentiment analysis was performed';
    
    COMMENT ON COLUMN customer.customer_satisfaction_raw.sentiment_batch_id 
    IS 'UUID for tracking bulk sentiment analysis operations';
    
    RAISE NOTICE 'Added comments for sentiment analysis columns';
END $$;

-- Step 5: Verification and summary
DO $$
DECLARE
    sentiment_columns_count INTEGER := 0;
    sentiment_indexes_count INTEGER := 0;
    sentiment_constraints_count INTEGER := 0;
BEGIN
    -- Count new sentiment columns
    SELECT COUNT(*) INTO sentiment_columns_count
    FROM information_schema.columns 
    WHERE table_schema = 'customer' 
    AND table_name = 'customer_satisfaction_raw' 
    AND column_name LIKE 'sentiment%';
    
    -- Count sentiment-related indexes
    SELECT COUNT(*) INTO sentiment_indexes_count
    FROM pg_indexes 
    WHERE schemaname = 'customer' 
    AND tablename = 'customer_satisfaction_raw' 
    AND indexname LIKE '%sentiment%';
    
    -- Count sentiment-related constraints
    SELECT COUNT(*) INTO sentiment_constraints_count
    FROM information_schema.check_constraints 
    WHERE constraint_schema = 'customer' 
    AND constraint_name LIKE '%sentiment%';
    
    -- Migration summary
    RAISE NOTICE '======= Migration 016 Summary =======';
    RAISE NOTICE 'Sentiment analysis columns added: %', sentiment_columns_count;
    RAISE NOTICE 'Sentiment analysis indexes created: %', sentiment_indexes_count;
    RAISE NOTICE 'Sentiment analysis constraints created: %', sentiment_constraints_count;
    
    IF sentiment_columns_count >= 7 AND sentiment_indexes_count >= 4 AND sentiment_constraints_count >= 2 THEN
        RAISE NOTICE '✅ Migration 016 completed successfully';
        RAISE NOTICE '✅ Customer satisfaction sentiment analysis fields created';
        RAISE NOTICE '✅ Proper indexing and constraints applied';
        RAISE NOTICE '✅ Ready for sentiment analysis API integration';
    ELSE
        RAISE WARNING '❌ Migration incomplete - please check column, index, and constraint creation';
        RAISE WARNING '   Expected: 7+ columns, 4+ indexes, 2+ constraints';
        RAISE WARNING '   Found: % columns, % indexes, % constraints', sentiment_columns_count, sentiment_indexes_count, sentiment_constraints_count;
    END IF;
END $$;

-- Step 6: Show new sentiment analysis columns for verification
SELECT 'customer_satisfaction_raw sentiment analysis columns' AS info_title,
       column_name, 
       data_type, 
       is_nullable, 
       character_maximum_length,
       numeric_precision,
       numeric_scale
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_satisfaction_raw' 
AND column_name LIKE 'sentiment%'
ORDER BY column_name;