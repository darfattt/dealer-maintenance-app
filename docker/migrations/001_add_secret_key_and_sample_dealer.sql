-- Migration: Add secret_key column and sample dealer data
-- Version: 001
-- Date: 2024-12-19
-- Description: Updates dealers table structure and adds sample dealer for testing

-- Add secret_key column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'dealers' 
        AND column_name = 'secret_key'
    ) THEN
        ALTER TABLE dealers ADD COLUMN secret_key VARCHAR(255) NULL;
        RAISE NOTICE 'Added secret_key column to dealers table';
    ELSE
        RAISE NOTICE 'secret_key column already exists in dealers table';
    END IF;
END $$;

-- Update existing dealers with default secret keys if they don't have one
UPDATE dealers 
SET secret_key = CASE 
    WHEN dealer_id = '00999' THEN 'default-secret-key-2024'
    ELSE 'generated-secret-key-' || dealer_id || '-2024'
END
WHERE secret_key IS NULL;

-- Insert sample dealer if it doesn't exist
INSERT INTO dealers (id, dealer_id, dealer_name, api_key, api_token, secret_key, is_active, created_at, updated_at)
VALUES (
    'e3a18c82-c500-450f-b6e1-5c5fbe68bf41'::uuid, 
    '12284', 
    'Sample Dealer', 
    'sample-api-key-12284', 
    'sample-api-token-12284', 
    'sample-secret-key-12284', 
    true, 
    CURRENT_TIMESTAMP, 
    CURRENT_TIMESTAMP
)
ON CONFLICT (dealer_id) DO UPDATE SET
    dealer_name = EXCLUDED.dealer_name,
    api_key = EXCLUDED.api_key,
    api_token = EXCLUDED.api_token,
    secret_key = EXCLUDED.secret_key,
    updated_at = CURRENT_TIMESTAMP;

-- Verify the changes
DO $$
DECLARE
    dealer_count INTEGER;
    secret_key_count INTEGER;
BEGIN
    -- Count total dealers
    SELECT COUNT(*) INTO dealer_count FROM dealers;
    
    -- Count dealers with secret keys
    SELECT COUNT(*) INTO secret_key_count FROM dealers WHERE secret_key IS NOT NULL;
    
    RAISE NOTICE 'Migration completed successfully:';
    RAISE NOTICE '- Total dealers: %', dealer_count;
    RAISE NOTICE '- Dealers with secret keys: %', secret_key_count;
    
    -- Verify sample dealer exists
    IF EXISTS (SELECT 1 FROM dealers WHERE dealer_id = '12284') THEN
        RAISE NOTICE '- Sample dealer (12284) exists';
    ELSE
        RAISE WARNING '- Sample dealer (12284) was not created';
    END IF;
    
    -- Verify default dealer exists
    IF EXISTS (SELECT 1 FROM dealers WHERE dealer_id = '00999') THEN
        RAISE NOTICE '- Default dealer (00999) exists';
    ELSE
        RAISE WARNING '- Default dealer (00999) was not found';
    END IF;
END $$;
