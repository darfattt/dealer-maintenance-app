"""
Middleware for API Gateway
"""

import time
import json
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import httpx
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.auth import decode_token
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, requests_per_window: int = 100, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.clients: Dict[str, Dict] = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make request"""
        current_time = time.time()
        
        if client_ip not in self.clients:
            self.clients[client_ip] = {
                "requests": 1,
                "window_start": current_time
            }
            return True
        
        client_data = self.clients[client_ip]
        
        # Reset window if expired
        if current_time - client_data["window_start"] > self.window_seconds:
            client_data["requests"] = 1
            client_data["window_start"] = current_time
            return True
        
        # Check if within limit
        if client_data["requests"] < self.requests_per_window:
            client_data["requests"] += 1
            return True
        
        return False


class AuthMiddleware:
    """Authentication middleware"""
    
    def __init__(self, jwt_secret: str, jwt_algorithm: str):
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.public_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/password-reset/request",
            "/api/v1/auth/password-reset/confirm",
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/"
        }
    
    def is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require authentication)"""
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
    def extract_user_from_token(self, request: Request) -> Optional[Dict]:
        """Extract user information from JWT token"""
        try:
            # Get authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # Extract token
            token = auth_header.split(" ")[1]
            
            # Decode token
            payload = decode_token(token)
            if not payload or payload.get("type") != "access":
                return None
            
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "dealer_id": payload.get("dealer_id")
            }
        except Exception as e:
            logger.warning(f"Failed to extract user from token: {str(e)}")
            return None


class ProxyMiddleware:
    """Proxy middleware for routing requests to services"""
    
    def __init__(self, service_routes: Dict[str, str], timeout: int = 30):
        self.service_routes = service_routes
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    def get_target_service(self, path: str) -> Optional[str]:
        """Get target service URL for given path"""
        for route_prefix, service_url in self.service_routes.items():
            if path.startswith(route_prefix):
                return service_url
        return None
    
    async def proxy_request(self, request: Request) -> Response:
        """Proxy request to target service"""
        path = str(request.url.path)
        full_url = str(request.url)
        method = request.method
        
        logger.info(f"=== PROXY REQUEST DEBUG ===")
        logger.info(f"Method: {method}")
        logger.info(f"Full URL: {full_url}")
        logger.info(f"Path: {path}")
        logger.info(f"Available service routes: {list(self.service_routes.keys())}")

        target_service = self.get_target_service(path)
        if not target_service:
            logger.error(f"❌ No service found for path: {path}")
            logger.error(f"Available routes: {list(self.service_routes.keys())}")
            # Check if any routes partially match
            partial_matches = [route for route in self.service_routes.keys() if route in path or path in route]
            if partial_matches:
                logger.error(f"Partial matches found: {partial_matches}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service not found for path: {path}"
            )

        logger.info(f"✅ Found target service: {target_service} for path: {path}")
        
        # Build target URL
        target_url = f"{target_service}{request.url.path}"
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        logger.info(f"🎯 Proxying {method} {path} -> {target_url}")
        
        try:
            # Get request body
            body = await request.body()
            
            # Prepare headers (exclude host and content-length)
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            
            # Make request to target service
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body
            )
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
            
        except httpx.TimeoutException:
            logger.error(f"Timeout when proxying to {target_url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Service timeout"
            )
        except httpx.ConnectError as e:
            logger.error(f"Connection error when proxying to {target_url}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {target_service}"
            )
        except Exception as e:
            logger.error(f"Error proxying request to {target_url}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Bad gateway"
            )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class LoggingMiddleware:
    """Request/response logging middleware"""
    
    def __init__(self):
        self.logger = setup_logger("gateway.requests")
    
    async def log_request(self, request: Request, response: Response, process_time: float):
        """Log request and response"""
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Add user info if available
        if hasattr(request.state, "user") and request.state.user:
            log_data["user_id"] = request.state.user.get("user_id")
            log_data["user_email"] = request.state.user.get("email")
        
        self.logger.info("Request processed", extra={"extra_fields": log_data})
