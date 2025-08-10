-- Migration: Add fonnte_api_key, fonnte_api_url, phone_number and autology_access_key columns to dealers table
-- Version: 002
-- Date: 2025-01-10
-- Description: Adds Fonnte WhatsApp, phone number and Autology integration columns to dealer_integration.dealers table

-- Add fonnte_api_key column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'fonnte_api_key'
    ) THEN
        ALTER TABLE dealer_integration.dealers ADD COLUMN fonnte_api_key VARCHAR(255) NULL;
        RAISE NOTICE 'Added fonnte_api_key column to dealer_integration.dealers table';
    ELSE
        RAISE NOTICE 'fonnte_api_key column already exists in dealer_integration.dealers table';
    END IF;
END $$;

-- Add fonnte_api_url column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'fonnte_api_url'
    ) THEN
        ALTER TABLE dealer_integration.dealers ADD COLUMN fonnte_api_url VARCHAR(255) NULL DEFAULT 'https://api.fonnte.com/send';
        RAISE NOTICE 'Added fonnte_api_url column to dealer_integration.dealers table';
    ELSE
        RAISE NOTICE 'fonnte_api_url column already exists in dealer_integration.dealers table';
    END IF;
END $$;

-- Add phone_number column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'phone_number'
    ) THEN
        ALTER TABLE dealer_integration.dealers ADD COLUMN phone_number VARCHAR(255) NULL;
        RAISE NOTICE 'Added phone_number column to dealer_integration.dealers table';
    ELSE
        RAISE NOTICE 'phone_number column already exists in dealer_integration.dealers table';
    END IF;
END $$;

-- Add autology_access_key column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'autology_access_key'
    ) THEN
        ALTER TABLE dealer_integration.dealers ADD COLUMN autology_access_key VARCHAR(255) NULL;
        RAISE NOTICE 'Added autology_access_key column to dealer_integration.dealers table';
    ELSE
        RAISE NOTICE 'autology_access_key column already exists in dealer_integration.dealers table';
    END IF;
END $$;

-- Set default fonnte_api_url for existing dealers that have NULL values
UPDATE dealer_integration.dealers 
SET fonnte_api_url = 'https://api.fonnte.com/send' 
WHERE fonnte_api_url IS NULL;

-- Verify the changes
DO $$
DECLARE
    fonnte_api_key_exists BOOLEAN := FALSE;
    fonnte_api_url_exists BOOLEAN := FALSE;
    phone_number_exists BOOLEAN := FALSE;
    autology_access_key_exists BOOLEAN := FALSE;
    dealer_count INTEGER;
    default_url_count INTEGER;
BEGIN
    -- Check if all columns exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'fonnte_api_key'
    ) INTO fonnte_api_key_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'fonnte_api_url'
    ) INTO fonnte_api_url_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'phone_number'
    ) INTO phone_number_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'autology_access_key'
    ) INTO autology_access_key_exists;
    
    -- Count total dealers and default URL assignments
    SELECT COUNT(*) INTO dealer_count FROM dealer_integration.dealers;
    SELECT COUNT(*) INTO default_url_count FROM dealer_integration.dealers WHERE fonnte_api_url = 'https://api.fonnte.com/send';
    
    RAISE NOTICE 'Migration 002 completed successfully:';
    RAISE NOTICE '- Total dealers: %', dealer_count;
    RAISE NOTICE '- fonnte_api_key column exists: %', fonnte_api_key_exists;
    RAISE NOTICE '- fonnte_api_url column exists: %', fonnte_api_url_exists;
    RAISE NOTICE '- phone_number column exists: %', phone_number_exists;
    RAISE NOTICE '- autology_access_key column exists: %', autology_access_key_exists;
    RAISE NOTICE '- Dealers with default Fonnte URL: %', default_url_count;
    
    IF fonnte_api_key_exists AND fonnte_api_url_exists AND phone_number_exists AND autology_access_key_exists THEN
        RAISE NOTICE '✅ All columns added successfully';
    ELSE
        RAISE WARNING '❌ Some columns were not added properly';
    END IF;
END $$;

-- Show current table structure for verification
DO $$
BEGIN
    RAISE NOTICE 'Current dealer_integration.dealers table columns:';
END $$;

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'dealer_integration' 
AND table_name = 'dealers' 
ORDER BY ordinal_position;