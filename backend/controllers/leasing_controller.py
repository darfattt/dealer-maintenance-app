"""
Leasing Controller
Handles HTTP endpoints for leasing data operations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func

from database import get_db, LeasingData, Dealer
from tasks.processors.leasing_processor import LeasingDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leasing", tags=["leasing"])


@router.get("/", response_model=Dict[str, Any])
async def get_leasing_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    search: Optional[str] = Query(None, description="Search in finance company name or SPK ID"),
    db: Session = Depends(get_db)
):
    """
    Get leasing data with optional filtering and pagination
    
    Args:
        dealer_id: Optional dealer ID filter
        limit: Maximum number of records to return
        offset: Number of records to skip for pagination
        search: Optional search term
        db: Database session
    
    Returns:
        Paginated leasing data with metadata
    """
    try:
        # Build base query
        query = db.query(LeasingData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(LeasingData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    LeasingData.nama_finance_company.ilike(search_term),
                    LeasingData.id_spk.ilike(search_term),
                    LeasingData.id_dokumen_pengajuan.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        leasing_records = query.order_by(desc(LeasingData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response data
        records = []
        for record in leasing_records:
            records.append({
                "id": str(record.id),
                "dealer_id": record.dealer_id,
                "dealer_name": record.dealer.dealer_name if record.dealer else "Unknown",
                "id_dokumen_pengajuan": record.id_dokumen_pengajuan,
                "id_spk": record.id_spk,
                "jumlah_dp": float(record.jumlah_dp) if record.jumlah_dp else None,
                "tenor": record.tenor,
                "jumlah_cicilan": float(record.jumlah_cicilan) if record.jumlah_cicilan else None,
                "tanggal_pengajuan": record.tanggal_pengajuan,
                "id_finance_company": record.id_finance_company,
                "nama_finance_company": record.nama_finance_company,
                "id_po_finance_company": record.id_po_finance_company,
                "tanggal_pembuatan_po": record.tanggal_pembuatan_po,
                "tanggal_pengiriman_po_finance_company": record.tanggal_pengiriman_po_finance_company,
                "created_time": record.created_time,
                "modified_time": record.modified_time,
                "fetched_at": record.fetched_at.isoformat() if record.fetched_at else None
            })
        
        return {
            "success": True,
            "data": records,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            },
            "filters": {
                "dealer_id": dealer_id,
                "search": search
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching leasing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching leasing data: {str(e)}")


@router.get("/summary", response_model=Dict[str, Any])
async def get_leasing_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """
    Get leasing data summary statistics
    
    Args:
        dealer_id: Optional dealer ID filter
        db: Database session
    
    Returns:
        Summary statistics for leasing data
    """
    try:
        processor = LeasingDataProcessor()
        
        if dealer_id:
            # Get summary for specific dealer
            summary = processor.get_summary_stats(db, dealer_id)
            summary["dealer_id"] = dealer_id
        else:
            # Get overall summary across all dealers
            total_records = db.query(LeasingData).count()
            
            # Top finance companies
            finance_companies = db.query(
                LeasingData.nama_finance_company,
                func.count(LeasingData.id).label('count')
            ).filter(
                LeasingData.nama_finance_company.isnot(None)
            ).group_by(
                LeasingData.nama_finance_company
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Overall averages
            avg_stats = db.query(
                func.avg(LeasingData.jumlah_dp).label('avg_dp'),
                func.avg(LeasingData.jumlah_cicilan).label('avg_cicilan'),
                func.avg(LeasingData.tenor).label('avg_tenor')
            ).filter(
                and_(
                    LeasingData.jumlah_dp.isnot(None),
                    LeasingData.jumlah_cicilan.isnot(None),
                    LeasingData.tenor.isnot(None)
                )
            ).first()
            
            summary = {
                "total_records": total_records,
                "finance_companies": [{"name": row[0], "count": row[1]} for row in finance_companies],
                "averages": {
                    "dp": float(avg_stats[0]) if avg_stats and avg_stats[0] else 0,
                    "cicilan": float(avg_stats[1]) if avg_stats and avg_stats[1] else 0,
                    "tenor": float(avg_stats[2]) if avg_stats and avg_stats[2] else 0
                },
                "dealer_id": "all"
            }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting leasing summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting leasing summary: {str(e)}")


@router.get("/dealers", response_model=Dict[str, Any])
async def get_dealers_with_leasing_data(db: Session = Depends(get_db)):
    """
    Get list of dealers that have leasing data
    
    Args:
        db: Database session
    
    Returns:
        List of dealers with leasing data counts
    """
    try:
        # Query dealers with leasing data counts
        dealers_with_counts = db.query(
            Dealer.dealer_id,
            Dealer.dealer_name,
            func.count(LeasingData.id).label('leasing_count')
        ).outerjoin(
            LeasingData, Dealer.dealer_id == LeasingData.dealer_id
        ).group_by(
            Dealer.dealer_id, Dealer.dealer_name
        ).order_by(
            desc('leasing_count')
        ).all()
        
        dealers = []
        for dealer_id, dealer_name, count in dealers_with_counts:
            dealers.append({
                "dealer_id": dealer_id,
                "dealer_name": dealer_name,
                "leasing_count": count,
                "has_data": count > 0
            })
        
        return {
            "success": True,
            "dealers": dealers,
            "total_dealers": len(dealers),
            "dealers_with_data": len([d for d in dealers if d["has_data"]])
        }
        
    except Exception as e:
        logger.error(f"Error getting dealers with leasing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dealers with leasing data: {str(e)}")


@router.post("/test-fetch", response_model=Dict[str, Any])
async def test_leasing_fetch(
    dealer_id: str = Query(..., description="Dealer ID to test"),
    from_time: Optional[str] = Query(None, description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: Optional[str] = Query(None, description="End time (YYYY-MM-DD HH:MM:SS)"),
    id_spk: Optional[str] = Query(None, description="SPK ID for filtering"),
    db: Session = Depends(get_db)
):
    """
    Test leasing data fetch without storing to database
    
    Args:
        dealer_id: Dealer ID to test
        from_time: Optional start time
        to_time: Optional end time
        id_spk: Optional SPK ID filter
        db: Database session
    
    Returns:
        Test fetch results
    """
    try:
        processor = LeasingDataProcessor()
        
        # Perform test fetch
        result = processor.fetch_data(
            dealer_id=dealer_id,
            from_time=from_time,
            to_time=to_time,
            id_spk=id_spk
        )
        
        return {
            "success": True,
            "test_result": result,
            "record_count": len(result.get('data', [])) if result else 0,
            "api_status": result.get('status') if result else None,
            "message": result.get('message') if result else "No response"
        }
        
    except Exception as e:
        logger.error(f"Error testing leasing fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing leasing fetch: {str(e)}")


@router.delete("/{dealer_id}", response_model=Dict[str, Any])
async def delete_leasing_data(
    dealer_id: str,
    confirm: bool = Query(False, description="Confirmation flag"),
    db: Session = Depends(get_db)
):
    """
    Delete all leasing data for a specific dealer
    
    Args:
        dealer_id: Dealer ID
        confirm: Confirmation flag (must be True)
        db: Database session
    
    Returns:
        Deletion result
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400, 
                detail="Confirmation required. Set confirm=true to proceed."
            )
        
        # Count records before deletion
        count_before = db.query(LeasingData).filter(LeasingData.dealer_id == dealer_id).count()
        
        if count_before == 0:
            return {
                "success": True,
                "message": f"No leasing data found for dealer {dealer_id}",
                "deleted_count": 0
            }
        
        # Delete records
        deleted_count = db.query(LeasingData).filter(LeasingData.dealer_id == dealer_id).delete()
        db.commit()
        
        logger.info(f"Deleted {deleted_count} leasing records for dealer {dealer_id}")
        
        return {
            "success": True,
            "message": f"Successfully deleted leasing data for dealer {dealer_id}",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting leasing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting leasing data: {str(e)}")
