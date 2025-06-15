#!/usr/bin/env python3
"""
Fix Unpaid HLO Tables Schema
Updates the unpaid_hlo_data and unpaid_hlo_parts tables to match the SQLAlchemy models
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
    print("🔧 Unpaid HLO Tables Schema Fix")
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
        
        print("🔍 Checking unpaid HLO tables...")
        
        # Check unpaid_hlo_data table
        print("\n📋 Unpaid HLO Data Table:")
        data_columns = check_table_columns(cursor, 'unpaid_hlo_data')
        data_column_names = [col[0] for col in data_columns]
        
        expected_data_columns = [
            'id', 'dealer_id', 'id_hlo_document', 'tanggal_pemesanan_hlo', 
            'no_work_order', 'no_buku_claim_c2', 'no_ktp', 'nama_customer', 
            'alamat', 'kode_propinsi', 'kode_kota', 'kode_kecamatan', 
            'kode_kelurahan', 'kode_pos', 'no_kontak', 'kode_tipe_unit', 
            'tahun_motor', 'no_mesin', 'no_rangka', 'flag_numbering', 
            'vehicle_off_road', 'job_return', 'created_time', 'modified_time', 'fetched_at'
        ]
        
        missing_data = [col for col in expected_data_columns if col not in data_column_names]
        extra_data = [col for col in data_column_names if col not in expected_data_columns]
        
        if missing_data:
            print(f"❌ Missing columns in data table: {missing_data}")
        if extra_data:
            print(f"⚠️  Extra columns in data table: {extra_data}")
        if not missing_data and not extra_data:
            print("✅ Data table structure is correct")
        
        # Check unpaid_hlo_parts table
        print("\n📋 Unpaid HLO Parts Table:")
        parts_columns = check_table_columns(cursor, 'unpaid_hlo_parts')
        parts_column_names = [col[0] for col in parts_columns]
        
        expected_parts_columns = [
            'id', 'unpaid_hlo_data_id', 'parts_number', 'kuantitas', 
            'harga_parts', 'total_harga_parts', 'uang_muka', 'sisa_bayar',
            'created_time', 'modified_time'
        ]
        
        missing_parts = [col for col in expected_parts_columns if col not in parts_column_names]
        extra_parts = [col for col in parts_column_names if col not in expected_parts_columns]
        
        if missing_parts:
            print(f"❌ Missing columns in parts table: {missing_parts}")
        if extra_parts:
            print(f"⚠️  Extra columns in parts table: {extra_parts}")
        if not missing_parts and not extra_parts:
            print("✅ Parts table structure is correct")
        
        # If both tables are correct, we're done
        if not missing_data and not extra_data and not missing_parts and not extra_parts:
            print("\n🎉 All unpaid HLO tables are correctly structured!")
            return 0
        
        # Check existing data
        cursor.execute("SELECT COUNT(*) FROM unpaid_hlo_data")
        data_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM unpaid_hlo_parts")
        parts_count = cursor.fetchone()[0]
        
        if data_count > 0 or parts_count > 0:
            print(f"\n⚠️  Found {data_count} data records and {parts_count} parts records. They will be lost!")
            response = input("Continue with table fixes? (y/N): ")
            if response.lower() != 'y':
                print("❌ Table fixes cancelled")
                return 1
        
        # Fix tables if needed
        if missing_data or extra_data:
            print("\n🔄 Fixing unpaid_hlo_data table...")
            
            # Drop and recreate data table
            print("🗑️  Dropping old unpaid_hlo_data table...")
            cursor.execute("DROP TABLE IF EXISTS unpaid_hlo_parts CASCADE")
            cursor.execute("DROP TABLE IF EXISTS unpaid_hlo_data CASCADE")
            
            print("🏗️  Creating new unpaid_hlo_data table...")
            cursor.execute("""
                CREATE TABLE unpaid_hlo_data (
                    id UUID NOT NULL DEFAULT uuid_generate_v4(),
                    dealer_id VARCHAR(10) NOT NULL,
                    id_hlo_document VARCHAR(100) NULL,
                    tanggal_pemesanan_hlo VARCHAR(50) NULL,
                    no_work_order VARCHAR(100) NULL,
                    no_buku_claim_c2 VARCHAR(100) NULL,
                    no_ktp VARCHAR(100) NULL,
                    nama_customer VARCHAR(200) NULL,
                    alamat TEXT NULL,
                    kode_propinsi VARCHAR(10) NULL,
                    kode_kota VARCHAR(10) NULL,
                    kode_kecamatan VARCHAR(20) NULL,
                    kode_kelurahan VARCHAR(20) NULL,
                    kode_pos VARCHAR(10) NULL,
                    no_kontak VARCHAR(50) NULL,
                    kode_tipe_unit VARCHAR(50) NULL,
                    tahun_motor VARCHAR(10) NULL,
                    no_mesin VARCHAR(100) NULL,
                    no_rangka VARCHAR(100) NULL,
                    flag_numbering VARCHAR(10) NULL,
                    vehicle_off_road VARCHAR(10) NULL,
                    job_return VARCHAR(10) NULL,
                    created_time VARCHAR(50) NULL,
                    modified_time VARCHAR(50) NULL,
                    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unpaid_hlo_data_pkey PRIMARY KEY (id),
                    CONSTRAINT unpaid_hlo_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
                )
            """)
            
            print("🏗️  Creating new unpaid_hlo_parts table...")
            cursor.execute("""
                CREATE TABLE unpaid_hlo_parts (
                    id UUID NOT NULL DEFAULT uuid_generate_v4(),
                    unpaid_hlo_data_id UUID NOT NULL,
                    parts_number VARCHAR(100) NULL,
                    kuantitas INTEGER NULL,
                    harga_parts NUMERIC(15,2) NULL,
                    total_harga_parts NUMERIC(15,2) NULL,
                    uang_muka NUMERIC(15,2) NULL,
                    sisa_bayar NUMERIC(15,2) NULL,
                    created_time VARCHAR(50) NULL,
                    modified_time VARCHAR(50) NULL,
                    CONSTRAINT unpaid_hlo_parts_pkey PRIMARY KEY (id),
                    CONSTRAINT unpaid_hlo_parts_unpaid_hlo_data_id_fkey 
                        FOREIGN KEY (unpaid_hlo_data_id) REFERENCES unpaid_hlo_data(id) ON DELETE CASCADE
                )
            """)
            
            print("📊 Creating indexes...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_dealer_id ON unpaid_hlo_data(dealer_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_id_hlo_document ON unpaid_hlo_data(id_hlo_document)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_no_work_order ON unpaid_hlo_data(no_work_order)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_no_ktp ON unpaid_hlo_data(no_ktp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_no_mesin ON unpaid_hlo_data(no_mesin)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_no_rangka ON unpaid_hlo_data(no_rangka)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_parts_unpaid_hlo_data_id ON unpaid_hlo_parts(unpaid_hlo_data_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_parts_parts_number ON unpaid_hlo_parts(parts_number)")
            
            print("✅ Unpaid HLO tables recreated successfully!")
        
        # Verify final structure
        print("\n🔍 Verifying final table structures...")
        
        # Verify data table
        final_data_columns = check_table_columns(cursor, 'unpaid_hlo_data')
        print(f"📋 Unpaid HLO Data table: {len(final_data_columns)} columns")
        for col_name, col_type in final_data_columns[:10]:  # Show first 10 columns
            print(f"   ✅ {col_name}: {col_type}")
        if len(final_data_columns) > 10:
            print(f"   ... and {len(final_data_columns) - 10} more columns")
        
        # Verify parts table
        final_parts_columns = check_table_columns(cursor, 'unpaid_hlo_parts')
        print(f"\n📋 Unpaid HLO Parts table: {len(final_parts_columns)} columns")
        for col_name, col_type in final_parts_columns:
            print(f"   ✅ {col_name}: {col_type}")
        
        print("\n🎉 Unpaid HLO tables fix completed!")
        print("💡 You can now view unpaid HLO data in the dashboard without errors")
        
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
