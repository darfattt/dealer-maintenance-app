"""
Sentiment Analysis Service for integrating with external AI API
"""

import re
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation for external service resilience"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
    
    def is_available(self) -> bool:
        """Check if the circuit breaker allows requests"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and (datetime.utcnow() - self.last_failure_time).total_seconds() > self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning from OPEN to HALF_OPEN")
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker transitioning from HALF_OPEN to CLOSED after successful request")
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPENING after {self.failure_count} failures")
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker transitioning from HALF_OPEN to OPEN after failure")


class SentimentAnalysisService:
    """Service for sentiment analysis using external API"""
    
    def __init__(self):
        self.api_url = settings.sentiment_api_url
        self.bearer_token = settings.sentiment_api_token
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "User-Agent": "SentimentAnalysisService/1.0",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        self.timeout = float(settings.sentiment_api_timeout)
        self.max_retries = settings.sentiment_api_max_retries
        self.retry_delay = settings.sentiment_api_retry_delay
        self.connect_timeout = settings.sentiment_api_connect_timeout
        self.read_timeout = settings.sentiment_api_read_timeout
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=settings.sentiment_circuit_breaker_failure_threshold,
            timeout=settings.sentiment_circuit_breaker_timeout
        )
    
    def _extract_json_from_response_text(self, response_text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extract JSON array from response text using regex pattern matching.
        
        The API returns a text response that contains a JSON array somewhere in the text.
        We need to extract and parse this JSON array.
        
        Args:
            response_text: Raw text response from the API
            
        Returns:
            List of sentiment analysis results or None if extraction fails
        """
        try:
            logger.info("Starting JSON extraction from API response")
            
            # Pattern 1: Look for JSON array in code blocks (```json ... ```)
            json_block_pattern = r'```json\s*(\[.*?\])\s*```'
            match = re.search(json_block_pattern, response_text, re.DOTALL | re.IGNORECASE)
            
            if match:
                json_str = match.group(1)
                logger.info("Found JSON in code block, parsing...")
                try:
                    parsed_data = json.loads(json_str)
                    logger.info(f"Successfully parsed JSON from code block: {len(parsed_data) if isinstance(parsed_data, list) else 1} items")
                    return parsed_data
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from code block: {e}")
                    # Continue to other patterns
            
            # Pattern 2: Look for standalone JSON array anywhere in the text
            logger.info("Searching for standalone JSON arrays in response text")
            json_array_pattern = r'\[(?:[^[\]]|(?:\[[^\]]*\]))*\]'
            matches = re.findall(json_array_pattern, response_text, re.DOTALL)
            
            logger.info(f"Found {len(matches)} potential JSON arrays")
            for i, match in enumerate(matches):
                try:
                    logger.debug(f"Attempting to parse JSON array {i+1}: {match[:100]}...")
                    # Try to parse each potential JSON array
                    parsed = json.loads(match)
                    # Verify it's a list of objects with expected structure
                    if isinstance(parsed, list) and len(parsed) > 0:
                        first_item = parsed[0]
                        if isinstance(first_item, dict) and 'id' in first_item and 'sentiment' in first_item:
                            logger.info(f"Found valid JSON array in text (pattern {i+1}): {len(parsed)} items")
                            return parsed
                        else:
                            logger.debug(f"JSON array {i+1} doesn't have expected structure: keys={list(first_item.keys()) if isinstance(first_item, dict) else type(first_item)}")
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON array {i+1}: {e}")
                    continue
            
            # Pattern 3: Try to extract JSON from structured text response
            # Look for patterns like: "id": "...", "sentiment": "...", etc.
            logger.warning("Could not extract JSON array from response, attempting manual parsing")
            logger.debug(f"Response text that failed parsing (first 1000 chars): {response_text[:1000]}")
            
            manual_results = self._manual_parse_sentiment_response(response_text)
            if manual_results:
                logger.info(f"Manual parsing successful: {len(manual_results)} items extracted")
                return manual_results
            else:
                logger.error("All parsing methods failed - no sentiment data could be extracted")
                return None
            
        except Exception as e:
            logger.error(f"Error extracting JSON from response: {str(e)}")
            return None
    
    def _manual_parse_sentiment_response(self, response_text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Manually parse sentiment response when JSON extraction fails.
        
        This is a fallback method to extract sentiment data from structured text.
        """
        try:
            results = []
            
            # Split response by record indicators
            # Look for patterns like "1. **Review ID: ..." or similar
            record_pattern = r'(\d+)\.\s*\*\*Review ID:\s*([\w\-]+)\*\*'
            records = re.split(record_pattern, response_text)
            
            for i in range(1, len(records), 3):
                try:
                    record_num = records[i]
                    record_id = records[i + 1]
                    record_content = records[i + 2] if i + 2 < len(records) else ""
                    
                    # Extract sentiment data using regex
                    review_match = re.search(r'\*\*Review\*\*:\s*["\']([^"\']+)["\']', record_content)
                    sentiment_match = re.search(r'\*\*Sentiment\*\*:\s*(\w+)', record_content)
                    score_match = re.search(r'\*\*Score\*\*:\s*([-\d\.]+)', record_content)
                    reasons_match = re.search(r'\*\*Reasons\*\*:\s*([^\n]+)', record_content)
                    themes_match = re.search(r'\*\*Themes\*\*:\s*\[([^\]]+)\]', record_content)
                    suggestion_match = re.search(r'\*\*Suggestion\*\*:\s*([^\n]+)', record_content)
                    
                    if sentiment_match:
                        # Extract no_tiket (might be in the content or need to be passed separately)
                        no_tiket = ""  # This would need to be matched from the original request
                        
                        result = {
                            "id": record_id,
                            "no_tiket": no_tiket,
                            "review": review_match.group(1) if review_match else "",
                            "sentiment": sentiment_match.group(1),
                            "score": float(score_match.group(1)) if score_match else 0.0,
                            "reasons": reasons_match.group(1).strip() if reasons_match else "",
                            "themes": [theme.strip().strip('"') for theme in themes_match.group(1).split(',')] if themes_match else [],
                            "suggestion": suggestion_match.group(1).strip() if suggestion_match and suggestion_match.group(1).lower() != 'null' else None
                        }
                        results.append(result)
                
                except Exception as e:
                    logger.warning(f"Error parsing record {i}: {str(e)}")
                    continue
            
            return results if results else None
            
        except Exception as e:
            logger.error(f"Manual parsing failed: {str(e)}")
            return None
    
    async def _make_api_request(self, request_data: Dict[str, Any]) -> Optional[str]:
        """
        Make HTTP request to sentiment analysis API with circuit breaker and exponential backoff.
        
        Args:
            request_data: Request payload for the API
            
        Returns:
            Response text or None if request fails
        """
        # Check circuit breaker state
        if not self.circuit_breaker.is_available():
            logger.warning(f"Circuit breaker is {self.circuit_breaker.state.value}, skipping sentiment analysis request")
            return None
        
        for attempt in range(self.max_retries):
            try:
                # Configure httpx client with improved timeout settings
                timeout_config = httpx.Timeout(
                    connect=float(self.connect_timeout),    # Connection timeout
                    read=float(self.read_timeout),          # Read timeout for AI processing (reduced)
                    write=10.0,                             # Write timeout
                    pool=10.0                               # Pool timeout
                )
                
                # Configure client with SSL and connection settings
                async with httpx.AsyncClient(
                    timeout=timeout_config,
                    verify=True,  # SSL verification
                    follow_redirects=True,
                    limits=httpx.Limits(
                        max_keepalive_connections=5,
                        max_connections=10
                    )
                ) as client:
                    # Calculate exponential backoff delay for this attempt
                    if attempt > 0:
                        backoff_delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                        logger.info(f"Waiting {backoff_delay:.2f}s before retry {attempt + 1}")
                        await asyncio.sleep(backoff_delay)
                    
                    logger.info(f"Making sentiment analysis API request (attempt {attempt + 1}/{self.max_retries})")
                    logger.debug(f"Circuit breaker state: {self.circuit_breaker.state.value}")
                    print(f"Request URL: {self.api_url}")
                    logger.debug(f"Request headers: {dict(self.headers)}")
                    print(f"Request data: {json.dumps(request_data)}")
                    response = await client.post(
                        self.api_url,
                        headers=self.headers,
                        json=request_data
                    )
                    
                    logger.debug(f"Response headers: {dict(response.headers)}")
                    
                    response.raise_for_status()
                    
                    # The API returns a JSON response with a 'text' field containing the analysis
                    response_json = response.json()
                    response_text = response_json.get('text', '')
                    
                    # Add comprehensive logging to debug response format
                    logger.info(f"API Response Status: {response.status_code}")
                    logger.info(f"API Response JSON Keys: {list(response_json.keys())}")
                    logger.debug(f"Full API Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    if not response_text:
                        logger.warning("API response does not contain 'text' field")
                        logger.warning(f"Available response keys: {list(response_json.keys())}")
                        logger.debug(f"Full response JSON: {response_json}")
                        # This is still considered a successful response for circuit breaker
                        self.circuit_breaker.record_success()
                        return None
                    
                    print(f"Sentiment analysis API request successful, response text length: {len(response_text)}")
                    logger.debug(f"Raw response text content: {response_text[:500]}..." if len(response_text) > 500 else response_text)
                    
                    # Record success in circuit breaker
                    self.circuit_breaker.record_success()
                    return response_text
                    
            except httpx.TimeoutException as e:
                logger.warning(f"API request timeout (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                self.circuit_breaker.record_failure()
                
                if attempt >= self.max_retries - 1:
                    break
                
            except httpx.HTTPStatusError as e:
                error_details = ""
                try:
                    error_details = e.response.text
                except:
                    error_details = "Could not read response text"
                    
                logger.error(f"API request failed with status {e.response.status_code}: {error_details}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                
                # Only record as failure for 5xx errors (server issues)
                if e.response.status_code >= 500:
                    self.circuit_breaker.record_failure()
                    
                    if attempt >= self.max_retries - 1:
                        break
                else:
                    # Client errors (4xx) don't trigger circuit breaker
                    logger.error(f"Client error {e.response.status_code}, not retrying")
                    return None
                
            except Exception as e:
                logger.error(f"Unexpected error in API request (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                self.circuit_breaker.record_failure()
                
                if attempt >= self.max_retries - 1:
                    break
        
        logger.error(f"All API request attempts failed. Circuit breaker state: {self.circuit_breaker.state.value}")
        return None
    
    def _format_request_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format records for API request.
        
        Args:
            records: List of records with id, no_tiket, and review (from inbox field)
            
        Returns:
            Formatted request data for the API
        """
        # Format records as required by API
        question_data = []
        for record in records:
            question_data.append({
                'id': record["id"],
                'no_tiket': record["no_tiket"],
                'review': record["review"]
            })
        
        # Convert to proper JSON string as expected by API
        question_str = json.dumps(question_data).replace('"', "'")

        return {
            "question": question_str
        }
    
    async def analyze_sentiments(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Analyze sentiments for a batch of records.
        
        Args:
            records: List of records with id, no_tiket, and review fields
            
        Returns:
            Tuple of (successful_results, error_messages)
        """
        if not records:
            return [], []
        
        try:
            # Format request data
            request_data = self._format_request_data(records)
            
            logger.info(f"Analyzing sentiment for {len(records)} records")
            
            # Make API request
            response_text = await self._make_api_request(request_data)
            
            if not response_text:
                error_msg = "Failed to get response from sentiment analysis API"
                logger.error(error_msg)
                return [], [error_msg]
            
            # Extract sentiment results from response text
            sentiment_results = self._extract_json_from_response_text(response_text)
            
            if not sentiment_results:
                error_msg = "Failed to extract sentiment analysis results from API response"
                logger.error(error_msg)
                return [], [error_msg]
            
            # Validate and enrich results
            valid_results = []
            errors = []
            
            for result in sentiment_results:
                try:
                    # Validate required fields
                    required_fields = ['id', 'sentiment', 'score']
                    if not all(field in result for field in required_fields):
                        errors.append(f"Missing required fields in result for ID {result.get('id', 'unknown')}")
                        continue
                    
                    # Normalize sentiment values
                    sentiment = result['sentiment'].strip().title()  # Normalize to Positive/Negative/Neutral
                    if sentiment not in ['Positive', 'Negative', 'Neutral']:
                        # Try to map common variations
                        sentiment_mapping = {
                            'Positif': 'Positive',
                            'Negatif': 'Negative',
                            'Netral': 'Neutral'
                        }
                        sentiment = sentiment_mapping.get(sentiment, sentiment)
                    
                    # Validate score range
                    score = float(result['score'])
                    if not (-5.0 <= score <= 5.0):
                        logger.warning(f"Score {score} outside expected range for ID {result['id']}")
                        score = max(-5.0, min(5.0, score))  # Clamp to valid range
                    
                    # Format themes as JSON string
                    themes = result.get('themes', [])
                    if isinstance(themes, list):
                        themes_json = json.dumps(themes)
                    else:
                        themes_json = json.dumps([])
                    
                    # Build validated result
                    validated_result = {
                        'id': result['id'],
                        'sentiment': sentiment,
                        'sentiment_score': score,
                        'sentiment_reasons': result.get('reasons', '').strip(),
                        'sentiment_suggestion': result.get('suggestion', '').strip() if result.get('suggestion') and result.get('suggestion').lower() != 'null' else None,
                        'sentiment_themes': themes_json,
                        'sentiment_analyzed_at': datetime.utcnow()
                    }
                    
                    valid_results.append(validated_result)
                    
                except Exception as e:
                    error_msg = f"Error processing result for ID {result.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            logger.info(f"Sentiment analysis completed: {len(valid_results)} successful, {len(errors)} errors")
            return valid_results, errors
            
        except Exception as e:
            error_msg = f"Unexpected error in sentiment analysis: {str(e)}"
            logger.error(error_msg)
            return [], [error_msg]
    
    async def analyze_single_record(self, record: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze sentiment for a single record.
        
        Args:
            record: Record with id, no_tiket, and review fields
            
        Returns:
            Tuple of (result_dict, error_message)
        """
        results, errors = await self.analyze_sentiments([record])
        
        if results:
            return results[0], None
        elif errors:
            return None, errors[0]
        else:
            return None, "Unknown error in sentiment analysis"