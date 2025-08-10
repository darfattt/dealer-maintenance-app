-- Migration: Remove autology_access_key column from dealers table
-- Version: 004
-- Date: 2025-01-10
-- Description: Removes autology_access_key column from dealer_integration.dealers table as access keys are now managed in separate table

-- Remove autology_access_key column if it exists
DO $$ 
BEGIN 
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'autology_access_key'
    ) THEN
        -- First, show data that will be lost (for backup purposes)
        RAISE NOTICE 'Existing autology_access_key values (for backup):';
        FOR r IN 
            SELECT dealer_id, autology_access_key 
            FROM dealer_integration.dealers 
            WHERE autology_access_key IS NOT NULL 
        LOOP
            RAISE NOTICE '- Dealer: %, Key: %', r.dealer_id, SUBSTRING(r.autology_access_key, 1, 10) || '...';
        END LOOP;
        
        -- Drop the column
        ALTER TABLE dealer_integration.dealers DROP COLUMN autology_access_key;
        RAISE NOTICE 'Removed autology_access_key column from dealer_integration.dealers table';
    ELSE
        RAISE NOTICE 'autology_access_key column does not exist in dealer_integration.dealers table';
    END IF;
END $$;

-- Verify the changes
DO $$
DECLARE
    column_exists BOOLEAN := FALSE;
    dealer_count INTEGER;
    access_key_table_exists BOOLEAN := FALSE;
BEGIN
    -- Check if column still exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealers' 
        AND column_name = 'autology_access_key'
    ) INTO column_exists;
    
    -- Check if new access key table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealer_access_key'
    ) INTO access_key_table_exists;
    
    -- Count dealers
    SELECT COUNT(*) INTO dealer_count FROM dealer_integration.dealers;
    
    RAISE NOTICE 'Migration 004 completed successfully:';
    RAISE NOTICE '- autology_access_key column exists: %', column_exists;
    RAISE NOTICE '- dealer_access_key table exists: %', access_key_table_exists;
    RAISE NOTICE '- Total dealers: %', dealer_count;
    
    IF NOT column_exists AND access_key_table_exists THEN
        RAISE NOTICE '✅ Migration successful - old column removed, new table available';
    ELSE
        RAISE WARNING '❌ Migration incomplete - check table structure';
    END IF;
END $$;

-- Show updated dealers table structure for verification
DO $$
BEGIN
    RAISE NOTICE 'Updated dealer_integration.dealers table columns (autology_access_key should be gone):';
END $$;

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'dealer_integration' 
AND table_name = 'dealers' 
ORDER BY ordinal_position;