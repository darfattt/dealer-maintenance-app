#!/usr/bin/env python3
"""
Direct database check for dealer 12284 and document handling data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection"""
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
    """Main function to check database"""
    print("🔍 DIRECT DATABASE CHECK FOR DEALER 12284")
    print("=" * 60)
    
    try:
        # Connect to database
        db_config = get_db_connection()
        print(f"🔗 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Set search path to use dealer_integration schema
        cursor.execute("SET search_path TO dealer_integration, public")
        print("✅ Connected to database with dealer_integration schema")
        
        # Check if dealer 12284 exists
        print("\n📋 CHECKING DEALER 12284...")
        cursor.execute("SELECT * FROM dealers WHERE dealer_id = %s", ("12284",))
        dealer = cursor.fetchone()
        
        if dealer:
            print(f"✅ Dealer found: {dealer['dealer_name']}")
            print(f"   Active: {dealer['is_active']}")
            print(f"   API Key: {'Yes' if dealer['api_key'] else 'No'}")
            print(f"   Secret Key: {'Yes' if dealer['secret_key'] else 'No'}")
        else:
            print("❌ Dealer 12284 not found!")
            return
        
        # Check document handling data
        print("\n📊 CHECKING DOCUMENT HANDLING DATA...")
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM document_handling_data 
            WHERE dealer_id = %s
        """, ("12284",))
        doc_count = cursor.fetchone()['count']
        print(f"📄 Document handling records: {doc_count}")
        
        # Check document handling units
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM document_handling_units dhu
            JOIN document_handling_data dhd ON dhu.document_handling_data_id = dhd.id
            WHERE dhd.dealer_id = %s
        """, ("12284",))
        unit_count = cursor.fetchone()['count']
        print(f"🚗 Document handling units: {unit_count}")
        
        # Get recent records if any exist
        if doc_count > 0:
            print("\n📋 RECENT DOCUMENT HANDLING RECORDS:")
            cursor.execute("""
                SELECT id, id_so, id_spk, created_time, modified_time, fetched_at
                FROM document_handling_data 
                WHERE dealer_id = %s
                ORDER BY fetched_at DESC
                LIMIT 5
            """, ("12284",))
            
            records = cursor.fetchall()
            for i, record in enumerate(records, 1):
                print(f"  {i}. SO: {record['id_so']}, SPK: {record['id_spk']}")
                print(f"     Created: {record['created_time']}, Fetched: {record['fetched_at']}")
        
        # Check fetch logs for document handling
        print("\n📝 CHECKING FETCH LOGS...")
        cursor.execute("""
            SELECT status, records_fetched, error_message, started_at, completed_at
            FROM fetch_logs 
            WHERE dealer_id = %s AND fetch_type = 'doch_read'
            ORDER BY started_at DESC
            LIMIT 5
        """, ("12284",))
        
        logs = cursor.fetchall()
        if logs:
            print(f"📊 Found {len(logs)} fetch log entries:")
            for i, log in enumerate(logs, 1):
                print(f"  {i}. Status: {log['status']}, Records: {log['records_fetched']}")
                print(f"     Started: {log['started_at']}, Completed: {log['completed_at']}")
                if log['error_message']:
                    print(f"     Error: {log['error_message']}")
        else:
            print("❌ No fetch logs found for document handling")
        
        # Check if tables exist
        print("\n🗃️  CHECKING TABLE STRUCTURE...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'dealer_integration' 
            AND table_name LIKE '%document_handling%'
        """)
        tables = cursor.fetchall()
        print(f"📋 Document handling tables found: {[t['table_name'] for t in tables]}")
        
        conn.close()
        print("\n✅ Database check completed successfully")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
