-- Migration: Create dealer_access_key table for access key authentication
-- Version: 003
-- Date: 2025-01-10
-- Description: Creates dealer_access_key table to support external API authentication with access keys

-- Create dealer_access_key table if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealer_access_key'
    ) THEN
        CREATE TABLE dealer_integration.dealer_access_key (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            dealer_id VARCHAR(10) NOT NULL,
            access_key VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(255), -- Key description/name
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            last_used_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE,
            CONSTRAINT fk_dealer_access_key_dealer_id 
                FOREIGN KEY (dealer_id) 
                REFERENCES dealer_integration.dealers(dealer_id) 
                ON DELETE CASCADE
        );
        
        -- Create indexes for better performance
        CREATE INDEX idx_dealer_access_key_dealer_id ON dealer_integration.dealer_access_key(dealer_id);
        CREATE INDEX idx_dealer_access_key_access_key ON dealer_integration.dealer_access_key(access_key);
        CREATE INDEX idx_dealer_access_key_is_active ON dealer_integration.dealer_access_key(is_active);
        
        RAISE NOTICE 'Created dealer_access_key table with indexes';
    ELSE
        RAISE NOTICE 'dealer_access_key table already exists';
    END IF;
END $$;

-- Insert sample access keys for existing dealers
DO $$
DECLARE
    sample_dealer_record RECORD;
BEGIN
    -- Generate sample access keys for existing dealers
    FOR sample_dealer_record IN 
        SELECT dealer_id FROM dealer_integration.dealers WHERE is_active = TRUE
    LOOP
        -- Insert sample access key if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM dealer_integration.dealer_access_key 
            WHERE dealer_id = sample_dealer_record.dealer_id
        ) THEN
            INSERT INTO dealer_integration.dealer_access_key (
                dealer_id, 
                access_key, 
                name, 
                is_active
            ) VALUES (
                sample_dealer_record.dealer_id,
                'ak_' || sample_dealer_record.dealer_id || '_' || EXTRACT(EPOCH FROM NOW())::bigint,
                'Default Access Key',
                TRUE
            );
            
            RAISE NOTICE 'Created sample access key for dealer: %', sample_dealer_record.dealer_id;
        END IF;
    END LOOP;
END $$;

-- Verify the changes
DO $$
DECLARE
    table_exists BOOLEAN := FALSE;
    access_key_count INTEGER;
    dealer_count INTEGER;
BEGIN
    -- Check if table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'dealer_integration'
        AND table_name = 'dealer_access_key'
    ) INTO table_exists;
    
    IF table_exists THEN
        -- Count access keys and dealers
        SELECT COUNT(*) INTO access_key_count FROM dealer_integration.dealer_access_key;
        SELECT COUNT(*) INTO dealer_count FROM dealer_integration.dealers WHERE is_active = TRUE;
        
        RAISE NOTICE 'Migration 003 completed successfully:';
        RAISE NOTICE '- dealer_access_key table exists: %', table_exists;
        RAISE NOTICE '- Total access keys created: %', access_key_count;
        RAISE NOTICE '- Active dealers: %', dealer_count;
        
        -- Show sample access keys (first 3 characters only for security)
        FOR table_exists IN 
            SELECT CONCAT('Dealer: ', dealer_id, ', Key: ', SUBSTRING(access_key, 1, 6), '...') as key_info
            FROM dealer_integration.dealer_access_key 
            LIMIT 5
        LOOP
            RAISE NOTICE '- %', table_exists;
        END LOOP;
        
        RAISE NOTICE '✅ dealer_access_key table created successfully';
    ELSE
        RAISE WARNING '❌ dealer_access_key table was not created';
    END IF;
END $$;

-- Show table structure for verification
DO $$
BEGIN
    RAISE NOTICE 'dealer_access_key table structure:';
END $$;

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'dealer_integration' 
AND table_name = 'dealer_access_key' 
ORDER BY ordinal_position;