"""
Billing Process Controller

This module provides REST API endpoints for billing process data management.
It handles CRUD operations and data retrieval for billing process information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, BillingProcessData, Dealer
from tasks.processors.billing_process_processor import BillingProcessDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing_process", tags=["billing_process"])


@router.get("/")
async def get_billing_process_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in invoice ID, SPK ID, customer ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get billing process data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(BillingProcessData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(BillingProcessData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BillingProcessData.id_invoice.ilike(search_term),
                    BillingProcessData.id_spk.ilike(search_term),
                    BillingProcessData.id_customer.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        billing_data = query.order_by(desc(BillingProcessData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for billing in billing_data:
            billing_dict = {
                "id": str(billing.id),
                "dealer_id": billing.dealer_id,
                "dealer_name": billing.dealer.dealer_name,
                "id_invoice": billing.id_invoice,
                "id_spk": billing.id_spk,
                "id_customer": billing.id_customer,
                "amount": float(billing.amount) if billing.amount else None,
                "tipe_pembayaran": billing.tipe_pembayaran,
                "cara_bayar": billing.cara_bayar,
                "status": billing.status,
                "note": billing.note,
                "created_time": billing.created_time,
                "modified_time": billing.modified_time,
                "fetched_at": billing.fetched_at.isoformat() if billing.fetched_at else None
            }
            result.append(billing_dict)
        
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
        logger.error(f"Error fetching billing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching billing process data: {str(e)}")


@router.get("/summary")
async def get_billing_process_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get billing process summary statistics"""
    try:
        processor = BillingProcessDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting billing process summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_billing_process_data(db: Session = Depends(get_db)):
    """Get list of dealers that have billing process data"""
    try:
        dealers = db.query(Dealer).join(BillingProcessData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with billing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_billing_process_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    id_spk: Optional[str] = Query("", description="SPK ID filter"),
    id_customer: Optional[str] = Query("", description="Customer ID filter"),
    db: Session = Depends(get_db)
):
    """Test billing process API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = BillingProcessDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            id_spk=id_spk,
            id_customer=id_customer
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing billing process fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_billing_process_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search billing process data across multiple fields"""
    try:
        # Base query
        query = db.query(BillingProcessData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(BillingProcessData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                BillingProcessData.id_invoice.ilike(search_term),
                BillingProcessData.id_spk.ilike(search_term),
                BillingProcessData.id_customer.ilike(search_term),
                BillingProcessData.note.ilike(search_term)
            )
        )
        
        billings = query.limit(limit).all()
        
        result = [
            {
                "id": str(billing.id),
                "dealer_id": billing.dealer_id,
                "dealer_name": billing.dealer.dealer_name,
                "id_invoice": billing.id_invoice,
                "id_spk": billing.id_spk,
                "id_customer": billing.id_customer,
                "amount": float(billing.amount) if billing.amount else None,
                "status": billing.status
            }
            for billing in billings
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching billing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
