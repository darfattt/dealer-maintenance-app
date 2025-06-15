#!/usr/bin/env python3
"""
Fix Workshop Invoice Tables Schema
Updates the workshop_invoice_nsc table to match the SQLAlchemy model
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

def check_table_columns(cursor, table_name):
    """Check current columns in a table"""
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s 
        AND table_schema = 'dealer_integration'
        ORDER BY ordinal_position
    """, (table_name,))
    return cursor.fetchall()

def main():
    """Main fix function"""
    print("🔧 Workshop Invoice Tables Schema Fix")
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
        
        print("🔍 Checking workshop invoice tables...")
        
        # Check NJB table
        print("\n📋 Workshop Invoice NJB (Services) Table:")
        njb_columns = check_table_columns(cursor, 'workshop_invoice_njb')
        njb_column_names = [col[0] for col in njb_columns]
        
        expected_njb_columns = [
            'id', 'workshop_invoice_data_id', 'id_job', 'harga_servis', 
            'promo_id_jasa', 'disc_service_amount', 'disc_service_percentage',
            'total_harga_servis', 'created_time', 'modified_time'
        ]
        
        missing_njb = [col for col in expected_njb_columns if col not in njb_column_names]
        if missing_njb:
            print(f"❌ Missing columns in NJB: {missing_njb}")
        else:
            print("✅ NJB table structure is correct")
        
        # Check NSC table
        print("\n📋 Workshop Invoice NSC (Parts) Table:")
        nsc_columns = check_table_columns(cursor, 'workshop_invoice_nsc')
        nsc_column_names = [col[0] for col in nsc_columns]
        
        expected_nsc_columns = [
            'id', 'workshop_invoice_data_id', 'id_job', 'parts_number', 
            'kuantitas', 'harga_parts', 'promo_id_parts', 'disc_parts_amount',
            'disc_parts_percentage', 'ppn', 'total_harga_parts', 'uang_muka',
            'created_time', 'modified_time'
        ]
        
        missing_nsc = [col for col in expected_nsc_columns if col not in nsc_column_names]
        if missing_nsc:
            print(f"❌ Missing columns in NSC: {missing_nsc}")
        else:
            print("✅ NSC table structure is correct")
        
        # If both tables are correct, we're done
        if not missing_njb and not missing_nsc:
            print("\n🎉 All workshop invoice tables are correctly structured!")
            return 0
        
        # Fix NSC table if needed
        if missing_nsc:
            print(f"\n🔄 Fixing NSC table (missing: {missing_nsc})...")
            
            # Check if there's existing data
            cursor.execute("SELECT COUNT(*) FROM workshop_invoice_nsc")
            nsc_count = cursor.fetchone()[0]
            
            if nsc_count > 0:
                print(f"⚠️  Found {nsc_count} existing NSC records. They will be lost!")
                response = input("Continue with NSC table fix? (y/N): ")
                if response.lower() != 'y':
                    print("❌ NSC table fix cancelled")
                    return 1
            
            # Recreate NSC table
            print("🗑️  Dropping old NSC table...")
            cursor.execute("DROP TABLE IF EXISTS workshop_invoice_nsc CASCADE")
            
            print("🏗️  Creating new NSC table...")
            cursor.execute("""
                CREATE TABLE workshop_invoice_nsc (
                    id UUID NOT NULL DEFAULT uuid_generate_v4(),
                    workshop_invoice_data_id UUID NOT NULL,
                    id_job VARCHAR(100) NULL,
                    parts_number VARCHAR(100) NULL,
                    kuantitas INTEGER NULL,
                    harga_parts NUMERIC(15,2) NULL,
                    promo_id_parts VARCHAR(100) NULL,
                    disc_parts_amount NUMERIC(15,2) NULL,
                    disc_parts_percentage VARCHAR(20) NULL,
                    ppn NUMERIC(15,2) NULL,
                    total_harga_parts NUMERIC(15,2) NULL,
                    uang_muka NUMERIC(15,2) NULL,
                    created_time VARCHAR(50) NULL,
                    modified_time VARCHAR(50) NULL,
                    CONSTRAINT workshop_invoice_nsc_pkey PRIMARY KEY (id),
                    CONSTRAINT workshop_invoice_nsc_workshop_invoice_data_id_fkey 
                        FOREIGN KEY (workshop_invoice_data_id) 
                        REFERENCES workshop_invoice_data(id) ON DELETE CASCADE
                )
            """)
            
            print("📊 Creating NSC indexes...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workshop_invoice_nsc_workshop_invoice_data_id 
                ON workshop_invoice_nsc(workshop_invoice_data_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workshop_invoice_nsc_id_job 
                ON workshop_invoice_nsc(id_job)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workshop_invoice_nsc_parts_number 
                ON workshop_invoice_nsc(parts_number)
            """)
            
            print("✅ NSC table recreated successfully!")
        
        # Verify final structure
        print("\n🔍 Verifying final table structures...")
        
        # Verify NJB
        final_njb_columns = check_table_columns(cursor, 'workshop_invoice_njb')
        print(f"📋 NJB table: {len(final_njb_columns)} columns")
        for col_name, col_type in final_njb_columns:
            print(f"   ✅ {col_name}: {col_type}")
        
        # Verify NSC
        final_nsc_columns = check_table_columns(cursor, 'workshop_invoice_nsc')
        print(f"\n📋 NSC table: {len(final_nsc_columns)} columns")
        for col_name, col_type in final_nsc_columns:
            print(f"   ✅ {col_name}: {col_type}")
        
        print("\n🎉 Workshop invoice tables fix completed!")
        print("💡 You can now run workshop invoice jobs without errors")
        
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
