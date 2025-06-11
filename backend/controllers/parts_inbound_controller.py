"""
Parts Inbound controller for Parts Inbound data endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from database import get_db, Dealer, PartsInboundData, PartsInboundPO
from models.schemas import PartsInboundDataResponse
from .base_controller import BaseController

router = APIRouter(prefix="/parts-inbound-data", tags=["parts-inbound"])


@router.get("/", response_model=List[PartsInboundDataResponse])
async def get_parts_inbound_data(
    dealer_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get Parts Inbound data with optional filters"""
    query = db.query(PartsInboundData)

    if dealer_id:
        query = query.filter(PartsInboundData.dealer_id == dealer_id)
    if from_date:
        query = query.filter(PartsInboundData.tgl_penerimaan.isnot(None))
    if to_date:
        query = query.filter(PartsInboundData.tgl_penerimaan.isnot(None))

    parts_records = query.offset(skip).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(parts_records)
    
    BaseController.log_operation("GET_PARTS_INBOUND_DATA", f"Retrieved {len(parts_records)} Parts Inbound records")
    return parts_records


@router.get("/analytics/{dealer_id}")
async def get_parts_inbound_analytics(dealer_id: str, db: Session = Depends(get_db)):
    """Get Parts Inbound analytics for a specific dealer"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)

    # Get total parts inbound records
    total_inbound = db.query(func.count(PartsInboundData.id)).filter(
        PartsInboundData.dealer_id == dealer_id
    ).scalar()

    # Get PO statistics
    total_po_items = db.query(func.count(PartsInboundPO.id)).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(
        PartsInboundData.dealer_id == dealer_id
    ).scalar()

    # Get PO distribution by type
    po_type_counts = db.query(
        PartsInboundPO.jenis_order,
        func.count(PartsInboundPO.id).label('count')
    ).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(
        PartsInboundData.dealer_id == dealer_id,
        PartsInboundPO.jenis_order.isnot(None)
    ).group_by(
        PartsInboundPO.jenis_order
    ).all()

    # Get warehouse distribution
    warehouse_counts = db.query(
        PartsInboundPO.id_warehouse,
        func.count(PartsInboundPO.id).label('count')
    ).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(
        PartsInboundData.dealer_id == dealer_id,
        PartsInboundPO.id_warehouse.isnot(None)
    ).group_by(
        PartsInboundPO.id_warehouse
    ).all()

    # Get total quantity
    total_quantity = db.query(func.sum(PartsInboundPO.kuantitas)).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(
        PartsInboundData.dealer_id == dealer_id,
        PartsInboundPO.kuantitas.isnot(None)
    ).scalar()

    analytics_data = {
        "dealer_id": dealer_id,
        "total_inbound_records": total_inbound or 0,
        "total_po_items": total_po_items or 0,
        "total_quantity": int(total_quantity) if total_quantity else 0,
        "po_type_distribution": [
            {"type": row.jenis_order, "count": row.count}
            for row in po_type_counts
        ],
        "warehouse_distribution": [
            {"warehouse": row.id_warehouse, "count": row.count}
            for row in warehouse_counts
        ]
    }
    
    BaseController.log_operation("GET_PARTS_INBOUND_ANALYTICS", f"Generated Parts Inbound analytics for dealer {dealer_id}")
    return analytics_data


@router.get("/summary/{dealer_id}")
async def get_parts_inbound_summary(dealer_id: str, db: Session = Depends(get_db)):
    """Get Parts Inbound summary statistics for a dealer"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)
    
    # Get summary statistics
    total_receipts = db.query(func.count(PartsInboundData.id)).filter(
        PartsInboundData.dealer_id == dealer_id
    ).scalar()
    
    # Get recent receipts (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    
    recent_receipts = db.query(func.count(PartsInboundData.id)).filter(
        PartsInboundData.dealer_id == dealer_id,
        PartsInboundData.fetched_at >= seven_days_ago
    ).scalar()
    
    # Get unique parts count
    unique_parts = db.query(func.count(func.distinct(PartsInboundPO.parts_number))).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(
        PartsInboundData.dealer_id == dealer_id,
        PartsInboundPO.parts_number.isnot(None)
    ).scalar()
    
    # Get unique PO count
    unique_pos = db.query(func.count(func.distinct(PartsInboundPO.no_po))).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(
        PartsInboundData.dealer_id == dealer_id,
        PartsInboundPO.no_po.isnot(None)
    ).scalar()
    
    summary_data = {
        "dealer_id": dealer_id,
        "total_receipts": total_receipts or 0,
        "recent_receipts": recent_receipts or 0,
        "unique_parts": unique_parts or 0,
        "unique_pos": unique_pos or 0,
        "avg_parts_per_receipt": round((unique_parts / total_receipts) if total_receipts > 0 else 0, 2)
    }
    
    BaseController.log_operation("GET_PARTS_INBOUND_SUMMARY", f"Generated Parts Inbound summary for dealer {dealer_id}")
    return summary_data


@router.get("/po-items/{dealer_id}")
async def get_po_items(dealer_id: str, no_po: Optional[str] = None, db: Session = Depends(get_db)):
    """Get PO items for a dealer with optional PO number filter"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, dealer_id, Dealer)
    
    query = db.query(PartsInboundPO).join(
        PartsInboundData, PartsInboundPO.parts_inbound_data_id == PartsInboundData.id
    ).filter(PartsInboundData.dealer_id == dealer_id)
    
    if no_po:
        query = query.filter(PartsInboundPO.no_po == no_po)
    
    po_items = query.order_by(PartsInboundPO.created_time.desc()).limit(100).all()
    BaseController.convert_list_uuids_to_strings(po_items)
    
    BaseController.log_operation("GET_PO_ITEMS", f"Retrieved {len(po_items)} PO items for dealer {dealer_id}")
    return po_items
