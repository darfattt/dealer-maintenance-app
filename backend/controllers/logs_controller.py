"""
Logs controller for fetch logs and system logs
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db, FetchLog
from models.schemas import FetchLogResponse
from .base_controller import BaseController

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/fetch-logs/", response_model=List[FetchLogResponse])
async def get_fetch_logs(
    dealer_id: Optional[str] = None,
    status: Optional[str] = None,
    fetch_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get fetch logs with optional filters"""
    query = db.query(FetchLog)

    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)
    if status:
        query = query.filter(FetchLog.status == status)
    if fetch_type:
        query = query.filter(FetchLog.fetch_type == fetch_type)

    logs = query.order_by(desc(FetchLog.completed_at)).offset(skip).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(logs)
    
    BaseController.log_operation("GET_FETCH_LOGS", f"Retrieved {len(logs)} fetch logs")
    return logs


@router.get("/fetch-logs/summary")
async def get_fetch_logs_summary(
    dealer_id: Optional[str] = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get fetch logs summary statistics"""
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(FetchLog).filter(
        FetchLog.completed_at >= start_date,
        FetchLog.completed_at <= end_date
    )
    
    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)
    
    # Get total logs
    total_logs = query.count()
    
    # Get success/failure counts
    success_count = query.filter(FetchLog.status == "success").count()
    failure_count = query.filter(FetchLog.status == "failed").count()
    
    # Get logs by fetch type
    fetch_type_counts = db.query(
        FetchLog.fetch_type,
        func.count(FetchLog.id).label('count')
    ).filter(
        FetchLog.completed_at >= start_date,
        FetchLog.completed_at <= end_date
    )
    
    if dealer_id:
        fetch_type_counts = fetch_type_counts.filter(FetchLog.dealer_id == dealer_id)
    
    fetch_type_counts = fetch_type_counts.group_by(FetchLog.fetch_type).all()
    
    # Get average duration
    avg_duration = query.filter(
        FetchLog.fetch_duration_seconds.isnot(None)
    ).with_entities(func.avg(FetchLog.fetch_duration_seconds)).scalar()
    
    # Get total records fetched
    total_records = query.filter(
        FetchLog.records_fetched.isnot(None)
    ).with_entities(func.sum(FetchLog.records_fetched)).scalar()
    
    summary_data = {
        "period_days": days,
        "total_logs": total_logs,
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": round((success_count / total_logs * 100) if total_logs > 0 else 0, 2),
        "avg_duration_seconds": round(float(avg_duration) if avg_duration else 0, 2),
        "total_records_fetched": int(total_records) if total_records else 0,
        "fetch_type_distribution": [
            {"fetch_type": row.fetch_type, "count": row.count}
            for row in fetch_type_counts
        ]
    }
    
    BaseController.log_operation("GET_FETCH_LOGS_SUMMARY", f"Generated fetch logs summary for {days} days")
    return summary_data


@router.get("/fetch-logs/errors")
async def get_recent_errors(
    dealer_id: Optional[str] = None,
    hours: int = 24,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent error logs"""
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    query = db.query(FetchLog).filter(
        FetchLog.status == "failed",
        FetchLog.completed_at >= start_time,
        FetchLog.completed_at <= end_time
    )
    
    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)
    
    error_logs = query.order_by(desc(FetchLog.completed_at)).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(error_logs)
    
    BaseController.log_operation("GET_RECENT_ERRORS", f"Retrieved {len(error_logs)} error logs from last {hours} hours")
    return {
        "period_hours": hours,
        "error_count": len(error_logs),
        "errors": error_logs
    }


@router.get("/fetch-logs/performance")
async def get_performance_metrics(
    dealer_id: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get performance metrics for fetch operations"""
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(FetchLog).filter(
        FetchLog.completed_at >= start_date,
        FetchLog.completed_at <= end_date,
        FetchLog.status == "success"
    )
    
    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)
    
    # Get performance metrics by fetch type
    performance_by_type = db.query(
        FetchLog.fetch_type,
        func.avg(FetchLog.fetch_duration_seconds).label('avg_duration'),
        func.min(FetchLog.fetch_duration_seconds).label('min_duration'),
        func.max(FetchLog.fetch_duration_seconds).label('max_duration'),
        func.avg(FetchLog.records_fetched).label('avg_records'),
        func.sum(FetchLog.records_fetched).label('total_records'),
        func.count(FetchLog.id).label('execution_count')
    ).filter(
        FetchLog.completed_at >= start_date,
        FetchLog.completed_at <= end_date,
        FetchLog.status == "success"
    )
    
    if dealer_id:
        performance_by_type = performance_by_type.filter(FetchLog.dealer_id == dealer_id)
    
    performance_by_type = performance_by_type.group_by(FetchLog.fetch_type).all()
    
    performance_data = {
        "period_days": days,
        "dealer_id": dealer_id,
        "performance_by_type": [
            {
                "fetch_type": row.fetch_type,
                "avg_duration_seconds": round(float(row.avg_duration) if row.avg_duration else 0, 2),
                "min_duration_seconds": int(row.min_duration) if row.min_duration else 0,
                "max_duration_seconds": int(row.max_duration) if row.max_duration else 0,
                "avg_records_per_execution": round(float(row.avg_records) if row.avg_records else 0, 2),
                "total_records_fetched": int(row.total_records) if row.total_records else 0,
                "execution_count": row.execution_count
            }
            for row in performance_by_type
        ]
    }
    
    BaseController.log_operation("GET_PERFORMANCE_METRICS", f"Generated performance metrics for {days} days")
    return performance_data


@router.delete("/fetch-logs/cleanup")
async def cleanup_old_logs(days_to_keep: int = 90, db: Session = Depends(get_db)):
    """Clean up old fetch logs (older than specified days)"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    # Count logs to be deleted
    logs_to_delete = db.query(FetchLog).filter(FetchLog.completed_at < cutoff_date).count()
    
    # Delete old logs
    deleted_count = db.query(FetchLog).filter(FetchLog.completed_at < cutoff_date).delete()
    db.commit()
    
    BaseController.log_operation("CLEANUP_LOGS", f"Deleted {deleted_count} logs older than {days_to_keep} days")
    return {
        "message": f"Cleaned up old fetch logs",
        "days_to_keep": days_to_keep,
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date.isoformat()
    }
