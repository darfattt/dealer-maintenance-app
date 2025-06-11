"""
PKB controller for PKB (Service Record) data endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from database import get_db, Dealer, PKBData
from models.schemas import PKBDataResponse
from .base_controller import BaseController

router = APIRouter(prefix="/pkb-data", tags=["pkb"])


@router.get("/", response_model=List[PKBDataResponse])
async def get_pkb_data(
    dealer_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get PKB data with optional filters"""
    query = db.query(PKBData)

    if dealer_id:
        query = query.filter(PKBData.dealer_id == dealer_id)
    if from_date:
        # Parse tanggal_servis string to date for comparison
        query = query.filter(PKBData.tanggal_servis.isnot(None))
    if to_date:
        query = query.filter(PKBData.tanggal_servis.isnot(None))

    pkb_records = query.offset(skip).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(pkb_records)
    
    BaseController.log_operation("GET_PKB_DATA", f"Retrieved {len(pkb_records)} PKB records")
    return pkb_records


@router.get("/analytics/{dealer_id}")
async def get_pkb_analytics(dealer_id: str, db: Session = Depends(get_db)):
    """Get PKB analytics for a specific dealer"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)

    # Count by status
    status_counts = db.query(
        PKBData.status_work_order,
        func.count(PKBData.id).label('count')
    ).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.status_work_order.isnot(None)
    ).group_by(
        PKBData.status_work_order
    ).all()

    # Count by unit type
    unit_counts = db.query(
        PKBData.kode_tipe_unit,
        func.count(PKBData.id).label('count')
    ).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.kode_tipe_unit.isnot(None)
    ).group_by(
        PKBData.kode_tipe_unit
    ).all()

    # Get total counts
    total_pkb = db.query(func.count(PKBData.id)).filter(
        PKBData.dealer_id == dealer_id
    ).scalar()

    # Average service cost
    avg_service_cost = db.query(func.avg(PKBData.total_biaya_service)).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.total_biaya_service.isnot(None)
    ).scalar()

    analytics_data = {
        "dealer_id": dealer_id,
        "total_pkb": total_pkb,
        "avg_service_cost": float(avg_service_cost) if avg_service_cost else 0,
        "status_distribution": [
            {"status": row.status_work_order, "count": row.count}
            for row in status_counts
        ],
        "unit_distribution": [
            {"unit": row.kode_tipe_unit, "count": row.count}
            for row in unit_counts
        ]
    }
    
    BaseController.log_operation("GET_PKB_ANALYTICS", f"Generated PKB analytics for dealer {dealer_id}")
    return analytics_data


@router.get("/summary/{dealer_id}")
async def get_pkb_summary(dealer_id: str, db: Session = Depends(get_db)):
    """Get PKB summary statistics for a dealer"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)
    
    # Get summary statistics
    total_services = db.query(func.count(PKBData.id)).filter(
        PKBData.dealer_id == dealer_id
    ).scalar()
    
    # Get completed services
    completed_services = db.query(func.count(PKBData.id)).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.status_work_order == "completed"
    ).scalar()
    
    # Get pending services
    pending_services = db.query(func.count(PKBData.id)).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.status_work_order.in_(["pending", "in_progress"])
    ).scalar()
    
    # Total revenue
    total_revenue = db.query(func.sum(PKBData.total_biaya_service)).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.total_biaya_service.isnot(None)
    ).scalar()
    
    summary_data = {
        "dealer_id": dealer_id,
        "total_services": total_services or 0,
        "completed_services": completed_services or 0,
        "pending_services": pending_services or 0,
        "total_revenue": float(total_revenue) if total_revenue else 0,
        "completion_rate": round((completed_services / total_services * 100) if total_services > 0 else 0, 2)
    }
    
    BaseController.log_operation("GET_PKB_SUMMARY", f"Generated PKB summary for dealer {dealer_id}")
    return summary_data


@router.get("/work-orders/{dealer_id}")
async def get_work_orders(dealer_id: str, status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get work orders for a dealer with optional status filter"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)
    
    query = db.query(PKBData).filter(PKBData.dealer_id == dealer_id)
    
    if status:
        query = query.filter(PKBData.status_work_order == status)
    
    work_orders = query.order_by(PKBData.fetched_at.desc()).limit(100).all()
    BaseController.convert_list_uuids_to_strings(work_orders)
    
    BaseController.log_operation("GET_WORK_ORDERS", f"Retrieved {len(work_orders)} work orders for dealer {dealer_id}")
    return work_orders
