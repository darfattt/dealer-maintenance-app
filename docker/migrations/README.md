# Database Migrations

This directory contains database migration scripts to update existing installations with the latest schema changes.

## Overview

The migration system helps you update your database schema when upgrading to newer versions of the dealer dashboard application. Each migration file contains SQL commands to modify the database structure and data.

## Migration Files

### 001_add_secret_key_and_sample_dealer.sql
- **Purpose**: Adds `secret_key` column to dealers table and inserts sample dealer data
- **Changes**:
  - Adds `secret_key VARCHAR(255) NULL` column to `dealers` table
  - Updates existing dealers with default secret keys
  - Inserts sample dealer (ID: 12284, UUID: e3a18c82-c500-450f-b6e1-5c5fbe68bf41)
  - Provides verification and status messages

## Running Migrations

### Method 1: Using Python Migration Runner (Recommended)

```bash
# From project root directory
python scripts/run_migrations.py
```

**Features:**
- ✅ Automatic migration tracking
- ✅ Prevents duplicate migrations
- ✅ Detailed progress reporting
- ✅ Error handling and rollback
- ✅ Environment variable support

### Method 2: Manual SQL Execution

```bash
# Connect to your PostgreSQL database
psql -h localhost -U dealer_user -d dealer_dashboard

# Run migration manually
\i docker/migrations/001_add_secret_key_and_sample_dealer.sql
```

## Environment Variables

The migration runner uses these environment variables:

```bash
DATABASE_URL=postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard
```

Or individual variables:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealer_dashboard
DB_USER=dealer_user
DB_PASSWORD=dealer_pass
```

## Migration Tracking

The system automatically creates a `schema_migrations` table to track applied migrations:

```sql
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## New Installation vs. Existing Installation

### New Installation
- Use the updated `docker/init.sql` file
- All latest schema changes are included
- Sample data is automatically inserted
- No migrations needed

### Existing Installation
- Run migrations to update schema
- Preserves existing data
- Adds new features and sample data
- Safe and reversible process

## Verification

After running migrations, verify the changes:

```sql
-- Check dealers table structure
\d dealers

-- Verify sample dealer exists
SELECT dealer_id, dealer_name, secret_key FROM dealers WHERE dealer_id = '12284';

-- Check migration history
SELECT * FROM schema_migrations ORDER BY applied_at;
```

## Expected Results

After successful migration:

1. **Dealers Table Updated**:
   - `secret_key` column added
   - Existing dealers have default secret keys
   - New sample dealer (12284) inserted

2. **Sample Data Available**:
   - Dealer ID: `12284`
   - UUID: `e3a18c82-c500-450f-b6e1-5c5fbe68bf41`
   - Name: `Sample Dealer`
   - API credentials configured

3. **Migration Tracking**:
   - `schema_migrations` table created
   - Migration history recorded

## Troubleshooting

### Common Issues

1. **Connection Failed**
   ```
   ❌ Failed to connect to database
   ```
   - Check DATABASE_URL environment variable
   - Verify PostgreSQL is running
   - Confirm credentials are correct

2. **Permission Denied**
   ```
   ❌ Permission denied for table dealers
   ```
   - Ensure database user has ALTER TABLE privileges
   - Run as database superuser if needed

3. **Migration Already Applied**
   ```
   ✅ All migrations are up to date!
   ```
   - This is normal - migrations are tracked automatically
   - No action needed

### Manual Verification

```sql
-- Check if secret_key column exists
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'dealers' AND column_name = 'secret_key';

-- Check sample dealer
SELECT * FROM dealers WHERE dealer_id = '12284';

-- View migration history
SELECT migration_name, applied_at FROM schema_migrations;
```

## Support

If you encounter issues:

1. Check the migration logs for specific error messages
2. Verify database connectivity and permissions
3. Ensure PostgreSQL version compatibility (15+)
4. Review the migration SQL files for any conflicts

For additional help, refer to the main project documentation or create an issue in the project repository.
