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

class LeasingAPIClient:
    """Client for Leasing Requirement API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_leasing_api") or APIConfigManager.get_default_config()
        self.endpoint = "/lsng/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str, id_spk: str = "") -> Dict[str, Any]:
        """Fetch Leasing data from DGI API"""
        # Generate token using token manager
        token_manager = DGITokenManager(api_key, secret_key)
        headers = token_manager.get_headers()

        payload = {
            "fromTime": from_time,
            "toTime": to_time,
            "dealerId": dealer_id
        }

        # Add idSPK if provided
        if id_spk:
            payload["idSPK"] = id_spk

        url = f"{self.config['base_url']}{self.endpoint}"

        logger.info(f"Calling Leasing API for dealer {dealer_id} at {url}")

        with httpx.Client(timeout=self.config['timeout_seconds']) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()


class DocumentHandlingAPIClient:
    """Client for Document Handling API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_document_handling_api") or APIConfigManager.get_default_config()
        self.endpoint = "/doch/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   id_spk: str = "", id_customer: str = "") -> Dict[str, Any]:
        """Fetch Document Handling data from DGI API"""
        # Generate token using token manager
        token_manager = DGITokenManager(api_key, secret_key)
        headers = token_manager.get_headers()

        payload = {
            "fromTime": from_time,
            "toTime": to_time
        }

        # Add optional parameters if provided
        if dealer_id:
            payload["dealerId"] = dealer_id
        if id_spk:
            payload["idSPK"] = id_spk
        if id_customer:
            payload["idCustomer"] = id_customer

        url = f"{self.config['base_url']}{self.endpoint}"

        logger.info(f"Calling Document Handling API for dealer {dealer_id} at {url}")

        with httpx.Client(timeout=self.config['timeout_seconds']) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()


class UnitInboundAPIClient:
    """Client for Unit Inbound from Purchase Order API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_unit_inbound_api") or APIConfigManager.get_default_config()
        self.endpoint = "/uinb/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   po_id: str = "", no_shipping_list: str = "") -> Dict[str, Any]:
        """Fetch Unit Inbound data from DGI API"""
        try:
            # Check if config is valid
            if not self.config:
                raise ValueError("API configuration is not available")

            # Generate token using token manager
            token_manager = DGITokenManager(api_key, secret_key)
            headers = token_manager.get_headers()

            payload = {
                "fromTime": from_time,
                "toTime": to_time,
                "dealerId": dealer_id
            }

            # Add optional parameters if provided
            if po_id:
                payload["poId"] = po_id
            if no_shipping_list:
                payload["noShippingList"] = no_shipping_list

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Unit Inbound API for dealer {dealer_id} at {url}")

            with httpx.Client(timeout=self.config.get('timeout_seconds', 30)) as client:
                logger.debug(f"Making POST request to {url}")
                logger.debug(f"Headers: {headers}")
                logger.debug(f"Payload: {payload}")

                response = client.post(url, headers=headers, json=payload)
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

                response.raise_for_status()

                # Get response text first for debugging
                response_text = response.text
                logger.debug(f"Response text: {response_text[:500]}...")  # First 500 chars

                # Get JSON response with validation
                if not response_text:
                    raise ValueError("API returned empty response")

                try:
                    json_response = response.json()
                except Exception as json_error:
                    raise ValueError(f"Failed to parse JSON response: {json_error}. Response text: {response_text[:200]}")

                if json_response is None:
                    raise ValueError("API returned None JSON response")

                logger.debug(f"API response type: {type(json_response)}")
                return json_response

        except httpx.ConnectError as e:
            logger.error(f"Unit Inbound API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Unit Inbound API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Unit Inbound API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Unit Inbound API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class DeliveryProcessAPIClient:
    """Client for Delivery Process (BAST) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_delivery_process_api") or APIConfigManager.get_default_config()
        self.endpoint = "/bast/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   delivery_document_id: str = "", id_spk: str = "", id_customer: str = "") -> Dict[str, Any]:
        """Fetch Delivery Process data from DGI API"""
        try:
            # Check if config is valid
            if not self.config:
                raise ValueError("API configuration is not available")

            # Generate token using token manager
            token_manager = DGITokenManager(api_key, secret_key)
            headers = token_manager.get_headers()

            payload = {
                "fromTime": from_time,
                "toTime": to_time,
                "dealerId": dealer_id
            }

            # Add optional parameters if provided
            if delivery_document_id:
                payload["deliveryDocumentId"] = delivery_document_id
            if id_spk:
                payload["idSPK"] = id_spk
            if id_customer:
                payload["idCustomer"] = id_customer

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Delivery Process API for dealer {dealer_id} at {url}")

            with httpx.Client(timeout=self.config.get('timeout_seconds', 30)) as client:
                logger.debug(f"Making POST request to {url}")
                logger.debug(f"Headers: {headers}")
                logger.debug(f"Payload: {payload}")

                response = client.post(url, headers=headers, json=payload)
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

                response.raise_for_status()

                # Get response text first for debugging
                response_text = response.text
                logger.debug(f"Response text: {response_text[:500]}...")  # First 500 chars

                # Get JSON response with validation
                if not response_text:
                    raise ValueError("API returned empty response")

                try:
                    json_response = response.json()
                except Exception as json_error:
                    raise ValueError(f"Failed to parse JSON response: {json_error}. Response text: {response_text[:200]}")

                if json_response is None:
                    raise ValueError("API returned None JSON response")

                logger.debug(f"API response type: {type(json_response)}")
                return json_response

        except httpx.ConnectError as e:
            logger.error(f"Delivery Process API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Delivery Process API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Delivery Process API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Delivery Process API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class BillingProcessAPIClient:
    """Client for Billing Process (INV1) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_billing_process_api") or APIConfigManager.get_default_config()
        self.endpoint = "/inv1/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   id_spk: str = "", id_customer: str = "") -> Dict[str, Any]:
        """Fetch Billing Process data from DGI API"""
        try:
            # Check if config is valid
            if not self.config:
                raise ValueError("API configuration is not available")

            # Generate token using token manager
            token_manager = DGITokenManager(api_key, secret_key)
            headers = token_manager.get_headers()

            payload = {
                "fromTime": from_time,
                "toTime": to_time,
                "dealerId": dealer_id
            }

            # Add optional parameters if provided
            if id_spk:
                payload["idSPK"] = id_spk
            if id_customer:
                payload["idCustomer"] = id_customer

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Billing Process API for dealer {dealer_id} at {url}")

            with httpx.Client(timeout=self.config.get('timeout_seconds', 30)) as client:
                logger.debug(f"Making POST request to {url}")
                logger.debug(f"Headers: {headers}")
                logger.debug(f"Payload: {payload}")

                response = client.post(url, headers=headers, json=payload)
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

                response.raise_for_status()

                # Get response text first for debugging
                response_text = response.text
                logger.debug(f"Response text: {response_text[:500]}...")  # First 500 chars

                # Get JSON response with validation
                if not response_text:
                    raise ValueError("API returned empty response")

                try:
                    json_response = response.json()
                except Exception as json_error:
                    raise ValueError(f"Failed to parse JSON response: {json_error}. Response text: {response_text[:200]}")

                if json_response is None:
                    raise ValueError("API returned None JSON response")

                logger.debug(f"API response type: {type(json_response)}")
                return json_response

        except httpx.ConnectError as e:
            logger.error(f"Billing Process API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Billing Process API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Billing Process API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Billing Process API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class UnitInvoiceAPIClient:
    """Client for Unit Invoice (MDINVH1) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_unit_invoice_api") or APIConfigManager.get_default_config()
        self.endpoint = "/mdinvh1/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   po_id: str = "", no_shipping_list: str = "") -> Dict[str, Any]:
        """Fetch Unit Invoice data from DGI API"""
        try:
            # Check if config is valid
            if not self.config:
                raise ValueError("API configuration is not available")

            # Generate token using token manager
            token_manager = DGITokenManager(api_key, secret_key)
            headers = token_manager.get_headers()

            payload = {
                "fromTime": from_time,
                "toTime": to_time,
                "dealerId": dealer_id
            }

            # Add optional parameters if provided
            if po_id:
                payload["poId"] = po_id
            if no_shipping_list:
                payload["noShippingList"] = no_shipping_list

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Unit Invoice API for dealer {dealer_id} at {url}")

            with httpx.Client(timeout=self.config.get('timeout_seconds', 30)) as client:
                logger.debug(f"Making POST request to {url}")
                logger.debug(f"Headers: {headers}")
                logger.debug(f"Payload: {payload}")

                response = client.post(url, headers=headers, json=payload)
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

                response.raise_for_status()

                # Get response text first for debugging
                response_text = response.text
                logger.debug(f"Response text: {response_text[:500]}...")  # First 500 chars

                # Get JSON response with validation
                if not response_text:
                    raise ValueError("API returned empty response")

                try:
                    json_response = response.json()
                except Exception as json_error:
                    raise ValueError(f"Failed to parse JSON response: {json_error}. Response text: {response_text[:200]}")

                if json_response is None:
                    raise ValueError("API returned None JSON response")

                logger.debug(f"API response type: {type(json_response)}")
                return json_response

        except httpx.ConnectError as e:
            logger.error(f"Unit Invoice API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Unit Invoice API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Unit Invoice API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Unit Invoice API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


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
            ),
            APIConfiguration(
                config_name="dgi_leasing_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Leasing Requirement Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_document_handling_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Document Handling Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unit_inbound_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Unit Inbound from Purchase Order Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_delivery_process_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Delivery Process Data (BAST)",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_billing_process_api",
                base_url="https://example.com/dgi-api/v1.3",
                description="DGI API for Billing Process Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unit_invoice_api",
                base_url="https://example.com/dgi-api/v1.3",
                description="DGI API for Unit Invoice (MD to Dealer) Data",
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
