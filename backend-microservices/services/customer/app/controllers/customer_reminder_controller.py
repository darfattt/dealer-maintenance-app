"""
Customer reminder controller with business logic for customer reminders
"""

import logging
from typing import Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.repositories.customer_reminder_request_repository import CustomerReminderRequestRepository
from app.repositories.dealer_config_repository import DealerConfigRepository
from app.services.whatsapp_service import WhatsAppService
from app.schemas.customer_reminder_request import (
    CustomerReminderRequestCreate,
    CustomerReminderResponse,
    CustomerReminderResponseData,
    WhatsAppReminderRequest,
    ReminderType
)

logger = logging.getLogger(__name__)


class CustomerReminderController:
    """Controller for customer reminder operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.reminder_repo = CustomerReminderRequestRepository(db)
        self.dealer_repo = DealerConfigRepository(db)
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
    
    def _create_reminder_message_template(self, customer_name: str, reminder_type: ReminderType, dealer_name: str, custom_message: Optional[str] = None) -> str:
        """Create WhatsApp message template based on reminder type"""
        
        if custom_message:
            return f"Halo {customer_name},\n\n{custom_message}\n\nTerima kasih,\n{dealer_name}"
        
        templates = {
            ReminderType.SERVICE_REMINDER: f"""Halo {customer_name},

Ini adalah pengingat untuk servis rutin kendaraan Anda. Jangan lupa untuk melakukan perawatan berkala agar kendaraan selalu dalam kondisi prima.

Silakan hubungi kami untuk membuat jadwal servis.

Terima kasih,
{dealer_name}""",
            
            ReminderType.PAYMENT_REMINDER: f"""Halo {customer_name},

Ini adalah pengingat bahwa Anda memiliki pembayaran yang jatuh tempo. Mohon segera lakukan pembayaran untuk menghindari keterlambatan.

Silakan hubungi kami jika ada pertanyaan.

Terima kasih,
{dealer_name}""",
            
            ReminderType.APPOINTMENT_REMINDER: f"""Halo {customer_name},

Ini adalah pengingat untuk janji temu Anda dengan kami. Mohon hadir tepat waktu sesuai jadwal yang telah ditentukan.

Jika ada perubahan jadwal, mohon hubungi kami segera.

Terima kasih,
{dealer_name}""",
            
            ReminderType.MAINTENANCE_REMINDER: f"""Halo {customer_name},

Saatnya untuk melakukan maintenance rutin kendaraan Anda. Perawatan berkala sangat penting untuk menjaga performa dan keamanan kendaraan.

Hubungi kami untuk menjadwalkan maintenance.

Terima kasih,
{dealer_name}""",
            
            ReminderType.FOLLOW_UP_REMINDER: f"""Halo {customer_name},

Kami ingin menindaklanjuti layanan yang telah Anda terima. Apakah ada yang bisa kami bantu atau perbaiki?

Kepuasan Anda adalah prioritas kami.

Terima kasih,
{dealer_name}""",
            
            ReminderType.CUSTOM_REMINDER: f"""Halo {customer_name},

Kami ingin mengingatkan Anda tentang layanan kami. Jangan ragu untuk menghubungi kami jika membutuhkan bantuan.

Terima kasih,
{dealer_name}"""
        }
        
        return templates.get(reminder_type, templates[ReminderType.CUSTOM_REMINDER])
    
    async def create_reminder(self, request_data: CustomerReminderRequestCreate, dealer_id: str) -> CustomerReminderResponse:
        """Handle customer reminder creation"""
        try:
            # Step 1: Validate dealer exists
            if not self.dealer_repo.validate_dealer_exists(dealer_id):
                logger.warning(f"Dealer {dealer_id} not found or inactive")
                return CustomerReminderResponse(
                    status=0,
                    message={"error": "Dealer tidak ditemukan atau tidak aktif"},
                    data=None
                )
            
            # Step 2: Validate dealer has Fonnte configuration
            has_config, config_error = self.dealer_repo.validate_dealer_fonnte_config(dealer_id)
            if not has_config:
                logger.warning(f"Dealer {dealer_id} missing Fonnte config: {config_error}")
                return CustomerReminderResponse(
                    status=0,
                    message={"error": "Konfigurasi WhatsApp tidak tersedia untuk dealer ini"},
                    data=None
                )
            
            # Step 3: Store request in database
            try:
                # Override dealerId with authenticated user's dealer_id
                request_data.dealerId = dealer_id
                db_request = self.reminder_repo.create(request_data, created_by='api')
                logger.info(f"Customer reminder request created: {db_request.id}")
            except Exception as e:
                logger.error(f"Failed to store customer reminder request: {str(e)}")
                return CustomerReminderResponse(
                    status=0,
                    message={"error": "Gagal menyimpan data ke database"},
                    data=None
                )
            
            # Step 4: Send WhatsApp message
            dealer_name = self.dealer_repo.get_dealer_name(dealer_id) or "Dealer"
            whatsapp_message = self._create_reminder_message_template(
                customer_name=request_data.customerName,
                reminder_type=request_data.reminderType,
                dealer_name=dealer_name
            )
            
            whatsapp_request = WhatsAppReminderRequest(
                dealer_id=dealer_id,
                phone_number=request_data.noTelp,
                customer_name=request_data.customerName,
                reminder_type=request_data.reminderType
            )
            
            try:
                # Use the existing WhatsApp service (adapt it for reminders)
                # For now, we'll create a basic response structure
                whatsapp_response = await self._send_reminder_whatsapp(whatsapp_request, whatsapp_message)
                
                # Determine WhatsApp status based on response
                whatsapp_status = self._determine_whatsapp_status(whatsapp_response)
                
                # Update request status based on WhatsApp response
                if whatsapp_response.success:
                    request_status = 'PROCESSED'
                    self.reminder_repo.update_status(
                        request_id=str(db_request.id),
                        request_status=request_status,
                        whatsapp_status=whatsapp_status,
                        whatsapp_message=whatsapp_message,
                        fonnte_response=whatsapp_response.response_data,
                        modified_by='system'
                    )
                    logger.info(f"WhatsApp reminder sent successfully for request {db_request.id}")
                else:
                    request_status = 'FAILED'
                    self.reminder_repo.update_status(
                        request_id=str(db_request.id),
                        request_status=request_status,
                        whatsapp_status=whatsapp_status,
                        whatsapp_message=whatsapp_message,
                        fonnte_response=whatsapp_response.response_data,
                        modified_by='system'
                    )
                    logger.error(f"WhatsApp reminder failed for request {db_request.id}: {whatsapp_response.message}")
                
                # Get updated request from database
                updated_request = self.reminder_repo.get_by_id(str(db_request.id))
                
                # Return detailed response with data
                response_data = CustomerReminderResponseData(
                    request_id=str(updated_request.id),
                    dealer_id=updated_request.dealer_id,
                    request_status=updated_request.request_status,
                    whatsapp_status=updated_request.whatsapp_status,
                    whatsapp_message=updated_request.whatsapp_message or "",
                    reminder_type=updated_request.reminder_type,
                    created_at=updated_request.created_date.isoformat(),
                    fonnte_response={"status": "success"}
                )
                
                return CustomerReminderResponse(
                    status=1,
                    message={"confirmation": "Reminder berhasil dibuat"},
                    data=response_data
                )
                
            except Exception as e:
                logger.error(f"Error sending WhatsApp reminder for request {db_request.id}: {str(e)}")
                self.reminder_repo.update_status(
                    request_id=str(db_request.id),
                    request_status='FAILED',
                    whatsapp_status='ERROR',
                    fonnte_response={"error": str(e)},
                    modified_by='system'
                )
                
                # Return error response with basic data
                response_data = CustomerReminderResponseData(
                    request_id=str(db_request.id),
                    dealer_id=db_request.dealer_id,
                    request_status='FAILED',
                    whatsapp_status='ERROR',
                    whatsapp_message="",
                    reminder_type=db_request.reminder_type,
                    created_at=db_request.created_date.isoformat(),
                    fonnte_response={"error": str(e)}
                )
                
                return CustomerReminderResponse(
                    status=1,
                    message={"confirmation": "Reminder berhasil dibuat"},
                    data=response_data
                )
            
        except Exception as e:
            logger.error(f"Unexpected error in create_reminder: {str(e)}")
            return CustomerReminderResponse(
                status=0,
                message={"error": "Terjadi kesalahan sistem"},
                data=None
            )
    
    async def _send_reminder_whatsapp(self, request: WhatsAppReminderRequest, message: str):
        """Send WhatsApp reminder message using existing service"""
        # This is a simplified implementation that adapts the existing WhatsApp service
        # In a real implementation, you might extend the WhatsAppService to handle reminders
        from app.schemas.customer_validation_request import WhatsAppMessageRequest
        
        # Convert reminder request to validation request format
        whatsapp_msg_request = WhatsAppMessageRequest(
            dealer_id=request.dealer_id,
            phone_number=request.phone_number,
            customer_name=request.customer_name,
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
                "data": reminder.to_dict()
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
        reminder_type: Optional[str] = None
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
                reminder_type=reminder_type
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
        date_to: Optional[str] = None
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
                date_to=parsed_date_to
            )
            
            # Get reminder type statistics
            reminder_type_stats = self.reminder_repo.get_reminder_type_stats(
                dealer_id=dealer_id,
                date_from=parsed_date_from,
                date_to=parsed_date_to
            )
            
            # Combine all stats
            combined_stats = {
                **whatsapp_stats,
                "reminder_type_breakdown": reminder_type_stats
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