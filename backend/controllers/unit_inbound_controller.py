"""
Unit Inbound Controller
Handles API endpoints for unit inbound from purchase order data management
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging

from database import get_db, UnitInboundData, UnitInboundUnit, Dealer
from tasks.processors.unit_inbound_processor import UnitInboundDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/unit_inbound", tags=["unit_inbound"])


@router.get("/", response_model=Dict[str, Any])
async def get_unit_inbound_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    search: Optional[str] = Query(None, description="Search in shipping list, invoice, or PO ID"),
    db: Session = Depends(get_db)
):
    """
    Get unit inbound data with pagination and search
    
    Args:
        dealer_id: Optional dealer ID filter
        limit: Maximum number of records to return
        offset: Number of records to skip for pagination
        search: Optional search term
        db: Database session
    
    Returns:
        Paginated unit inbound data with metadata
    """
    try:
        # Build base query
        query = db.query(UnitInboundData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(UnitInboundData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (UnitInboundData.no_shipping_list.ilike(search_term)) |
                (UnitInboundData.no_invoice.ilike(search_term))
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and get results
        shipments = query.order_by(UnitInboundData.fetched_at.desc()).offset(offset).limit(limit).all()
        
        # Format results
        results = []
        for shipment in shipments:
            # Get units for this shipment
            units = db.query(UnitInboundUnit).filter(
                UnitInboundUnit.unit_inbound_data_id == shipment.id
            ).all()
            
            shipment_data = {
                "id": str(shipment.id),
                "dealer_id": shipment.dealer_id,
                "dealer_name": shipment.dealer.dealer_name if shipment.dealer else "Unknown",
                "no_shipping_list": shipment.no_shipping_list,
                "tanggal_terima": shipment.tanggal_terima,
                "main_dealer_id": shipment.main_dealer_id,
                "no_invoice": shipment.no_invoice,
                "status_shipping_list": shipment.status_shipping_list,
                "created_time": shipment.created_time,
                "modified_time": shipment.modified_time,
                "fetched_at": shipment.fetched_at.isoformat() if shipment.fetched_at else None,
                "unit_count": len(units),
                "units": [
                    {
                        "id": str(unit.id),
                        "kode_tipe_unit": unit.kode_tipe_unit,
                        "kode_warna": unit.kode_warna,
                        "kuantitas_terkirim": unit.kuantitas_terkirim,
                        "kuantitas_diterima": unit.kuantitas_diterima,
                        "no_mesin": unit.no_mesin,
                        "no_rangka": unit.no_rangka,
                        "status_rfs": unit.status_rfs,
                        "po_id": unit.po_id,
                        "kelengkapan_unit": unit.kelengkapan_unit,
                        "no_goods_receipt": unit.no_goods_receipt,
                        "doc_nrfs_id": unit.doc_nrfs_id
                    } for unit in units
                ]
            }
            results.append(shipment_data)
        
        return {
            "success": True,
            "data": results,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total_count,
                "has_prev": offset > 0
            },
            "filters": {
                "dealer_id": dealer_id,
                "search": search
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving unit inbound data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


@router.get("/summary", response_model=Dict[str, Any])
async def get_unit_inbound_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for unit inbound data
    
    Args:
        dealer_id: Optional dealer ID filter
        db: Database session
    
    Returns:
        Summary statistics including totals and status distribution
    """
    try:
        processor = UnitInboundDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting unit inbound summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers", response_model=Dict[str, Any])
async def get_dealers_with_unit_inbound_data(db: Session = Depends(get_db)):
    """
    Get list of dealers that have unit inbound data
    
    Args:
        db: Database session
    
    Returns:
        List of dealers with unit inbound data counts
    """
    try:
        # Query dealers with unit inbound data
        dealers_with_data = db.query(
            Dealer.dealer_id,
            Dealer.dealer_name,
            db.func.count(UnitInboundData.id).label('shipment_count')
        ).join(
            UnitInboundData, Dealer.dealer_id == UnitInboundData.dealer_id
        ).group_by(
            Dealer.dealer_id, Dealer.dealer_name
        ).all()
        
        dealers = [
            {
                "dealer_id": dealer.dealer_id,
                "dealer_name": dealer.dealer_name,
                "shipment_count": dealer.shipment_count
            }
            for dealer in dealers_with_data
        ]
        
        return {
            "success": True,
            "dealers": dealers,
            "total_dealers": len(dealers)
        }
        
    except Exception as e:
        logger.error(f"Error getting dealers with unit inbound data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dealers: {str(e)}")


@router.post("/test-fetch", response_model=Dict[str, Any])
async def test_unit_inbound_fetch(
    dealer_id: str = Query(..., description="Dealer ID to test"),
    from_time: str = Query("2024-01-15 00:00:00", description="Start time"),
    to_time: str = Query("2024-01-16 23:59:59", description="End time"),
    po_id: str = Query("", description="Optional PO ID filter"),
    no_shipping_list: str = Query("", description="Optional Shipping List filter"),
    db: Session = Depends(get_db)
):
    """
    Test unit inbound API connectivity without storing data
    
    Args:
        dealer_id: Dealer ID to test
        from_time: Start time for data fetch
        to_time: End time for data fetch
        po_id: Optional PO ID filter
        no_shipping_list: Optional Shipping List filter
        db: Database session
    
    Returns:
        API response without storing to database
    """
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test API call
        processor = UnitInboundDataProcessor()
        api_response = processor.fetch_api_data(
            dealer, from_time, to_time, 
            po_id=po_id, no_shipping_list=no_shipping_list
        )
        
        return {
            "success": True,
            "dealer_id": dealer_id,
            "test_result": api_response,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing unit inbound API for dealer {dealer_id}: {e}")
        return {
            "success": False,
            "dealer_id": dealer_id,
            "error": str(e),
            "message": "API test failed"
        }
