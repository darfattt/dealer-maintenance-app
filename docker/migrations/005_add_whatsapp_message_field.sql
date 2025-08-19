-- Migration: Add whatsapp_message field to customer_validation_request table
-- Version: 005
-- Date: 2025-01-10
-- Description: Adds whatsapp_message TEXT field to store the generated WhatsApp message content

-- Add whatsapp_message column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'whatsapp_message'
    ) THEN
        ALTER TABLE customer.customer_validation_request ADD COLUMN whatsapp_message TEXT NULL;
        RAISE NOTICE 'Added whatsapp_message column to customer.customer_validation_request table';
    ELSE
        RAISE NOTICE 'whatsapp_message column already exists in customer.customer_validation_request table';
    END IF;
END $$;

-- Verify the changes
DO $$
DECLARE
    column_exists BOOLEAN := FALSE;
    table_exists BOOLEAN := FALSE;
    request_count INTEGER;
BEGIN
    -- Check if customer_validation_request table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request'
    ) INTO table_exists;
    
    -- Check if whatsapp_message column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'whatsapp_message'
    ) INTO column_exists;
    
    RAISE NOTICE 'Migration 005 completed successfully:';
    RAISE NOTICE '- customer_validation_request table exists: %', table_exists;
    RAISE NOTICE '- whatsapp_message column exists: %', column_exists;
    
    IF table_exists THEN
        -- Count existing requests
        SELECT COUNT(*) INTO request_count FROM customer.customer_validation_request;
        RAISE NOTICE '- Total existing requests: %', request_count;
    END IF;
    
    IF table_exists AND column_exists THEN
        RAISE NOTICE '✅ whatsapp_message field added successfully';
    ELSE
        RAISE WARNING '❌ Migration incomplete - check table structure';
    END IF;
END $$;

-- Show updated table structure for verification
DO $$
BEGIN
    RAISE NOTICE 'Updated customer_validation_request table columns (whatsapp_message should be included):';
END $$;

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_validation_request' 
ORDER BY ordinal_position;