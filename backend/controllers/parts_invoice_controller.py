"""
Parts Invoice Controller

This module provides REST API endpoints for parts invoice data management.
It handles CRUD operations and data retrieval for parts invoice information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, PartsInvoiceData, PartsInvoicePart, Dealer
from tasks.processors.parts_invoice_processor import PartsInvoiceDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/parts_invoice", tags=["parts_invoice"])


@router.get("/")
async def get_parts_invoice_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in invoice number, PO number, parts number"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get parts invoice data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(PartsInvoiceData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(PartsInvoiceData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join with parts to search in parts data
            query = query.join(PartsInvoicePart, PartsInvoiceData.id == PartsInvoicePart.parts_invoice_data_id, isouter=True)
            search_filter = or_(
                PartsInvoiceData.no_invoice.ilike(search_term),
                PartsInvoiceData.main_dealer_id.ilike(search_term),
                PartsInvoicePart.no_po.ilike(search_term),
                PartsInvoicePart.parts_number.ilike(search_term)
            )
            query = query.filter(search_filter).distinct()
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        invoice_records = query.order_by(desc(PartsInvoiceData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for invoice in invoice_records:
            # Get parts for this invoice
            parts = db.query(PartsInvoicePart).filter(
                PartsInvoicePart.parts_invoice_data_id == invoice.id
            ).all()
            
            invoice_dict = {
                "id": str(invoice.id),
                "dealer_id": invoice.dealer_id,
                "dealer_name": invoice.dealer.dealer_name,
                "no_invoice": invoice.no_invoice,
                "tgl_invoice": invoice.tgl_invoice,
                "tgl_jatuh_tempo": invoice.tgl_jatuh_tempo,
                "main_dealer_id": invoice.main_dealer_id,
                "total_harga_sebelum_diskon": float(invoice.total_harga_sebelum_diskon) if invoice.total_harga_sebelum_diskon else None,
                "total_diskon_per_parts_number": float(invoice.total_diskon_per_parts_number) if invoice.total_diskon_per_parts_number else None,
                "potongan_per_invoice": float(invoice.potongan_per_invoice) if invoice.potongan_per_invoice else None,
                "total_ppn": float(invoice.total_ppn) if invoice.total_ppn else None,
                "total_harga": float(invoice.total_harga) if invoice.total_harga else None,
                "created_time": invoice.created_time,
                "modified_time": invoice.modified_time,
                "fetched_at": invoice.fetched_at.isoformat() if invoice.fetched_at else None,
                "parts_count": len(parts),
                "parts": [
                    {
                        "id": str(part.id),
                        "no_po": part.no_po,
                        "jenis_order": part.jenis_order,
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "uom": part.uom,
                        "harga_satuan_sebelum_diskon": float(part.harga_satuan_sebelum_diskon) if part.harga_satuan_sebelum_diskon else None,
                        "diskon_per_parts_number": float(part.diskon_per_parts_number) if part.diskon_per_parts_number else None,
                        "created_time": part.created_time,
                        "modified_time": part.modified_time
                    }
                    for part in parts
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
        logger.error(f"Error fetching parts invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching parts invoice data: {str(e)}")


@router.get("/summary")
async def get_parts_invoice_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get parts invoice summary statistics"""
    try:
        processor = PartsInvoiceDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting parts invoice summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_parts_invoice_data(db: Session = Depends(get_db)):
    """Get list of dealers that have parts invoice data"""
    try:
        dealers = db.query(Dealer).join(PartsInvoiceData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with parts invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_parts_invoice_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    no_po: Optional[str] = Query("", description="PO number filter"),
    db: Session = Depends(get_db)
):
    """Test parts invoice API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = PartsInvoiceDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time, no_po=no_po
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing parts invoice fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_parts_invoice_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search parts invoice data across multiple fields"""
    try:
        # Base query
        query = db.query(PartsInvoiceData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(PartsInvoiceData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                PartsInvoiceData.no_invoice.ilike(search_term),
                PartsInvoiceData.main_dealer_id.ilike(search_term)
            )
        )
        
        # Also search in parts data
        part_query = db.query(PartsInvoicePart).filter(
            or_(
                PartsInvoicePart.no_po.ilike(search_term),
                PartsInvoicePart.parts_number.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Get invoice IDs from parts search
        invoice_ids_from_parts = [part.parts_invoice_data_id for part in part_query]
        
        # Combine results
        if invoice_ids_from_parts:
            query = query.filter(
                or_(
                    PartsInvoiceData.id.in_(invoice_ids_from_parts),
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
                "tgl_invoice": invoice.tgl_invoice,
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
        logger.error(f"Error searching parts invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
