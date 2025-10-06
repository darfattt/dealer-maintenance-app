#!/usr/bin/env python3
"""
Test script to verify APIConfigManager database retrieval fix
"""

import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and schema with enhanced diagnostics"""
    try:
        # First check if psycopg2 is available
        try:
            import psycopg2
            logger.info("✓ psycopg2 driver is available")
        except ImportError as e:
            logger.error(f"✗ psycopg2 driver not available: {e}")
            logger.error("Please install: pip install psycopg2-binary")
            return False

        from database import SessionLocal, APIConfiguration
        logger.info("Testing database connection...")

        db = SessionLocal()
        try:
            # Test basic connection
            result = db.execute("SELECT 1").scalar()
            logger.info(f"✓ Database connection successful: {result}")

            # Check if api_configurations table exists
            try:
                count = db.query(APIConfiguration).count()
                logger.info(f"✓ api_configurations table exists with {count} records")

                # If table exists, show some sample data
                if count > 0:
                    sample_configs = db.query(APIConfiguration.config_name, APIConfiguration.is_active).limit(3).all()
                    logger.info(f"Sample configs: {[(c.config_name, c.is_active) for c in sample_configs]}")

                return True
            except Exception as table_error:
                logger.error(f"✗ api_configurations table issue: {table_error}")
                logger.error(f"Error type: {type(table_error)}")
                if "does not exist" in str(table_error).lower():
                    logger.error("Table does not exist. Please run database migrations.")
                return False

        finally:
            db.close()

    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        logger.error(f"Error type: {type(e)}")

        # Provide specific guidance
        if "connection" in str(e).lower():
            logger.error("Check if PostgreSQL is running and connection parameters are correct")
        elif "authentication" in str(e).lower():
            logger.error("Check database username/password")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            logger.error("Database does not exist. Please create the database first.")

        return False

def test_api_config_manager():
    """Test APIConfigManager functionality"""
    try:
        from tasks.api_clients import APIConfigManager, initialize_default_api_configs

        logger.info("Testing APIConfigManager...")

        # Test getting PKB API config
        config = APIConfigManager.get_api_config("dgi_pkb_api")

        if config:
            logger.info(f"✓ Successfully retrieved dgi_pkb_api config: {config}")
            return True
        else:
            logger.warning("✗ Failed to retrieve dgi_pkb_api config - got None")

            # Try manual initialization
            logger.info("Attempting manual initialization...")
            try:
                result = initialize_default_api_configs()
                logger.info(f"Initialization result: {result}")

                # Retry getting config
                config = APIConfigManager.get_api_config("dgi_pkb_api")
                if config:
                    logger.info(f"✓ After initialization, retrieved config: {config}")
                    return True
                else:
                    logger.error("✗ Still failed to retrieve config after initialization")
                    return False

            except Exception as init_error:
                logger.error(f"Initialization failed: {init_error}")
                return False

    except Exception as e:
        logger.error(f"APIConfigManager test failed: {e}")
        return False

def test_pkb_client():
    """Test PKBAPIClient initialization with detailed diagnostics"""
    try:
        from tasks.api_clients import PKBAPIClient

        logger.info("Testing PKBAPIClient initialization...")

        # Create client and check initialization
        client = PKBAPIClient()

        # Verify client was created
        if not client:
            logger.error("✗ PKBAPIClient creation failed")
            return False

        # Check configuration
        if not client.config:
            logger.error("✗ PKBAPIClient has no configuration")
            return False

        logger.info(f"✓ PKBAPIClient initialized successfully")
        logger.info(f"  - Base URL: {client.config.get('base_url')}")
        logger.info(f"  - Timeout: {client.config.get('timeout_seconds')}")
        logger.info(f"  - Retry attempts: {client.config.get('retry_attempts')}")
        logger.info(f"  - Endpoint: {client.endpoint}")

        # Check if it's using database or fallback config
        base_url = client.config.get('base_url', '')
        if 'dev-gvt-gateway.eksad.com' in base_url:
            logger.info("✓ Using development configuration")
        elif 'gvt-apigateway.daya-dms.id' in base_url:
            logger.info("✓ Using production configuration (likely fallback)")
        else:
            logger.warning(f"⚠️ Unknown configuration source: {base_url}")

        return True

    except Exception as e:
        logger.error(f"✗ PKBAPIClient test failed: {e}")
        logger.error(f"Error type: {type(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("=== Starting API Config Fix Verification ===")

    tests = [
        ("Database Connection", test_database_connection),
        ("APIConfigManager", test_api_config_manager),
        ("PKBAPIClient", test_pkb_client)
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            result = test_func()
            results[test_name] = result
            logger.info(f"{test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"{test_name} test error: {e}")
            results[test_name] = False

    # Summary
    logger.info("\n=== Test Results Summary ===")
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")

    all_passed = all(results.values())
    logger.info(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)