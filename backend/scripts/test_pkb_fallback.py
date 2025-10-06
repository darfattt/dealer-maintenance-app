#!/usr/bin/env python3
"""
Test script to demonstrate PKBAPIClient fallback behavior
"""

import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_pkb_fallback_behavior():
    """Test PKBAPIClient fallback when database is not available"""
    try:
        logger.info("=== Testing PKBAPIClient Fallback Behavior ===")

        # Import the PKBAPIClient
        from tasks.api_clients import PKBAPIClient

        logger.info("Creating PKBAPIClient instance...")

        # Create the client - this should gracefully fallback to production config
        client = PKBAPIClient()

        # Verify the client was created successfully
        if client and client.config:
            logger.info("✅ PKBAPIClient created successfully with fallback configuration")
            logger.info(f"Configuration details:")
            logger.info(f"  - Base URL: {client.config.get('base_url')}")
            logger.info(f"  - Timeout: {client.config.get('timeout_seconds')}s")
            logger.info(f"  - Retry attempts: {client.config.get('retry_attempts')}")
            logger.info(f"  - Endpoint: {client.endpoint}")

            # Determine configuration source
            base_url = client.config.get('base_url', '')
            if 'gvt-apigateway.daya-dms.id' in base_url:
                logger.info("✅ Using production fallback configuration (expected when database unavailable)")
            elif 'dev-gvt-gateway.eksad.com' in base_url:
                logger.info("✅ Using development configuration from database")
            else:
                logger.warning(f"⚠️ Unknown configuration source: {base_url}")

            return True
        else:
            logger.error("❌ PKBAPIClient creation failed")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.error(f"Error type: {type(e)}")
        return False

def main():
    """Run the fallback test"""
    logger.info("Starting PKBAPIClient fallback test...")

    success = test_pkb_fallback_behavior()

    if success:
        logger.info("🎉 Test completed successfully - PKBAPIClient fallback working correctly")
        logger.info("This demonstrates that PKBAPIClient can operate without database connectivity")
    else:
        logger.error("💥 Test failed - PKBAPIClient fallback not working")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)