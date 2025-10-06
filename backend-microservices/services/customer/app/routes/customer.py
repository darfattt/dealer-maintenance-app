"""
Customer validation API routes
"""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.controllers.customer_controller import CustomerController
from app.repositories.api_request_log_repository import ApiRequestLogRepository
from app.services.request_logging_service import RequestLoggingService
from app.schemas.customer_validation_request import (
    CustomerValidationRequestCreate,
    CustomerValidationResponse,
    CustomerValidationRequestResponse
)
from app.dependencies import get_db, get_current_user, UserContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customer", tags=["Customer Validation"])


@router.post(
    "/validate-customer",
    response_model=CustomerValidationResponse,
    summary="Validate customer and send WhatsApp notification",
    description="Process customer validation request with JWT Bearer token authentication, store in database, and send WhatsApp notification via Fonnte API"
)
async def validate_customer(
    request: CustomerValidationRequestCreate,
    fastapi_request: Request,
    background_tasks: BackgroundTasks,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CustomerValidationResponse:
    """
    Validate customer data and send WhatsApp notification

    This endpoint:
    1. Validates JWT Bearer token authentication (user identification)
    2. Validates dealer exists and has Fonnte configuration
    3. Stores the request in the database
    4. Sends a WhatsApp message to the customer
    5. Returns a success confirmation

    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    start_time = datetime.utcnow()
    log_repository = ApiRequestLogRepository(db)
    logging_service = RequestLoggingService(log_repository)
    log_id = None

    try:
        # Use kode_ahass as dealer_id
        dealer_id = request.kode_ahass

        # Start async request logging
        client_ip = fastapi_request.client.host if fastapi_request.client else None
        headers_dict = dict(fastapi_request.headers)

        log_id = await logging_service.log_request_start(
            request_name="validate_customer",
            request_method="POST",
            endpoint="/v1/customer/validate-customer",
            dealer_id=dealer_id,
            request_payload=request.dict(),
            request_headers=headers_dict,
            request_ip=client_ip,
            user_email=current_user.email
        )

        logger.info(f"Processing customer validation for dealer {dealer_id}, user {current_user.email}")

        controller = CustomerController(db)
        result = await controller.validate_customer(request, dealer_id, created_by=current_user.email)

        logger.info(f"Customer validation processed for dealer {dealer_id}, customer {request.nama_pembawa}")

        # Log successful completion
        if log_id:
            background_tasks.add_task(
                logging_service.log_request_completion,
                log_id=log_id,
                response_status="success" if result.status == 1 else "error",
                response_code=200,
                start_time=start_time,
                response_data={"status": result.status, "message_keys": list(result.message.keys()) if result.message else []}
            )

        return result

    except HTTPException as he:
        # Log HTTP exceptions
        if log_id:
            background_tasks.add_task(
                logging_service.log_request_error,
                log_id=log_id,
                error_message=str(he.detail),
                response_code=he.status_code,
                start_time=start_time
            )
        raise
    except Exception as e:
        error_msg = f"Error processing customer validation: {str(e)}"
        logger.error(error_msg)

        # Log unexpected errors
        if log_id:
            background_tasks.add_task(
                logging_service.log_request_error,
                log_id=log_id,
                error_message=error_msg,
                response_code=500,
                start_time=start_time
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing request"
        )


@router.get(
    "/request/{request_id}",
    include_in_schema=False,
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
    include_in_schema=False,
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