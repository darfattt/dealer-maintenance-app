#!/usr/bin/env python3
"""
Database Migration Script: Add Document Handling Tables
Creates the document_handling_data and document_handling_units tables
"""

import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/app')

from sqlalchemy import create_engine, text
from database import DocumentHandlingData, DocumentHandlingUnit, Base
from config import get_database_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_document_handling_tables(engine):
    """Create the document handling tables"""
    try:
        # Create document_handling_data table
        DocumentHandlingData.__table__.create(engine, checkfirst=True)
        logger.info("✅ document_handling_data table created successfully!")
        
        # Create document_handling_units table
        DocumentHandlingUnit.__table__.create(engine, checkfirst=True)
        logger.info("✅ document_handling_units table created successfully!")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error creating document handling tables: {e}")
        return False

def verify_tables(engine):
    """Verify that the tables were created correctly"""
    try:
        with engine.connect() as conn:
            # Check document_handling_data table
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'document_handling_data'"))
            doc_table_exists = result.scalar() > 0
            
            # Check document_handling_units table
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'document_handling_units'"))
            units_table_exists = result.scalar() > 0
            
            if doc_table_exists and units_table_exists:
                logger.info("✅ Both document handling tables verified successfully!")
                
                # Check table structure
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'document_handling_data' ORDER BY ordinal_position"))
                doc_columns = [row[0] for row in result.fetchall()]
                logger.info(f"📋 document_handling_data columns: {', '.join(doc_columns)}")
                
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'document_handling_units' ORDER BY ordinal_position"))
                units_columns = [row[0] for row in result.fetchall()]
                logger.info(f"📋 document_handling_units columns: {', '.join(units_columns)}")
                
                return True
            else:
                logger.error(f"❌ Table verification failed - doc_table: {doc_table_exists}, units_table: {units_table_exists}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting Document Handling tables migration...")
    logger.info(f"📅 Migration started at: {datetime.now()}")
    
    try:
        # Get database URL
        database_url = get_database_url()
        logger.info(f"🔗 Connecting to database...")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful!")
        
        # Create tables
        logger.info("📋 Creating document handling tables...")
        if create_document_handling_tables(engine):
            logger.info("✅ Tables created successfully!")
            
            # Verify tables
            logger.info("🔍 Verifying table creation...")
            if verify_tables(engine):
                logger.info("✅ Migration completed successfully!")
                logger.info("📄 Document Handling tables are ready for use!")
                return True
            else:
                logger.error("❌ Table verification failed!")
                return False
        else:
            logger.error("❌ Table creation failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
    
    finally:
        logger.info(f"📅 Migration ended at: {datetime.now()}")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Document Handling tables migration completed successfully!")
        print("📄 The following tables are now available:")
        print("   - document_handling_data (main document records)")
        print("   - document_handling_units (unit/vehicle details)")
        print("\n🔗 You can now:")
        print("   - Add document handling jobs in the Admin Panel")
        print("   - View document handling data in the Dashboard")
        print("   - Use the /document_handling/ API endpoints")
        sys.exit(0)
    else:
        print("\n❌ Migration failed! Please check the logs above.")
        sys.exit(1)
