"""
Parts Sales Controller

This module provides REST API endpoints for parts sales data management.
It handles CRUD operations and data retrieval for parts sales information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, PartsSalesData, PartsSalesPart, Dealer
from tasks.processors.parts_sales_processor import PartsSalesDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/parts_sales", tags=["parts_sales"])


@router.get("/")
async def get_parts_sales_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in SO number, customer ID, parts number"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get parts sales data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(PartsSalesData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(PartsSalesData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join with parts to search in parts data
            query = query.join(PartsSalesPart, PartsSalesData.id == PartsSalesPart.parts_sales_data_id, isouter=True)
            search_filter = or_(
                PartsSalesData.no_so.ilike(search_term),
                PartsSalesData.id_customer.ilike(search_term),
                PartsSalesData.nama_customer.ilike(search_term),
                PartsSalesPart.parts_number.ilike(search_term),
                PartsSalesPart.booking_id_reference.ilike(search_term)
            )
            query = query.filter(search_filter).distinct()
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        sales_records = query.order_by(desc(PartsSalesData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for sales in sales_records:
            # Get parts for this sales order
            parts = db.query(PartsSalesPart).filter(
                PartsSalesPart.parts_sales_data_id == sales.id
            ).all()
            
            sales_dict = {
                "id": str(sales.id),
                "dealer_id": sales.dealer_id,
                "dealer_name": sales.dealer.dealer_name,
                "no_so": sales.no_so,
                "tgl_so": sales.tgl_so,
                "id_customer": sales.id_customer,
                "nama_customer": sales.nama_customer,
                "disc_so": float(sales.disc_so) if sales.disc_so else None,
                "total_harga_so": float(sales.total_harga_so) if sales.total_harga_so else None,
                "created_time": sales.created_time,
                "modified_time": sales.modified_time,
                "fetched_at": sales.fetched_at.isoformat() if sales.fetched_at else None,
                "parts_count": len(parts),
                "parts": [
                    {
                        "id": str(part.id),
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "harga_parts": float(part.harga_parts) if part.harga_parts else None,
                        "promo_id_parts": part.promo_id_parts,
                        "disc_amount": float(part.disc_amount) if part.disc_amount else None,
                        "disc_percentage": part.disc_percentage,
                        "ppn": float(part.ppn) if part.ppn else None,
                        "total_harga_parts": float(part.total_harga_parts) if part.total_harga_parts else None,
                        "uang_muka": float(part.uang_muka) if part.uang_muka else None,
                        "booking_id_reference": part.booking_id_reference,
                        "created_time": part.created_time,
                        "modified_time": part.modified_time
                    }
                    for part in parts
                ]
            }
            result.append(sales_dict)
        
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
        logger.error(f"Error fetching parts sales data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching parts sales data: {str(e)}")


@router.get("/summary")
async def get_parts_sales_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get parts sales summary statistics"""
    try:
        processor = PartsSalesDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting parts sales summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_parts_sales_data(db: Session = Depends(get_db)):
    """Get list of dealers that have parts sales data"""
    try:
        dealers = db.query(Dealer).join(PartsSalesData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with parts sales data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_parts_sales_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    no_po: Optional[str] = Query("", description="PO number filter"),
    db: Session = Depends(get_db)
):
    """Test parts sales API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = PartsSalesDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time, no_po=no_po
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing parts sales fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_parts_sales_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search parts sales data across multiple fields"""
    try:
        # Base query
        query = db.query(PartsSalesData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(PartsSalesData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                PartsSalesData.no_so.ilike(search_term),
                PartsSalesData.id_customer.ilike(search_term),
                PartsSalesData.nama_customer.ilike(search_term)
            )
        )
        
        # Also search in parts data
        part_query = db.query(PartsSalesPart).filter(
            or_(
                PartsSalesPart.parts_number.ilike(search_term),
                PartsSalesPart.booking_id_reference.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Get sales order IDs from parts search
        sales_ids_from_parts = [part.parts_sales_data_id for part in part_query]
        
        # Combine results
        if sales_ids_from_parts:
            query = query.filter(
                or_(
                    PartsSalesData.id.in_(sales_ids_from_parts),
                    # Original sales-level search conditions already applied
                )
            )
        
        sales_orders = query.limit(limit).all()
        
        result = [
            {
                "id": str(sales.id),
                "dealer_id": sales.dealer_id,
                "dealer_name": sales.dealer.dealer_name,
                "no_so": sales.no_so,
                "tgl_so": sales.tgl_so,
                "nama_customer": sales.nama_customer,
                "total_harga_so": float(sales.total_harga_so) if sales.total_harga_so else None
            }
            for sales in sales_orders
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching parts sales data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
