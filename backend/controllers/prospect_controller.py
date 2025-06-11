"""
Prospect controller for prospect data endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from database import get_db, Dealer, ProspectData
from models.schemas import ProspectDataResponse
from .base_controller import BaseController

router = APIRouter(prefix="/prospect-data", tags=["prospect"])


@router.get("/", response_model=List[ProspectDataResponse])
async def get_prospect_data(
    dealer_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get prospect data with optional filters"""
    query = db.query(ProspectData)

    if dealer_id:
        query = query.filter(ProspectData.dealer_id == dealer_id)
    if from_date:
        query = query.filter(ProspectData.tanggal_prospect >= from_date)
    if to_date:
        query = query.filter(ProspectData.tanggal_prospect <= to_date)

    prospects = query.offset(skip).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(prospects)
    
    BaseController.log_operation("GET_PROSPECT_DATA", f"Retrieved {len(prospects)} prospect records")
    return prospects


@router.get("/analytics/{dealer_id}")
async def get_prospect_analytics(dealer_id: str, db: Session = Depends(get_db)):
    """Get prospect analytics for a specific dealer"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)
    
    # Get prospect data grouped by date
    daily_counts = db.query(
        ProspectData.tanggal_prospect,
        func.count(ProspectData.id).label('count')
    ).filter(
        ProspectData.dealer_id == dealer_id,
        ProspectData.tanggal_prospect.isnot(None)
    ).group_by(
        ProspectData.tanggal_prospect
    ).order_by(
        ProspectData.tanggal_prospect
    ).all()
    
    # Get status distribution
    status_counts = db.query(
        ProspectData.status_prospect,
        func.count(ProspectData.id).label('count')
    ).filter(
        ProspectData.dealer_id == dealer_id,
        ProspectData.status_prospect.isnot(None)
    ).group_by(
        ProspectData.status_prospect
    ).all()
    
    # Get total counts
    total_prospects = db.query(func.count(ProspectData.id)).filter(
        ProspectData.dealer_id == dealer_id
    ).scalar()
    
    analytics_data = {
        "dealer_id": dealer_id,
        "total_prospects": total_prospects,
        "daily_counts": [
            {"date": str(row.tanggal_prospect), "count": row.count}
            for row in daily_counts
        ],
        "status_distribution": [
            {"status": row.status_prospect, "count": row.count}
            for row in status_counts
        ]
    }
    
    BaseController.log_operation("GET_PROSPECT_ANALYTICS", f"Generated analytics for dealer {dealer_id}")
    return analytics_data


@router.get("/summary/{dealer_id}")
async def get_prospect_summary(dealer_id: str, db: Session = Depends(get_db)):
    """Get prospect summary statistics for a dealer"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)
    
    # Get summary statistics
    total_prospects = db.query(func.count(ProspectData.id)).filter(
        ProspectData.dealer_id == dealer_id
    ).scalar()
    
    # Get recent prospects (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    
    recent_prospects = db.query(func.count(ProspectData.id)).filter(
        ProspectData.dealer_id == dealer_id,
        ProspectData.tanggal_prospect >= seven_days_ago
    ).scalar()
    
    # Get active prospects (assuming status_prospect indicates activity)
    active_prospects = db.query(func.count(ProspectData.id)).filter(
        ProspectData.dealer_id == dealer_id,
        ProspectData.status_prospect.isnot(None),
        ProspectData.status_prospect != "closed"
    ).scalar()
    
    summary_data = {
        "dealer_id": dealer_id,
        "total_prospects": total_prospects or 0,
        "recent_prospects": recent_prospects or 0,
        "active_prospects": active_prospects or 0,
        "conversion_rate": round((active_prospects / total_prospects * 100) if total_prospects > 0 else 0, 2)
    }
    
    BaseController.log_operation("GET_PROSPECT_SUMMARY", f"Generated summary for dealer {dealer_id}")
    return summary_data
