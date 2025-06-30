"""
Dashboard routes for analytics data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from app.dependencies import get_db
from app.controllers.dashboard_controller import DashboardController
from app.schemas.dashboard import UnitInboundStatusResponse, PaymentTypeResponse, DeliveryProcessStatusResponse, ProspectFollowUpResponse, SPKStatusResponse, TopLeasingResponse, DocumentHandlingCountResponse, StatusProspectResponse, MetodeFollowUpResponse, SumberProspectResponse, SebaranProspectResponse, ProspectDataTableResponse, TopDealingUnitsResponse, RevenueResponse, TopDriverResponse, DeliveryLocationResponse, DeliveryDataHistoryResponse, SPKDealingProcessDataResponse

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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/prospect/followup-status-counts", response_model=ProspectFollowUpResponse)
async def get_prospect_followup_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get prospect data count grouped by status_follow_up_prospecting for dashboard visualization

    This endpoint returns statistics about prospect data grouped by follow-up prospecting status
    for a specific dealer within a date range filtered by tanggal_appointment. The data is suitable for prospect widgets.

    Status mapping:
    - 1 = Low
    - 2 = Medium  
    - 3 = Hot
    - 4 = Deal
    - 5 = Not Deal

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_appointment (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_appointment (YYYY-MM-DD format)

    Returns:
        ProspectFollowUpResponse: Contains follow-up status counts and total records

    Example:
        GET /api/v1/dashboard/prospect/followup-status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_prospect_followup_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/spk/status-counts", response_model=SPKStatusResponse)
async def get_spk_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get SPK dealing process data count grouped by status_spk for dashboard visualization

    This endpoint returns statistics about SPK dealing process data grouped by SPK status
    for a specific dealer within a date range filtered by tanggal_pesanan. The data is suitable for SPK widgets.

    Status mapping:
    - 1 = Open
    - 2 = Indent  
    - 3 = Complete
    - 4 = Cancelled

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_pesanan (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_pesanan (YYYY-MM-DD format)

    Returns:
        SPKStatusResponse: Contains SPK status counts and total records

    Example:
        GET /api/v1/dashboard/spk/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_spk_status_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/leasing/top-companies", response_model=TopLeasingResponse)
async def get_top_leasing_companies(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top 5 leasing companies count grouped by nama_finance_company for dashboard visualization

    This endpoint returns statistics about leasing data grouped by finance company name,
    counting id_po_finance_company records for a specific dealer within a date range filtered by tanggal_pengajuan.
    Returns top 5 companies ordered by count descending. The data is suitable for top leasing company widgets.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_pengajuan (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_pengajuan (YYYY-MM-DD format)

    Returns:
        TopLeasingResponse: Contains top 5 leasing companies with counts and total records

    Example:
        GET /api/v1/dashboard/leasing/top-companies?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_leasing_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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

@router.get("/dashboard/document-handling/count", response_model=DocumentHandlingCountResponse)
async def get_document_handling_count(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get document handling count where status_faktur_stnk == 1 for dashboard visualization

    This endpoint returns count of id_spk from document_handling_data joined with document_handling_units
    where status_faktur_stnk equals 1, for a specific dealer within a date range filtered by tanggal_pengajuan_stnk_ke_biro.
    The data is suitable for document handling widgets showing approved STNK applications.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_pengajuan_stnk_ke_biro (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_pengajuan_stnk_ke_biro (YYYY-MM-DD format)

    Returns:
        DocumentHandlingCountResponse: Contains count of approved STNK applications and total records

    Example:
        GET /api/v1/dashboard/document-handling/count?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_document_handling_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/prospect/status-counts", response_model=StatusProspectResponse)
async def get_prospect_status_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get prospect data count grouped by status_prospect for dashboard visualization

    This endpoint returns statistics about prospect data grouped by status_prospect
    for a specific dealer within a date range filtered by tanggal_appointment. The data is suitable for status prospect widgets.

    Status mapping:
    - 1 = Low
    - 2 = Medium  
    - 3 = Hot
    - 4 = Deal
    - 5 = Not Deal

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_appointment (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_appointment (YYYY-MM-DD format)

    Returns:
        StatusProspectResponse: Contains status prospect counts and total records

    Example:
        GET /api/v1/dashboard/prospect/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_status_prospect_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/prospect/metode-followup-counts", response_model=MetodeFollowUpResponse)
async def get_prospect_metode_followup_counts(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get prospect data count grouped by metode_follow_up for dashboard visualization

    This endpoint returns statistics about prospect data grouped by metode_follow_up
    for a specific dealer within a date range filtered by tanggal_appointment. The data is suitable for metode follow up widgets.

    Metode mapping:
    - 1 = SMS (WA/Line)
    - 2 = Call  
    - 3 = Visit
    - 4 = Direct Touch

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_appointment (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_appointment (YYYY-MM-DD format)

    Returns:
        MetodeFollowUpResponse: Contains metode follow up counts and total records

    Example:
        GET /api/v1/dashboard/prospect/metode-followup-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_metode_follow_up_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/prospect/sumber-top5", response_model=SumberProspectResponse)
async def get_prospect_sumber_top5(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top 5 prospect data count grouped by sumber_prospect for dashboard visualization

    This endpoint returns statistics about prospect data grouped by sumber_prospect
    for a specific dealer within a date range filtered by tanggal_prospect. Returns top 5 sources ordered by count descending.

    Sumber mapping:
    - 0001 = Pameran (Joint Promo, Grebek Pasar, Alfamart, Indomart, Mall dll)
    - 0002 = Showroom Event
    - 0003 = Roadshow
    - 0004 = Walk in
    - 0005 = Customer RO H1
    - 0006 = Customer RO H23
    - 0007 = Website
    - 0008 = Social media
    - 0009 = External parties (leasing, insurance)
    - 0010 = Mobile Apps MD/Dealer
    - 0011 = Refferal
    - 0012 = Contact Center
    - 9999 = Others

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering tanggal_prospect (YYYY-MM-DD format)
        date_to: End date for filtering tanggal_prospect (YYYY-MM-DD format)

    Returns:
        SumberProspectResponse: Contains top 5 sumber prospect counts and total records

    Example:
        GET /api/v1/dashboard/prospect/sumber-top5?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_sumber_prospect_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/prospect/sebaran-kecamatan", response_model=SebaranProspectResponse)
async def get_sebaran_prospect_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get prospect data distribution by kecamatan for map visualization
    
    This endpoint returns statistics about prospect data grouped by kecamatan code
    for a specific dealer within a date range. The data includes latitude/longitude
    coordinates suitable for map visualization and shows the top 5 kecamatan areas.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_appointment (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_appointment (YYYY-MM-DD format)
        
    Returns:
        SebaranProspectResponse: Contains kecamatan distribution counts and coordinates
        
    Example:
        GET /api/v1/dashboard/prospect/sebaran-kecamatan?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_sebaran_prospect_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/prospect/data-table", response_model=ProspectDataTableResponse)
async def get_prospect_data_table(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    page: int = Query(1, description="Page number (1-based)", ge=1),
    per_page: int = Query(20, description="Records per page", ge=1, le=100),
    id_prospect: Optional[str] = Query(None, description="Filter by prospect ID"),
    nama_lengkap: Optional[str] = Query(None, description="Filter by name (partial match)"),
    alamat: Optional[str] = Query(None, description="Filter by address (partial match)"),
    no_kontak: Optional[str] = Query(None, description="Filter by contact number"),
    tanggal_prospect: Optional[str] = Query(None, description="Filter by prospect date (YYYY-MM-DD)"),
    status_prospect: Optional[str] = Query(None, description="Filter by prospect status"),
    db: Session = Depends(get_db)
):
    """
    Get prospect data for table display with pagination and filters
    
    This endpoint returns paginated prospect data for tabular display with optional filters.
    The data is filtered by dealer_id and tanggal_appointment date range, with additional
    optional filters for prospect fields.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_appointment (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_appointment (YYYY-MM-DD format)
        page: Page number (1-based, default 1)
        per_page: Records per page (default 20, max 100)
        id_prospect: Optional filter by prospect ID
        nama_lengkap: Optional filter by name (partial match)
        alamat: Optional filter by address (partial match)
        no_kontak: Optional filter by contact number
        tanggal_prospect: Optional filter by prospect date
        status_prospect: Optional filter by prospect status
        
    Returns:
        ProspectDataTableResponse: Contains paginated prospect data and metadata
        
    Example:
        GET /api/v1/dashboard/prospect/data-table?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31&page=1&per_page=20
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

        # Validate tanggal_prospect if provided
        if tanggal_prospect:
            try:
                datetime.strptime(tanggal_prospect, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid tanggal_prospect format. Use YYYY-MM-DD format."
                )
        
        # Create controller and get data
        controller = DashboardController(db)
        result = await controller.get_prospect_data_table(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
            id_prospect=id_prospect,
            nama_lengkap=nama_lengkap,
            alamat=alamat,
            no_kontak=no_kontak,
            tanggal_prospect=tanggal_prospect,
            status_prospect=status_prospect
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/dealing/top-units", response_model=TopDealingUnitsResponse)
async def get_top_dealing_units_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top dealing units statistics by quantity for dashboard visualization
    
    This endpoint returns the top 3 unit types by total quantity from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The quantity is summed
    for each kode_tipe_unit to show the most popular units.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDealingUnitsResponse: Contains top 3 unit types by quantity and total records
        
    Example:
        GET /api/v1/dashboard/dealing/top-units?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_dealing_units_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/revenue", response_model=RevenueResponse)
async def get_revenue_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get revenue statistics by summing harga_jual from SPK dealing process units
    
    This endpoint returns total revenue by summing harga_jual from SPK dealing process
    units, filtered by dealer_id and tanggal_pengiriman date range. The revenue calculation
    excludes records where harga_jual is null or zero.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        RevenueResponse: Contains total revenue and record count
        
    Example:
        GET /api/v1/dashboard/revenue?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_revenue_statistics(
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


@router.get("/dashboard/delivery/top-drivers", response_model=TopDriverResponse)
async def get_top_driver_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get top driver statistics by delivery count from delivery process data
    
    This endpoint returns the top 5 drivers by delivery count, joining delivery_process_data
    with delivery_process_details to count id_spk per driver. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes drivers with valid IDs and delivery records.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        TopDriverResponse: Contains top 5 drivers by delivery count and total records
        
    Example:
        GET /api/v1/dashboard/delivery/top-drivers?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
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
        result = await controller.get_top_driver_statistics(
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


@router.get("/dashboard/delivery/locations", response_model=DeliveryLocationResponse)
async def get_delivery_location_statistics(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get delivery location statistics by count from delivery process data
    
    This endpoint returns the top 5 delivery locations by count, joining delivery_process_data
    with delivery_process_details to count lokasi_pengiriman per location. Filtered by dealer_id and 
    tanggal_pengiriman date range. Only includes locations with valid data and calculates percentages.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        
    Returns:
        DeliveryLocationResponse: Contains top 5 delivery locations by count with percentages
        
    Example:
        GET /api/v1/dashboard/delivery/locations?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
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
        result = await controller.get_delivery_location_statistics(
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


@router.get("/dashboard/delivery/data-history", response_model=DeliveryDataHistoryResponse)
async def get_delivery_data_history(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    page: int = Query(1, description="Page number (1-based)", ge=1),
    per_page: int = Query(20, description="Records per page", ge=1, le=100),
    delivery_document_id: Optional[str] = Query(None, description="Filter by delivery document ID"),
    tanggal_pengiriman: Optional[str] = Query(None, description="Filter by delivery date"),
    status_delivery_document: Optional[str] = Query(None, description="Filter by delivery status"),
    id_driver: Optional[str] = Query(None, description="Filter by driver ID"),
    id_spk: Optional[str] = Query(None, description="Filter by SPK ID"),
    nama_penerima: Optional[str] = Query(None, description="Filter by recipient name"),
    no_kontak_penerima: Optional[str] = Query(None, description="Filter by recipient contact"),
    lokasi_pengiriman: Optional[str] = Query(None, description="Filter by delivery location"),
    waktu_pengiriman: Optional[str] = Query(None, description="Filter by delivery time"),
    db: Session = Depends(get_db)
):
    """
    Get delivery data history for table display with pagination and filters
    
    This endpoint returns paginated delivery data for tabular display with optional filters.
    Joins delivery_process_data with delivery_process_details to get complete delivery information.
    The data is filtered by dealer_id and tanggal_pengiriman date range, with additional
    optional filters for all displayed fields.
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        date_to: End date for filtering by tanggal_pengiriman (YYYY-MM-DD format)
        page: Page number (1-based, default 1)
        per_page: Records per page (default 20, max 100)
        delivery_document_id: Optional filter by delivery document ID
        tanggal_pengiriman: Optional filter by delivery date
        status_delivery_document: Optional filter by delivery status
        id_driver: Optional filter by driver ID
        id_spk: Optional filter by SPK ID
        nama_penerima: Optional filter by recipient name (partial match)
        no_kontak_penerima: Optional filter by recipient contact
        lokasi_pengiriman: Optional filter by delivery location (partial match)
        waktu_pengiriman: Optional filter by delivery time
        
    Returns:
        DeliveryDataHistoryResponse: Contains paginated delivery data and metadata
        
    Example:
        GET /api/v1/dashboard/delivery/data-history?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31&page=1&per_page=20
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
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

        # Validate tanggal_pengiriman filter if provided
        if tanggal_pengiriman:
            try:
                datetime.strptime(tanggal_pengiriman, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid tanggal_pengiriman format. Use YYYY-MM-DD format."
                )
        
        # Create controller and get data
        controller = DashboardController(db)
        result = await controller.get_delivery_data_history(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
            delivery_document_id=delivery_document_id,
            tanggal_pengiriman=tanggal_pengiriman,
            status_delivery_document=status_delivery_document,
            id_driver=id_driver,
            id_spk=id_spk,
            nama_penerima=nama_penerima,
            no_kontak_penerima=no_kontak_penerima,
            lokasi_pengiriman=lokasi_pengiriman,
            waktu_pengiriman=waktu_pengiriman
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


@router.get("/dashboard/spk-dealing-process/data", response_model=SPKDealingProcessDataResponse)
async def get_spk_dealing_process_data(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    page: int = Query(1, description="Page number (1-based)", ge=1),
    per_page: int = Query(20, description="Records per page", ge=1, le=100),
    id_spk: Optional[str] = Query(None, description="Filter by SPK ID"),
    nama_customer: Optional[str] = Query(None, description="Filter by customer name"),
    alamat: Optional[str] = Query(None, description="Filter by address"),
    no_kontak: Optional[str] = Query(None, description="Filter by contact number"),
    email: Optional[str] = Query(None, description="Filter by email"),
    status_spk: Optional[str] = Query(None, description="Filter by SPK status"),
    nama_bpkb: Optional[str] = Query(None, description="Filter by BPKB name"),
    db: Session = Depends(get_db)
):
    """
    Get SPK dealing process data for table display with pagination and filters
    
    This endpoint returns paginated SPK dealing process data for tabular display with optional filters.
    Retrieves all fields from spk_dealing_process_data table filtered by dealer_id, with additional
    optional filters for key fields like SPK ID, customer name, address, contact, email, status, and BPKB name.
    
    Args:
        dealer_id: The dealer ID to filter records
        page: Page number (1-based, default 1)
        per_page: Records per page (default 20, max 100)
        id_spk: Optional filter by SPK ID (partial match)
        nama_customer: Optional filter by customer name (partial match)
        alamat: Optional filter by address (partial match)
        no_kontak: Optional filter by contact number (partial match)
        email: Optional filter by email (partial match)
        status_spk: Optional filter by SPK status (partial match)
        nama_bpkb: Optional filter by BPKB name (partial match)
        
    Returns:
        SPKDealingProcessDataResponse: Contains paginated SPK data and metadata
        
    Example:
        GET /api/v1/dashboard/spk-dealing-process/data?dealer_id=12284&page=1&per_page=20
        GET /api/v1/dashboard/spk-dealing-process/data?dealer_id=12284&page=1&per_page=20&nama_customer=John&status_spk=1
    """
    try:
        # Create controller and get data
        controller = DashboardController(db)
        result = await controller.get_spk_dealing_process_data(
            dealer_id=dealer_id,
            page=page,
            per_page=per_page,
            id_spk=id_spk,
            nama_customer=nama_customer,
            alamat=alamat,
            no_kontak=no_kontak,
            email=email,
            status_spk=status_spk,
            nama_bpkb=nama_bpkb
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
