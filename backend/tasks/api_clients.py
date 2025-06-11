"""
API Client modules for different DGI endpoints
Provides centralized API configuration and client management
"""

import httpx
import logging
from typing import Dict, List, Any, Optional
from database import SessionLocal, APIConfiguration
from utils.dgi_token_generator import DGITokenManager

# Setup logging
logger = logging.getLogger(__name__)

class APIConfigManager:
    """Manages API configurations from database"""
    
    @staticmethod
    def get_api_config(config_name: str) -> Optional[Dict[str, Any]]:
        """Get API configuration by name"""
        db = SessionLocal()
        try:
            config = db.query(APIConfiguration).filter(
                APIConfiguration.config_name == config_name,
                APIConfiguration.is_active == True
            ).first()
            
            if config:
                return {
                    "base_url": config.base_url,
                    "timeout_seconds": config.timeout_seconds,
                    "retry_attempts": config.retry_attempts,
                    "description": config.description
                }
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default API configuration"""
        return {
            "base_url": "https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "description": "Default DGI API Configuration"
        }

class ProspectAPIClient:
    """Client for Prospect Data API calls"""
    
    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_prospect_api") or APIConfigManager.get_default_config()
        self.endpoint = "/prsp/read"
    
    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str) -> Dict[str, Any]:
        """Fetch prospect data from DGI API"""
        # Generate token using token manager
        token_manager = DGITokenManager(api_key, secret_key)
        headers = token_manager.get_headers()
        
        payload = {
            "fromTime": from_time,
            "toTime": to_time,
            "dealerId": dealer_id,
            "idProspect": "",
            "idSalesPeople": ""
        }
        
        url = f"{self.config['base_url']}{self.endpoint}"
        
        logger.info(f"Calling Prospect API for dealer {dealer_id} at {url}")
        
        with httpx.Client(timeout=self.config['timeout_seconds']) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

class PKBAPIClient:
    """Client for PKB (Service Record) API calls"""
    
    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_pkb_api") or APIConfigManager.get_default_config()
        self.endpoint = "/pkb/read"
    
    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str, no_work_order: str = "") -> Dict[str, Any]:
        """Fetch PKB data from DGI API"""
        # Generate token using token manager
        token_manager = DGITokenManager(api_key, secret_key)
        headers = token_manager.get_headers()
        
        payload = {
            "fromTime": from_time,
            "toTime": to_time,
            "dealerId": dealer_id,
            "noWorkOrder": no_work_order
        }
        
        url = f"{self.config['base_url']}{self.endpoint}"
        
        logger.info(f"Calling PKB API for dealer {dealer_id} at {url}")
        
        with httpx.Client(timeout=self.config['timeout_seconds']) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

class PartsInboundAPIClient:
    """Client for Parts Inbound API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_parts_inbound_api") or APIConfigManager.get_default_config()
        self.endpoint = "/pinb/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str, no_po: str = "") -> Dict[str, Any]:
        """Fetch Parts Inbound data from DGI API"""
        # Generate token using token manager
        token_manager = DGITokenManager(api_key, secret_key)
        headers = token_manager.get_headers()

        payload = {
            "fromTime": from_time,
            "toTime": to_time,
            "dealerId": dealer_id,
            "noPO": no_po
        }

        url = f"{self.config['base_url']}{self.endpoint}"

        logger.info(f"Calling Parts Inbound API for dealer {dealer_id} at {url}")

        with httpx.Client(timeout=self.config['timeout_seconds']) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

def initialize_default_api_configs():
    """Initialize default API configurations in database"""
    db = SessionLocal()
    try:
        # Check if configurations already exist
        existing_configs = db.query(APIConfiguration).count()
        if existing_configs > 0:
            logger.info("API configurations already exist, skipping initialization")
            return
        
        # Create default configurations
        configs = [
            APIConfiguration(
                config_name="dgi_prospect_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Prospect Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_pkb_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for PKB (Service Record) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_parts_inbound_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Parts Inbound Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            )
        ]
        
        for config in configs:
            db.add(config)
        
        db.commit()
        logger.info("Default API configurations initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API configurations: {e}")
        db.rollback()
    finally:
        db.close()
