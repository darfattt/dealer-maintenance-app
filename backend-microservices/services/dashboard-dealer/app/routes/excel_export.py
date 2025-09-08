"""
Excel Export routes for downloading Excel files
"""

import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.dependencies import get_db
from app.controllers.excel_export_controller import ExcelExportController
from app.schemas.excel_export import (
    ExcelExportResponse,
    ExcelExportError
)

router = APIRouter(tags=["excel-exports"])


@router.get("/h23-dashboard/exports/work-order-excel")
async def export_work_order_excel(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Export Work Order data to Excel file
    
    This endpoint generates and downloads an Excel file containing Work Order data from PKB records
    for a specific dealer within a date range.
    
    Excel Columns:
    - No (Row Number)
    - No. Work Order
    - No. SA Form
    - Tgl Service
    - Nomor Polisi
    - Nomor Mesin
    - Nomor Rangka
    - Nama Pembawa
    - No Telp Pembawa
    - Total Biaya
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        StreamingResponse: Excel file download
        
    Example:
        GET /api/v1/h23-dashboard/exports/work-order-excel?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Create controller instance
        controller = ExcelExportController(db)
        
        # Validate request
        controller.validate_export_request(dealer_id, date_from, date_to)
        
        # Generate Excel file
        excel_bytes, metadata = controller.export_work_order_excel(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Create streaming response
        excel_stream = io.BytesIO(excel_bytes)
        
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={metadata.filename}",
                "Content-Length": str(metadata.file_size_bytes),
                "X-Export-Records": str(metadata.total_records),
                "X-Export-Type": metadata.export_type
            }
        )
        
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/exports/njb-nsc-excel")
async def export_njb_nsc_excel(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Export NJB/NSC data to Excel file
    
    This endpoint generates and downloads an Excel file containing NJB (Nota Jasa Bengkel) and 
    NSC (Nota Suku Cadang) data from workshop invoice records for a specific dealer within a date range.
    
    Excel Columns:
    - No (Row Number)
    - Honda SA
    - Honda Mekanik
    - No. Work Order
    - No. NJB
    - Tgl NJB
    - Total Harga NJB
    - No. NSC
    - Tgl NSC
    - Total Harga NSC
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        StreamingResponse: Excel file download
        
    Example:
        GET /api/v1/h23-dashboard/exports/njb-nsc-excel?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Create controller instance
        controller = ExcelExportController(db)
        
        # Validate request
        controller.validate_export_request(dealer_id, date_from, date_to)
        
        # Generate Excel file
        excel_bytes, metadata = controller.export_njb_nsc_excel(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={metadata.filename}",
                "Content-Length": str(metadata.file_size_bytes),
                "X-Export-Records": str(metadata.total_records),
                "X-Export-Type": metadata.export_type
            }
        )
        
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/exports/hlo-excel")
async def export_hlo_excel(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Export HLO data to Excel file
    
    This endpoint generates and downloads an Excel file containing HLO (Honda Layanan Otomotif) data 
    from DP HLO records with their associated parts for a specific dealer within a date range.
    
    Excel Columns:
    - No (Row Number)
    - ID HLO Document
    - Tgl Pemesanan HLO
    - No Work Order
    - ID Customer
    - Part Number
    - Kuantitas Part
    - Total Harga Parts
    
    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        StreamingResponse: Excel file download
        
    Example:
        GET /api/v1/h23-dashboard/exports/hlo-excel?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Create controller instance
        controller = ExcelExportController(db)
        
        # Validate request
        controller.validate_export_request(dealer_id, date_from, date_to)
        
        # Generate Excel file
        excel_bytes, metadata = controller.export_hlo_excel(
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={metadata.filename}",
                "Content-Length": str(metadata.file_size_bytes),
                "X-Export-Records": str(metadata.total_records),
                "X-Export-Type": metadata.export_type
            }
        )
        
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/h23-dashboard/exports/preview")
async def get_export_preview(
    export_type: str = Query(..., description="Export type: work_order, njb_nsc, or hlo"),
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get preview information for Excel export
    
    This endpoint returns preview information about the export including the estimated number
    of records that would be exported, without actually generating the Excel file.
    
    Args:
        export_type: Type of export (work_order, njb_nsc, or hlo)
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)
        
    Returns:
        JSON: Export preview information
        
    Example:
        GET /api/v1/h23-dashboard/exports/preview?export_type=work_order&dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate export_type
        valid_types = ['work_order', 'njb_nsc', 'hlo']
        if export_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid export_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Create controller instance
        controller = ExcelExportController(db)
        
        # Get preview information
        preview = controller.get_export_preview(
            export_type=export_type,
            dealer_id=dealer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return {
            "success": True,
            "message": "Export preview generated successfully",
            "preview": preview
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )