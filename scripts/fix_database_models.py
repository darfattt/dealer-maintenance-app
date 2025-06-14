#!/usr/bin/env python3
"""
Fix Database Models Mismatch
Applies the updated database schema to match the SQLAlchemy models
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

def test_table_columns(cursor, table_name, expected_columns):
    """Test if table has expected columns"""
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
        actual_columns = [desc[0] for desc in cursor.description]
        
        missing_columns = []
        for col in expected_columns:
            if col not in actual_columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ Table {table_name} missing columns: {missing_columns}")
            return False
        else:
            print(f"✅ Table {table_name} has all expected columns")
            return True
            
    except Exception as e:
        print(f"❌ Error checking table {table_name}: {str(e)}")
        return False

def main():
    """Main fix function"""
    print("🔧 Database Models Mismatch Fix")
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
        
        # Test key tables that were causing issues
        test_tables = {
            "pkb_data": ["waktu_pkb", "no_rangka", "no_mesin", "kode_tipe_unit"],
            "parts_inbound_data": ["tgl_penerimaan", "no_shipping_list"],
            "parts_inbound_po": ["jenis_order", "id_warehouse", "parts_number", "kuantitas", "uom"],
            "leasing_data": ["id_spk", "jumlah_dp", "tenor", "jumlah_cicilan"],
            "document_handling_data": ["id_spk"],
            "document_handling_units": ["nomor_faktur_stnk", "plat_nomor", "nomor_bpkb"],
            "unit_inbound_data": ["no_shipping_list", "tanggal_terima", "main_dealer_id", "no_invoice"],
            "delivery_process_data": ["delivery_document_id", "tanggal_pengiriman", "id_driver"],
            "billing_process_data": ["id_invoice", "id_spk", "id_customer", "amount"],
            "parts_sales_data": ["no_so", "tgl_so", "id_customer", "disc_so", "total_harga_so"],
            "dp_hlo_data": ["no_invoice_uang_jaminan", "id_hlo_document", "no_work_order"],
            "workshop_invoice_data": ["no_work_order", "no_njb", "no_nsc", "honda_id_sa"]
        }
        
        print("\n🔍 Testing table structures...")
        all_passed = True
        
        for table_name, expected_columns in test_tables.items():
            if not test_table_columns(cursor, table_name, expected_columns):
                all_passed = False
        
        if all_passed:
            print("\n🎉 All table structures match the models!")
            print("💡 You can now restart your dashboard:")
            print("   streamlit run dashboard_analytics/dashboard_analytics.py --server.port 8501")
            return 0
        else:
            print("\n⚠️  Some tables need to be updated")
            print("💡 To fix this, run:")
            print("   docker-compose down -v")
            print("   docker-compose up -d")
            print("   # Wait 60 seconds for database initialization")
            print("   python scripts/verify_database.py")
            return 1
        
    except Exception as e:
        print(f"❌ Fix failed: {str(e)}")
        print("\n💡 Troubleshooting steps:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check DATABASE_URL environment variable")
        print("3. Run: docker-compose down -v && docker-compose up -d")
        return 1
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
