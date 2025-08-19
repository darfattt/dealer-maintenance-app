-- Migration 010: Add customer reminder processing tracker
-- Date: 2025-08-17
-- Description: Create new table to track bulk reminder processing and add transaction_id to customer_reminder_request

-- Create customer_reminder_processing table
CREATE TABLE customer.customer_reminder_processing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    status VARCHAR(20) DEFAULT 'inprogress' CHECK (status IN ('inprogress', 'completed')),
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT NOW(),
    last_modified_by VARCHAR(100),
    last_modified_date TIMESTAMP DEFAULT NOW()
);

-- Add transaction_id to customer_reminder_request table
ALTER TABLE customer.customer_reminder_request 
ADD COLUMN transaction_id UUID;

-- Create indexes for performance
CREATE INDEX idx_customer_reminder_processing_transaction_id ON customer.customer_reminder_processing(transaction_id);
CREATE INDEX idx_customer_reminder_processing_status ON customer.customer_reminder_processing(status);
CREATE INDEX idx_customer_reminder_request_transaction_id ON customer.customer_reminder_request(transaction_id);

-- Add comments for clarity
COMMENT ON TABLE customer.customer_reminder_processing IS 'Tracks progress and status of bulk customer reminder processing operations';
COMMENT ON COLUMN customer.customer_reminder_processing.transaction_id IS 'Unique identifier for bulk processing transaction';
COMMENT ON COLUMN customer.customer_reminder_processing.progress IS 'Processing progress percentage (0-100)';
COMMENT ON COLUMN customer.customer_reminder_processing.status IS 'Processing status: inprogress or completed';
COMMENT ON COLUMN customer.customer_reminder_request.transaction_id IS 'Links reminder request to bulk processing transaction';