-- Migration 015: Create customer satisfaction tables
-- Date: 2025-08-28
-- Description: Create customer_satisfaction_raw and customer_satisfaction_upload_tracker tables
-- This migration adds support for customer satisfaction data import and tracking

-- Step 1: Create customer_satisfaction_raw table
DO $$ 
BEGIN 
    -- Create customer_satisfaction_raw table if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_raw'
    ) THEN
        CREATE TABLE customer.customer_satisfaction_raw (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            
            -- CSV columns (keeping original Indonesian field names)
            no_tiket VARCHAR(50),
            no_booking_no_order_pemesanan VARCHAR(100),
            nama_konsumen VARCHAR(255),
            no_hp VARCHAR(20),
            alamat_email VARCHAR(255),
            source VARCHAR(100),
            kota VARCHAR(100),
            fu_by_se VARCHAR(100),
            fu_by_sda VARCHAR(100),
            no_ahass VARCHAR(10),
            status VARCHAR(50),
            nama_ahass VARCHAR(255),
            tanggal_service VARCHAR(50),
            periode_service VARCHAR(10),
            tanggal_rating VARCHAR(50),
            jenis_hari VARCHAR(50),
            periode_utk_suspend VARCHAR(100),
            submit_review_date_first_fu_cs VARCHAR(50),
            lt_tgl_rating_submit VARCHAR(10),
            sesuai_lt VARCHAR(50),
            periode_fu VARCHAR(10),
            inbox TEXT,
            indikasi_keluhan VARCHAR(100),
            rating VARCHAR(10),
            departemen VARCHAR(100),
            no_ahass_duplicate VARCHAR(10),
            status_duplicate VARCHAR(50),
            nama_ahass_duplicate VARCHAR(255),
            
            -- Upload tracking
            upload_batch_id UUID,
            
            -- Audit fields
            created_by VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            last_modified_by VARCHAR(100),
            last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
        
        -- Create indexes for filtering
        CREATE INDEX idx_customer_satisfaction_raw_no_ahass ON customer.customer_satisfaction_raw(no_ahass);
        CREATE INDEX idx_customer_satisfaction_raw_periode_suspend ON customer.customer_satisfaction_raw(periode_utk_suspend);
        CREATE INDEX idx_customer_satisfaction_raw_submit_review ON customer.customer_satisfaction_raw(submit_review_date_first_fu_cs);
        CREATE INDEX idx_customer_satisfaction_raw_upload_batch ON customer.customer_satisfaction_raw(upload_batch_id);
        CREATE INDEX idx_customer_satisfaction_raw_created_date ON customer.customer_satisfaction_raw(created_date);
        
        -- Add trigger for last_modified_date
        CREATE OR REPLACE FUNCTION customer.update_customer_satisfaction_raw_modified_date()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.last_modified_date = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER trigger_customer_satisfaction_raw_update
            BEFORE UPDATE ON customer.customer_satisfaction_raw
            FOR EACH ROW EXECUTE FUNCTION customer.update_customer_satisfaction_raw_modified_date();
        
        RAISE NOTICE 'Created customer_satisfaction_raw table with indexes and trigger';
    ELSE
        RAISE NOTICE 'customer_satisfaction_raw table already exists';
    END IF;
END $$;

-- Step 2: Create customer_satisfaction_upload_tracker table
DO $$ 
BEGIN 
    -- Create customer_satisfaction_upload_tracker table if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_upload_tracker'
    ) THEN
        CREATE TABLE customer.customer_satisfaction_upload_tracker (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            
            -- File information
            file_name VARCHAR(255) NOT NULL,
            file_size INTEGER,
            
            -- Upload summary
            total_records INTEGER NOT NULL DEFAULT 0,
            successful_records INTEGER NOT NULL DEFAULT 0,
            failed_records INTEGER NOT NULL DEFAULT 0,
            
            -- Processing status
            upload_status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING',
            
            -- Error details
            error_message TEXT,
            
            -- Audit fields
            uploaded_by VARCHAR(100),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            completed_date TIMESTAMP
        );
        
        -- Create indexes for tracker
        CREATE INDEX idx_customer_satisfaction_upload_tracker_status ON customer.customer_satisfaction_upload_tracker(upload_status);
        CREATE INDEX idx_customer_satisfaction_upload_tracker_upload_date ON customer.customer_satisfaction_upload_tracker(upload_date);
        CREATE INDEX idx_customer_satisfaction_upload_tracker_uploaded_by ON customer.customer_satisfaction_upload_tracker(uploaded_by);
        
        -- Add constraint for upload_status
        ALTER TABLE customer.customer_satisfaction_upload_tracker
        ADD CONSTRAINT chk_upload_status CHECK (upload_status IN ('PROCESSING', 'COMPLETED', 'FAILED'));
        
        RAISE NOTICE 'Created customer_satisfaction_upload_tracker table with indexes and constraints';
    ELSE
        RAISE NOTICE 'customer_satisfaction_upload_tracker table already exists';
    END IF;
END $$;

-- Step 3: Add table comments for documentation
DO $$
BEGIN
    -- Add comments for customer_satisfaction_raw table
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_raw'
    ) THEN
        COMMENT ON TABLE customer.customer_satisfaction_raw 
        IS 'Raw customer satisfaction data imported from Excel/CSV files';
        
        COMMENT ON COLUMN customer.customer_satisfaction_raw.no_tiket 
        IS 'Ticket number from customer satisfaction system';
        
        COMMENT ON COLUMN customer.customer_satisfaction_raw.periode_utk_suspend 
        IS 'Period for suspension - used for filtering';
        
        COMMENT ON COLUMN customer.customer_satisfaction_raw.submit_review_date_first_fu_cs 
        IS 'Submit review date for first follow-up CS - used for filtering';
        
        COMMENT ON COLUMN customer.customer_satisfaction_raw.no_ahass 
        IS 'AHASS number - used for filtering';
        
        COMMENT ON COLUMN customer.customer_satisfaction_raw.upload_batch_id 
        IS 'Links to upload tracker for batch processing';
        
        RAISE NOTICE 'Added comments for customer_satisfaction_raw table';
    END IF;
    
    -- Add comments for upload tracker table
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_upload_tracker'
    ) THEN
        COMMENT ON TABLE customer.customer_satisfaction_upload_tracker 
        IS 'Tracks customer satisfaction file uploads and processing status';
        
        COMMENT ON COLUMN customer.customer_satisfaction_upload_tracker.upload_status 
        IS 'Upload processing status: PROCESSING, COMPLETED, FAILED';
        
        RAISE NOTICE 'Added comments for customer_satisfaction_upload_tracker table';
    END IF;
END $$;

-- Step 4: Verification and summary
DO $$
DECLARE
    satisfaction_table_exists BOOLEAN := FALSE;
    tracker_table_exists BOOLEAN := FALSE;
    satisfaction_indexes INTEGER := 0;
    tracker_indexes INTEGER := 0;
BEGIN
    -- Check table existence
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_raw'
    ) INTO satisfaction_table_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_satisfaction_upload_tracker'
    ) INTO tracker_table_exists;
    
    -- Count indexes
    SELECT COUNT(*) INTO satisfaction_indexes
    FROM pg_indexes 
    WHERE schemaname = 'customer' 
    AND tablename = 'customer_satisfaction_raw';
    
    SELECT COUNT(*) INTO tracker_indexes
    FROM pg_indexes 
    WHERE schemaname = 'customer' 
    AND tablename = 'customer_satisfaction_upload_tracker';
    
    -- Migration summary
    RAISE NOTICE '======= Migration 015 Summary =======';
    RAISE NOTICE 'customer_satisfaction_raw table exists: %', satisfaction_table_exists;
    RAISE NOTICE 'customer_satisfaction_upload_tracker table exists: %', tracker_table_exists;
    RAISE NOTICE 'customer_satisfaction_raw indexes count: %', satisfaction_indexes;
    RAISE NOTICE 'customer_satisfaction_upload_tracker indexes count: %', tracker_indexes;
    
    IF satisfaction_table_exists AND tracker_table_exists AND satisfaction_indexes >= 5 AND tracker_indexes >= 3 THEN
        RAISE NOTICE '✅ Migration 015 completed successfully';
        RAISE NOTICE '✅ Customer satisfaction tables created with proper indexing';
        RAISE NOTICE '✅ Ready for customer satisfaction API implementation';
    ELSE
        RAISE WARNING '❌ Migration incomplete - please check table and index creation';
    END IF;
END $$;

-- Step 5: Show final table structures for verification
SELECT 'customer_satisfaction_raw' AS table_name, 
       column_name, 
       data_type, 
       is_nullable, 
       character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_satisfaction_raw' 
ORDER BY ordinal_position
LIMIT 10;

SELECT 'customer_satisfaction_upload_tracker' AS table_name,
       column_name, 
       data_type, 
       is_nullable, 
       character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_satisfaction_upload_tracker' 
ORDER BY ordinal_position;