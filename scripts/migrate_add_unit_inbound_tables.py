#!/usr/bin/env python3
"""
Database Migration Script: Add Unit Inbound Tables
Creates the unit_inbound_data and unit_inbound_units tables
"""

import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/app')

from sqlalchemy import create_engine, text
from database import UnitInboundData, UnitInboundUnit, Base
from config import get_database_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_unit_inbound_tables(engine):
    """Create the unit inbound tables"""
    try:
        # Create unit_inbound_data table
        UnitInboundData.__table__.create(engine, checkfirst=True)
        logger.info("✅ unit_inbound_data table created successfully!")
        
        # Create unit_inbound_units table
        UnitInboundUnit.__table__.create(engine, checkfirst=True)
        logger.info("✅ unit_inbound_units table created successfully!")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error creating unit inbound tables: {e}")
        return False

def verify_tables(engine):
    """Verify that the tables were created correctly"""
    try:
        with engine.connect() as conn:
            # Check unit_inbound_data table
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'unit_inbound_data'"))
            data_table_exists = result.scalar() > 0
            
            # Check unit_inbound_units table
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'unit_inbound_units'"))
            units_table_exists = result.scalar() > 0
            
            if data_table_exists and units_table_exists:
                logger.info("✅ Both unit inbound tables verified successfully!")
                
                # Check table structure
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'unit_inbound_data' ORDER BY ordinal_position"))
                data_columns = [row[0] for row in result.fetchall()]
                logger.info(f"📋 unit_inbound_data columns: {', '.join(data_columns)}")
                
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'unit_inbound_units' ORDER BY ordinal_position"))
                units_columns = [row[0] for row in result.fetchall()]
                logger.info(f"📋 unit_inbound_units columns: {', '.join(units_columns)}")
                
                return True
            else:
                logger.error(f"❌ Table verification failed - data_table: {data_table_exists}, units_table: {units_table_exists}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting Unit Inbound tables migration...")
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
        logger.info("📋 Creating unit inbound tables...")
        if create_unit_inbound_tables(engine):
            logger.info("✅ Tables created successfully!")
            
            # Verify tables
            logger.info("🔍 Verifying table creation...")
            if verify_tables(engine):
                logger.info("✅ Migration completed successfully!")
                logger.info("🚚 Unit Inbound tables are ready for use!")
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
        print("\n🎉 Unit Inbound tables migration completed successfully!")
        print("🚚 The following tables are now available:")
        print("   - unit_inbound_data (main shipment records)")
        print("   - unit_inbound_units (individual unit details)")
        print("\n🔗 You can now:")
        print("   - Add unit inbound jobs in the Admin Panel")
        print("   - View unit inbound data in the Dashboard")
        print("   - Use the /unit_inbound/ API endpoints")
        sys.exit(0)
    else:
        print("\n❌ Migration failed! Please check the logs above.")
        sys.exit(1)
