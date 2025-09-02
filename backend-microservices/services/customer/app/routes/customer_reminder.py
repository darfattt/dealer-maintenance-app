"""
Customer reminder API routes
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.customer_reminder_controller import CustomerReminderController
from app.schemas.customer_reminder_request import (
    CustomerReminderRequestCreate,
    CustomerReminderResponse,
    CustomerReminderRequestResponse,
    CustomerReminderStatsResponse,
    BulkReminderRequest,
    BulkReminderResponse
)
from app.dependencies import get_db, get_current_user, UserContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reminder", tags=["Customer Reminder"])


@router.post(
    "/add-bulk",
    response_model=BulkReminderResponse,
    summary="Create bulk customer reminders and send WhatsApp notifications",
    description="Process bulk customer reminder requests with JWT Bearer token authentication, store in database, and send WhatsApp reminders via Fonnte API"
)
async def add_bulk_reminders(
    request: BulkReminderRequest,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> BulkReminderResponse:
    """
    Create bulk customer reminders and send WhatsApp notifications
    
    This endpoint:
    1. Validates JWT Bearer token authentication (user identification)
    2. Validates dealer exists and has Fonnte configuration
    3. Stores multiple reminder requests in the database
    4. Sends WhatsApp reminder messages to customers
    5. Returns a success confirmation with processing statistics
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        # Use dealer_id from authenticated user context
        dealer_id = current_user.dealer_id
        
        if not dealer_id:
            logger.warning(f"User {current_user.email} does not have a dealer_id")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a dealer"
            )
        
        # Validate that kode_ahass matches dealer_id
        if request.kode_ahass != dealer_id:
            logger.warning(f"kode_ahass mismatch for user {current_user.email}: request.kode_ahass='{request.kode_ahass}' != dealer_id='{dealer_id}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="kode_ahass must match the authenticated user's dealer ID"
            )
        
        logger.info(f"Processing bulk customer reminders for dealer {dealer_id}, user {current_user.email}, customers: {len(request.data)}")
        
        controller = CustomerReminderController(db)
        result = await controller.add_bulk_reminders(request, dealer_id)
        
        logger.info(f"Bulk customer reminders processed for dealer {dealer_id}, total customers: {len(request.data)}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing bulk customer reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing request"
        )


@router.get(
    "/reminders",
    summary="Get customer reminder requests for dealer",
    description="Retrieve paginated customer reminder requests with date and type filtering. SUPER_ADMIN can specify dealer_id, others use their own dealer."
)
async def get_dealer_reminders(
    page: int = 1,
    page_size: int = 10,
    date_from: str = None,
    date_to: str = None,
    reminder_target: str = None,
    dealer_id: str = None,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get paginated customer reminder requests for dealer with filtering"""
    try:
        # Determine effective dealer_id based on user role
        if current_user.role == "SUPER_ADMIN":
            # SUPER_ADMIN can specify dealer_id or use their own
            effective_dealer_id = dealer_id or current_user.dealer_id
        else:
            # DEALER_ADMIN and DEALER_USER must use their own dealer_id
            effective_dealer_id = current_user.dealer_id
            if not effective_dealer_id:
                logger.warning(f"User {current_user.email} does not have a dealer_id")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not associated with a dealer"
                )
        
        controller = CustomerReminderController(db)
        result = controller.get_reminders_by_dealer(
            dealer_id=effective_dealer_id,
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
            reminder_target=reminder_target
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reminders for dealer {effective_dealer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/stats",
    summary="Get reminder statistics for dealer",
    description="Get statistics and breakdown for reminder types and WhatsApp status with date and target filtering. SUPER_ADMIN can specify dealer_id, others use their own dealer."
)
async def get_dealer_reminder_stats(
    date_from: str = None,
    date_to: str = None,
    reminder_target: str = None,
    dealer_id: str = None,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dealer reminder statistics with type and status breakdown"""
    try:
        # Determine effective dealer_id based on user role
        if current_user.role == "SUPER_ADMIN":
            # SUPER_ADMIN can specify dealer_id or use their own
            effective_dealer_id = dealer_id or current_user.dealer_id
        else:
            # DEALER_ADMIN and DEALER_USER must use their own dealer_id
            effective_dealer_id = current_user.dealer_id
            if not effective_dealer_id:
                logger.warning(f"User {current_user.email} does not have a dealer_id")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not associated with a dealer"
                )
        
        controller = CustomerReminderController(db)
        result = controller.get_reminder_stats(
            dealer_id=effective_dealer_id,
            date_from=date_from,
            date_to=date_to,
            reminder_target=reminder_target
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reminder stats for dealer {effective_dealer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/types",
    summary="Get available reminder types",
    description="Get list of available reminder types"
)
async def get_reminder_types() -> Dict[str, Any]:
    """Get available reminder types"""
    from app.schemas.customer_reminder_request import ReminderType
    
    return {
        "success": True,
        "message": "Available reminder types",
        "data": {
            "reminder_types": [
                {
                    "value": reminder_type.value,
                    "description": reminder_type.value.replace('_', ' ').title()
                }
                for reminder_type in ReminderType
            ]
        }
    }


@router.post(
    "/test-whatsapp",
    include_in_schema=False,
    summary="Test WhatsApp configuration for reminders",
    description="Test the Fonnte WhatsApp configuration for reminder sending for the authenticated dealer"
)
async def test_reminder_whatsapp_config(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test WhatsApp configuration for reminder sending"""
    try:
        # Use dealer_id from authenticated user context
        dealer_id = current_user.dealer_id
        
        if not dealer_id:
            logger.warning(f"User {current_user.email} does not have a dealer_id")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a dealer"
            )
        
        controller = CustomerReminderController(db)
        result = await controller.test_reminder_whatsapp_config(dealer_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing reminder WhatsApp config for dealer {current_user.dealer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/transaction/{transaction_id}",
    summary="Get customer reminder requests by transaction ID",
    description="Retrieve all customer reminder requests for a specific transaction ID without pagination"
)
async def get_reminders_by_transaction(
    transaction_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get customer reminder requests by transaction ID"""
    try:
        # Use dealer_id from authenticated user context
        dealer_id = current_user.dealer_id
        
        if not dealer_id:
            logger.warning(f"User {current_user.email} does not have a dealer_id")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a dealer"
            )
        controller = CustomerReminderController(db)
        result = controller.get_reminders_by_transaction_id(transaction_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reminders for transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{reminder_id}",
    include_in_schema=False,
    summary="Get customer reminder request by ID",
    description="Retrieve a specific customer reminder request by its ID"
)
async def get_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get customer reminder request by ID"""
    try:
        controller = CustomerReminderController(db)
        result = controller.get_reminder_by_id(reminder_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reminder {reminder_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )