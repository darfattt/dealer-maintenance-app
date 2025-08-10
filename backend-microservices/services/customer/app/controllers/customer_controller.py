"""
Customer controller with business logic for customer validation
"""

import logging
from typing import Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.repositories.customer_validation_request_repository import CustomerValidationRequestRepository
from app.repositories.dealer_config_repository import DealerConfigRepository
from app.services.whatsapp_service import WhatsAppService
from app.schemas.customer_validation_request import (
    CustomerValidationRequestCreate,
    CustomerValidationResponse,
    CustomerValidationResponseData,
    WhatsAppMessageRequest
)

logger = logging.getLogger(__name__)


class CustomerController:
    """Controller for customer validation operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerValidationRequestRepository(db)
        self.dealer_repo = DealerConfigRepository(db)
        self.whatsapp_service = WhatsAppService(self.dealer_repo)
    
    def _determine_whatsapp_status(self, whatsapp_response) -> str:
        """
        Determine WhatsApp status based on Fonnte API response
        
        Args:
            whatsapp_response: WhatsAppMessageResponse object
            
        Returns:
            str: WhatsApp status ('SENT', 'FAILED', 'ERROR')
        """
        if not whatsapp_response.success:
            return 'ERROR'
        
        # Check Fonnte API response data
        response_data = whatsapp_response.response_data or {}
        
        # If status is explicitly false, it's failed
        if response_data.get('status') == False:
            return 'FAILED'
        
        # If status is true, it's sent (or queued but we'll treat as sent)
        if response_data.get('status') == True:
            return 'SENT'
        
        # If no status field or unclear, default to ERROR
        return 'ERROR'
    
    async def validate_customer(self, request_data: CustomerValidationRequestCreate) -> CustomerValidationResponse:
        """Handle customer validation request"""
        try:
            # Step 1: Validate dealer exists
            if not self.dealer_repo.validate_dealer_exists(request_data.dealerId):
                logger.warning(f"Dealer {request_data.dealerId} not found or inactive")
                return CustomerValidationResponse(
                    status=0,
                    message={"error": "Dealer tidak ditemukan atau tidak aktif"},
                    data=None
                )
            
            # Step 2: Validate dealer has Fonnte configuration
            has_config, config_error = self.dealer_repo.validate_dealer_fonnte_config(request_data.dealerId)
            if not has_config:
                logger.warning(f"Dealer {request_data.dealerId} missing Fonnte config: {config_error}")
                return CustomerValidationResponse(
                    status=0,
                    message={"error": "Konfigurasi WhatsApp tidak tersedia untuk dealer ini"},
                    data=None
                )
            
            # Step 3: Store request in database
            try:
                db_request = self.customer_repo.create(request_data, created_by='api')
                logger.info(f"Customer validation request created: {db_request.id}")
            except Exception as e:
                logger.error(f"Failed to store customer validation request: {str(e)}")
                return CustomerValidationResponse(
                    status=0,
                    message={"error": "Gagal menyimpan data ke database"},
                    data=None
                )
            
            # Step 4: Send WhatsApp message
            whatsapp_request = WhatsAppMessageRequest(
                dealer_id=request_data.dealerId,
                phone_number=request_data.noTelp,
                customer_name=request_data.namaPembawa,
                unit_type=request_data.tipeUnit,
                license_plate=request_data.noPol
            )
            
            try:
                whatsapp_response = await self.whatsapp_service.send_customer_validation_message(whatsapp_request)
                
                # Get the generated WhatsApp message from the service
                whatsapp_message = self.whatsapp_service._create_message_template(
                    customer_name=request_data.namaPembawa,
                    unit_type=request_data.tipeUnit,
                    license_plate=request_data.noPol,
                    dealer_name=self.dealer_repo.get_dealer_name(request_data.dealerId) or "Dealer"
                )
                
                # Determine WhatsApp status based on response
                whatsapp_status = self._determine_whatsapp_status(whatsapp_response)
                
                # Update request status based on WhatsApp response
                if whatsapp_response.success:
                    request_status = 'PROCESSED'
                    self.customer_repo.update_status(
                        request_id=str(db_request.id),
                        request_status=request_status,
                        whatsapp_status=whatsapp_status,
                        whatsapp_message=whatsapp_message,
                        fonnte_response=whatsapp_response.response_data,
                        modified_by='system'
                    )
                    logger.info(f"WhatsApp message sent successfully for request {db_request.id}")
                else:
                    request_status = 'FAILED'
                    self.customer_repo.update_status(
                        request_id=str(db_request.id),
                        request_status=request_status,
                        whatsapp_status=whatsapp_status,
                        whatsapp_message=whatsapp_message,
                        fonnte_response=whatsapp_response.response_data,
                        modified_by='system'
                    )
                    logger.error(f"WhatsApp message failed for request {db_request.id}: {whatsapp_response.message}")
                
                # Get updated request from database
                updated_request = self.customer_repo.get_by_id(str(db_request.id))
                
                # Return detailed response with data
                response_data = CustomerValidationResponseData(
                    request_id=str(updated_request.id),
                    dealer_id=updated_request.dealer_id,
                    request_status=updated_request.request_status,
                    whatsapp_status=updated_request.whatsapp_status,
                    whatsapp_message=updated_request.whatsapp_message or "",
                    created_at=updated_request.created_date.isoformat(),
                    fonnte_response={"status": "success"}
                )
                
                return CustomerValidationResponse(
                    status=1,
                    message={"confirmation": "Data berhasil disimpan"},
                    data=response_data
                )
                
            except Exception as e:
                logger.error(f"Error sending WhatsApp message for request {db_request.id}: {str(e)}")
                self.customer_repo.update_status(
                    request_id=str(db_request.id),
                    request_status='FAILED',
                    whatsapp_status='ERROR',
                    fonnte_response={"error": str(e)},
                    modified_by='system'
                )
                
                # Return error response with basic data
                response_data = CustomerValidationResponseData(
                    request_id=str(db_request.id),
                    dealer_id=db_request.dealer_id,
                    request_status='FAILED',
                    whatsapp_status='ERROR',
                    whatsapp_message="",
                    created_at=db_request.created_date.isoformat(),
                    fonnte_response={"error": str(e)}
                )
                
                return CustomerValidationResponse(
                    status=1,
                    message={"confirmation": "Data berhasil disimpan"},
                    data=response_data
                )
            
        except Exception as e:
            logger.error(f"Unexpected error in validate_customer: {str(e)}")
            return CustomerValidationResponse(
                status=0,
                message={"error": "Terjadi kesalahan sistem"},
                data=None
            )
    
    def get_request_by_id(self, request_id: str) -> Dict[str, Any]:
        """Get customer validation request by ID"""
        try:
            request = self.customer_repo.get_by_id(request_id)
            if not request:
                return {
                    "success": False,
                    "message": "Request not found",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Request found",
                "data": request.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting request {request_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    def get_requests_by_dealer(
        self, 
        dealer_id: str, 
        page: int = 1,
        page_size: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated customer validation requests by dealer ID with date filtering"""
        try:
            # Validate dealer exists
            if not self.dealer_repo.validate_dealer_exists(dealer_id):
                return {
                    "success": False,
                    "message": "Dealer not found or inactive",
                    "data": None
                }
            
            # Parse date strings if provided
            parsed_date_from = None
            parsed_date_to = None
            
            if date_from:
                try:
                    parsed_date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid date_from format: {date_from}")
            
            if date_to:
                try:
                    parsed_date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid date_to format: {date_to}")
            
            # Get paginated requests
            result = self.customer_repo.get_paginated_requests_by_dealer(
                dealer_id=dealer_id,
                page=page,
                page_size=page_size,
                date_from=parsed_date_from,
                date_to=parsed_date_to
            )
            
            return {
                "success": True,
                "message": f"Found {result['total']} requests",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error getting requests for dealer {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    def get_dealer_stats(
        self, 
        dealer_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get dealer statistics with WhatsApp status breakdown"""
        try:
            # Validate dealer exists
            # if not self.dealer_repo.validate_dealer_exists(dealer_id):
            #     return {
            #         "success": False,
            #         "message": "Dealer not found or inactive",
            #         "data": None
            #     }
            print("By pass validate dealer....")
            # Parse date strings if provided
            parsed_date_from = None
            parsed_date_to = None
            
            if date_from:
                try:
                    parsed_date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid date_from format: {date_from}")
            
            if date_to:
                try:
                    parsed_date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid date_to format: {date_to}")
            
            # Get dealer info
            dealer_stats = self.dealer_repo.get_dealer_stats(dealer_id) or {}
            
            # Get WhatsApp status statistics
            whatsapp_stats = self.customer_repo.get_whatsapp_status_stats(
                dealer_id=dealer_id,
                date_from=parsed_date_from,
                date_to=parsed_date_to
            )
            
            # Get general request counts
            # total_requests = self.customer_repo.count_requests_by_dealer(
            #     dealer_id=dealer_id,
            #     date_from=parsed_date_from,
            #     date_to=parsed_date_to
            # )
            #pending_requests = len(self.customer_repo.get_requests_by_status('PENDING'))
            #processed_requests = len(self.customer_repo.get_requests_by_status('PROCESSED'))
            #failed_requests = len(self.customer_repo.get_requests_by_status('FAILED'))
            
            # Merge all stats
            combined_stats = {
                **dealer_stats,
                **whatsapp_stats
            }
            
            return {
                "success": True,
                "message": "Dealer statistics retrieved",
                "data": combined_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting dealer stats for {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    async def test_whatsapp_config(self, dealer_id: str) -> Dict[str, Any]:
        """Test WhatsApp configuration for a dealer"""
        try:
            # Validate dealer exists
            if not self.dealer_repo.validate_dealer_exists(dealer_id):
                return {
                    "success": False,
                    "message": "Dealer not found or inactive"
                }
            
            # Test Fonnte connection
            result = await self.whatsapp_service.test_fonnte_connection(dealer_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing WhatsApp config for dealer {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }