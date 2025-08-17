-- Migration: Create customer_reminder_request table
-- Version: 006
-- Date: 2025-01-13
-- Description: Creates customer_reminder_request table in customer schema for storing customer reminder requests

-- Create customer_reminder_request table if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
    ) THEN
        CREATE TABLE customer.customer_reminder_request (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            dealer_id VARCHAR(10) NOT NULL,
            request_date DATE NOT NULL,
            request_time TIME NOT NULL,
            customer_name VARCHAR(255) NOT NULL,
            no_telp VARCHAR(20) NOT NULL,
            request_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
            whatsapp_status VARCHAR(20) NOT NULL DEFAULT 'NOT_SENT',
            reminder_type VARCHAR(50) NOT NULL,
            whatsapp_message TEXT NULL,
            fonnte_response JSONB NULL,
            created_by VARCHAR(100) NULL,
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_modified_by VARCHAR(100) NULL,
            last_modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX idx_customer_reminder_request_dealer_id ON customer.customer_reminder_request(dealer_id);
        CREATE INDEX idx_customer_reminder_request_phone ON customer.customer_reminder_request(no_telp);
        CREATE INDEX idx_customer_reminder_request_status ON customer.customer_reminder_request(request_status);
        CREATE INDEX idx_customer_reminder_request_whatsapp_status ON customer.customer_reminder_request(whatsapp_status);
        CREATE INDEX idx_customer_reminder_request_reminder_type ON customer.customer_reminder_request(reminder_type);
        CREATE INDEX idx_customer_reminder_request_date ON customer.customer_reminder_request(request_date);
        CREATE INDEX idx_customer_reminder_request_created_date ON customer.customer_reminder_request(created_date);
        
        RAISE NOTICE 'Created customer_reminder_request table with indexes';
    ELSE
        RAISE NOTICE 'customer_reminder_request table already exists';
    END IF;
END $$;

-- Add constraints and check constraints
DO $$
BEGIN
    -- Add check constraint for request_status
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_request_status'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD CONSTRAINT chk_request_status 
        CHECK (request_status IN ('PENDING', 'PROCESSED', 'FAILED', 'CANCELLED'));
        RAISE NOTICE 'Added request_status check constraint';
    END IF;
    
    -- Add check constraint for whatsapp_status
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_whatsapp_status'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD CONSTRAINT chk_whatsapp_status 
        CHECK (whatsapp_status IN ('NOT_SENT', 'SENT', 'FAILED', 'ERROR'));
        RAISE NOTICE 'Added whatsapp_status check constraint';
    END IF;
    
    -- Add check constraint for reminder_type
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_reminder_type'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD CONSTRAINT chk_reminder_type 
        CHECK (reminder_type IN (
            'SERVICE_REMINDER', 
            'PAYMENT_REMINDER', 
            'APPOINTMENT_REMINDER', 
            'MAINTENANCE_REMINDER', 
            'FOLLOW_UP_REMINDER', 
            'CUSTOM_REMINDER'
        ));
        RAISE NOTICE 'Added reminder_type check constraint';
    END IF;
    
    -- Add check constraint for phone number format (basic validation)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_phone_format'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD CONSTRAINT chk_phone_format 
        CHECK (no_telp ~ '^08[0-9]{8,11}$');
        RAISE NOTICE 'Added phone number format check constraint';
    END IF;
    
    -- Add check constraint for customer_name not empty
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_customer_name_not_empty'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD CONSTRAINT chk_customer_name_not_empty 
        CHECK (LENGTH(TRIM(customer_name)) > 0);
        RAISE NOTICE 'Added customer_name not empty check constraint';
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Error adding constraints: %', SQLERRM;
END $$;

-- Create trigger for automatic last_modified_date update
DO $$
BEGIN
    -- Create function to update last_modified_date
    CREATE OR REPLACE FUNCTION customer.update_reminder_last_modified_date()
    RETURNS TRIGGER AS $func$
    BEGIN
        NEW.last_modified_date = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql;
    
    -- Drop trigger if exists and create new one
    DROP TRIGGER IF EXISTS trg_update_reminder_last_modified_date ON customer.customer_reminder_request;
    CREATE TRIGGER trg_update_reminder_last_modified_date
        BEFORE UPDATE ON customer.customer_reminder_request
        FOR EACH ROW
        EXECUTE FUNCTION customer.update_reminder_last_modified_date();
    
    RAISE NOTICE 'Created trigger for automatic last_modified_date update';
END $$;

-- Verify the changes and show table structure
DO $$
DECLARE
    table_exists BOOLEAN := FALSE;
    index_count INTEGER;
    constraint_count INTEGER;
BEGIN
    -- Check if table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
    ) INTO table_exists;
    
    -- Count indexes
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes 
    WHERE schemaname = 'customer' 
    AND tablename = 'customer_reminder_request';
    
    -- Count constraints
    SELECT COUNT(*) INTO constraint_count
    FROM information_schema.check_constraints 
    WHERE constraint_schema = 'customer' 
    AND table_name = 'customer_reminder_request';
    
    RAISE NOTICE 'Migration 006 completed successfully:';
    RAISE NOTICE '- customer_reminder_request table exists: %', table_exists;
    RAISE NOTICE '- Number of indexes created: %', index_count;
    RAISE NOTICE '- Number of check constraints: %', constraint_count;
    
    IF table_exists THEN
        RAISE NOTICE '✅ customer_reminder_request table created successfully with all constraints and indexes';
    ELSE
        RAISE WARNING '❌ Migration incomplete - table not created';
    END IF;
END $$;

-- Show table structure for verification
DO $$
BEGIN
    RAISE NOTICE 'customer_reminder_request table columns:';
END $$;

SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_reminder_request' 
ORDER BY ordinal_position;

-- Show indexes
SELECT 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE schemaname = 'customer' 
AND tablename = 'customer_reminder_request'
ORDER BY indexname;

-- Show check constraints
SELECT 
    constraint_name,
    check_clause
FROM information_schema.check_constraints 
WHERE constraint_schema = 'customer' 
AND table_name = 'customer_reminder_request'
ORDER BY constraint_name;