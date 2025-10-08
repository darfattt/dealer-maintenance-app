"""
Audit routes for login activity tracking
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.schemas.audit import AuditLogResponse, AuditLogListResponse, AuditStatsResponse
from app.models.login_audit import AuditAction
from app.models.user import UserRole
from app.repositories.audit_repository import AuditRepository
from app.dependencies import get_db, get_current_user
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/login-activities", response_model=AuditLogListResponse)
def get_login_activities(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    email: Optional[str] = Query(None, description="Filter by email (partial match)"),
    action: Optional[AuditAction] = Query(None, description="Filter by action type"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get login activities with filtering and pagination

    Regular users can only see their own login activities.
    Admins (SUPER_ADMIN, SYSTEM_ADMIN) can see all activities.
    """
    audit_repo = AuditRepository(db)

    # Check permissions
    # Regular users can only see their own logs
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.SYSTEM_ADMIN]:
        # Override user_id filter to current user
        user_id = str(current_user.id)
        logger.info(f"User {current_user.email} accessing their own audit logs")
    else:
        logger.info(f"Admin {current_user.email} accessing audit logs")

    # Calculate skip
    skip = (page - 1) * per_page

    # Convert user_id string to UUID if provided
    import uuid
    user_uuid = None
    if user_id:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format"
            )

    # Get audit logs
    logs, total = audit_repo.get_audit_logs(
        skip=skip,
        limit=per_page,
        user_id=user_uuid,
        email=email,
        action=action,
        success=success,
        ip_address=ip_address,
        date_from=date_from,
        date_to=date_to
    )

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            email=log.email,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            success=log.success,
            failure_reason=log.failure_reason,
            created_at=log.created_at
        )
        for log in logs
    ]

    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=total_pages
    )


@router.get("/login-activities/stats", response_model=AuditStatsResponse)
def get_login_stats(
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get login statistics

    Only admins (SUPER_ADMIN, SYSTEM_ADMIN) can access statistics.
    """
    # Check permissions - only admins can see stats
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access login statistics"
        )

    audit_repo = AuditRepository(db)

    # Get statistics
    stats = audit_repo.get_login_stats(
        date_from=date_from,
        date_to=date_to
    )

    return AuditStatsResponse(
        total_attempts=stats["total_attempts"],
        successful_logins=stats["successful_logins"],
        failed_logins=stats["failed_logins"],
        logouts=stats["logouts"],
        success_rate=stats["success_rate"],
        date_from=date_from,
        date_to=date_to
    )


@router.get("/login-activities/failed", response_model=AuditLogListResponse)
def get_failed_login_attempts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    email: Optional[str] = Query(None, description="Filter by email"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get failed login attempts for security monitoring

    Only admins (SUPER_ADMIN, SYSTEM_ADMIN) can access this endpoint.
    """
    # Check permissions - only admins can see failed login attempts
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access failed login attempts"
        )

    audit_repo = AuditRepository(db)

    # Calculate skip
    skip = (page - 1) * per_page

    # Get failed login attempts
    failed_attempts, total = audit_repo.get_failed_login_attempts(
        email=email,
        ip_address=ip_address,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=per_page
    )

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            email=log.email,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            success=log.success,
            failure_reason=log.failure_reason,
            created_at=log.created_at
        )
        for log in failed_attempts
    ]

    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=total_pages
    )


@router.get("/login-activities/my-history", response_model=AuditLogListResponse)
def get_my_login_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    action: Optional[AuditAction] = Query(None, description="Filter by action type"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's login history

    Any authenticated user can access their own login history.
    """
    audit_repo = AuditRepository(db)

    # Calculate skip
    skip = (page - 1) * per_page

    # Get user's login history
    logs, total = audit_repo.get_user_login_history(
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
        action=action
    )

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            email=log.email,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            success=log.success,
            failure_reason=log.failure_reason,
            created_at=log.created_at
        )
        for log in logs
    ]

    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=total_pages
    )


@router.get("/login-activities/today")
def get_today_login_activities(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all login activities from today (no pagination, no filters)

    Only admins (SUPER_ADMIN, SYSTEM_ADMIN) can access this endpoint.
    Returns all activities from 00:00:00 today to current time in Indonesia timezone (WIB/UTC+7).
    """
    # Check permissions - only admins
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access today's login activities"
        )

    from app.utils.timezone_utils import get_indonesia_datetime
    audit_repo = AuditRepository(db)

    # Get today's date range in Indonesia timezone (00:00:00 to 23:59:59 WIB)
    indonesia_now = get_indonesia_datetime()
    today_start = datetime.combine(indonesia_now.date(), datetime.min.time())
    today_end = datetime.combine(indonesia_now.date(), datetime.max.time())

    # Get all logs from today without pagination
    logs, total = audit_repo.get_audit_logs(
        skip=0,
        limit=999999,  # Very large number to get all records
        date_from=today_start,
        date_to=today_end
    )

    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            email=log.email,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            success=log.success,
            failure_reason=log.failure_reason,
            created_at=log.created_at
        )
        for log in logs
    ]

    return {
        "date": indonesia_now.date().isoformat(),
        "total": total,
        "activities": log_responses
    }
