#!/usr/bin/env python3
"""
Fix Parts Invoice Table Schema
Updates the parts_invoice_parts table to match the SQLAlchemy model
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
    print("🔧 Parts Invoice Table Schema Fix")
    print("=" * 50)
    
    try:
        # Connect to database
        db_config = get_database_connection()
        print(f"🔗 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Set search path
        cursor.execute("SET search_path TO dealer_integration, public")
        
        print("🔍 Checking current table structure...")
        
        # Check current columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'parts_invoice_parts' 
            AND table_schema = 'dealer_integration'
            ORDER BY ordinal_position
        """)
        current_columns = cursor.fetchall()
        
        print("📋 Current columns:")
        for col_name, col_type in current_columns:
            print(f"   - {col_name}: {col_type}")
        
        # Expected columns from SQLAlchemy model
        expected_columns = [
            'id', 'parts_invoice_data_id', 'no_po', 'jenis_order', 
            'parts_number', 'kuantitas', 'uom', 'harga_satuan_sebelum_diskon',
            'diskon_per_parts_number', 'created_time', 'modified_time'
        ]
        
        current_column_names = [col[0] for col in current_columns]
        missing_columns = [col for col in expected_columns if col not in current_column_names]
        extra_columns = [col for col in current_column_names if col not in expected_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
        if extra_columns:
            print(f"⚠️  Extra columns: {extra_columns}")
        
        if not missing_columns and not extra_columns:
            print("✅ Table structure is correct!")
            return 0
        
        print("\n🔄 Recreating table with correct structure...")
        
        # Backup existing data if any
        cursor.execute("SELECT COUNT(*) FROM parts_invoice_parts")
        row_count = cursor.fetchone()[0]
        
        if row_count > 0:
            print(f"⚠️  Found {row_count} existing records. They will be lost!")
            response = input("Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled")
                return 1
        
        # Drop and recreate table
        print("🗑️  Dropping old table...")
        cursor.execute("DROP TABLE IF EXISTS parts_invoice_parts CASCADE")
        
        print("🏗️  Creating new table...")
        cursor.execute("""
            CREATE TABLE parts_invoice_parts (
                id UUID NOT NULL DEFAULT uuid_generate_v4(),
                parts_invoice_data_id UUID NOT NULL,
                no_po VARCHAR(100) NULL,
                jenis_order VARCHAR(10) NULL,
                parts_number VARCHAR(100) NULL,
                kuantitas INTEGER NULL,
                uom VARCHAR(20) NULL,
                harga_satuan_sebelum_diskon NUMERIC(15,2) NULL,
                diskon_per_parts_number NUMERIC(15,2) NULL,
                created_time VARCHAR(50) NULL,
                modified_time VARCHAR(50) NULL,
                CONSTRAINT parts_invoice_parts_pkey PRIMARY KEY (id),
                CONSTRAINT parts_invoice_parts_parts_invoice_data_id_fkey 
                    FOREIGN KEY (parts_invoice_data_id) 
                    REFERENCES parts_invoice_data(id) ON DELETE CASCADE
            )
        """)
        
        print("📊 Creating index...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parts_invoice_parts_parts_invoice_data_id 
            ON parts_invoice_parts(parts_invoice_data_id)
        """)
        
        print("✅ Table recreated successfully!")
        
        # Verify new structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'parts_invoice_parts' 
            AND table_schema = 'dealer_integration'
            ORDER BY ordinal_position
        """)
        new_columns = cursor.fetchall()
        
        print("\n📋 New table structure:")
        for col_name, col_type in new_columns:
            print(f"   ✅ {col_name}: {col_type}")
        
        print("\n🎉 Parts invoice table fix completed!")
        print("💡 You can now run parts invoice jobs without errors")
        
        return 0
        
    except Exception as e:
        print(f"❌ Fix failed: {str(e)}")
        return 1
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
