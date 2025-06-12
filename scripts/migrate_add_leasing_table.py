#!/usr/bin/env python3
"""
Database Migration: Add Leasing Data Table
Creates the leasing_data table for storing leasing requirement data
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from database import Base, LeasingData
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "dealer_dashboard")
    db_user = os.getenv("DB_USER", "dealer_user")
    db_password = os.getenv("DB_PASSWORD", "dealer_password")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                );
            """), {"table_name": table_name})
            return result.scalar()
    except Exception as e:
        logger.error(f"Error checking if table exists: {e}")
        return False

def create_leasing_table(engine):
    """Create the leasing_data table"""
    try:
        logger.info("Creating leasing_data table...")
        
        # Create the table using SQLAlchemy
        LeasingData.__table__.create(engine, checkfirst=True)
        
        logger.info("✅ leasing_data table created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating leasing_data table: {e}")
        return False

def verify_table_structure(engine):
    """Verify the table structure"""
    try:
        with engine.connect() as conn:
            # Get table columns
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'leasing_data'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            
            logger.info("📋 Table structure verification:")
            for column_name, data_type, is_nullable in columns:
                nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                logger.info(f"  - {column_name}: {data_type} ({nullable})")
            
            # Check indexes
            result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'leasing_data'
                AND schemaname = 'public';
            """))
            
            indexes = result.fetchall()
            
            if indexes:
                logger.info("📋 Table indexes:")
                for index_name, index_def in indexes:
                    logger.info(f"  - {index_name}: {index_def}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verifying table structure: {e}")
        return False

def add_sample_data(engine):
    """Add sample leasing data for testing"""
    try:
        logger.info("Adding sample leasing data...")
        
        with engine.connect() as conn:
            # Check if sample data already exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM leasing_data WHERE dealer_id = '12284';
            """))
            
            existing_count = result.scalar()
            
            if existing_count > 0:
                logger.info(f"Sample data already exists ({existing_count} records). Skipping...")
                return True
            
            # Insert sample data
            sample_data = {
                'dealer_id': '12284',
                'id_dokumen_pengajuan': 'FIF01/12284/24/01/00001',
                'id_spk': 'SPK/12284/24/01/00001',
                'jumlah_dp': 2000000.00,
                'tenor': 36,
                'jumlah_cicilan': 750000.00,
                'tanggal_pengajuan': '15/01/2024',
                'id_finance_company': 'FC/FIF01',
                'nama_finance_company': 'Astra FIF',
                'id_po_finance_company': 'PO/FC/FIF01/24/01/0001',
                'tanggal_pembuatan_po': '15/01/2024',
                'tanggal_pengiriman_po_finance_company': '16/01/2024',
                'created_time': '15/01/2024 10:30:00',
                'modified_time': '15/01/2024 10:30:00'
            }
            
            conn.execute(text("""
                INSERT INTO leasing_data (
                    dealer_id, id_dokumen_pengajuan, id_spk, jumlah_dp, tenor, 
                    jumlah_cicilan, tanggal_pengajuan, id_finance_company, 
                    nama_finance_company, id_po_finance_company, tanggal_pembuatan_po,
                    tanggal_pengiriman_po_finance_company, created_time, modified_time
                ) VALUES (
                    :dealer_id, :id_dokumen_pengajuan, :id_spk, :jumlah_dp, :tenor,
                    :jumlah_cicilan, :tanggal_pengajuan, :id_finance_company,
                    :nama_finance_company, :id_po_finance_company, :tanggal_pembuatan_po,
                    :tanggal_pengiriman_po_finance_company, :created_time, :modified_time
                );
            """), sample_data)
            
            conn.commit()
            
            logger.info("✅ Sample leasing data added successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error adding sample data: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting Leasing Data Table Migration")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Get database connection
        database_url = get_database_url()
        logger.info(f"Connecting to database...")
        
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("✅ Database connection successful!")
        
        # Check if table already exists
        if check_table_exists(engine, "leasing_data"):
            logger.info("⚠️  leasing_data table already exists!")
            
            # Verify structure
            if verify_table_structure(engine):
                logger.info("✅ Table structure verification passed!")
            
            # Add sample data
            add_sample_data(engine)
            
        else:
            # Create the table
            if create_leasing_table(engine):
                logger.info("✅ Table creation successful!")
                
                # Verify structure
                if verify_table_structure(engine):
                    logger.info("✅ Table structure verification passed!")
                
                # Add sample data
                add_sample_data(engine)
                
            else:
                logger.error("❌ Table creation failed!")
                return False
        
        logger.info("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
