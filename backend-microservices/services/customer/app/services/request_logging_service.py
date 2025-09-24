"""
Async request logging service for API request tracking
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.repositories.api_request_log_repository import ApiRequestLogRepository

logger = logging.getLogger(__name__)


class RequestLoggingService:
    """Service for async API request logging"""

    def __init__(self, log_repository: ApiRequestLogRepository):
        self.log_repository = log_repository

    def _sanitize_payload(self, payload: Dict[str, Any], max_size: int = 10000) -> Dict[str, Any]:
        """
        Sanitize payload for logging by removing sensitive data and limiting size

        Args:
            payload: Original payload
            max_size: Maximum size of serialized payload

        Returns:
            Sanitized payload
        """
        if not payload:
            return {}

        try:
            # Create a copy to avoid modifying original
            sanitized = payload.copy()

            # Remove sensitive fields
            sensitive_fields = [
                'password', 'token', 'secret', 'key', 'auth', 'authorization',
                'nomor_telepon_pelanggan'  # Phone numbers are sensitive
            ]

            def _remove_sensitive(obj, path=""):
                if isinstance(obj, dict):
                    for key in list(obj.keys()):
                        current_path = f"{path}.{key}" if path else key
                        if any(sensitive in key.lower() for sensitive in sensitive_fields):
                            obj[key] = "[REDACTED]"
                        else:
                            _remove_sensitive(obj[key], current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        _remove_sensitive(item, f"{path}[{i}]")

            _remove_sensitive(sanitized)

            # Check size and truncate if necessary
            serialized = json.dumps(sanitized, default=str)
            if len(serialized) > max_size:
                # Truncate large payloads
                sanitized = {
                    "_truncated": True,
                    "_original_size": len(serialized),
                    "_sample": str(sanitized)[:max_size-100] + "..."
                }

            return sanitized

        except Exception as e:
            logger.warning(f"Error sanitizing payload: {str(e)}")
            return {"_error": "Failed to sanitize payload", "_original_type": str(type(payload))}

    def _sanitize_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize headers by removing sensitive information

        Args:
            headers: Original headers

        Returns:
            Sanitized headers
        """
        if not headers:
            return {}

        sensitive_headers = ['authorization', 'cookie', 'x-api-key', 'x-auth-token']
        sanitized = {}

        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

    async def log_request_start(
        self,
        request_name: str,
        request_method: str,
        endpoint: str,
        dealer_id: Optional[str] = None,
        request_payload: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        request_ip: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Log the start of an API request (async background task)

        Args:
            request_name: Name/type of the request
            request_method: HTTP method
            endpoint: API endpoint path
            dealer_id: Optional dealer ID
            request_payload: Optional request body
            request_headers: Optional request headers
            request_ip: Optional client IP
            user_email: Optional user email

        Returns:
            Log entry ID for later updates, or None if logging failed
        """
        try:
            # Sanitize data for logging
            sanitized_payload = self._sanitize_payload(request_payload) if request_payload else None
            sanitized_headers = self._sanitize_headers(request_headers) if request_headers else None

            log_entry = self.log_repository.create_request_log(
                request_name=request_name,
                request_method=request_method,
                endpoint=endpoint,
                dealer_id=dealer_id,
                request_payload=sanitized_payload,
                request_headers=sanitized_headers,
                request_ip=request_ip,
                user_email=user_email
            )

            if log_entry:
                logger.debug(f"Started request logging for {request_name}: {log_entry.id}")
                return str(log_entry.id)
            else:
                logger.warning(f"Failed to create request log for {request_name}")
                return None

        except Exception as e:
            logger.error(f"Error logging request start for {request_name}: {str(e)}")
            return None

    async def log_request_completion(
        self,
        log_id: str,
        response_status: str,
        response_code: int,
        start_time: datetime,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Log the completion of an API request (async background task)

        Args:
            log_id: ID of the log entry to update
            response_status: Response status ('success', 'error', 'partial_success')
            response_code: HTTP status code
            start_time: Request start time for calculating processing time
            response_data: Optional response data to log
            error_message: Optional error message

        Returns:
            True if logging successful, False otherwise
        """
        try:
            # Calculate processing time
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Sanitize response data if provided
            sanitized_response = None
            if response_data:
                sanitized_response = self._sanitize_payload(response_data, max_size=5000)

            success = self.log_repository.update_response_log(
                log_id=log_id,
                response_status=response_status,
                response_code=response_code,
                processing_time_ms=processing_time_ms,
                response_data=sanitized_response,
                error_message=error_message
            )

            if success:
                logger.debug(f"Completed request logging for {log_id} (took {processing_time_ms}ms)")
            else:
                logger.warning(f"Failed to update request log {log_id}")

            return success

        except Exception as e:
            logger.error(f"Error logging request completion for {log_id}: {str(e)}")
            return False

    async def log_request_error(
        self,
        log_id: str,
        error_message: str,
        response_code: int,
        start_time: datetime
    ) -> bool:
        """
        Log an API request error (async background task)

        Args:
            log_id: ID of the log entry to update
            error_message: Error message
            response_code: HTTP status code
            start_time: Request start time

        Returns:
            True if logging successful, False otherwise
        """
        return await self.log_request_completion(
            log_id=log_id,
            response_status="error",
            response_code=response_code,
            start_time=start_time,
            error_message=error_message
        )