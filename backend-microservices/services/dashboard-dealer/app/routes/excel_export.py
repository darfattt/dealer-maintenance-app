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


@router.get("/h23-dashboard/exports/work-order-detail-excel")
async def export_work_order_detail_excel(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Export Work Order Detail data to Excel file

    This endpoint generates and downloads an Excel file containing comprehensive Work Order data
    including PKBData, PKBService, and PKBPart information for a specific dealer within a date range.

    Excel Columns:
    - PKB Data: dealer_id, no_work_order, no_sa_form, tanggal_servis, etc.
    - Service Data: id_job, nama_pekerjaan, jenis_pekerjaan, biaya_service, etc.
    - Parts Data: parts_number, harga_parts, kuantitas_parts, total_harga_parts, etc.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        StreamingResponse: Excel file download

    Example:
        GET /api/v1/h23-dashboard/exports/work-order-detail-excel?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Create controller instance
        controller = ExcelExportController(db)

        # Validate request
        controller.validate_export_request(dealer_id, date_from, date_to)

        # Generate Excel file
        excel_bytes, metadata = controller.export_work_order_detail_excel(
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


@router.get("/h23-dashboard/exports/njb-nsc-detail-excel")
async def export_njb_nsc_detail_excel(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Export NJB/NSC Detail data to Excel file

    This endpoint generates and downloads an Excel file containing comprehensive NJB/NSC data
    including WorkshopInvoiceData, WorkshopInvoiceNJB, and WorkshopInvoiceNSC information
    for a specific dealer within a date range.

    Excel Columns:
    - Workshop Invoice Data: dealer_id, no_work_order, no_njb, tanggal_njb, no_nsc, tanggal_nsc, etc.
    - NJB Service Data: id_job, harga_servis, disc_service_amount, total_harga_servis, etc.
    - NSC Parts Data: parts_number, kuantitas, harga_parts, total_harga_parts, etc.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        StreamingResponse: Excel file download

    Example:
        GET /api/v1/h23-dashboard/exports/njb-nsc-detail-excel?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Create controller instance
        controller = ExcelExportController(db)

        # Validate request
        controller.validate_export_request(dealer_id, date_from, date_to)

        # Generate Excel file
        excel_bytes, metadata = controller.export_njb_nsc_detail_excel(
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


@router.get("/h23-dashboard/exports/hlo-detail-excel")
async def export_hlo_detail_excel(
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Export HLO Detail data to Excel file

    This endpoint generates and downloads an Excel file containing comprehensive HLO data
    including DPHLOData and DPHLOPart information for a specific dealer within a date range.

    Excel Columns:
    - HLO Data: dealer_id, no_invoice_uang_jaminan, id_hlo_document, tanggal_pemesanan_hlo, etc.
    - Parts Data: dp_hlo_data_id, parts_number, kuantitas, harga_parts, total_harga_parts, etc.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        StreamingResponse: Excel file download

    Example:
        GET /api/v1/h23-dashboard/exports/hlo-detail-excel?dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Create controller instance
        controller = ExcelExportController(db)

        # Validate request
        controller.validate_export_request(dealer_id, date_from, date_to)

        # Generate Excel file
        excel_bytes, metadata = controller.export_hlo_detail_excel(
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
    export_type: str = Query(..., description="Export type: work_order, work_order_detail, njb_nsc, njb_nsc_detail, hlo, or hlo_detail"),
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
        export_type: Type of export (work_order, work_order_detail, njb_nsc, njb_nsc_detail, hlo, or hlo_detail)
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        JSON: Export preview information

    Example:
        GET /api/v1/h23-dashboard/exports/preview?export_type=hlo_detail&dealer_id=12284&date_from=2024-01-01&date_to=2024-01-31
    """
    try:
        # Validate export_type
        valid_types = ['work_order', 'work_order_detail', 'njb_nsc', 'njb_nsc_detail', 'hlo', 'hlo_detail']
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