-- Migration 012: Replace no_telp with nomor_telepon_pelanggan
-- Date: 2025-08-17
-- Description: Replace legacy no_telp column with semantic nomor_telepon_pelanggan field

-- Current state: customer_reminder_request table has no_telp VARCHAR(20) NOT NULL
-- Target: Replace with nomor_telepon_pelanggan VARCHAR(20) NOT NULL for better semantics

-- Step 1: Add the new nomor_telepon_pelanggan column
ALTER TABLE customer.customer_reminder_request 
ADD COLUMN nomor_telepon_pelanggan VARCHAR(20);

-- Step 2: Copy all existing data from no_telp to nomor_telepon_pelanggan
UPDATE customer.customer_reminder_request 
SET nomor_telepon_pelanggan = no_telp 
WHERE no_telp IS NOT NULL;

-- Step 3: Make the new column NOT NULL since it's a required field
ALTER TABLE customer.customer_reminder_request 
ALTER COLUMN nomor_telepon_pelanggan SET NOT NULL;

-- Step 4: Drop the old no_telp column and its related constraints/indexes
-- Drop the phone index that references no_telp
DROP INDEX IF EXISTS customer.idx_customer_reminder_request_phone;

-- Drop the phone format check constraint
ALTER TABLE customer.customer_reminder_request 
DROP CONSTRAINT IF EXISTS chk_phone_format;

-- Drop the old no_telp column
ALTER TABLE customer.customer_reminder_request 
DROP COLUMN no_telp;

-- Step 5: Add proper constraints and index for the new column
-- Add phone number format check constraint for nomor_telepon_pelanggan
ALTER TABLE customer.customer_reminder_request 
ADD CONSTRAINT chk_nomor_telepon_pelanggan_format 
CHECK (nomor_telepon_pelanggan ~ '^08[0-9]{8,11}$');

-- Add index for performance on the new column
CREATE INDEX idx_customer_reminder_request_nomor_telepon_pelanggan 
ON customer.customer_reminder_request(nomor_telepon_pelanggan);

-- Step 6: Add column comment for documentation
COMMENT ON COLUMN customer.customer_reminder_request.nomor_telepon_pelanggan 
IS 'Customer primary phone number for WhatsApp reminders';

-- Migration completed: no_telp replaced with nomor_telepon_pelanggan, all data preserved