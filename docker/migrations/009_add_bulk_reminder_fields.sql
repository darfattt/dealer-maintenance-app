-- Migration 009: Add bulk reminder fields to customer_reminder_request table
-- Date: 2025-08-17
-- Description: Add vehicle data, AHASS data, and reminder categorization fields for bulk reminder functionality

-- Add vehicle and customer data fields
ALTER TABLE customer.customer_reminder_request 
ADD COLUMN nama_pemilik VARCHAR(255),
ADD COLUMN nama_pembawa VARCHAR(255),
ADD COLUMN no_telepon_pembawa VARCHAR(20),
ADD COLUMN nomor_mesin VARCHAR(50),
ADD COLUMN nomor_polisi VARCHAR(20),
ADD COLUMN tipe_unit VARCHAR(100),
ADD COLUMN tanggal_beli DATE,
ADD COLUMN tanggal_expired_kpb DATE;

-- Add AHASS data fields
ALTER TABLE customer.customer_reminder_request 
ADD COLUMN kode_ahass VARCHAR(10),
ADD COLUMN nama_ahass VARCHAR(255),
ADD COLUMN alamat_ahass TEXT;

-- Add reminder categorization field
ALTER TABLE customer.customer_reminder_request 
ADD COLUMN reminder_target VARCHAR(50);

-- Update reminder_type column to support longer descriptions
ALTER TABLE customer.customer_reminder_request 
ALTER COLUMN reminder_type TYPE VARCHAR(100);

-- Add comments for clarity
COMMENT ON COLUMN customer.customer_reminder_request.nama_pemilik IS 'Vehicle owner name';
COMMENT ON COLUMN customer.customer_reminder_request.nama_pembawa IS 'Person bringing the vehicle';
COMMENT ON COLUMN customer.customer_reminder_request.no_telepon_pembawa IS 'Phone number of person bringing vehicle';
COMMENT ON COLUMN customer.customer_reminder_request.nomor_mesin IS 'Vehicle engine number';
COMMENT ON COLUMN customer.customer_reminder_request.nomor_polisi IS 'Vehicle license plate number';
COMMENT ON COLUMN customer.customer_reminder_request.tipe_unit IS 'Vehicle unit type';
COMMENT ON COLUMN customer.customer_reminder_request.tanggal_beli IS 'Vehicle purchase date';
COMMENT ON COLUMN customer.customer_reminder_request.tanggal_expired_kpb IS 'KPB expiry date';
COMMENT ON COLUMN customer.customer_reminder_request.kode_ahass IS 'AHASS code';
COMMENT ON COLUMN customer.customer_reminder_request.nama_ahass IS 'AHASS name';
COMMENT ON COLUMN customer.customer_reminder_request.alamat_ahass IS 'AHASS address';
COMMENT ON COLUMN customer.customer_reminder_request.reminder_target IS 'Reminder target category (KPB-1, KPB-2, etc.)';

-- Update existing records to have default reminder_target if needed
UPDATE customer.customer_reminder_request 
SET reminder_target = 'CUSTOM' 
WHERE reminder_target IS NULL;