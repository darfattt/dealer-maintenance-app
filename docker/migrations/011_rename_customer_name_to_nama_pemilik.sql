-- Migration 011: Rename customer_name column to nama_pemilik
-- Date: 2025-08-17
-- Description: Consolidate customer_name and nama_pemilik columns into single nama_pemilik column

-- Current state: 
-- - customer_name VARCHAR(255) NOT NULL (from migration 006, used by legacy endpoints)
-- - nama_pemilik VARCHAR(255) NULL (from migration 009, used by bulk endpoints)
-- Target: Single nama_pemilik VARCHAR(255) NOT NULL column

-- Step 1: Safely consolidate any data from nama_pemilik back to customer_name if needed
-- (This handles edge case where nama_pemilik has data but customer_name is somehow NULL)
UPDATE customer.customer_reminder_request 
SET customer_name = nama_pemilik 
WHERE customer_name IS NULL AND nama_pemilik IS NOT NULL;

-- Step 2: Drop the duplicate nama_pemilik column that was added in migration 009
ALTER TABLE customer.customer_reminder_request 
DROP COLUMN IF EXISTS nama_pemilik;

-- Step 3: Rename customer_name to nama_pemilik (simple direct rename)
ALTER TABLE customer.customer_reminder_request 
RENAME COLUMN customer_name TO nama_pemilik;

-- Step 4: Update the check constraint to reflect the new column name
-- Drop the old constraint
ALTER TABLE customer.customer_reminder_request 
DROP CONSTRAINT IF EXISTS chk_customer_name_not_empty;

-- Add new constraint with updated column name
ALTER TABLE customer.customer_reminder_request 
ADD CONSTRAINT chk_nama_pemilik_not_empty 
CHECK (LENGTH(TRIM(nama_pemilik)) > 0);

-- Step 5: Update column comment to reflect its primary role
COMMENT ON COLUMN customer.customer_reminder_request.nama_pemilik IS 'Primary customer/vehicle owner name field';

-- Migration completed: Single nama_pemilik column with all existing customer_name data preserved