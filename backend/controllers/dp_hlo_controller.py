"""
DP HLO Controller

This module provides REST API endpoints for DP HLO data management.
It handles CRUD operations and data retrieval for DP HLO information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, DPHLOData, DPHLOPart, Dealer
from tasks.processors.dp_hlo_processor import DPHLODataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dp_hlo", tags=["dp_hlo"])


@router.get("/")
async def get_dp_hlo_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in HLO document, work order, customer ID, parts number"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get DP HLO data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(DPHLOData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(DPHLOData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join with parts to search in parts data
            query = query.join(DPHLOPart, DPHLOData.id == DPHLOPart.dp_hlo_data_id, isouter=True)
            search_filter = or_(
                DPHLOData.id_hlo_document.ilike(search_term),
                DPHLOData.no_work_order.ilike(search_term),
                DPHLOData.id_customer.ilike(search_term),
                DPHLOData.no_invoice_uang_jaminan.ilike(search_term),
                DPHLOPart.parts_number.ilike(search_term)
            )
            query = query.filter(search_filter).distinct()
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        hlo_records = query.order_by(desc(DPHLOData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for hlo in hlo_records:
            # Get parts for this HLO document
            parts = db.query(DPHLOPart).filter(
                DPHLOPart.dp_hlo_data_id == hlo.id
            ).all()
            
            hlo_dict = {
                "id": str(hlo.id),
                "dealer_id": hlo.dealer_id,
                "dealer_name": hlo.dealer.dealer_name,
                "no_invoice_uang_jaminan": hlo.no_invoice_uang_jaminan,
                "id_hlo_document": hlo.id_hlo_document,
                "tanggal_pemesanan_hlo": hlo.tanggal_pemesanan_hlo,
                "no_work_order": hlo.no_work_order,
                "id_customer": hlo.id_customer,
                "created_time": hlo.created_time,
                "modified_time": hlo.modified_time,
                "fetched_at": hlo.fetched_at.isoformat() if hlo.fetched_at else None,
                "parts_count": len(parts),
                "parts": [
                    {
                        "id": str(part.id),
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "harga_parts": float(part.harga_parts) if part.harga_parts else None,
                        "total_harga_parts": float(part.total_harga_parts) if part.total_harga_parts else None,
                        "uang_muka": float(part.uang_muka) if part.uang_muka else None,
                        "sisa_bayar": float(part.sisa_bayar) if part.sisa_bayar else None,
                        "created_time": part.created_time,
                        "modified_time": part.modified_time
                    }
                    for part in parts
                ]
            }
            result.append(hlo_dict)
        
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
        logger.error(f"Error fetching DP HLO data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching DP HLO data: {str(e)}")


@router.get("/summary")
async def get_dp_hlo_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get DP HLO summary statistics"""
    try:
        processor = DPHLODataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting DP HLO summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_dp_hlo_data(db: Session = Depends(get_db)):
    """Get list of dealers that have DP HLO data"""
    try:
        dealers = db.query(Dealer).join(DPHLOData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with DP HLO data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_dp_hlo_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    no_work_order: Optional[str] = Query("", description="Work order number filter"),
    id_hlo_document: Optional[str] = Query("", description="HLO document ID filter"),
    db: Session = Depends(get_db)
):
    """Test DP HLO API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = DPHLODataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            no_work_order=no_work_order,
            id_hlo_document=id_hlo_document
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing DP HLO fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_dp_hlo_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search DP HLO data across multiple fields"""
    try:
        # Base query
        query = db.query(DPHLOData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(DPHLOData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                DPHLOData.id_hlo_document.ilike(search_term),
                DPHLOData.no_work_order.ilike(search_term),
                DPHLOData.id_customer.ilike(search_term),
                DPHLOData.no_invoice_uang_jaminan.ilike(search_term)
            )
        )
        
        # Also search in parts data
        part_query = db.query(DPHLOPart).filter(
            DPHLOPart.parts_number.ilike(search_term)
        ).limit(limit).all()
        
        # Get HLO document IDs from parts search
        hlo_ids_from_parts = [part.dp_hlo_data_id for part in part_query]
        
        # Combine results
        if hlo_ids_from_parts:
            query = query.filter(
                or_(
                    DPHLOData.id.in_(hlo_ids_from_parts),
                    # Original HLO-level search conditions already applied
                )
            )
        
        hlo_documents = query.limit(limit).all()
        
        result = [
            {
                "id": str(hlo.id),
                "dealer_id": hlo.dealer_id,
                "dealer_name": hlo.dealer.dealer_name,
                "id_hlo_document": hlo.id_hlo_document,
                "no_work_order": hlo.no_work_order,
                "tanggal_pemesanan_hlo": hlo.tanggal_pemesanan_hlo,
                "id_customer": hlo.id_customer
            }
            for hlo in hlo_documents
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching DP HLO data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
