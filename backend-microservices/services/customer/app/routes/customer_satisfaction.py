"""
Customer satisfaction API routes
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.controllers.customer_satisfaction_controller import CustomerSatisfactionController
from app.schemas.customer_satisfaction import (
    CustomerSatisfactionUploadResponse,
    CustomerSatisfactionListResponse,
    CustomerSatisfactionStatisticsResponse,
    UploadTrackersListResponse,
    CustomerSatisfactionFilters,
    ErrorResponse
)
from app.dependencies import get_db, get_current_user, UserContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customer-satisfaction", tags=["Customer Satisfaction"])


@router.post(
    "/upload",
    response_model=CustomerSatisfactionUploadResponse,
    summary="Upload customer satisfaction Excel/CSV file",
    description="Upload and process customer satisfaction data from Excel (.xlsx, .xls) or CSV files. The file should have the same format as the sample CSV with Indonesian column names."
)
async def upload_satisfaction_file(
    file: UploadFile = File(..., description="Excel or CSV file with customer satisfaction data"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CustomerSatisfactionUploadResponse:
    """
    Upload customer satisfaction file
    
    This endpoint:
    1. Validates the uploaded file (format, size)
    2. Creates an upload tracker for logging
    3. Processes the Excel/CSV data
    4. Stores records in customer_satisfaction_raw table
    5. Updates upload tracker with results
    6. Returns upload summary
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    
    Supported formats: .xlsx, .xls, .csv
    Maximum file size: 10MB
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Error reading uploaded file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error reading uploaded file"
            )
        
        # Process file
        controller = CustomerSatisfactionController(db)
        result = await controller.upload_customer_satisfaction_file(
            file_content=file_content,
            filename=file.filename,
            uploaded_by=current_user.email
        )
        
        logger.info(f"File upload processed for user {current_user.email}, file: {file.filename}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing file upload"
        )


@router.get(
    "/records",
    response_model=CustomerSatisfactionListResponse,
    summary="Get customer satisfaction records",
    description="Retrieve customer satisfaction records with filtering and pagination. Supports filtering by PERIODE UTK SUSPEND, Submit Review Date, and No AHASS."
)
async def get_satisfaction_records(
    periode_utk_suspend: str = Query(None, description="Filter by periode untuk suspend"),
    submit_review_date: str = Query(None, description="Filter by submit review date (partial match)"),
    no_ahass: str = Query(None, description="Filter by No AHASS"),
    date_from: str = Query(None, description="Filter by created date from (YYYY-MM-DD format)"),
    date_to: str = Query(None, description="Filter by created date to (YYYY-MM-DD format)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CustomerSatisfactionListResponse:
    """
    Get customer satisfaction records with filtering
    
    This endpoint supports filtering by:
    - periode_utk_suspend: Exact match for suspension period
    - submit_review_date: Partial match for submit review date
    - no_ahass: Exact match for AHASS number
    - date_from/date_to: Filter by record creation date range
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        # Create filters object
        filters = CustomerSatisfactionFilters(
            periode_utk_suspend=periode_utk_suspend,
            submit_review_date=submit_review_date,
            no_ahass=no_ahass,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size
        )
        
        # Get records
        controller = CustomerSatisfactionController(db)
        result = controller.get_customer_satisfaction_records(filters)
        
        logger.info(f"Retrieved customer satisfaction records for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving customer satisfaction records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving records"
        )


@router.get(
    "/statistics",
    response_model=CustomerSatisfactionStatisticsResponse,
    summary="Get customer satisfaction statistics",
    description="Get statistics and analysis of customer satisfaction data with filtering support"
)
async def get_satisfaction_statistics(
    periode_utk_suspend: str = Query(None, description="Filter by periode untuk suspend"),
    submit_review_date: str = Query(None, description="Filter by submit review date (partial match)"),
    no_ahass: str = Query(None, description="Filter by No AHASS"),
    date_from: str = Query(None, description="Filter by created date from (YYYY-MM-DD format)"),
    date_to: str = Query(None, description="Filter by created date to (YYYY-MM-DD format)"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CustomerSatisfactionStatisticsResponse:
    """
    Get customer satisfaction statistics
    
    Returns:
    - Total records count
    - Rating distribution
    - Top AHASS by satisfaction count
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        # Create filters object (no pagination for statistics)
        filters = CustomerSatisfactionFilters(
            periode_utk_suspend=periode_utk_suspend,
            submit_review_date=submit_review_date,
            no_ahass=no_ahass,
            date_from=date_from,
            date_to=date_to,
            page=1,
            page_size=10  # Not used for statistics
        )
        
        # Get statistics
        controller = CustomerSatisfactionController(db)
        result = controller.get_customer_satisfaction_statistics(filters)
        
        logger.info(f"Retrieved customer satisfaction statistics for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving customer satisfaction statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving statistics"
        )


@router.get(
    "/uploads",
    response_model=UploadTrackersListResponse,
    summary="Get upload trackers",
    description="Get paginated list of file upload trackers with status information"
)
async def get_upload_trackers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of trackers per page"),
    status: str = Query(None, description="Filter by upload status (PROCESSING, COMPLETED, FAILED)"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UploadTrackersListResponse:
    """
    Get upload trackers
    
    Returns paginated list of file upload trackers showing:
    - File information
    - Upload status and progress
    - Success/failure statistics
    - Error messages (if any)
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        controller = CustomerSatisfactionController(db)
        result = controller.get_upload_trackers(
            page=page,
            page_size=page_size,
            status=status
        )
        
        logger.info(f"Retrieved upload trackers for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving upload trackers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving upload trackers"
        )


@router.get(
    "/uploads/{tracker_id}",
    summary="Get upload tracker by ID",
    description="Get detailed information about a specific upload tracker"
)
async def get_upload_tracker(
    tracker_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get upload tracker by ID
    
    Returns detailed information about a specific upload including:
    - File details
    - Processing status
    - Success/failure counts
    - Error messages
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        controller = CustomerSatisfactionController(db)
        result = controller.get_upload_tracker_by_id(tracker_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        logger.info(f"Retrieved upload tracker {tracker_id} for user {current_user.email}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upload tracker {tracker_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving upload tracker"
        )