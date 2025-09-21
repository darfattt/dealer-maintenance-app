"""
WhatsApp template audit logging repository
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, and_, or_

from app.models.whatsapp_template_logs import WhatsAppTemplateLogs

logger = logging.getLogger(__name__)


class WhatsAppTemplateLogsRepository:
    """Repository for WhatsApp template audit logging operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_log(
        self,
        operation: str,
        user_email: str,
        template_id: Optional[str] = None,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        dealer_id: Optional[str] = None,
        source_dealer_id: Optional[str] = None,
        target_dealer_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        operation_notes: Optional[str] = None
    ) -> Optional[WhatsAppTemplateLogs]:
        """
        Create a new audit log entry

        Args:
            operation: Type of operation (CREATE, UPDATE, DELETE, COPY)
            user_email: Email of user performing operation
            template_id: ID of affected template
            old_data: Previous template data
            new_data: New template data
            dealer_id: Primary dealer ID
            source_dealer_id: Source dealer for copy operations
            target_dealer_id: Target dealer for copy operations
            client_ip: Client IP address
            user_agent: Client user agent
            operation_notes: Optional operation notes

        Returns:
            WhatsAppTemplateLogs object or None if creation failed
        """
        try:
            log_entry = WhatsAppTemplateLogs.create_log_entry(
                operation=operation,
                user_email=user_email,
                template_id=template_id,
                old_data=old_data,
                new_data=new_data,
                dealer_id=dealer_id,
                source_dealer_id=source_dealer_id,
                target_dealer_id=target_dealer_id,
                client_ip=client_ip,
                user_agent=user_agent,
                operation_notes=operation_notes
            )

            self.db.add(log_entry)
            self.db.commit()
            self.db.refresh(log_entry)

            logger.debug(f"Created template log entry: {log_entry.id} for operation {operation}")
            return log_entry

        except SQLAlchemyError as e:
            logger.error(f"Database error creating template log: {str(e)}")
            self.db.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating template log: {str(e)}")
            self.db.rollback()
            return None

    def get_logs_by_template_id(
        self,
        template_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[WhatsAppTemplateLogs]:
        """
        Get audit logs for a specific template

        Args:
            template_id: Template ID
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of WhatsAppTemplateLogs objects
        """
        try:
            return (
                self.db.query(WhatsAppTemplateLogs)
                .filter(WhatsAppTemplateLogs.template_id == template_id)
                .order_by(desc(WhatsAppTemplateLogs.operation_timestamp))
                .limit(limit)
                .offset(offset)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting logs for template {template_id}: {str(e)}")
            return []

    def get_logs_by_dealer_id(
        self,
        dealer_id: str,
        operation: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WhatsAppTemplateLogs]:
        """
        Get audit logs for a specific dealer

        Args:
            dealer_id: Dealer ID
            operation: Optional operation filter
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of WhatsAppTemplateLogs objects
        """
        try:
            query = self.db.query(WhatsAppTemplateLogs).filter(
                or_(
                    WhatsAppTemplateLogs.dealer_id == dealer_id,
                    WhatsAppTemplateLogs.source_dealer_id == dealer_id,
                    WhatsAppTemplateLogs.target_dealer_id == dealer_id
                )
            )

            if operation:
                query = query.filter(WhatsAppTemplateLogs.operation == operation)

            return (
                query
                .order_by(desc(WhatsAppTemplateLogs.operation_timestamp))
                .limit(limit)
                .offset(offset)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting logs for dealer {dealer_id}: {str(e)}")
            return []

    def get_logs_by_user(
        self,
        user_email: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[WhatsAppTemplateLogs]:
        """
        Get audit logs for a specific user

        Args:
            user_email: User email
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of WhatsAppTemplateLogs objects
        """
        try:
            return (
                self.db.query(WhatsAppTemplateLogs)
                .filter(WhatsAppTemplateLogs.user_email == user_email)
                .order_by(desc(WhatsAppTemplateLogs.operation_timestamp))
                .limit(limit)
                .offset(offset)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting logs for user {user_email}: {str(e)}")
            return []

    def get_copy_operations(
        self,
        source_dealer_id: Optional[str] = None,
        target_dealer_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WhatsAppTemplateLogs]:
        """
        Get copy operation logs

        Args:
            source_dealer_id: Source dealer filter
            target_dealer_id: Target dealer filter
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of WhatsAppTemplateLogs objects for copy operations
        """
        try:
            query = self.db.query(WhatsAppTemplateLogs).filter(
                WhatsAppTemplateLogs.operation == "COPY"
            )

            if source_dealer_id:
                query = query.filter(WhatsAppTemplateLogs.source_dealer_id == source_dealer_id)

            if target_dealer_id:
                query = query.filter(WhatsAppTemplateLogs.target_dealer_id == target_dealer_id)

            return (
                query
                .order_by(desc(WhatsAppTemplateLogs.operation_timestamp))
                .limit(limit)
                .offset(offset)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting copy operations: {str(e)}")
            return []

    def get_recent_operations(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[WhatsAppTemplateLogs]:
        """
        Get recent operations within specified hours

        Args:
            hours: Number of hours to look back
            limit: Maximum number of records

        Returns:
            List of recent WhatsAppTemplateLogs objects
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            return (
                self.db.query(WhatsAppTemplateLogs)
                .filter(WhatsAppTemplateLogs.operation_timestamp >= cutoff_time)
                .order_by(desc(WhatsAppTemplateLogs.operation_timestamp))
                .limit(limit)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting recent operations: {str(e)}")
            return []

    def get_operation_statistics(
        self,
        dealer_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get operation statistics

        Args:
            dealer_id: Optional dealer filter
            days: Number of days to analyze

        Returns:
            Dictionary with operation counts
        """
        try:
            cutoff_time = datetime.utcnow() - datetime.timedelta(days=days)

            query = self.db.query(WhatsAppTemplateLogs).filter(
                WhatsAppTemplateLogs.operation_timestamp >= cutoff_time
            )

            if dealer_id:
                query = query.filter(
                    or_(
                        WhatsAppTemplateLogs.dealer_id == dealer_id,
                        WhatsAppTemplateLogs.source_dealer_id == dealer_id,
                        WhatsAppTemplateLogs.target_dealer_id == dealer_id
                    )
                )

            logs = query.all()

            stats = {
                "CREATE": 0,
                "UPDATE": 0,
                "DELETE": 0,
                "COPY": 0,
                "total": len(logs)
            }

            for log in logs:
                if log.operation in stats:
                    stats[log.operation] += 1

            return stats

        except SQLAlchemyError as e:
            logger.error(f"Database error getting operation statistics: {str(e)}")
            return {"CREATE": 0, "UPDATE": 0, "DELETE": 0, "COPY": 0, "total": 0}