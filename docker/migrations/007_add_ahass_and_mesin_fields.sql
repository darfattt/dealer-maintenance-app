-- Migration: Add AHASS and engine number fields to customer_validation_request table
-- Version: 007
-- Date: 2025-01-17
-- Description: Adds kode_ahass, nama_ahass, alamat_ahass, and nomor_mesin fields for enhanced customer validation data

-- Add kode_ahass column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'kode_ahass'
    ) THEN
        ALTER TABLE customer.customer_validation_request ADD COLUMN kode_ahass VARCHAR(10) NULL;
        RAISE NOTICE 'Added kode_ahass column to customer.customer_validation_request table';
    ELSE
        RAISE NOTICE 'kode_ahass column already exists in customer.customer_validation_request table';
    END IF;
END $$;

-- Add nama_ahass column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'nama_ahass'
    ) THEN
        ALTER TABLE customer.customer_validation_request ADD COLUMN nama_ahass VARCHAR(255) NULL;
        RAISE NOTICE 'Added nama_ahass column to customer.customer_validation_request table';
    ELSE
        RAISE NOTICE 'nama_ahass column already exists in customer.customer_validation_request table';
    END IF;
END $$;

-- Add alamat_ahass column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'alamat_ahass'
    ) THEN
        ALTER TABLE customer.customer_validation_request ADD COLUMN alamat_ahass TEXT NULL;
        RAISE NOTICE 'Added alamat_ahass column to customer.customer_validation_request table';
    ELSE
        RAISE NOTICE 'alamat_ahass column already exists in customer.customer_validation_request table';
    END IF;
END $$;

-- Add nomor_mesin column if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'nomor_mesin'
    ) THEN
        ALTER TABLE customer.customer_validation_request ADD COLUMN nomor_mesin VARCHAR(50) NULL;
        RAISE NOTICE 'Added nomor_mesin column to customer.customer_validation_request table';
    ELSE
        RAISE NOTICE 'nomor_mesin column already exists in customer.customer_validation_request table';
    END IF;
END $$;

-- Verify the changes
DO $$
DECLARE
    kode_ahass_exists BOOLEAN := FALSE;
    nama_ahass_exists BOOLEAN := FALSE;
    alamat_ahass_exists BOOLEAN := FALSE;
    nomor_mesin_exists BOOLEAN := FALSE;
    table_exists BOOLEAN := FALSE;
    request_count INTEGER;
BEGIN
    -- Check if customer_validation_request table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request'
    ) INTO table_exists;
    
    -- Check if new columns exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'kode_ahass'
    ) INTO kode_ahass_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'nama_ahass'
    ) INTO nama_ahass_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'alamat_ahass'
    ) INTO alamat_ahass_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'customer'
        AND table_name = 'customer_validation_request' 
        AND column_name = 'nomor_mesin'
    ) INTO nomor_mesin_exists;
    
    RAISE NOTICE 'Migration 007 completed successfully:';
    RAISE NOTICE '- customer_validation_request table exists: %', table_exists;
    RAISE NOTICE '- kode_ahass column exists: %', kode_ahass_exists;
    RAISE NOTICE '- nama_ahass column exists: %', nama_ahass_exists;
    RAISE NOTICE '- alamat_ahass column exists: %', alamat_ahass_exists;
    RAISE NOTICE '- nomor_mesin column exists: %', nomor_mesin_exists;
    
    IF table_exists THEN
        -- Count existing requests
        SELECT COUNT(*) INTO request_count FROM customer.customer_validation_request;
        RAISE NOTICE '- Total existing requests: %', request_count;
    END IF;
    
    IF table_exists AND kode_ahass_exists AND nama_ahass_exists AND alamat_ahass_exists AND nomor_mesin_exists THEN
        RAISE NOTICE '✅ All AHASS and engine number fields added successfully';
    ELSE
        RAISE WARNING '❌ Migration incomplete - check table structure';
    END IF;
END $$;

-- Show updated table structure for verification
DO $$
BEGIN
    RAISE NOTICE 'Updated customer_validation_request table columns (new fields should be included):';
END $$;

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'customer' 
AND table_name = 'customer_validation_request' 
ORDER BY ordinal_position;