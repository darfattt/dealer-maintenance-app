-- Migration: Create WhatsApp template audit logging table
-- This migration creates the whatsapp_template_logs table for tracking all
-- template operations including create, update, delete, and copy operations

-- Create the whatsapp_template_logs table
CREATE TABLE IF NOT EXISTS customer.whatsapp_template_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template reference (nullable for delete operations where template no longer exists)
    template_id UUID,

    -- Operation type
    operation VARCHAR(20) NOT NULL,  -- CREATE, UPDATE, DELETE, COPY

    -- Template data tracking (JSONB for flexibility)
    old_data JSONB,  -- Previous template data (for UPDATE/DELETE operations)
    new_data JSONB,  -- New template data (for CREATE/UPDATE operations)

    -- Operation context
    dealer_id VARCHAR(50),          -- Primary dealer involved in operation
    user_email VARCHAR(255) NOT NULL,  -- User who performed the operation

    -- Copy operation specific fields
    source_dealer_id VARCHAR(50),   -- Source dealer ID for copy operations
    target_dealer_id VARCHAR(50),   -- Target dealer ID for copy operations

    -- Metadata
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(45),          -- Client IP address (IPv4/IPv6)
    user_agent TEXT,                -- Browser/client user agent
    operation_notes TEXT,           -- Optional notes about the operation

    -- Audit timestamps
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_template_id
ON customer.whatsapp_template_logs (template_id);

CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_operation
ON customer.whatsapp_template_logs (operation);

CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_dealer_id
ON customer.whatsapp_template_logs (dealer_id);

CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_user_email
ON customer.whatsapp_template_logs (user_email);

CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_timestamp
ON customer.whatsapp_template_logs (operation_timestamp);

-- Create composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_dealer_operation
ON customer.whatsapp_template_logs (dealer_id, operation, operation_timestamp);

-- Create index for copy operations
CREATE INDEX IF NOT EXISTS idx_whatsapp_template_logs_copy_operations
ON customer.whatsapp_template_logs (source_dealer_id, target_dealer_id, operation)
WHERE operation = 'COPY';

-- Add comments for documentation
COMMENT ON TABLE customer.whatsapp_template_logs IS 'Audit log for all WhatsApp template operations including CRUD and copy operations';
COMMENT ON COLUMN customer.whatsapp_template_logs.operation IS 'Type of operation: CREATE, UPDATE, DELETE, COPY';
COMMENT ON COLUMN customer.whatsapp_template_logs.old_data IS 'Previous template data as JSON (for UPDATE/DELETE operations)';
COMMENT ON COLUMN customer.whatsapp_template_logs.new_data IS 'New template data as JSON (for CREATE/UPDATE operations)';
COMMENT ON COLUMN customer.whatsapp_template_logs.source_dealer_id IS 'Source dealer ID for template copy operations';
COMMENT ON COLUMN customer.whatsapp_template_logs.target_dealer_id IS 'Target dealer ID for template copy operations';
COMMENT ON COLUMN customer.whatsapp_template_logs.operation_notes IS 'Optional notes describing the operation context or reason';