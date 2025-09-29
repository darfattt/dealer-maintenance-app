"""
API Client modules for different DGI endpoints
Provides centralized API configuration and client management
"""

import httpx
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional
from database import SessionLocal, APIConfiguration
from utils.dgi_token_generator import DGITokenManager

# Setup logging
logger = logging.getLogger(__name__)

class APIRetryConfig:
    """Configuration for API retry logic"""
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

class CircuitBreaker:
    """Simple circuit breaker for API calls"""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if API call can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful API call"""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed API call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

def retry_with_backoff(retry_config: APIRetryConfig = None):
    """Decorator for API calls with exponential backoff retry"""
    if retry_config is None:
        retry_config = APIRetryConfig()

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadTimeout) as e:
                    last_exception = e
                    if attempt < retry_config.max_retries:
                        delay = min(
                            retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                            retry_config.max_delay
                        )
                        logger.warning(f"API call failed (attempt {attempt + 1}/{retry_config.max_retries + 1}), retrying in {delay:.2f}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"API call failed after {retry_config.max_retries + 1} attempts: {e}")
                        raise
                except Exception as e:
                    # Don't retry on non-network errors
                    logger.error(f"API call failed with non-retryable error: {e}")
                    raise

            raise last_exception
        return wrapper
    return decorator

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
        """Get enhanced default API configuration"""
        return {
            "base_url": "https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            "timeout_seconds": 45,  # Increased from 30s
            "connect_timeout": 10,  # Connection timeout
            "read_timeout": 35,     # Read timeout
            "retry_attempts": 3,
            "retry_delay": 1.0,     # Base retry delay
            "max_retry_delay": 30.0, # Max retry delay
            "circuit_breaker_threshold": 5,  # Circuit breaker failure threshold
            "circuit_breaker_timeout": 300,  # Circuit breaker recovery timeout (5 min)
            "description": "Enhanced DGI API Configuration with Retry Logic"
        }
    
    @staticmethod
    def get_default_prod_config() -> Dict[str, Any]:
        """Get enhanced default API configuration"""
        return {
            "base_url": "https://gvt-apigateway.daya-dms.id/dgi-api/v1.3",
            "timeout_seconds": 45,  # Increased from 30s
            "connect_timeout": 10,  # Connection timeout
            "read_timeout": 35,     # Read timeout
            "retry_attempts": 3,
            "retry_delay": 1.0,     # Base retry delay
            "max_retry_delay": 30.0, # Max retry delay
            "circuit_breaker_threshold": 5,  # Circuit breaker failure threshold
            "circuit_breaker_timeout": 300,  # Circuit breaker recovery timeout (5 min)
            "description": "Enhanced DGI API Configuration with Retry Logic"
        }

    @staticmethod
    def create_enhanced_client_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced HTTP client configuration"""
        return {
            "timeout": httpx.Timeout(
                connect=config.get("connect_timeout", 10),
                read=config.get("read_timeout", 35),
                write=config.get("write_timeout", 10),
                pool=config.get("pool_timeout", 5)
            ),
            "limits": httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30
            ),
            "follow_redirects": True,
            "verify": True
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
        self.config = APIConfigManager.get_api_config("dgi_pkb_api") or APIConfigManager.get_default_prod_config()
        self.endpoint = "/pkb/read"
    
    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str, no_work_order: str = "") -> Dict[str, Any]:
        """Fetch PKB data from DGI API"""
        # Generate token using token manager
        token_manager = DGITokenManager(api_key, secret_key)
        headers = token_manager.get_headers()
        print(f"Headers : {headers}")
        payload = {
            "fromTime": from_time,
            "toTime": to_time,
            "dealerId": dealer_id,
            "noWorkOrder": no_work_order
        }
        base_prod_url = 'https://gvt-apigateway.daya-dms.id/dgi-api/v1.3'
        url = f"{base_prod_url}{self.endpoint}"
        
        logger.info(f"Calling PKB API for dealer {dealer_id} at {url} with payload {payload}" )
        
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


class PartsSalesAPIClient:
    """Client for Parts Sales (PRSL) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_parts_sales_api") or APIConfigManager.get_default_config()
        self.endpoint = "/prsl/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   no_po: str = "") -> Dict[str, Any]:
        """Fetch Parts Sales data from DGI API"""
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
            if no_po:
                payload["noPO"] = no_po

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Parts Sales API for dealer {dealer_id} at {url}")

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
            logger.error(f"Parts Sales API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Parts Sales API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Parts Sales API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Parts Sales API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class DPHLOAPIClient:
    """Enhanced Client for DP HLO (DPHLO) API calls with retry logic and circuit breaker"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_dp_hlo_api") or APIConfigManager.get_default_config()
        self.endpoint = "/dphlo/read"
        self.retry_config = APIRetryConfig(
            max_retries=self.config.get("retry_attempts", 3),
            base_delay=self.config.get("retry_delay", 1.0),
            max_delay=self.config.get("max_retry_delay", 30.0)
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.get("circuit_breaker_threshold", 5),
            recovery_timeout=self.config.get("circuit_breaker_timeout", 300)
        )

    @retry_with_backoff()
    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   no_work_order: str = "", id_hlo_document: str = "") -> Dict[str, Any]:
        """Fetch DP HLO data from DGI API with enhanced error handling"""
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise ValueError(f"Circuit breaker is OPEN for DP HLO API. Service temporarily unavailable.")

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
            if no_work_order:
                payload["noWorkOrder"] = no_work_order
            if id_hlo_document:
                payload["idHLODocument"] = id_hlo_document

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling DP HLO API for dealer {dealer_id} at {url}")

            # Enhanced client configuration
            client_config = APIConfigManager.create_enhanced_client_config(self.config)

            with httpx.Client(**client_config) as client:
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

                # Record success for circuit breaker
                self.circuit_breaker.record_success()
                return json_response

        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
            # Record failure for circuit breaker
            self.circuit_breaker.record_failure()

            if isinstance(e, httpx.ConnectError):
                logger.error(f"DP HLO API connection failed: {e}")
                raise ValueError(f"Connection failed to {url}: {e}")
            elif isinstance(e, httpx.TimeoutException):
                logger.error(f"DP HLO API timeout: {e}")
                raise ValueError(f"Request timeout to {url}: {e}")
            else:  # HTTPStatusError
                logger.error(f"DP HLO API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"DP HLO API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class WorkshopInvoiceAPIClient:
    """Client for Workshop Invoice (INV2) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_workshop_invoice_api") or APIConfigManager.get_default_prod_config()
        self.endpoint = "/inv2/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   no_work_order: str = "") -> Dict[str, Any]:
        """Fetch Workshop Invoice data from DGI API"""
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
            if no_work_order:
                payload["noWorkOrder"] = no_work_order

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Workshop Invoice API for dealer {dealer_id} at {url}")

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
            logger.error(f"Workshop Invoice API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Workshop Invoice API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Workshop Invoice API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Workshop Invoice API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class UnpaidHLOAPIClient:
    """Client for Unpaid HLO (UNPAIDHLO) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_unpaid_hlo_api") or APIConfigManager.get_default_config()
        self.endpoint = "/unpaidhlo/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   no_work_order: str = "", id_hlo_document: str = "") -> Dict[str, Any]:
        """Fetch Unpaid HLO data from DGI API"""
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
            if no_work_order:
                payload["noWorkOrder"] = no_work_order
            if id_hlo_document:
                payload["idHLODocument"] = id_hlo_document

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Unpaid HLO API for dealer {dealer_id} at {url}")

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
            logger.error(f"Unpaid HLO API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Unpaid HLO API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Unpaid HLO API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Unpaid HLO API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class PartsInvoiceAPIClient:
    """Client for Parts Invoice (MDINVH3) API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_parts_invoice_api") or APIConfigManager.get_default_config()
        self.endpoint = "/mdinvh3/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str, api_key: str, secret_key: str,
                   no_po: str = "") -> Dict[str, Any]:
        """Fetch Parts Invoice data from DGI API"""
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
            if no_po:
                payload["noPO"] = no_po

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling Parts Invoice API for dealer {dealer_id} at {url}")

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
            logger.error(f"Parts Invoice API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"Parts Invoice API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Parts Invoice API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Parts Invoice API call failed: {e}")
            logger.error(f"Error type: {type(e)}")
            raise ValueError(f"API call failed: {e}")


class SPKDealingProcessAPIClient:
    """Client for SPK Dealing Process API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_spk_dealing_process_api") or APIConfigManager.get_default_config()
        self.endpoint = "/spk/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str,
                   api_key: str, secret_key: str, id_prospect: str = "",
                   id_sales_people: str = "") -> Dict[str, Any]:
        """Fetch SPK dealing process data from DGI API"""
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
            if id_prospect:
                payload["idProspect"] = id_prospect
            if id_sales_people:
                payload["idSalesPeople"] = id_sales_people

            url = f"{self.config['base_url']}{self.endpoint}"

            logger.info(f"Calling SPK Dealing Process API for dealer {dealer_id} at {url}")

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
            logger.error(f"SPK Dealing Process API connection failed: {e}")
            raise ValueError(f"Connection failed to {url}: {e}")
        except httpx.TimeoutException as e:
            logger.error(f"SPK Dealing Process API timeout: {e}")
            raise ValueError(f"Request timeout to {url}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"SPK Dealing Process API HTTP error: {e}")
            raise ValueError(f"HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"SPK Dealing Process API call failed: {e}")
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
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Billing Process Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unit_invoice_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Unit Invoice (MD to Dealer) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_parts_sales_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Parts Sales Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_dp_hlo_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for DP HLO Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_workshop_invoice_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Workshop Invoice (NJB & NSC) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unpaid_hlo_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Unpaid HLO Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_parts_invoice_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Parts Invoice (MD to Dealer) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_spk_dealing_process_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for SPK Dealing Process Data",
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
