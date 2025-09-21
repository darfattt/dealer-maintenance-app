-- Migration: Create API request logging table
-- This migration creates the api_request_log table for tracking API requests and responses
-- for audit, debugging, and performance monitoring purposes

-- Create the api_request_log table
CREATE TABLE IF NOT EXISTS customer.api_request_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Request identification
    request_name VARCHAR(100) NOT NULL,          -- e.g., 'add_bulk_reminders', 'validate_customer'
    dealer_id VARCHAR(50),                       -- Dealer ID from request
    request_method VARCHAR(10) NOT NULL,         -- HTTP method: GET, POST, etc.
    endpoint VARCHAR(200) NOT NULL,              -- API endpoint path

    -- Request data
    request_payload JSONB,                       -- Full request body as JSON
    request_headers JSONB,                       -- Important request headers
    request_ip VARCHAR(45),                      -- Client IP address (IPv4/IPv6)
    user_email VARCHAR(255),                     -- User email from JWT token

    -- Response data
    response_status VARCHAR(20),                 -- 'success', 'error', 'partial_success'
    response_code INTEGER,                       -- HTTP status code
    response_data JSONB,                         -- Response payload (optional, for important responses)
    error_message TEXT,                          -- Error details if any

    -- Performance metrics
    processing_time_ms INTEGER,                  -- Request processing duration in milliseconds

    -- Timestamps
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_timestamp TIMESTAMP,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_api_request_log_dealer
ON customer.api_request_log (dealer_id);

CREATE INDEX IF NOT EXISTS idx_api_request_log_request_name
ON customer.api_request_log (request_name);

CREATE INDEX IF NOT EXISTS idx_api_request_log_timestamp
ON customer.api_request_log (request_timestamp);

CREATE INDEX IF NOT EXISTS idx_api_request_log_status
ON customer.api_request_log (response_status);

CREATE INDEX IF NOT EXISTS idx_api_request_log_user
ON customer.api_request_log (user_email);

-- Create composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_api_request_log_dealer_date
ON customer.api_request_log (dealer_id, request_timestamp);

-- Add comments for documentation
COMMENT ON TABLE customer.api_request_log IS 'Stores API request logs for audit, debugging, and performance monitoring';
COMMENT ON COLUMN customer.api_request_log.request_name IS 'Identifies the type of API request for categorization';
COMMENT ON COLUMN customer.api_request_log.request_payload IS 'JSON payload of the request (may be limited for large payloads)';
COMMENT ON COLUMN customer.api_request_log.processing_time_ms IS 'Total processing time in milliseconds for performance monitoring';
COMMENT ON COLUMN customer.api_request_log.response_status IS 'High-level status: success, error, or partial_success';