"""
Dashboard routes for analytics data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from app.dependencies import get_db
from app.controllers.dashboard_controller import DashboardController
from app.schemas.dashboard import UnitInboundStatusResponse, PaymentTypeResponse, DeliveryProcessStatusResponse

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/unit-inbound/status-counts", response_model=UnitInboundStatusResponse)
async def get_unit_inbound_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get unit inbound data count grouped by status_shipping_list for pie chart visualization
    
    This endpoint returns statistics about unit inbound data grouped by shipping list status
    for a specific dealer within a date range. The data is suitable for pie chart visualization.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        UnitInboundStatusResponse: Contains status counts and total records
        
    Example:
        GET /api/v1/dashboard/unit-inbound/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        
        # Validate date range
        if date_from > date_to:
            raise HTTPException(
                status_code=400, 
                detail="date_from must be less than or equal to date_to"
            )
        
        # Create controller and get data
        controller = DashboardController(db)
        result = await controller.get_unit_inbound_status_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/dashboard/payment-type/statistics", response_model=PaymentTypeResponse)
async def get_payment_type_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get payment type statistics from billing process data for dashboard visualization

    This endpoint returns count and sum of amounts grouped by tipe_pembayaran (payment type)
    for a specific dealer within a date range. The data is suitable for payment type widgets.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        PaymentTypeResponse: Contains payment type counts, amounts, and totals

    Example:
        GET /api/v1/dashboard/payment-type/statistics?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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

        # Validate date range
        if date_from > date_to:
            raise HTTPException(
                status_code=400,
                detail="date_from must be less than or equal to date_to"
            )

        # Create controller and get data
        controller = DashboardController(db)
        result = await controller.get_payment_type_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/dashboard/delivery-process/status-counts", response_model=DeliveryProcessStatusResponse)
async def get_delivery_process_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get delivery process data count grouped by status_delivery_document for dashboard visualization

    This endpoint returns statistics about delivery process data grouped by delivery document status
    for a specific dealer within a date range. The data is suitable for delivery process widgets.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        DeliveryProcessStatusResponse: Contains delivery status counts and total records

    Example:
        GET /api/v1/dashboard/delivery-process/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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

        # Validate date range
        if date_from > date_to:
            raise HTTPException(
                status_code=400,
                detail="date_from must be less than or equal to date_to"
            )

        # Create controller and get data
        controller = DashboardController(db)
        result = await controller.get_delivery_process_status_statistics(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
