-- Migration: Create login audit table
-- Version: 022
-- Date: 2025-10-08
-- Description: Creates login_audit table to track user login/logout activities and failed attempts

-- Create account schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS account;

-- ============================================================================
-- PART 1: Create AuditAction Enum
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 022: Create login audit table';
    RAISE NOTICE '================================================';

    -- Check if auditaction enum already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'auditaction'
    ) THEN
        RAISE NOTICE 'Creating auditaction enum...';

        -- Create enum for audit actions
        CREATE TYPE auditaction AS ENUM ('LOGIN', 'LOGOUT', 'LOGIN_FAILED');

        RAISE NOTICE '✓ auditaction enum created';
    ELSE
        RAISE NOTICE '✓ auditaction enum already exists';
    END IF;
END $$;

-- ============================================================================
-- PART 2: Create login_audit Table
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Creating login_audit table...';

    -- Check if table already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'account'
        AND table_name = 'login_audit'
    ) THEN
        -- Create login_audit table
        CREATE TABLE account.login_audit (
            -- Primary key
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

            -- User reference (nullable for failed login attempts with unknown user)
            user_id UUID REFERENCES account.users(id) ON DELETE SET NULL,

            -- Audit information
            action auditaction NOT NULL,
            email VARCHAR(255) NOT NULL,  -- Store email for failed attempts

            -- Request metadata
            ip_address VARCHAR(45),  -- IPv4: 15 chars, IPv6: 45 chars
            user_agent TEXT,

            -- Result
            success BOOLEAN NOT NULL DEFAULT false,
            failure_reason TEXT,  -- Store reason for failed attempts

            -- Timestamp
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        RAISE NOTICE '✓ login_audit table created';
    ELSE
        RAISE NOTICE '✓ login_audit table already exists';
    END IF;
END $$;

-- ============================================================================
-- PART 3: Create Indexes for Performance
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Creating indexes...';

    -- Index on id (primary key index already exists)
    -- Index on user_id for user-specific queries
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'account'
        AND tablename = 'login_audit'
        AND indexname = 'ix_login_audit_user_id'
    ) THEN
        CREATE INDEX ix_login_audit_user_id ON account.login_audit(user_id);
        RAISE NOTICE '✓ Index ix_login_audit_user_id created';
    ELSE
        RAISE NOTICE '✓ Index ix_login_audit_user_id already exists';
    END IF;

    -- Index on email for tracking failed attempts
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'account'
        AND tablename = 'login_audit'
        AND indexname = 'ix_login_audit_email'
    ) THEN
        CREATE INDEX ix_login_audit_email ON account.login_audit(email);
        RAISE NOTICE '✓ Index ix_login_audit_email created';
    ELSE
        RAISE NOTICE '✓ Index ix_login_audit_email already exists';
    END IF;

    -- Index on action for filtering by action type
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'account'
        AND tablename = 'login_audit'
        AND indexname = 'ix_login_audit_action'
    ) THEN
        CREATE INDEX ix_login_audit_action ON account.login_audit(action);
        RAISE NOTICE '✓ Index ix_login_audit_action created';
    ELSE
        RAISE NOTICE '✓ Index ix_login_audit_action already exists';
    END IF;

    -- Index on created_at for time-based queries
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'account'
        AND tablename = 'login_audit'
        AND indexname = 'ix_login_audit_created_at'
    ) THEN
        CREATE INDEX ix_login_audit_created_at ON account.login_audit(created_at DESC);
        RAISE NOTICE '✓ Index ix_login_audit_created_at created';
    ELSE
        RAISE NOTICE '✓ Index ix_login_audit_created_at already exists';
    END IF;

    -- Composite index for common queries (user + date range)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'account'
        AND tablename = 'login_audit'
        AND indexname = 'ix_login_audit_user_created'
    ) THEN
        CREATE INDEX ix_login_audit_user_created ON account.login_audit(user_id, created_at DESC);
        RAISE NOTICE '✓ Index ix_login_audit_user_created created';
    ELSE
        RAISE NOTICE '✓ Index ix_login_audit_user_created already exists';
    END IF;

    -- Index on IP address for security monitoring
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'account'
        AND tablename = 'login_audit'
        AND indexname = 'ix_login_audit_ip_address'
    ) THEN
        CREATE INDEX ix_login_audit_ip_address ON account.login_audit(ip_address);
        RAISE NOTICE '✓ Index ix_login_audit_ip_address created';
    ELSE
        RAISE NOTICE '✓ Index ix_login_audit_ip_address already exists';
    END IF;
END $$;

-- ============================================================================
-- PART 4: Add Comments for Documentation
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Adding table and column comments...';

    -- Table comment
    COMMENT ON TABLE account.login_audit IS 'Audit log for user login/logout activities and authentication attempts';

    -- Column comments
    COMMENT ON COLUMN account.login_audit.id IS 'Unique identifier for the audit log entry';
    COMMENT ON COLUMN account.login_audit.user_id IS 'Reference to the user (NULL for failed login attempts with unknown user)';
    COMMENT ON COLUMN account.login_audit.action IS 'Type of audit action: LOGIN, LOGOUT, or LOGIN_FAILED';
    COMMENT ON COLUMN account.login_audit.email IS 'Email address used in the login attempt';
    COMMENT ON COLUMN account.login_audit.ip_address IS 'IP address of the client making the request';
    COMMENT ON COLUMN account.login_audit.user_agent IS 'User agent string from the client browser/application';
    COMMENT ON COLUMN account.login_audit.success IS 'Whether the action was successful';
    COMMENT ON COLUMN account.login_audit.failure_reason IS 'Reason for failure (e.g., invalid password, account disabled)';
    COMMENT ON COLUMN account.login_audit.created_at IS 'Timestamp when the audit log was created';

    RAISE NOTICE '✓ Comments added';
END $$;

-- ============================================================================
-- PART 5: Verification
-- ============================================================================

DO $$
DECLARE
    table_exists BOOLEAN;
    enum_exists BOOLEAN;
    index_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Verification Results:';
    RAISE NOTICE '================================================';

    -- Check table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'account'
        AND table_name = 'login_audit'
    ) INTO table_exists;

    IF table_exists THEN
        RAISE NOTICE '✓ login_audit table exists';
    ELSE
        RAISE WARNING '✗ login_audit table does not exist';
    END IF;

    -- Check enum exists
    SELECT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'auditaction'
    ) INTO enum_exists;

    IF enum_exists THEN
        RAISE NOTICE '✓ auditaction enum exists';
    ELSE
        RAISE WARNING '✗ auditaction enum does not exist';
    END IF;

    -- Count indexes
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'account'
    AND tablename = 'login_audit';

    RAISE NOTICE '✓ Number of indexes created: %', index_count;

    RAISE NOTICE '';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Migration 022 completed successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'The login_audit table is ready to track:';
    RAISE NOTICE '  - Successful login attempts';
    RAISE NOTICE '  - Failed login attempts';
    RAISE NOTICE '  - Logout events';
    RAISE NOTICE '  - IP addresses and user agents';
    RAISE NOTICE '================================================';
END $$;
