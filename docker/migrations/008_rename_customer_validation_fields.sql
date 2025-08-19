-- Migration 008: Rename customer validation request fields
-- Date: 2025-08-17
-- Description: Rename no_pol to nomor_polisi and no_telp to nomor_telepon_pembawa for better field naming consistency

-- Rename no_pol to nomor_polisi
ALTER TABLE customer.customer_validation_request 
RENAME COLUMN no_pol TO nomor_polisi;

-- Rename no_telp to nomor_telepon_pembawa  
ALTER TABLE customer.customer_validation_request 
RENAME COLUMN no_telp TO nomor_telepon_pembawa;

-- Add comment for clarity
COMMENT ON COLUMN customer.customer_validation_request.nomor_polisi IS 'Vehicle license plate number (renamed from no_pol)';
COMMENT ON COLUMN customer.customer_validation_request.nomor_telepon_pembawa IS 'Customer phone number (renamed from no_telp)';