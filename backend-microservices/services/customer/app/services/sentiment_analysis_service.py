"""
Sentiment Analysis Service for integrating with external AI API
"""

import re
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class SentimentAnalysisService:
    """Service for sentiment analysis using external API"""
    
    def __init__(self):
        self.api_url = "https://ai.daya-group.co.id:8090/api/v1/prediction/f482750b-b270-4515-8e91-c36d1c215e0b"
        self.bearer_token = "VQF6fIutCf5Md2s7MR5qiJmvAoGJe6jynNGWydXHxyI"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "User-Agent": "SentimentAnalysisService/1.0",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        self.timeout = 120.0  # Increased timeout for AI processing
        self.max_retries = 3
        self.retry_delay = 2.0
    
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
            # Pattern 1: Look for JSON array in code blocks (```json ... ```)
            json_block_pattern = r'```json\s*(\[.*?\])\s*```'
            match = re.search(json_block_pattern, response_text, re.DOTALL | re.IGNORECASE)
            
            if match:
                json_str = match.group(1)
                logger.info("Found JSON in code block")
                return json.loads(json_str)
            
            # Pattern 2: Look for standalone JSON array anywhere in the text
            json_array_pattern = r'\[(?:[^[\]]|(?:\[[^\]]*\]))*\]'
            matches = re.findall(json_array_pattern, response_text, re.DOTALL)
            
            for match in matches:
                try:
                    # Try to parse each potential JSON array
                    parsed = json.loads(match)
                    # Verify it's a list of objects with expected structure
                    if isinstance(parsed, list) and len(parsed) > 0:
                        first_item = parsed[0]
                        if isinstance(first_item, dict) and 'id' in first_item and 'sentiment' in first_item:
                            logger.info("Found valid JSON array in text")
                            return parsed
                except json.JSONDecodeError:
                    continue
            
            # Pattern 3: Try to extract JSON from structured text response
            # Look for patterns like: "id": "...", "sentiment": "...", etc.
            logger.warning("Could not extract JSON array from response, attempting manual parsing")
            return self._manual_parse_sentiment_response(response_text)
            
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
        Make HTTP request to sentiment analysis API with retry logic.
        
        Args:
            request_data: Request payload for the API
            
        Returns:
            Response text or None if request fails
        """
        for attempt in range(self.max_retries):
            try:
                # Configure httpx client with better settings
                timeout_config = httpx.Timeout(
                    connect=10.0,    # Connection timeout
                    read=120.0,      # Read timeout for AI processing
                    write=10.0,      # Write timeout
                    pool=10.0        # Pool timeout
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
                    logger.info(f"Making sentiment analysis API request (attempt {attempt + 1}/{self.max_retries})")
                    logger.debug(f"Request URL: {self.api_url}")
                    logger.debug(f"Request headers: {dict(self.headers)}")
                    logger.debug(f"Request data: {request_data}")
                    
                    response = await client.post(
                        self.api_url,
                        headers=self.headers,
                        json=request_data
                    )
                    
                    logger.info(f"Response status: {response.status_code}")
                    logger.debug(f"Response headers: {dict(response.headers)}")
                    
                    response.raise_for_status()
                    
                    # The API returns a JSON response with a 'text' field containing the analysis
                    response_json = response.json()
                    response_text = response_json.get('text', '')
                    
                    if not response_text:
                        logger.warning("API response does not contain 'text' field")
                        logger.debug(f"Full response JSON: {response_json}")
                        return None
                    
                    logger.info(f"Sentiment analysis API request successful, response length: {len(response_text)}")
                    return response_text
                    
            except httpx.TimeoutException as e:
                logger.warning(f"API request timeout (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                
            except httpx.HTTPStatusError as e:
                error_details = ""
                try:
                    error_details = e.response.text
                except:
                    error_details = "Could not read response text"
                    
                logger.error(f"API request failed with status {e.response.status_code}: {error_details}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    # Retry on server errors
                    logger.info(f"Retrying in {self.retry_delay * (attempt + 1)} seconds...")
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    return None
                
            except Exception as e:
                logger.error(f"Unexpected error in API request (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay * (attempt + 1)} seconds...")
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        logger.error("All API request attempts failed")
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
                "id": record["id"],
                "no_tiket": record["no_tiket"],
                "review": record["review"]
            })
        
        # Convert to proper JSON string as expected by API
        question_str = json.dumps(question_data)
        
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