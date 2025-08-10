"""
WhatsApp service using Fonnte API with per-dealer configuration
"""

import logging
import requests
from typing import Optional, Dict, Any
from app.repositories.dealer_config_repository import DealerConfigRepository
from app.schemas.customer_validation_request import WhatsAppMessageRequest, WhatsAppMessageResponse

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending WhatsApp messages via Fonnte API"""
    
    def __init__(self, dealer_config_repo: DealerConfigRepository):
        self.dealer_config_repo = dealer_config_repo
        self.default_timeout = 30
    
    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number for international use"""
        # Remove spaces, dashes, and other formatting
        cleaned = phone_number.replace(' ', '').replace('-', '').replace('+', '')
        
        # Convert Indonesian format to international
        if cleaned.startswith('0'):
            cleaned = '62' + cleaned[1:]
        elif not cleaned.startswith('62'):
            cleaned = '62' + cleaned
        
        return cleaned
    
    def _create_message_template(self, customer_name: str, unit_type: str, license_plate: str, dealer_name: str) -> str:
        """Create WhatsApp message template"""
        message = f"""Halo {customer_name},

Terima kasih telah melakukan validasi customer untuk unit {unit_type} dengan nomor polisi {license_plate}.

Data Anda telah kami terima dan sedang dalam proses verifikasi oleh tim {dealer_name}.

Kami akan menghubungi Anda kembali untuk proses selanjutnya.

Terima kasih atas kepercayaan Anda.

Best regards,
{dealer_name}"""
        
        return message
    
    async def send_customer_validation_message(
        self, 
        request: WhatsAppMessageRequest
    ) -> WhatsAppMessageResponse:
        """Send WhatsApp message for customer validation"""
        try:
            # Get dealer's Fonnte configuration
            fonnte_config = self.dealer_config_repo.get_fonnte_config(request.dealer_id)
            
            if not fonnte_config:
                logger.error(f"No Fonnte configuration found for dealer {request.dealer_id}")
                return WhatsAppMessageResponse(
                    success=False,
                    message=f"Fonnte configuration not found for dealer {request.dealer_id}",
                    response_data=None
                )
            
            # Format phone number
            formatted_phone = self._format_phone_number(request.phone_number)
            
            # Create message
            message = self._create_message_template(
                customer_name=request.customer_name,
                unit_type=request.unit_type,
                license_plate=request.license_plate,
                dealer_name=fonnte_config['dealer_name']
            )
            
            # Prepare Fonnte API request
            api_url = fonnte_config['api_url']
            api_key = fonnte_config['api_key']
            
            payload = {
                'target': formatted_phone,
                'message': message,
                'countryCode': '62'
            }
            
            headers = {
                'Authorization': api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            logger.info(f"Sending WhatsApp message to {formatted_phone} via dealer {request.dealer_id}")
            
            # Send request to Fonnte API
            response = requests.post(
                api_url,
                data=payload,
                headers=headers,
                timeout=self.default_timeout
            )
            
            response_data = {}
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"raw_response": response.text}
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {formatted_phone}")
                return WhatsAppMessageResponse(
                    success=True,
                    message="WhatsApp message sent successfully",
                    response_data=response_data
                )
            else:
                logger.error(f"Failed to send WhatsApp message: {response.status_code} - {response.text}")
                return WhatsAppMessageResponse(
                    success=False,
                    message=f"Failed to send WhatsApp message: {response.status_code}",
                    response_data=response_data
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending WhatsApp message to {request.phone_number}")
            return WhatsAppMessageResponse(
                success=False,
                message="Timeout while sending WhatsApp message",
                response_data={"error": "timeout"}
            )
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error sending WhatsApp message to {request.phone_number}")
            return WhatsAppMessageResponse(
                success=False,
                message="Connection error while sending WhatsApp message",
                response_data={"error": "connection_error"}
            )
            
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {str(e)}")
            return WhatsAppMessageResponse(
                success=False,
                message=f"Unexpected error: {str(e)}",
                response_data={"error": "unexpected_error", "details": str(e)}
            )
    
    def validate_fonnte_config(self, dealer_id: str) -> tuple[bool, Optional[str]]:
        """Validate Fonnte configuration for a dealer"""
        return self.dealer_config_repo.validate_dealer_fonnte_config(dealer_id)
    
    async def test_fonnte_connection(self, dealer_id: str) -> Dict[str, Any]:
        """Test Fonnte API connection for a dealer"""
        try:
            # Get dealer's Fonnte configuration
            fonnte_config = self.dealer_config_repo.get_fonnte_config(dealer_id)
            
            if not fonnte_config:
                return {
                    "success": False,
                    "message": f"No Fonnte configuration found for dealer {dealer_id}"
                }
            
            # Test with a simple API call (you might need to adjust this based on Fonnte's test endpoint)
            api_url = fonnte_config['api_url']
            api_key = fonnte_config['api_key']
            
            # Simple test payload (adjust based on Fonnte's documentation)
            test_payload = {
                'target': '628123456789',  # Test number
                'message': 'Test message from customer service',
                'countryCode': '62'
            }
            
            headers = {
                'Authorization': api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                api_url,
                data=test_payload,
                headers=headers,
                timeout=10
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "message": "Connection test completed",
                "response_data": response.text[:200] if response.text else None
            }
            
        except Exception as e:
            logger.error(f"Error testing Fonnte connection for dealer {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error testing connection: {str(e)}"
            }