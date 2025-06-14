#!/usr/bin/env python3
"""
Database Structure Verification Script
Verifies that the database has the latest structure and sample data
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get database connection from environment variables"""
    database_url = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")
    
    # Parse the database URL
    if database_url.startswith("postgresql://"):
        # Remove postgresql:// prefix
        url_parts = database_url[13:].split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        host_port = host_db[0].split(":")
        
        return {
            "host": host_port[0],
            "port": int(host_port[1]) if len(host_port) > 1 else 5432,
            "database": host_db[1],
            "user": user_pass[0],
            "password": user_pass[1]
        }
    else:
        raise ValueError("Invalid DATABASE_URL format")

def check_table_structure(cursor, table_name, expected_columns):
    """Check if table has expected columns"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        AND table_schema = 'dealer_integration'
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cursor.fetchall()
    
    print(f"\n📋 Table: {table_name}")
    print("-" * 50)
    
    if not columns:
        print("❌ Table not found!")
        return False
    
    # Check for expected columns
    found_columns = {col['column_name'] for col in columns}
    missing_columns = set(expected_columns) - found_columns
    extra_columns = found_columns - set(expected_columns)
    
    if missing_columns:
        print(f"❌ Missing columns: {', '.join(missing_columns)}")
    
    if extra_columns:
        print(f"ℹ️  Extra columns: {', '.join(extra_columns)}")
    
    # Display all columns
    for col in columns:
        status = "✅" if col['column_name'] in expected_columns else "ℹ️"
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
        print(f"{status} {col['column_name']}: {col['data_type']} {nullable}{default}")
    
    return len(missing_columns) == 0

def check_sample_data(cursor):
    """Check if sample dealer data exists"""
    print(f"\n👥 Sample Dealer Data")
    print("-" * 50)
    
    # Check for sample dealer
    cursor.execute("SELECT * FROM dealers WHERE dealer_id = %s", ('12284',))
    sample_dealer = cursor.fetchone()
    
    if sample_dealer:
        print("✅ Sample dealer (12284) found:")
        print(f"   - ID: {sample_dealer['id']}")
        print(f"   - Name: {sample_dealer['dealer_name']}")
        print(f"   - API Key: {sample_dealer['api_key']}")
        print(f"   - Secret Key: {sample_dealer['secret_key']}")
        print(f"   - Active: {sample_dealer['is_active']}")
    else:
        print("❌ Sample dealer (12284) not found!")
        return False
    
    # Check for default dealer
    cursor.execute("SELECT * FROM dealers WHERE dealer_id = %s", ('00999',))
    default_dealer = cursor.fetchone()
    
    if default_dealer:
        print("✅ Default dealer (00999) found:")
        print(f"   - Name: {default_dealer['dealer_name']}")
        print(f"   - Secret Key: {default_dealer['secret_key']}")
    else:
        print("❌ Default dealer (00999) not found!")
        return False
    
    return True

def check_migration_tracking(cursor):
    """Check migration tracking table"""
    print(f"\n🔄 Migration Tracking")
    print("-" * 50)
    
    # Check if migration table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'schema_migrations'
            AND table_schema = 'dealer_integration'
        )
    """)
    
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("✅ Migration tracking table exists")
        
        # Get applied migrations
        cursor.execute("SELECT migration_name, applied_at FROM schema_migrations ORDER BY applied_at")
        migrations = cursor.fetchall()
        
        if migrations:
            print("📋 Applied migrations:")
            for migration in migrations:
                print(f"   - {migration['migration_name']} ({migration['applied_at']})")
        else:
            print("ℹ️  No migrations recorded (fresh installation)")
    else:
        print("ℹ️  Migration tracking table not found (fresh installation)")
    
    return True

def main():
    """Main verification function"""
    print("🔍 Database Structure Verification")
    print("=" * 60)
    
    # Expected dealers table structure
    expected_dealers_columns = {
        'id', 'dealer_id', 'dealer_name', 'api_key', 'api_token', 
        'secret_key', 'is_active', 'created_at', 'updated_at'
    }
    
    try:
        # Connect to database
        db_config = get_database_connection()
        print(f"🔗 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        # Set search path to use dealer_integration schema
        cursor.execute("SET search_path TO dealer_integration, public")
        
        # Run checks
        checks_passed = 0
        total_checks = 3
        
        # Check dealers table structure
        if check_table_structure(cursor, 'dealers', expected_dealers_columns):
            checks_passed += 1
        
        # Check sample data
        if check_sample_data(cursor):
            checks_passed += 1
        
        # Check migration tracking
        if check_migration_tracking(cursor):
            checks_passed += 1
        
        # Summary
        print(f"\n📊 Verification Summary")
        print("=" * 60)
        print(f"Checks passed: {checks_passed}/{total_checks}")
        
        if checks_passed == total_checks:
            print("🎉 All checks passed! Database is ready.")
            return 0
        else:
            print("⚠️  Some checks failed. Please review the issues above.")
            print("\n💡 Suggested actions:")
            print("   1. Run database migrations: python scripts/run_migrations.py")
            print("   2. Check database connection and permissions")
            print("   3. Verify init.sql was applied correctly")
            return 1
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return 1
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
