"""
Customer reminder controller with business logic for customer reminders
"""

import logging
from typing import Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.repositories.customer_reminder_request_repository import CustomerReminderRequestRepository
from app.repositories.dealer_config_repository import DealerConfigRepository
from app.repositories.customer_reminder_processing_repository import CustomerReminderProcessingRepository
from app.repositories.whatsapp_template_repository import WhatsAppTemplateRepository
from app.services.whatsapp_service import WhatsAppService
from app.schemas.customer_reminder_request import (
    CustomerReminderRequestCreate,
    CustomerReminderResponse,
    CustomerReminderResponseData,
    WhatsAppReminderRequest,
    ReminderType,
    BulkReminderRequest,
    BulkReminderResponse,
    BulkReminderCustomerData
)

logger = logging.getLogger(__name__)


class CustomerReminderController:
    """Controller for customer reminder operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.reminder_repo = CustomerReminderRequestRepository(db)
        self.dealer_repo = DealerConfigRepository(db)
        self.processing_repo = CustomerReminderProcessingRepository(db)
        self.template_repo = WhatsAppTemplateRepository(db)
        self.whatsapp_service = WhatsAppService(self.dealer_repo)
    
    def _determine_whatsapp_status(self, whatsapp_response) -> str:
        """
        Determine WhatsApp status based on Fonnte API response
        
        Args:
            whatsapp_response: WhatsAppReminderResponse object
            
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
    
    
    async def add_bulk_reminders(self, request_data: BulkReminderRequest, dealer_id: str) -> BulkReminderResponse:
        """Handle bulk customer reminder creation"""
        try:
            # Step 1: Validate dealer exists
            if not self.dealer_repo.validate_dealer_exists(dealer_id):
                logger.warning(f"Dealer {dealer_id} not found or inactive")
                return BulkReminderResponse(
                    status=0,
                    message={"error": "Dealer tidak ditemukan atau tidak aktif"},
                    data=None
                )
            
            # Step 2: Validate dealer has Fonnte configuration
            has_config, config_error = self.dealer_repo.validate_dealer_fonnte_config(dealer_id)
            if not has_config:
                logger.warning(f"Dealer {dealer_id} missing Fonnte config: {config_error}")
                return BulkReminderResponse(
                    status=0,
                    message={"error": "Konfigurasi WhatsApp tidak tersedia untuk dealer ini"},
                    data=None
                )
            
            # Step 3: Create processing tracker
            processing_tracker = self.processing_repo.create_processing_tracker(
                created_by='api'
            )
            transaction_id = processing_tracker.transaction_id
            
            # Step 4: Process each customer in the bulk request
            total_customers = len(request_data.data)
            successful_reminders = 0
            failed_reminders = 0
            
            logger.info(f"Processing {total_customers} customer reminders for dealer {dealer_id} (transaction: {transaction_id})")
            
            for customer_data in request_data.data:
                try:
                    # Create individual reminder record with transaction_id
                    db_request = self.reminder_repo.create_bulk_reminder(
                        customer_data=customer_data,
                        ahass_data={
                            "kode_ahass": request_data.kode_ahass,
                            "nama_ahass": request_data.nama_ahass,
                            "alamat_ahass": request_data.alamat_ahass
                        },
                        reminder_target=request_data.filter_target,
                        reminder_type=request_data.filter_data,
                        dealer_id=dealer_id,
                        transaction_id=transaction_id,
                        created_by='api'
                    )
                    
                    # Send WhatsApp message to customer using enhanced template formatting
                    whatsapp_message = self._create_bulk_reminder_message_template(
                        customer_data=customer_data,
                        reminder_target=request_data.filter_target,
                        reminder_type=request_data.filter_data,
                        ahass_data={
                            "kode_ahass": request_data.kode_ahass,
                            "nama_ahass": request_data.nama_ahass,
                            "alamat_ahass": request_data.alamat_ahass
                        },
                        dealer_name=self.dealer_repo.get_dealer_name(dealer_id) or "Dealer"
                    )
                    
                    try:
                        # Send WhatsApp to customer phone number
                        whatsapp_response = await self._send_bulk_reminder_whatsapp(
                            dealer_id=dealer_id,
                            phone_number=customer_data.nomor_telepon_pelanggan,
                            nama_pelanggan=customer_data.nama_pelanggan,
                            message=whatsapp_message
                        )
                        
                        # Determine WhatsApp status
                        whatsapp_status = self._determine_whatsapp_status(whatsapp_response)
                        
                        # Update request status
                        request_status = 'PROCESSED' if whatsapp_response.success else 'FAILED'
                        self.reminder_repo.update_status(
                            request_id=str(db_request.id),
                            request_status=request_status,
                            whatsapp_status=whatsapp_status,
                            whatsapp_message=whatsapp_message,
                            fonnte_response=whatsapp_response.response_data,
                            modified_by='system'
                        )
                        
                        if whatsapp_response.success:
                            successful_reminders += 1
                            logger.info(f"WhatsApp reminder sent successfully for customer {customer_data.nama_pelanggan}")
                        else:
                            failed_reminders += 1
                            logger.error(f"WhatsApp reminder failed for customer {customer_data.nama_pelanggan}")
                        
                        # Update processing progress
                        progress = round((successful_reminders + failed_reminders) / total_customers * 100)
                        self.processing_repo.update_progress(
                            transaction_id=transaction_id,
                            progress=progress,
                            modified_by='system'
                        )
                            
                    except Exception as e:
                        failed_reminders += 1
                        logger.error(f"Error sending WhatsApp for customer {customer_data.nama_pelanggan}: {str(e)}")
                        self.reminder_repo.update_status(
                            request_id=str(db_request.id),
                            request_status='FAILED',
                            whatsapp_status='ERROR',
                            fonnte_response={"error": str(e)},
                            modified_by='system'
                        )
                        
                        # Update processing progress
                        progress = round((successful_reminders + failed_reminders) / total_customers * 100)
                        self.processing_repo.update_progress(
                            transaction_id=transaction_id,
                            progress=progress,
                            modified_by='system'
                        )
                        
                except Exception as e:
                    failed_reminders += 1
                    logger.error(f"Error processing customer {customer_data.nama_pelanggan}: {str(e)}")
                    
                    # Update processing progress even on error
                    progress = round((successful_reminders + failed_reminders) / total_customers * 100)
                    self.processing_repo.update_progress(
                        transaction_id=transaction_id,
                        progress=progress,
                        modified_by='system'
                    )
            
            # Mark processing as completed
            self.processing_repo.update_status(
                transaction_id=transaction_id,
                status='completed',
                progress=100,
                modified_by='system'
            )
            
            # Calculate success rate
            success_rate = round((successful_reminders / total_customers * 100) if total_customers > 0 else 0, 2)
            
            # Return response with statistics
            return BulkReminderResponse(
                status=1,
                message={"confirmation": "Bulk reminders berhasil diproses"},
                data={
                    "transaction_id": str(transaction_id),
                    "total_customers": total_customers,
                    "successful_reminders": successful_reminders,
                    "failed_reminders": failed_reminders,
                    "success_rate": success_rate,
                    "processing_status": "completed",
                    "kode_ahass": request_data.kode_ahass,
                    "filter_target": request_data.filter_target,
                    "filter_data": request_data.filter_data
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in add_bulk_reminders: {str(e)}")
            return BulkReminderResponse(
                status=0,
                message={"error": "Terjadi kesalahan sistem"},
                data=None
            )
    
    def _create_bulk_reminder_message_template(
        self, 
        customer_data,
        reminder_target: str, 
        reminder_type: str, 
        ahass_data: Dict[str, Any],
        dealer_name: str
    ) -> str:
        """Create WhatsApp message template for bulk reminders using enhanced database templates"""
        
        # Try to get template from database with complete customer data
        formatted_message = self.template_repo.format_template_with_customer_data(
            reminder_target=reminder_target,
            reminder_type=reminder_type,
            customer_data=customer_data,
            ahass_data=ahass_data,
            dealer_name=dealer_name
        )
        
        if formatted_message:
            return formatted_message
        
        # Fallback to basic template if no database template found
        logger.warning(f"No template found for {reminder_target} - {reminder_type}, using fallback")
        customer_name = getattr(customer_data, 'nama_pelanggan', 'Bpk/Ibu')
        return f"""Halo {customer_name},

Ini adalah pengingat dari {dealer_name} terkait {reminder_target}.

{reminder_type}

Terima kasih atas perhatian Anda.

Salam,
{dealer_name}"""
    
    async def _send_bulk_reminder_whatsapp(self, dealer_id: str, phone_number: str, nama_pelanggan: str, message: str):
        """Send WhatsApp message for bulk reminder using Fonnte API"""
        return await self.whatsapp_service.send_reminder_message(
            dealer_id=dealer_id,
            phone_number=phone_number,
            customer_name=nama_pelanggan,
            message=message
        )

# NOTE: create_reminder method has been removed and replaced with add_bulk_reminders
    
    async def _send_reminder_whatsapp(self, request: WhatsAppReminderRequest, message: str):
        """Send WhatsApp reminder message using existing service"""
        # This is a simplified implementation that adapts the existing WhatsApp service
        # In a real implementation, you might extend the WhatsAppService to handle reminders
        from app.schemas.customer_validation_request import WhatsAppMessageRequest
        
        # Convert reminder request to validation request format
        whatsapp_msg_request = WhatsAppMessageRequest(
            dealer_id=request.dealer_id,
            phone_number=request.phone_number,
            customer_name=request.nama_pelanggan,
            unit_type="",  # Not applicable for reminders
            license_plate=""  # Not applicable for reminders
        )
        
        # Use existing WhatsApp service but with custom message
        try:
            # For now, return a mock successful response
            # In production, you would integrate with the actual Fonnte API
            return type('WhatsAppResponse', (), {
                'success': True,
                'message': 'Reminder sent successfully',
                'response_data': {
                    'status': True,
                    'id': ['reminder_id_123'],
                    'requestid': 123456
                }
            })()
        except Exception as e:
            return type('WhatsAppResponse', (), {
                'success': False,
                'message': f'Failed to send reminder: {str(e)}',
                'response_data': {'error': str(e)}
            })()
    
    def get_reminder_by_id(self, request_id: str) -> Dict[str, Any]:
        """Get customer reminder request by ID"""
        try:
            reminder = self.reminder_repo.get_by_id(request_id)
            if not reminder:
                return {
                    "success": False,
                    "message": "Reminder not found",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Reminder found",
                "data": reminder.to_safe_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting reminder {request_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    def get_reminders_by_dealer(
        self, 
        dealer_id: str, 
        page: int = 1,
        page_size: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        reminder_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated customer reminder requests by dealer ID with filtering"""
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
            
            # Get paginated reminders
            result = self.reminder_repo.get_paginated_requests_by_dealer(
                dealer_id=dealer_id,
                page=page,
                page_size=page_size,
                date_from=parsed_date_from,
                date_to=parsed_date_to,
                reminder_target=reminder_target
            )
            
            return {
                "success": True,
                "message": f"Found {result['total']} reminders",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error getting reminders for dealer {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    def get_reminder_stats(
        self, 
        dealer_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        reminder_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get dealer reminder statistics with breakdown by type and status"""
        try:
            # Validate dealer exists (bypass for now, similar to customer controller)
            print("Bypassing dealer validation for reminders...")
            
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
            
            # Get WhatsApp status statistics
            whatsapp_stats = self.reminder_repo.get_whatsapp_status_stats(
                dealer_id=dealer_id,
                date_from=parsed_date_from,
                date_to=parsed_date_to,
                reminder_target=reminder_target
            )
            
            # Get reminder type statistics
            reminder_type_stats = self.reminder_repo.get_reminder_type_stats(
                dealer_id=dealer_id,
                date_from=parsed_date_from,
                date_to=parsed_date_to,
                reminder_target=reminder_target
            )
            
            # Get reminder target statistics
            reminder_target_stats = self.reminder_repo.get_reminder_target_stats(
                dealer_id=dealer_id,
                date_from=parsed_date_from,
                date_to=parsed_date_to,
                reminder_target=reminder_target
            )
            
            # Combine all stats
            combined_stats = {
                **whatsapp_stats,
                "reminder_type_breakdown": reminder_type_stats,
                "reminder_target_breakdown": reminder_target_stats
            }
            
            return {
                "success": True,
                "message": "Dealer reminder statistics retrieved",
                "data": combined_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting reminder stats for {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    def get_reminders_by_transaction_id(self, transaction_id: str) -> Dict[str, Any]:
        """Get customer reminder requests by transaction ID without pagination"""
        try:
            # Validate transaction_id is provided
            if not transaction_id:
                return {
                    "success": False,
                    "message": "Transaction ID is required",
                    "data": None
                }
            
            # Get reminders by transaction ID
            result = self.reminder_repo.get_reminders_by_transaction_id(transaction_id)
            
            return {
                "success": True,
                "message": f"Found {result['total']} reminders for transaction",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error getting reminders for transaction {transaction_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": None
            }
    
    async def test_reminder_whatsapp_config(self, dealer_id: str) -> Dict[str, Any]:
        """Test WhatsApp configuration for reminder sending"""
        try:
            # Validate dealer exists
            if not self.dealer_repo.validate_dealer_exists(dealer_id):
                return {
                    "success": False,
                    "message": "Dealer not found or inactive"
                }
            
            # Test Fonnte connection using existing service
            result = await self.whatsapp_service.test_fonnte_connection(dealer_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing reminder WhatsApp config for dealer {dealer_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }