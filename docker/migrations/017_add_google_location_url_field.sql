-- Migration: Add google_location_url column to dealers table
-- Version: 017
-- Date: 2025-01-20
-- Description: Adds google_location_url field to store Google Maps location URLs for dealers

-- Add google_location_url column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers'
        AND column_name = 'google_location_url'
    ) THEN
        ALTER TABLE dealer_integration.dealers ADD COLUMN google_location_url VARCHAR(500) NULL;
        RAISE NOTICE 'Added google_location_url column to dealer_integration.dealers table';
    ELSE
        RAISE NOTICE 'google_location_url column already exists in dealer_integration.dealers table';
    END IF;
END $$;

-- Add comment to document the column purpose
COMMENT ON COLUMN dealer_integration.dealers.google_location_url IS 'Google Maps location URL for the dealer location';

-- Verify the changes
DO $$
DECLARE
    column_exists BOOLEAN;
BEGIN
    -- Check if column was created successfully
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers'
        AND column_name = 'google_location_url'
    ) INTO column_exists;

    IF column_exists THEN
        RAISE NOTICE 'Migration 017 completed successfully:';
        RAISE NOTICE '- google_location_url column added to dealer_integration.dealers table';
        RAISE NOTICE '- Column type: VARCHAR(500), nullable: true';
    ELSE
        RAISE WARNING 'Migration 017 failed: google_location_url column was not created';
    END IF;
END $$;