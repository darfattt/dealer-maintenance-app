"""
Audit repository for database operations
"""

import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.models.login_audit import LoginAudit, AuditAction


class AuditRepository:
    """Repository for audit log database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_audit_log(
        self,
        action: AuditAction,
        email: str,
        user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None
    ) -> LoginAudit:
        """
        Create a new audit log entry

        Args:
            action: Type of action (LOGIN, LOGOUT, LOGIN_FAILED)
            email: Email address used in the action
            user_id: User ID (optional, None for failed login with unknown user)
            ip_address: IP address of the client
            user_agent: User agent string
            success: Whether the action was successful
            failure_reason: Reason for failure (if applicable)

        Returns:
            Created audit log instance
        """
        audit_log = LoginAudit(
            action=action,
            email=email,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            created_at=datetime.utcnow()
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def get_audit_log_by_id(self, audit_id: uuid.UUID) -> Optional[LoginAudit]:
        """
        Get audit log by ID

        Args:
            audit_id: Audit log ID

        Returns:
            Audit log instance or None
        """
        return self.db.query(LoginAudit).filter(LoginAudit.id == audit_id).first()

    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[uuid.UUID] = None,
        email: Optional[str] = None,
        action: Optional[AuditAction] = None,
        success: Optional[bool] = None,
        ip_address: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Tuple[List[LoginAudit], int]:
        """
        Get audit logs with filtering and pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Filter by user ID
            email: Filter by email (partial match)
            action: Filter by action type
            success: Filter by success status
            ip_address: Filter by IP address
            date_from: Filter by start date
            date_to: Filter by end date

        Returns:
            Tuple of (audit logs list, total count)
        """
        query = self.db.query(LoginAudit)

        # Apply filters
        if user_id:
            query = query.filter(LoginAudit.user_id == user_id)

        if email:
            query = query.filter(LoginAudit.email.ilike(f"%{email}%"))

        if action:
            query = query.filter(LoginAudit.action == action)

        if success is not None:
            query = query.filter(LoginAudit.success == success)

        if ip_address:
            query = query.filter(LoginAudit.ip_address == ip_address)

        if date_from:
            query = query.filter(LoginAudit.created_at >= date_from)

        if date_to:
            query = query.filter(LoginAudit.created_at <= date_to)

        # Get total count
        total = query.count()

        # Apply pagination and order by created_at DESC (most recent first)
        audit_logs = query.order_by(desc(LoginAudit.created_at)).offset(skip).limit(limit).all()

        return audit_logs, total

    def get_user_login_history(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        action: Optional[AuditAction] = None
    ) -> Tuple[List[LoginAudit], int]:
        """
        Get login history for a specific user

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            action: Filter by action type (optional)

        Returns:
            Tuple of (audit logs list, total count)
        """
        query = self.db.query(LoginAudit).filter(LoginAudit.user_id == user_id)

        if action:
            query = query.filter(LoginAudit.action == action)

        # Get total count
        total = query.count()

        # Apply pagination and order by created_at DESC
        audit_logs = query.order_by(desc(LoginAudit.created_at)).offset(skip).limit(limit).all()

        return audit_logs, total

    def get_failed_login_attempts(
        self,
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[LoginAudit], int]:
        """
        Get failed login attempts for security monitoring

        Args:
            email: Filter by email
            ip_address: Filter by IP address
            date_from: Filter by start date
            date_to: Filter by end date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (failed login attempts, total count)
        """
        query = self.db.query(LoginAudit).filter(
            and_(
                LoginAudit.action == AuditAction.LOGIN_FAILED,
                LoginAudit.success == False
            )
        )

        if email:
            query = query.filter(LoginAudit.email.ilike(f"%{email}%"))

        if ip_address:
            query = query.filter(LoginAudit.ip_address == ip_address)

        if date_from:
            query = query.filter(LoginAudit.created_at >= date_from)

        if date_to:
            query = query.filter(LoginAudit.created_at <= date_to)

        # Get total count
        total = query.count()

        # Apply pagination and order by created_at DESC
        failed_attempts = query.order_by(desc(LoginAudit.created_at)).offset(skip).limit(limit).all()

        return failed_attempts, total

    def get_recent_activity_by_email(
        self,
        email: str,
        hours: int = 24,
        limit: int = 10
    ) -> List[LoginAudit]:
        """
        Get recent activity for an email address (useful for rate limiting)

        Args:
            email: Email address
            hours: Number of hours to look back
            limit: Maximum number of records to return

        Returns:
            List of recent audit logs
        """
        date_from = datetime.utcnow() - timedelta(hours=hours)

        query = self.db.query(LoginAudit).filter(
            and_(
                LoginAudit.email == email,
                LoginAudit.created_at >= date_from
            )
        )

        return query.order_by(desc(LoginAudit.created_at)).limit(limit).all()

    def count_failed_attempts_by_email(
        self,
        email: str,
        minutes: int = 15
    ) -> int:
        """
        Count failed login attempts for an email in recent minutes

        Args:
            email: Email address
            minutes: Number of minutes to look back

        Returns:
            Count of failed attempts
        """
        from datetime import timedelta
        date_from = datetime.utcnow() - timedelta(minutes=minutes)

        return self.db.query(LoginAudit).filter(
            and_(
                LoginAudit.email == email,
                LoginAudit.action == AuditAction.LOGIN_FAILED,
                LoginAudit.success == False,
                LoginAudit.created_at >= date_from
            )
        ).count()

    def get_login_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> dict:
        """
        Get login statistics

        Args:
            date_from: Filter by start date
            date_to: Filter by end date

        Returns:
            Dictionary with login statistics
        """
        query = self.db.query(LoginAudit)

        if date_from:
            query = query.filter(LoginAudit.created_at >= date_from)

        if date_to:
            query = query.filter(LoginAudit.created_at <= date_to)

        total_attempts = query.count()
        successful_logins = query.filter(
            and_(
                LoginAudit.action == AuditAction.LOGIN,
                LoginAudit.success == True
            )
        ).count()
        failed_logins = query.filter(
            LoginAudit.action == AuditAction.LOGIN_FAILED
        ).count()
        logouts = query.filter(
            LoginAudit.action == AuditAction.LOGOUT
        ).count()

        return {
            "total_attempts": total_attempts,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "logouts": logouts,
            "success_rate": (successful_logins / total_attempts * 100) if total_attempts > 0 else 0
        }
