"""
Workshop Invoice Controller

This module provides REST API endpoints for workshop invoice data management.
It handles CRUD operations and data retrieval for workshop invoice information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, WorkshopInvoiceData, WorkshopInvoiceNJB, WorkshopInvoiceNSC, Dealer
from tasks.processors.workshop_invoice_processor import WorkshopInvoiceDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workshop_invoice", tags=["workshop_invoice"])


@router.get("/")
async def get_workshop_invoice_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in work order, NJB, NSC, job ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get workshop invoice data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(WorkshopInvoiceData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(WorkshopInvoiceData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join with services and parts to search
            query = query.join(WorkshopInvoiceNJB, WorkshopInvoiceData.id == WorkshopInvoiceNJB.workshop_invoice_data_id, isouter=True)
            query = query.join(WorkshopInvoiceNSC, WorkshopInvoiceData.id == WorkshopInvoiceNSC.workshop_invoice_data_id, isouter=True)
            search_filter = or_(
                WorkshopInvoiceData.no_work_order.ilike(search_term),
                WorkshopInvoiceData.no_njb.ilike(search_term),
                WorkshopInvoiceData.no_nsc.ilike(search_term),
                WorkshopInvoiceNJB.id_job.ilike(search_term),
                WorkshopInvoiceNSC.id_job.ilike(search_term),
                WorkshopInvoiceNSC.parts_number.ilike(search_term)
            )
            query = query.filter(search_filter).distinct()
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        invoice_records = query.order_by(desc(WorkshopInvoiceData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for invoice in invoice_records:
            # Get services and parts for this invoice
            services = db.query(WorkshopInvoiceNJB).filter(
                WorkshopInvoiceNJB.workshop_invoice_data_id == invoice.id
            ).all()
            
            parts = db.query(WorkshopInvoiceNSC).filter(
                WorkshopInvoiceNSC.workshop_invoice_data_id == invoice.id
            ).all()
            
            invoice_dict = {
                "id": str(invoice.id),
                "dealer_id": invoice.dealer_id,
                "dealer_name": invoice.dealer.dealer_name,
                "no_work_order": invoice.no_work_order,
                "no_njb": invoice.no_njb,
                "tanggal_njb": invoice.tanggal_njb,
                "total_harga_njb": float(invoice.total_harga_njb) if invoice.total_harga_njb else None,
                "no_nsc": invoice.no_nsc,
                "tanggal_nsc": invoice.tanggal_nsc,
                "total_harga_nsc": float(invoice.total_harga_nsc) if invoice.total_harga_nsc else None,
                "honda_id_sa": invoice.honda_id_sa,
                "honda_id_mekanik": invoice.honda_id_mekanik,
                "created_time": invoice.created_time,
                "modified_time": invoice.modified_time,
                "fetched_at": invoice.fetched_at.isoformat() if invoice.fetched_at else None,
                "services_count": len(services),
                "parts_count": len(parts),
                "services": [
                    {
                        "id": str(service.id),
                        "id_job": service.id_job,
                        "harga_servis": float(service.harga_servis) if service.harga_servis else None,
                        "promo_id_jasa": service.promo_id_jasa,
                        "disc_service_amount": float(service.disc_service_amount) if service.disc_service_amount else None,
                        "disc_service_percentage": service.disc_service_percentage,
                        "total_harga_servis": float(service.total_harga_servis) if service.total_harga_servis else None,
                        "created_time": service.created_time,
                        "modified_time": service.modified_time
                    }
                    for service in services
                ],
                "parts": [
                    {
                        "id": str(part.id),
                        "id_job": part.id_job,
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "harga_parts": float(part.harga_parts) if part.harga_parts else None,
                        "promo_id_parts": part.promo_id_parts,
                        "disc_parts_amount": float(part.disc_parts_amount) if part.disc_parts_amount else None,
                        "disc_parts_percentage": part.disc_parts_percentage,
                        "ppn": float(part.ppn) if part.ppn else None,
                        "total_harga_parts": float(part.total_harga_parts) if part.total_harga_parts else None,
                        "uang_muka": float(part.uang_muka) if part.uang_muka else None,
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
        logger.error(f"Error fetching workshop invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching workshop invoice data: {str(e)}")


@router.get("/summary")
async def get_workshop_invoice_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get workshop invoice summary statistics"""
    try:
        processor = WorkshopInvoiceDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting workshop invoice summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_workshop_invoice_data(db: Session = Depends(get_db)):
    """Get list of dealers that have workshop invoice data"""
    try:
        dealers = db.query(Dealer).join(WorkshopInvoiceData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with workshop invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_workshop_invoice_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    no_work_order: Optional[str] = Query("", description="Work order number filter"),
    db: Session = Depends(get_db)
):
    """Test workshop invoice API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = WorkshopInvoiceDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time, no_work_order=no_work_order
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing workshop invoice fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_workshop_invoice_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search workshop invoice data across multiple fields"""
    try:
        # Base query
        query = db.query(WorkshopInvoiceData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(WorkshopInvoiceData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                WorkshopInvoiceData.no_work_order.ilike(search_term),
                WorkshopInvoiceData.no_njb.ilike(search_term),
                WorkshopInvoiceData.no_nsc.ilike(search_term)
            )
        )
        
        invoices = query.limit(limit).all()
        
        result = [
            {
                "id": str(invoice.id),
                "dealer_id": invoice.dealer_id,
                "dealer_name": invoice.dealer.dealer_name,
                "no_work_order": invoice.no_work_order,
                "no_njb": invoice.no_njb,
                "no_nsc": invoice.no_nsc,
                "total_harga_njb": float(invoice.total_harga_njb) if invoice.total_harga_njb else None,
                "total_harga_nsc": float(invoice.total_harga_nsc) if invoice.total_harga_nsc else None
            }
            for invoice in invoices
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching workshop invoice data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
