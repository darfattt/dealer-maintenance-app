-- Migration 014: Add nama_pelanggan and remove unused fields
-- Date: 2025-08-21
-- Description: Add nama_pelanggan column and remove nama_pemilik, nama_pembawa, no_telepon_pembawa
-- This migration syncs the database schema with the updated SQLAlchemy model

-- Step 1: Add nama_pelanggan column
DO $$ 
BEGIN 
    -- Add nama_pelanggan column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pelanggan'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD COLUMN nama_pelanggan VARCHAR(255);
        RAISE NOTICE 'Added nama_pelanggan column';
    ELSE
        RAISE NOTICE 'nama_pelanggan column already exists';
    END IF;
END $$;

-- Step 2: Migrate data from nama_pemilik to nama_pelanggan
DO $$
DECLARE
    migrated_count INTEGER := 0;
BEGIN
    -- Check if nama_pemilik column exists and has data
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pemilik'
    ) THEN
        -- Migrate data from nama_pemilik to nama_pelanggan
        UPDATE customer.customer_reminder_request 
        SET nama_pelanggan = nama_pemilik 
        WHERE nama_pemilik IS NOT NULL 
        AND (nama_pelanggan IS NULL OR nama_pelanggan = '');
        
        GET DIAGNOSTICS migrated_count = ROW_COUNT;
        RAISE NOTICE 'Migrated % records from nama_pemilik to nama_pelanggan', migrated_count;
    ELSE
        RAISE NOTICE 'nama_pemilik column does not exist, skipping data migration';
    END IF;
END $$;

-- Step 3: Make nama_pelanggan NOT NULL after data migration
DO $$
BEGIN
    -- Only proceed if nama_pelanggan exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pelanggan'
    ) THEN
        -- Set default value for any NULL nama_pelanggan
        UPDATE customer.customer_reminder_request 
        SET nama_pelanggan = 'Unknown Customer'
        WHERE nama_pelanggan IS NULL OR nama_pelanggan = '';
        
        -- Make column NOT NULL
        ALTER TABLE customer.customer_reminder_request 
        ALTER COLUMN nama_pelanggan SET NOT NULL;
        
        RAISE NOTICE 'Set nama_pelanggan column to NOT NULL';
    END IF;
END $$;

-- Step 4: Drop constraint related to nama_pemilik
DO $$
BEGIN
    -- Drop the old constraint if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_nama_pemilik_not_empty'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        DROP CONSTRAINT chk_nama_pemilik_not_empty;
        RAISE NOTICE 'Dropped chk_nama_pemilik_not_empty constraint';
    END IF;
END $$;

-- Step 5: Add constraint for nama_pelanggan
DO $$
BEGIN
    -- Add new constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_schema = 'customer' 
        AND table_name = 'customer_reminder_request'
        AND constraint_name = 'chk_nama_pelanggan_not_empty'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        ADD CONSTRAINT chk_nama_pelanggan_not_empty 
        CHECK (LENGTH(TRIM(nama_pelanggan)) > 0);
        RAISE NOTICE 'Added chk_nama_pelanggan_not_empty constraint';
    END IF;
END $$;

-- Step 6: Remove unused columns
DO $$
BEGIN
    -- Remove nama_pemilik column if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pemilik'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        DROP COLUMN nama_pemilik;
        RAISE NOTICE 'Dropped nama_pemilik column';
    END IF;
    
    -- Remove nama_pembawa column if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pembawa'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        DROP COLUMN nama_pembawa;
        RAISE NOTICE 'Dropped nama_pembawa column';
    END IF;
    
    -- Remove no_telepon_pembawa column if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'no_telepon_pembawa'
    ) THEN
        ALTER TABLE customer.customer_reminder_request 
        DROP COLUMN no_telepon_pembawa;
        RAISE NOTICE 'Dropped no_telepon_pembawa column';
    END IF;
END $$;

-- Step 7: Add column comment for documentation
DO $$
BEGIN
    -- Add comment for nama_pelanggan column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pelanggan'
    ) THEN
        COMMENT ON COLUMN customer.customer_reminder_request.nama_pelanggan 
        IS 'Customer name for WhatsApp reminders (replaces nama_pemilik)';
        RAISE NOTICE 'Added comment for nama_pelanggan column';
    END IF;
END $$;

-- Step 8: Verification and summary
DO $$
DECLARE
    nama_pelanggan_exists BOOLEAN := FALSE;
    nama_pemilik_exists BOOLEAN := FALSE;
    nama_pembawa_exists BOOLEAN := FALSE;
    no_telepon_pembawa_exists BOOLEAN := FALSE;
    record_count INTEGER;
BEGIN
    -- Check final column state
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pelanggan'
    ) INTO nama_pelanggan_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pemilik'
    ) INTO nama_pemilik_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'nama_pembawa'
    ) INTO nama_pembawa_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_reminder_request'
        AND column_name = 'no_telepon_pembawa'
    ) INTO no_telepon_pembawa_exists;
    
    -- Count records with nama_pelanggan
    SELECT COUNT(*) INTO record_count
    FROM customer.customer_reminder_request
    WHERE nama_pelanggan IS NOT NULL;
    
    -- Migration summary
    RAISE NOTICE '======= Migration 014 Summary =======';
    RAISE NOTICE 'nama_pelanggan exists: %', nama_pelanggan_exists;
    RAISE NOTICE 'nama_pemilik exists: %', nama_pemilik_exists;
    RAISE NOTICE 'nama_pembawa exists: %', nama_pembawa_exists;
    RAISE NOTICE 'no_telepon_pembawa exists: %', no_telepon_pembawa_exists;
    RAISE NOTICE 'Records with nama_pelanggan: %', record_count;
    
    IF nama_pelanggan_exists AND NOT nama_pemilik_exists AND NOT nama_pembawa_exists AND NOT no_telepon_pembawa_exists THEN
        RAISE NOTICE '✅ Migration 014 completed successfully';
        RAISE NOTICE '✅ Database schema now matches SQLAlchemy model';
        RAISE NOTICE '✅ reminder/add-bulk API should work correctly';
    ELSE
        RAISE WARNING '❌ Migration incomplete - please check column states above';
    END IF;
END $$;

-- Step 9: Show final table structure for verification
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_reminder_request' 
AND column_name IN ('nama_pelanggan', 'nomor_telepon_pelanggan', 'nama_pemilik', 'nama_pembawa', 'no_telepon_pembawa')
ORDER BY ordinal_position;