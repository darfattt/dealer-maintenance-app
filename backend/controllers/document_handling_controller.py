"""
Document Handling Controller
Handles API endpoints for document handling data management
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging

from database import get_db, DocumentHandlingData, DocumentHandlingUnit, Dealer
from tasks.processors.document_handling_processor import DocumentHandlingDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document_handling", tags=["document_handling"])


@router.get("/", response_model=Dict[str, Any])
async def get_document_handling_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    search: Optional[str] = Query(None, description="Search in SO ID, SPK ID, or chassis number"),
    db: Session = Depends(get_db)
):
    """
    Get document handling data with pagination and search
    
    Args:
        dealer_id: Optional dealer ID filter
        limit: Maximum number of records to return
        offset: Number of records to skip for pagination
        search: Optional search term
        db: Database session
    
    Returns:
        Paginated document handling data with metadata
    """
    try:
        # Build base query
        query = db.query(DocumentHandlingData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(DocumentHandlingData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (DocumentHandlingData.id_so.ilike(search_term)) |
                (DocumentHandlingData.id_spk.ilike(search_term))
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and get results
        documents = query.order_by(DocumentHandlingData.fetched_at.desc()).offset(offset).limit(limit).all()
        
        # Format results
        results = []
        for doc in documents:
            # Get units for this document
            units = db.query(DocumentHandlingUnit).filter(
                DocumentHandlingUnit.document_handling_data_id == doc.id
            ).all()
            
            doc_data = {
                "id": str(doc.id),
                "dealer_id": doc.dealer_id,
                "dealer_name": doc.dealer.dealer_name if doc.dealer else "Unknown",
                "id_so": doc.id_so,
                "id_spk": doc.id_spk,
                "created_time": doc.created_time,
                "modified_time": doc.modified_time,
                "fetched_at": doc.fetched_at.isoformat() if doc.fetched_at else None,
                "unit_count": len(units),
                "units": [
                    {
                        "id": str(unit.id),
                        "nomor_rangka": unit.nomor_rangka,
                        "nomor_faktur_stnk": unit.nomor_faktur_stnk,
                        "status_faktur_stnk": unit.status_faktur_stnk,
                        "nomor_stnk": unit.nomor_stnk,
                        "plat_nomor": unit.plat_nomor,
                        "nomor_bpkb": unit.nomor_bpkb,
                        "nama_penerima_bpkb": unit.nama_penerima_bpkb,
                        "nama_penerima_stnk": unit.nama_penerima_stnk,
                        "tanggal_terima_stnk_oleh_konsumen": unit.tanggal_terima_stnk_oleh_konsumen,
                        "tanggal_terima_bpkb_oleh_konsumen": unit.tanggal_terima_bpkb_oleh_konsumen
                    } for unit in units
                ]
            }
            results.append(doc_data)
        
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
        logger.error(f"Error retrieving document handling data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


@router.get("/summary", response_model=Dict[str, Any])
async def get_document_handling_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for document handling data
    
    Args:
        dealer_id: Optional dealer ID filter
        db: Database session
    
    Returns:
        Summary statistics including totals and status distribution
    """
    try:
        processor = DocumentHandlingDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting document handling summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers", response_model=Dict[str, Any])
async def get_dealers_with_document_handling_data(db: Session = Depends(get_db)):
    """
    Get list of dealers that have document handling data
    
    Args:
        db: Database session
    
    Returns:
        List of dealers with document handling data counts
    """
    try:
        # Query dealers with document handling data
        dealers_with_data = db.query(
            Dealer.dealer_id,
            Dealer.dealer_name,
            db.func.count(DocumentHandlingData.id).label('document_count')
        ).join(
            DocumentHandlingData, Dealer.dealer_id == DocumentHandlingData.dealer_id
        ).group_by(
            Dealer.dealer_id, Dealer.dealer_name
        ).all()
        
        dealers = [
            {
                "dealer_id": dealer.dealer_id,
                "dealer_name": dealer.dealer_name,
                "document_count": dealer.document_count
            }
            for dealer in dealers_with_data
        ]
        
        return {
            "success": True,
            "dealers": dealers,
            "total_dealers": len(dealers)
        }
        
    except Exception as e:
        logger.error(f"Error getting dealers with document handling data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dealers: {str(e)}")


@router.post("/test-fetch", response_model=Dict[str, Any])
async def test_document_handling_fetch(
    dealer_id: str = Query(..., description="Dealer ID to test"),
    from_time: str = Query("2024-01-15 00:00:00", description="Start time"),
    to_time: str = Query("2024-01-16 23:59:59", description="End time"),
    id_spk: str = Query("", description="Optional SPK ID filter"),
    id_customer: str = Query("", description="Optional Customer ID filter"),
    db: Session = Depends(get_db)
):
    """
    Test document handling API connectivity without storing data
    
    Args:
        dealer_id: Dealer ID to test
        from_time: Start time for data fetch
        to_time: End time for data fetch
        id_spk: Optional SPK ID filter
        id_customer: Optional Customer ID filter
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
        processor = DocumentHandlingDataProcessor()
        api_response = processor.fetch_api_data(
            dealer, from_time, to_time, 
            id_spk=id_spk, id_customer=id_customer
        )
        
        return {
            "success": True,
            "dealer_id": dealer_id,
            "test_result": api_response,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing document handling API for dealer {dealer_id}: {e}")
        return {
            "success": False,
            "dealer_id": dealer_id,
            "error": str(e),
            "message": "API test failed"
        }
