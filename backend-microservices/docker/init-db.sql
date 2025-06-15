-- Initialize database for microservices
-- This script creates the necessary schemas and extensions

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create account schema for user management
CREATE SCHEMA IF NOT EXISTS account;

-- Create dealer_integration schema (for existing dealer dashboard data)
CREATE SCHEMA IF NOT EXISTS dealer_integration;

-- Set default search path
ALTER DATABASE dealer_dashboard SET search_path TO account, dealer_integration, public;

-- Grant permissions to dealer_user
GRANT ALL PRIVILEGES ON SCHEMA account TO dealer_user;
GRANT ALL PRIVILEGES ON SCHEMA dealer_integration TO dealer_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA account TO dealer_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dealer_integration TO dealer_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA account TO dealer_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dealer_integration TO dealer_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA account GRANT ALL ON TABLES TO dealer_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA account GRANT ALL ON SEQUENCES TO dealer_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dealer_integration GRANT ALL ON TABLES TO dealer_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dealer_integration GRANT ALL ON SEQUENCES TO dealer_user;

-- Create a simple health check function
CREATE OR REPLACE FUNCTION public.health_check()
RETURNS TEXT AS $$
BEGIN
    RETURN 'Database is healthy';
END;
$$ LANGUAGE plpgsql;
