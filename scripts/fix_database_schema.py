#!/usr/bin/env python3
"""
Quick Database Schema Fix
Applies the dealer_integration schema and ensures tables are accessible
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

def main():
    """Main fix function"""
    print("🔧 Database Schema Quick Fix")
    print("=" * 40)
    
    try:
        # Connect to database
        db_config = get_database_connection()
        print(f"🔗 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if dealer_integration schema exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.schemata 
                WHERE schema_name = 'dealer_integration'
            )
        """)
        schema_exists = cursor.fetchone()[0]
        
        if not schema_exists:
            print("❌ dealer_integration schema does not exist")
            print("💡 You need to run the database initialization script:")
            print("   python scripts/setup_database_schema.py")
            print("   OR")
            print("   psql -U dealer_user -d dealer_dashboard -f docker/init.sql")
            return 1
        
        print("✅ dealer_integration schema exists")
        
        # Check if tables exist in the schema
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'dealer_integration'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found in dealer_integration schema")
            print("💡 You need to run the database initialization:")
            print("   docker-compose down -v")
            print("   docker-compose up -d")
            return 1
        
        print(f"✅ Found {len(tables)} tables in dealer_integration schema")
        
        # Set search path and test dealers table
        cursor.execute("SET search_path TO dealer_integration, public")
        
        try:
            cursor.execute("SELECT COUNT(*) FROM dealers")
            dealer_count = cursor.fetchone()[0]
            print(f"✅ Dealers table accessible: {dealer_count} dealers found")
            
            # Get sample dealers
            cursor.execute("SELECT dealer_id, dealer_name FROM dealers LIMIT 3")
            sample_dealers = cursor.fetchall()
            
            if sample_dealers:
                print("📋 Sample dealers:")
                for dealer_id, dealer_name in sample_dealers:
                    print(f"   - {dealer_id}: {dealer_name}")
            
        except Exception as e:
            print(f"❌ Error accessing dealers table: {str(e)}")
            return 1
        
        print("\n🎉 Database schema is properly configured!")
        print("💡 You can now restart your Streamlit dashboard:")
        print("   streamlit run dashboard_analytics.py --server.port 8501")
        
        return 0
        
    except Exception as e:
        print(f"❌ Fix failed: {str(e)}")
        print("\n💡 Troubleshooting steps:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify DATABASE_URL environment variable")
        print("3. Ensure database user has proper permissions")
        print("4. Run: docker-compose down -v && docker-compose up -d")
        return 1
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
