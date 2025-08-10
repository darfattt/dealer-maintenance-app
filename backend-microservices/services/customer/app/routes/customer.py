"""
Customer validation API routes
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.customer_controller import CustomerController
from app.schemas.customer_validation_request import (
    CustomerValidationRequestCreate,
    CustomerValidationResponse,
    CustomerValidationRequestResponse
)
from app.dependencies import get_db, get_dealer_from_access_key
from app.models.dealer_access_key import DealerAccessKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customer", tags=["Customer Validation"])


@router.post(
    "/validate-customer",
    response_model=CustomerValidationResponse,
    summary="Validate customer and send WhatsApp notification",
    description="Process customer validation request with access key authentication, store in database, and send WhatsApp notification via Fonnte API"
)
async def validate_customer(
    request: CustomerValidationRequestCreate,
    access_key_record: DealerAccessKey = Depends(get_dealer_from_access_key),
    db: Session = Depends(get_db)
) -> CustomerValidationResponse:
    """
    Validate customer data and send WhatsApp notification
    
    This endpoint:
    1. Validates access key authentication (dealer identification)
    2. Validates that dealerId in request matches access key dealer
    3. Validates dealer exists and has Fonnte configuration
    4. Stores the request in the database
    5. Sends a WhatsApp message to the customer
    6. Returns a success confirmation
    
    Authentication: Requires X-Access-Key header with valid access key
    """
    try:
        # Validate that dealer ID in request matches the access key dealer
        if request.dealerId != access_key_record.dealer_id:
            logger.warning(f"Dealer ID mismatch: request={request.dealerId}, access_key={access_key_record.dealer_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dealer ID in request body ({request.dealerId}) does not match access key dealer ({access_key_record.dealer_id})"
            )
        
        logger.info(f"Dealer ID validation passed: {request.dealerId}")
        
        # Dealer ID is already correct, no need to override
        # request.dealerId = access_key_record.dealer_id
        
        controller = CustomerController(db)
        result = await controller.validate_customer(request)
        
        logger.info(f"Customer validation processed for dealer {access_key_record.dealer_id}, customer {request.namaPembawa}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing customer validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing request"
        )


@router.get(
    "/request/{request_id}",
    summary="Get customer validation request by ID",
    description="Retrieve a specific customer validation request by its ID"
)
async def get_request(
    request_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get customer validation request by ID"""
    try:
        controller = CustomerController(db)
        result = controller.get_request_by_id(request_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/dealer/{dealer_id}/requests",
    summary="Get customer validation requests for a dealer",
    description="Retrieve paginated customer validation requests for a specific dealer with date filtering"
)
async def get_dealer_requests(
    dealer_id: str,
    page: int = 1,
    page_size: int = 10,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get paginated customer validation requests for a dealer with date filtering"""
    try:
        controller = CustomerController(db)
        result = controller.get_requests_by_dealer(
            dealer_id=dealer_id,
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to
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
        logger.error(f"Error getting requests for dealer {dealer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/dealer/{dealer_id}/stats",
    summary="Get dealer statistics",
    description="Get statistics and WhatsApp status breakdown for a dealer with date filtering"
)
async def get_dealer_stats(
    dealer_id: str,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dealer statistics with WhatsApp status breakdown"""
    try:
        controller = CustomerController(db)
        result = controller.get_dealer_stats(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
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
        logger.error(f"Error getting dealer stats for {dealer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/dealer/{dealer_id}/test-whatsapp",
    summary="Test WhatsApp configuration",
    description="Test the Fonnte WhatsApp configuration for a dealer"
)
async def test_whatsapp_config(
    dealer_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test WhatsApp configuration for a dealer"""
    try:
        controller = CustomerController(db)
        result = await controller.test_whatsapp_config(dealer_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing WhatsApp config for dealer {dealer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )