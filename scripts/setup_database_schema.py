#!/usr/bin/env python3
"""
Database Schema Setup Script
Ensures the dealer_integration schema exists and is properly configured
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
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

def check_schema_exists(cursor):
    """Check if dealer_integration schema exists"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.schemata 
            WHERE schema_name = 'dealer_integration'
        )
    """)
    return cursor.fetchone()[0]

def check_tables_exist(cursor):
    """Check if tables exist in dealer_integration schema"""
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'dealer_integration'
    """)
    return cursor.fetchone()[0]

def create_schema_if_needed(cursor):
    """Create dealer_integration schema if it doesn't exist"""
    if not check_schema_exists(cursor):
        print("📁 Creating dealer_integration schema...")
        cursor.execute("CREATE SCHEMA dealer_integration")
        print("✅ Schema created successfully")
    else:
        print("✅ dealer_integration schema already exists")

def set_search_path(cursor):
    """Set search path to use dealer_integration schema"""
    cursor.execute("SET search_path TO dealer_integration, public")
    print("✅ Search path set to dealer_integration, public")

def check_sample_data(cursor):
    """Check if sample dealers exist"""
    cursor.execute("SELECT COUNT(*) FROM dealers WHERE dealer_id IN ('00999', '12284')")
    return cursor.fetchone()[0]

def main():
    """Main setup function"""
    print("🔧 Database Schema Setup")
    print("=" * 50)
    
    try:
        # Connect to database
        db_config = get_database_connection()
        print(f"🔗 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check and create schema
        create_schema_if_needed(cursor)
        
        # Set search path
        set_search_path(cursor)
        
        # Check if tables exist
        table_count = check_tables_exist(cursor)
        print(f"📊 Found {table_count} tables in dealer_integration schema")
        
        if table_count == 0:
            print("⚠️  No tables found in dealer_integration schema")
            print("💡 You need to run the database initialization:")
            print("   docker-compose down -v")
            print("   docker-compose up -d")
            print("   OR")
            print("   psql -U dealer_user -d dealer_dashboard -f docker/init.sql")
            return 1
        
        # Check sample data
        sample_count = check_sample_data(cursor)
        print(f"👥 Found {sample_count} sample dealers")
        
        if sample_count == 0:
            print("⚠️  No sample dealers found")
            print("💡 Sample dealers may need to be inserted")
        
        # Test a simple query
        cursor.execute("SELECT dealer_id, dealer_name FROM dealers LIMIT 5")
        dealers = cursor.fetchall()
        
        if dealers:
            print("✅ Database connection test successful")
            print("📋 Available dealers:")
            for dealer_id, dealer_name in dealers:
                print(f"   - {dealer_id}: {dealer_name}")
        else:
            print("⚠️  No dealers found in database")
        
        print("\n🎉 Database schema setup completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return 1
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
