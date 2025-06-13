"""
Unit Invoice Controller

This module provides REST API endpoints for unit invoice data management.
It handles CRUD operations and data retrieval for unit invoice information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, UnitInvoiceData, UnitInvoiceUnit, Dealer
from tasks.processors.unit_invoice_processor import UnitInvoiceDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/unit_invoice", tags=["unit_invoice"])


@router.get("/")
async def get_unit_invoice_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in invoice number, PO ID, unit type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get unit invoice data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(UnitInvoiceData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(UnitInvoiceData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join with units to search in unit data
            query = query.join(UnitInvoiceUnit, UnitInvoiceData.id == UnitInvoiceUnit.unit_invoice_data_id, isouter=True)
            search_filter = or_(
                UnitInvoiceData.no_invoice.ilike(search_term),
                UnitInvoiceData.main_dealer_id.ilike(search_term),
                UnitInvoiceUnit.po_id.ilike(search_term),
                UnitInvoiceUnit.kode_tipe_unit.ilike(search_term),
                UnitInvoiceUnit.no_mesin.ilike(search_term),
                UnitInvoiceUnit.no_rangka.ilike(search_term)
            )
            query = query.filter(search_filter).distinct()
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        invoice_records = query.order_by(desc(UnitInvoiceData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for invoice in invoice_records:
            # Get units for this invoice
            units = db.query(UnitInvoiceUnit).filter(
                UnitInvoiceUnit.unit_invoice_data_id == invoice.id
            ).all()
            
            invoice_dict = {
                "id": str(invoice.id),
                "dealer_id": invoice.dealer_id,
                "dealer_name": invoice.dealer.dealer_name,
                "no_invoice": invoice.no_invoice,
                "tanggal_invoice": invoice.tanggal_invoice,
                "tanggal_jatuh_tempo": invoice.tanggal_jatuh_tempo,
                "main_dealer_id": invoice.main_dealer_id,
                "total_harga_sebelum_diskon": float(invoice.total_harga_sebelum_diskon) if invoice.total_harga_sebelum_diskon else None,
                "total_diskon_per_unit": float(invoice.total_diskon_per_unit) if invoice.total_diskon_per_unit else None,
                "potongan_per_invoice": float(invoice.potongan_per_invoice) if invoice.potongan_per_invoice else None,
                "total_ppn": float(invoice.total_ppn) if invoice.total_ppn else None,
                "total_harga": float(invoice.total_harga) if invoice.total_harga else None,
                "created_time": invoice.created_time,
                "modified_time": invoice.modified_time,
                "fetched_at": invoice.fetched_at.isoformat() if invoice.fetched_at else None,
                "unit_count": len(units),
                "units": [
                    {
                        "id": str(unit.id),
                        "kode_tipe_unit": unit.kode_tipe_unit,
                        "kode_warna": unit.kode_warna,
                        "kuantitas": unit.kuantitas,
                        "no_mesin": unit.no_mesin,
                        "no_rangka": unit.no_rangka,
                        "harga_satuan_sebelum_diskon": float(unit.harga_satuan_sebelum_diskon) if unit.harga_satuan_sebelum_diskon else None,
                        "diskon_per_unit": float(unit.diskon_per_unit) if unit.diskon_per_unit else None,
                        "po_id": unit.po_id,
                        "created_time": unit.created_time,
                        "modified_time": unit.modified_time
                    }
                    for unit in units
                ]
            }
            result.append(invoice_dict)
        
        return {
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching unit invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching unit invoice data: {str(e)}")


@router.get("/summary")
async def get_unit_invoice_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get unit invoice summary statistics"""
    try:
        processor = UnitInvoiceDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting unit invoice summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_unit_invoice_data(db: Session = Depends(get_db)):
    """Get list of dealers that have unit invoice data"""
    try:
        dealers = db.query(Dealer).join(UnitInvoiceData).distinct().all()
        
        result = [
            {
                "dealer_id": dealer.dealer_id,
                "dealer_name": dealer.dealer_name
            }
            for dealer in dealers
        ]
        
        return {
            "success": True,
            "dealers": result
        }
        
    except Exception as e:
        logger.error(f"Error fetching dealers with unit invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_unit_invoice_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    po_id: Optional[str] = Query("", description="PO ID filter"),
    no_shipping_list: Optional[str] = Query("", description="Shipping list number filter"),
    db: Session = Depends(get_db)
):
    """Test unit invoice API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = UnitInvoiceDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            po_id=po_id,
            no_shipping_list=no_shipping_list
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing unit invoice fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_unit_invoice_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search unit invoice data across multiple fields"""
    try:
        # Base query
        query = db.query(UnitInvoiceData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(UnitInvoiceData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                UnitInvoiceData.no_invoice.ilike(search_term),
                UnitInvoiceData.main_dealer_id.ilike(search_term)
            )
        )
        
        # Also search in unit data
        unit_query = db.query(UnitInvoiceUnit).filter(
            or_(
                UnitInvoiceUnit.po_id.ilike(search_term),
                UnitInvoiceUnit.kode_tipe_unit.ilike(search_term),
                UnitInvoiceUnit.no_mesin.ilike(search_term),
                UnitInvoiceUnit.no_rangka.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Get invoice IDs from unit search
        invoice_ids_from_units = [unit.unit_invoice_data_id for unit in unit_query]
        
        # Combine results
        if invoice_ids_from_units:
            query = query.filter(
                or_(
                    UnitInvoiceData.id.in_(invoice_ids_from_units),
                    # Original invoice-level search conditions already applied
                )
            )
        
        invoices = query.limit(limit).all()
        
        result = [
            {
                "id": str(invoice.id),
                "dealer_id": invoice.dealer_id,
                "dealer_name": invoice.dealer.dealer_name,
                "no_invoice": invoice.no_invoice,
                "tanggal_invoice": invoice.tanggal_invoice,
                "main_dealer_id": invoice.main_dealer_id,
                "total_harga": float(invoice.total_harga) if invoice.total_harga else None
            }
            for invoice in invoices
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching unit invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
