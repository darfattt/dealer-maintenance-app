"""
H23 Dashboard routes for analytics data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from app.dependencies import get_db
from app.controllers.h23_dashboard_controller import H23DashboardController
from app.schemas.h23_dashboard import (
    TotalUnitEntryResponse, 
    WorkOrderRevenueResponse,
    WorkOrderStatusResponse,
    NJBStatisticsResponse,
    NSCStatisticsResponse,
    HLOStatisticsResponse,
    H23DashboardErrorResponse
)

router = APIRouter(tags=["h23-dashboard"])


# Work Order Section APIs

@router.get("/h23-dashboard/work-order/total-unit-entry", response_model=TotalUnitEntryResponse)
async def get_total_unit_entry(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get total unit entry count with trend indicator from PKB data
    
    This endpoint returns the total count of work orders (unit entries) for a specific dealer
    within a date range, including comparison with previous month and trend indicator.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        TotalUnitEntryResponse: Contains current count, previous count, trend, and percentage change
        
    Example:
        GET /api/v1/h23-dashboard/work-order/total-unit-entry?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate dealer_id
        if not dealer_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Dealer ID is required and cannot be empty."
            )

        # Create controller instance
        controller = H23DashboardController(db)
        
        # Get data
        result = await controller.get_total_unit_entry(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/work-order/revenue", response_model=WorkOrderRevenueResponse)
async def get_work_order_revenue(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get work order revenue statistics from PKB data
    
    This endpoint returns the total revenue from work orders by summing total_biaya_service
    for a specific dealer within a date range.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        WorkOrderRevenueResponse: Contains total revenue amount and record count
        
    Example:
        GET /api/v1/h23-dashboard/work-order/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate dealer_id
        if not dealer_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Dealer ID is required and cannot be empty."
            )

        # Create controller instance
        controller = H23DashboardController(db)
        
        # Get data
        result = await controller.get_work_order_revenue(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/work-order/status-counts", response_model=WorkOrderStatusResponse)
async def get_work_order_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get work order status distribution from PKB data
    
    This endpoint returns the count of work orders grouped by status_work_order
    for a specific dealer within a date range. Status mapping:
    1 = Start, 2 = Pause, 3 = Pending, 4 = Finish, 5 = Cancel
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        WorkOrderStatusResponse: Contains status distribution and total records
        
    Example:
        GET /api/v1/h23-dashboard/work-order/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate dealer_id
        if not dealer_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Dealer ID is required and cannot be empty."
            )

        # Create controller instance
        controller = H23DashboardController(db)
        
        # Get data
        result = await controller.get_work_order_status_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Pembayaran Section APIs

@router.get("/h23-dashboard/pembayaran/njb-statistics", response_model=NJBStatisticsResponse)
async def get_njb_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get NJB (Nota Jasa Bengkel) statistics from workshop invoice data
    
    This endpoint returns the total amount and count of NJB records where no_njb is not null
    for a specific dealer within a date range.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        NJBStatisticsResponse: Contains total amount and record count for NJB
        
    Example:
        GET /api/v1/h23-dashboard/pembayaran/njb-statistics?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate dealer_id
        if not dealer_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Dealer ID is required and cannot be empty."
            )

        # Create controller instance
        controller = H23DashboardController(db)
        
        # Get data
        result = await controller.get_njb_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/pembayaran/nsc-statistics", response_model=NSCStatisticsResponse)
async def get_nsc_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get NSC (Nota Suku Cadang) statistics from workshop invoice data
    
    This endpoint returns the total combined amount (total_harga_njb + total_harga_nsc) 
    and count of NSC records where no_nsc is not null for a specific dealer within a date range.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        NSCStatisticsResponse: Contains total combined amount and record count for NSC
        
    Example:
        GET /api/v1/h23-dashboard/pembayaran/nsc-statistics?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate dealer_id
        if not dealer_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Dealer ID is required and cannot be empty."
            )

        # Create controller instance
        controller = H23DashboardController(db)
        
        # Get data
        result = await controller.get_nsc_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/pembayaran/hlo-statistics", response_model=HLOStatisticsResponse)
async def get_hlo_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get HLO (Honda Layanan Otomotif) statistics from DP HLO data
    
    This endpoint returns the count of distinct HLO documents (id_hlo_document) and 
    the total count of parts from dp_hlo_parts for a specific dealer within a date range.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        HLOStatisticsResponse: Contains HLO document count, parts count, and total records
        
    Example:
        GET /api/v1/h23-dashboard/pembayaran/hlo-statistics?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate dealer_id
        if not dealer_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Dealer ID is required and cannot be empty."
            )

        # Create controller instance
        controller = H23DashboardController(db)
        
        # Get data
        result = await controller.get_hlo_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )