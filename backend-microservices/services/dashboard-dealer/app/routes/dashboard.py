"""
Dashboard routes for analytics data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from app.dependencies import get_db
from app.controllers.dashboard_controller import DashboardController
from app.schemas.dashboard import UnitInboundStatusResponse, PaymentTypeResponse, DeliveryProcessStatusResponse, ProspectFollowUpResponse, SPKStatusResponse, TopLeasingResponse, DocumentHandlingCountResponse, StatusProspectResponse, MetodeFollowUpResponse, SumberProspectResponse

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
