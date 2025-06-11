"""
DGI API Token Generator
Implements the token generation logic for DGI API authentication
"""

import hashlib
import time
from typing import Dict, Any

def generate_api_token(api_key: str, secret_key: str, api_time: int = None) -> Dict[str, Any]:
    """
    Generate DGI API token using SHA256 hash
    
    Args:
        api_key: The API key provided by DGI
        secret_key: The secret key provided by DGI
        api_time: Unix timestamp (optional, defaults to current time)
    
    Returns:
        Dictionary containing token, timestamp, and other details
    """
    if api_time is None:
        api_time = int(time.time())
    
    # Create the hash string: apikey + secretkey + apitime
    hash_string = f"{api_key}{secret_key}{api_time}"
    
    # Generate SHA256 hash
    token = hashlib.sha256(hash_string.encode()).hexdigest()
    
    return {
        "api_token": token,
        "api_time": api_time,
        "timestamp": api_time,
        "expires_in": 3600  # Token typically expires in 1 hour
    }

def refresh_token(api_key: str, secret_key: str) -> Dict[str, Any]:
    """
    Refresh the API token with current timestamp
    
    Args:
        api_key: The API key provided by DGI
        secret_key: The secret key provided by DGI
    
    Returns:
        Dictionary containing new token and timestamp
    """
    return generate_api_token(api_key, secret_key)

def is_token_expired(api_time: int, expiry_seconds: int = 3600) -> bool:
    """
    Check if the token is expired
    
    Args:
        api_time: The timestamp when token was generated
        expiry_seconds: Token expiry time in seconds (default: 1 hour)
    
    Returns:
        True if token is expired, False otherwise
    """
    current_time = int(time.time())
    return (current_time - api_time) > expiry_seconds

def get_current_timestamp() -> int:
    """
    Get current Unix timestamp
    
    Returns:
        Current Unix timestamp as integer
    """
    return int(time.time())

class DGITokenManager:
    """
    Manages DGI API tokens with automatic refresh capability
    """
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self._token_data = None
    
    def get_valid_token(self) -> Dict[str, Any]:
        """
        Get a valid token, refreshing if necessary
        
        Returns:
            Dictionary containing valid token and timestamp
        """
        if self._token_data is None or self._is_current_token_expired():
            self._token_data = self._generate_new_token()
        
        return self._token_data
    
    def _generate_new_token(self) -> Dict[str, Any]:
        """Generate a new token"""
        return generate_api_token(self.api_key, self.secret_key)
    
    def _is_current_token_expired(self) -> bool:
        """Check if current token is expired"""
        if self._token_data is None:
            return True
        
        return is_token_expired(self._token_data['api_time'])
    
    def force_refresh(self) -> Dict[str, Any]:
        """Force refresh the token"""
        self._token_data = self._generate_new_token()
        return self._token_data
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for DGI API requests
        
        Returns:
            Dictionary containing required headers
        """
        token_data = self.get_valid_token()
        
        return {
            "DGI-API-KEY": self.api_key,
            "DGI-API-Token": token_data['api_token'],
            "X-Request-Time": str(token_data['api_time']),
            "Content-Type": "application/json"
        }
