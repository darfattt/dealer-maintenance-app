"""
Customer satisfaction API routes
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Form
from sqlalchemy.orm import Session

from app.controllers.customer_satisfaction_controller import CustomerSatisfactionController
from app.schemas.customer_satisfaction import (
    CustomerSatisfactionUploadResponse,
    CustomerSatisfactionListResponse,
    CustomerSatisfactionStatisticsResponse,
    UploadTrackersListResponse,
    CustomerSatisfactionFilters,
    SentimentAnalysisResponse,
    BulkSentimentAnalysisResponse,
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
    override_existing: bool = Form(False, description="Override existing records with same No Tiket"),
    reformat_tanggal_rating: bool = Form(False, description="Reformat tanggal_rating to Indonesian format before validation"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CustomerSatisfactionUploadResponse:
    """
    Upload customer satisfaction file
    
    This endpoint:
    1. Validates the uploaded file (format, size)
    2. Creates an upload tracker for logging
    3. Processes the Excel/CSV data
    4. Handles duplicate records based on override_existing flag
    5. Stores records in customer_satisfaction_raw table
    6. Updates upload tracker with results
    7. Returns upload summary with override statistics
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    
    Supported formats: .xlsx, .xls, .csv
    Maximum file size: 10MB
    
    Override behavior:
    - If override_existing=true: Replace existing records with same No Tiket
    - If override_existing=false: Skip duplicate records and mark as failed
    
    Reformat behavior:
    - If reformat_tanggal_rating=true: Convert various date formats to Indonesian format before validation
    - If reformat_tanggal_rating=false: Use tanggal_rating values as-is for strict validation
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
            uploaded_by=current_user.email,
            override_existing=override_existing,
            reformat_tanggal_rating=reformat_tanggal_rating
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


@router.get(
    "/uploads/latest",
    summary="Get latest upload information",
    description="Get the most recent upload information for quick display including upload date, status, and statistics"
)
async def get_latest_upload_info(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get latest upload information
    
    Returns the most recent upload information including:
    - Upload date and uploaded by user
    - File name and size
    - Processing statistics
    - Upload status and completion time
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        controller = CustomerSatisfactionController(db)
        result = controller.get_latest_upload_info()
        
        logger.info(f"Retrieved latest upload info for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting latest upload info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving latest upload information"
        )


@router.get(
    "/latest-upload-simple",
    summary="Get latest upload information (simplified)",
    description="Get the most recent upload date from customer satisfaction records (simplified version)"
)
async def get_latest_upload_info_simple(
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get latest upload information (simplified)
    
    Returns only the most recent created_date from customer satisfaction records.
    This is a lightweight alternative to the full upload tracker information.
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        controller = CustomerSatisfactionController(db)
        result = controller.get_latest_upload_info_simple()
        
        logger.info(f"Retrieved latest upload info simple for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting latest upload info simple: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving latest upload date"
        )


@router.get(
    "/top-complaints",
    summary="Get top indikasi keluhan (complaint indicators)",
    description="Get the top complaint indicators with counts and percentages based on filtering"
)
async def get_top_indikasi_keluhan(
    periode_utk_suspend: str = Query(None, description="Filter by periode untuk suspend"),
    submit_review_date: str = Query(None, description="Filter by submit review date (partial match)"),
    no_ahass: str = Query(None, description="Filter by No AHASS"),
    date_from: str = Query(None, description="Filter by created date from (YYYY-MM-DD format)"),
    date_to: str = Query(None, description="Filter by created date to (YYYY-MM-DD format)"),
    limit: int = Query(3, ge=1, le=10, description="Number of top complaints to return"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get top indikasi keluhan (complaint indicators)
    
    Returns the top complaint indicators with:
    - Complaint text (indikasi_keluhan)
    - Count of occurrences
    - Percentage of total records
    
    Supports the same filtering options as other endpoints.
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        # Create filters object (same as other endpoints)
        filters = CustomerSatisfactionFilters(
            periode_utk_suspend=periode_utk_suspend,
            submit_review_date=submit_review_date,
            no_ahass=no_ahass,
            date_from=date_from,
            date_to=date_to,
            page=1,
            page_size=10  # Not used for this endpoint
        )
        
        # Get top complaints
        controller = CustomerSatisfactionController(db)
        result = controller.get_top_indikasi_keluhan(filters, limit)
        
        logger.info(f"Retrieved top {limit} indikasi keluhan for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving top indikasi keluhan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving top indikasi keluhan"
        )


@router.get(
    "/overall-rating",
    summary="Get overall rating with period comparison",
    description="Get overall customer satisfaction rating with optional comparison to previous period"
)
async def get_overall_rating(
    periode_utk_suspend: str = Query(None, description="Filter by periode untuk suspend"),
    submit_review_date: str = Query(None, description="Filter by submit review date (partial match)"),
    no_ahass: str = Query(None, description="Filter by No AHASS"),
    date_from: str = Query(None, description="Filter by date from (YYYY-MM-DD format) - will use tanggal_rating field"),
    date_to: str = Query(None, description="Filter by date to (YYYY-MM-DD format) - will use tanggal_rating field"),
    compare_previous_period: bool = Query(True, description="Whether to compare with previous period"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get overall rating with period comparison
    
    Returns overall rating information including:
    - Current period average rating
    - Total number of ratings
    - Previous period average rating (if comparison enabled)
    - Change amount and direction compared to previous period
    
    When date_from/date_to are provided, they filter by tanggal_rating field.
    When no dates provided, defaults to current month comparison.
    
    Supports the same filtering options as other endpoints.
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        # Create filters object (same as other endpoints)
        filters = CustomerSatisfactionFilters(
            periode_utk_suspend=periode_utk_suspend,
            submit_review_date=submit_review_date,
            no_ahass=no_ahass,
            date_from=date_from,
            date_to=date_to,
            page=1,
            page_size=10  # Not used for this endpoint
        )
        
        # Get overall rating
        controller = CustomerSatisfactionController(db)
        result = controller.get_overall_rating(filters, compare_previous_period)
        
        logger.info(f"Retrieved overall rating for user {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving overall rating: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving overall rating"
        )


# Sentiment Analysis Endpoints

@router.post(
    "/sentiment-analysis/{record_id}",
    response_model=SentimentAnalysisResponse,
    summary="Analyze sentiment for a single record",
    description="Perform sentiment analysis on a single customer satisfaction record using external AI API"
)
async def analyze_record_sentiment(
    record_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SentimentAnalysisResponse:
    """
    Analyze sentiment for a single customer satisfaction record
    
    This endpoint:
    1. Fetches the customer satisfaction record by ID
    2. Extracts review text from the inbox field
    3. Calls external sentiment analysis API
    4. Updates the record with sentiment results
    5. Returns analysis results including sentiment, score, reasons, and suggestions
    
    Requirements:
    - Record must exist and have content in the inbox field
    - External sentiment analysis API must be accessible
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        controller = CustomerSatisfactionController(db)
        result = await controller.analyze_record_sentiment(record_id)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        logger.info(f"Sentiment analysis completed for record {record_id} by user {current_user.email}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment for record {record_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during sentiment analysis"
        )


@router.post(
    "/sentiment-analysis/bulk",
    response_model=BulkSentimentAnalysisResponse,
    summary="Perform bulk sentiment analysis",
    description="Analyze sentiment for multiple unanalyzed customer satisfaction records"
)
async def bulk_analyze_sentiment(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to analyze"),
    upload_batch_id: str = Query(None, description="Optional filter by specific upload batch"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> BulkSentimentAnalysisResponse:
    """
    Perform bulk sentiment analysis on unanalyzed records
    
    This endpoint:
    1. Fetches unanalyzed customer satisfaction records (up to limit)
    2. Optionally filters by specific upload batch
    3. Processes records in batches through external sentiment API
    4. Updates database with sentiment results
    5. Returns processing statistics and results
    
    Features:
    - Processes records with review content (inbox field)
    - Handles API rate limiting and errors gracefully
    - Updates records with sentiment, score, reasons, themes, and suggestions
    - Provides detailed processing statistics
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        controller = CustomerSatisfactionController(db)
        result = await controller.bulk_analyze_sentiment(
            limit=limit,
            upload_batch_id=upload_batch_id
        )
        
        logger.info(f"Bulk sentiment analysis completed by user {current_user.email}: "
                   f"{result.data.get('analyzed_records', 0) if result.data else 0} records processed")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk sentiment analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during bulk sentiment analysis"
        )


@router.get(
    "/sentiment-analysis/statistics",
    summary="Get sentiment analysis statistics",
    description="Get comprehensive statistics about sentiment analysis results with filtering support"
)
async def get_sentiment_statistics(
    periode_utk_suspend: str = Query(None, description="Filter by periode untuk suspend"),
    submit_review_date: str = Query(None, description="Filter by submit review date (partial match)"),
    no_ahass: str = Query(None, description="Filter by No AHASS"),
    date_from: str = Query(None, description="Filter by analysis date from (YYYY-MM-DD format)"),
    date_to: str = Query(None, description="Filter by analysis date to (YYYY-MM-DD format)"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get sentiment analysis statistics
    
    Returns comprehensive sentiment analysis statistics including:
    - Total analyzed records count
    - Sentiment distribution (Positive/Negative/Neutral)
    - Average sentiment score
    - Records with themes count
    - Analysis summary breakdown
    
    Supports filtering by:
    - Period for suspend
    - Submit review date
    - AHASS number
    - Analysis date range
    
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
            page=1,
            page_size=10  # Not used for statistics
        )
        
        # Get sentiment statistics
        controller = CustomerSatisfactionController(db)
        result = controller.get_sentiment_analysis_statistics(filters)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        logger.info(f"Retrieved sentiment analysis statistics for user {current_user.email}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sentiment analysis statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving sentiment statistics"
        )


@router.get(
    "/sentiment-analysis/records/{sentiment}",
    response_model=CustomerSatisfactionListResponse,
    summary="Get records by sentiment",
    description="Get customer satisfaction records filtered by specific sentiment (Positive/Negative/Neutral)"
)
async def get_records_by_sentiment(
    sentiment: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    periode_utk_suspend: str = Query(None, description="Filter by periode untuk suspend"),
    submit_review_date: str = Query(None, description="Filter by submit review date (partial match)"),
    no_ahass: str = Query(None, description="Filter by No AHASS"),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CustomerSatisfactionListResponse:
    """
    Get customer satisfaction records filtered by sentiment
    
    Returns paginated list of customer satisfaction records that have been analyzed
    and match the specified sentiment classification.
    
    Sentiment options:
    - "Positive": Records with positive sentiment
    - "Negative": Records with negative sentiment  
    - "Neutral": Records with neutral sentiment
    
    Each record includes:
    - Basic customer satisfaction data
    - Sentiment analysis results (sentiment, score, reasons, suggestions, themes)
    - Analysis timestamp
    
    Supports additional filtering by standard customer satisfaction filters.
    Results are ordered by sentiment analysis date (most recent first).
    
    Authentication: Requires Authorization: Bearer <token> header with valid JWT token
    """
    try:
        # Validate sentiment parameter
        if sentiment not in ['Positive', 'Negative', 'Neutral']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sentiment must be 'Positive', 'Negative', or 'Neutral'"
            )
        
        # Get records by sentiment
        controller = CustomerSatisfactionController(db)
        result = controller.repository.get_records_by_sentiment(
            sentiment=sentiment,
            page=page,
            page_size=page_size,
            periode_utk_suspend=periode_utk_suspend,
            submit_review_date=submit_review_date,
            no_ahass=no_ahass
        )
        
        logger.info(f"Retrieved {len(result['records'])} {sentiment} sentiment records for user {current_user.email}")
        
        return CustomerSatisfactionListResponse(
            success=True,
            message=f"Retrieved {len(result['records'])} records with {sentiment} sentiment",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving records by sentiment '{sentiment}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving sentiment records"
        )