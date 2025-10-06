-- Migration: Add SYSTEM_ADMIN role and create default system admin user
-- Version: 021
-- Date: 2025-10-06
-- Description: Updates userrole enum to include SYSTEM_ADMIN and creates default system administrator account

-- Enable pgcrypto extension for password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create account schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS account;

-- ============================================================================
-- PART 1: Update UserRole Enum to Add SYSTEM_ADMIN
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 021: Add SYSTEM_ADMIN role and user';
    RAISE NOTICE '================================================';

    -- Check if SYSTEM_ADMIN already exists in the enum
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'userrole' AND e.enumlabel = 'SYSTEM_ADMIN'
    ) THEN
        -- SYSTEM_ADMIN doesn't exist, need to update the enum
        RAISE NOTICE 'Updating userrole enum to add SYSTEM_ADMIN...';

        -- Step 1: Rename old enum
        ALTER TYPE userrole RENAME TO userrole_old;

        -- Step 2: Create new enum with SYSTEM_ADMIN as highest level
        CREATE TYPE userrole AS ENUM ('SYSTEM_ADMIN', 'SUPER_ADMIN', 'DEALER_ADMIN', 'DEALER_USER');

        -- Step 3: Update column to use new enum (cast through text)
        ALTER TABLE account.users ALTER COLUMN role TYPE userrole USING role::text::userrole;

        -- Step 4: Drop old enum
        DROP TYPE userrole_old;

        RAISE NOTICE '✓ SYSTEM_ADMIN role added to userrole enum';
    ELSE
        RAISE NOTICE '✓ SYSTEM_ADMIN role already exists in userrole enum';
    END IF;
END $$;

-- ============================================================================
-- PART 2: Create Default SYSTEM_ADMIN User
-- ============================================================================

DO $$
DECLARE
    user_exists BOOLEAN;
    new_user_id UUID;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Creating default SYSTEM_ADMIN user...';

    -- Check if user already exists
    SELECT EXISTS (
        SELECT 1 FROM account.users
        WHERE email = 'system.admin@autology.id'
    ) INTO user_exists;

    IF NOT user_exists THEN
        -- Generate UUID for the user
        new_user_id := uuid_generate_v4();

        -- Insert system admin user
        -- Password: admin123 (hashed with bcrypt)
        -- IMPORTANT: This password should be changed immediately after first login!
        INSERT INTO account.users (
            id,
            email,
            username,
            full_name,
            hashed_password,
            is_active,
            is_verified,
            role,
            dealer_id,
            created_at,
            updated_at,
            last_login_at,
            password_reset_token,
            password_reset_expires,
            email_verification_token,
            email_verification_expires
        ) VALUES (
            new_user_id,
            'system.admin@autology.id',
            'system.admin',
            'System Administrator',
            -- Bcrypt hash for 'admin123' - CHANGE THIS PASSWORD IMMEDIATELY!
            crypt('admin123', gen_salt('bf')),
            true,
            true,
            'SYSTEM_ADMIN'::userrole,
            NULL,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL
        );

        RAISE NOTICE '✓ System admin user created successfully';
        RAISE NOTICE '  - ID: %', new_user_id;
        RAISE NOTICE '  - Email: system.admin@autology.id';
        RAISE NOTICE '  - Username: system.admin';
        RAISE NOTICE '  - Role: SYSTEM_ADMIN';
    ELSE
        RAISE NOTICE '✓ System admin user already exists';
    END IF;
END $$;

-- ============================================================================
-- PART 3: Verification
-- ============================================================================

DO $$
DECLARE
    user_count INTEGER;
    system_admin_count INTEGER;
    enum_has_system_admin BOOLEAN;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'Verification Results:';
    RAISE NOTICE '================================================';

    -- Count total users
    SELECT COUNT(*) INTO user_count FROM account.users;
    RAISE NOTICE '✓ Total users in system: %', user_count;

    -- Count SYSTEM_ADMIN users
    SELECT COUNT(*) INTO system_admin_count
    FROM account.users
    WHERE role = 'SYSTEM_ADMIN'::userrole;
    RAISE NOTICE '✓ SYSTEM_ADMIN users: %', system_admin_count;

    -- Verify enum has SYSTEM_ADMIN
    SELECT EXISTS (
        SELECT 1 FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'userrole' AND e.enumlabel = 'SYSTEM_ADMIN'
    ) INTO enum_has_system_admin;

    IF enum_has_system_admin THEN
        RAISE NOTICE '✓ userrole enum contains SYSTEM_ADMIN';
    ELSE
        RAISE WARNING '✗ userrole enum does not contain SYSTEM_ADMIN';
    END IF;

    -- Verify system admin user
    IF EXISTS (
        SELECT 1 FROM account.users
        WHERE email = 'system.admin@autology.id'
        AND role = 'SYSTEM_ADMIN'::userrole
        AND is_active = true
    ) THEN
        RAISE NOTICE '✓ System admin user (system.admin@autology.id) is active';
    ELSE
        RAISE WARNING '✗ System admin user not found or not active';
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Migration 021 completed successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'SECURITY NOTICE:';
    RAISE NOTICE '⚠️  Default credentials created:';
    RAISE NOTICE '   Email: system.admin@autology.id';
    RAISE NOTICE '   Password: admin123';
    RAISE NOTICE '   ';
    RAISE NOTICE '   🔒 CHANGE THIS PASSWORD IMMEDIATELY!';
    RAISE NOTICE '   ';
    RAISE NOTICE '   Access the System Admin Portal at:';
    RAISE NOTICE '   http://localhost:5001 (production)';
    RAISE NOTICE '   http://localhost:5174 (development)';
    RAISE NOTICE '================================================';
END $$;
