"""
API request log repository for database operations
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.api_request_log import ApiRequestLog

logger = logging.getLogger(__name__)


class ApiRequestLogRepository:
    """Repository for API request log operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_request_log(
        self,
        request_name: str,
        request_method: str,
        endpoint: str,
        dealer_id: Optional[str] = None,
        request_payload: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        request_ip: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Optional[ApiRequestLog]:
        """
        Create a new API request log entry

        Args:
            request_name: Name/type of the request
            request_method: HTTP method
            endpoint: API endpoint path
            dealer_id: Optional dealer ID
            request_payload: Optional request body
            request_headers: Optional request headers
            request_ip: Optional client IP
            user_email: Optional user email from JWT

        Returns:
            ApiRequestLog object or None if creation failed
        """
        try:
            log_entry = ApiRequestLog(
                request_name=request_name,
                dealer_id=dealer_id,
                request_method=request_method,
                endpoint=endpoint,
                request_payload=request_payload,
                request_headers=request_headers,
                request_ip=request_ip,
                user_email=user_email,
                request_timestamp=datetime.utcnow()
            )

            self.db.add(log_entry)
            self.db.commit()
            self.db.refresh(log_entry)

            logger.debug(f"Created request log entry: {log_entry.id} for {request_name}")
            return log_entry

        except SQLAlchemyError as e:
            logger.error(f"Database error creating request log: {str(e)}")
            self.db.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating request log: {str(e)}")
            self.db.rollback()
            return None

    def update_response_log(
        self,
        log_id: str,
        response_status: str,
        response_code: int,
        processing_time_ms: int,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update an existing log entry with response information

        Args:
            log_id: ID of the log entry to update
            response_status: Response status ('success', 'error', 'partial_success')
            response_code: HTTP status code
            processing_time_ms: Processing time in milliseconds
            response_data: Optional response data
            error_message: Optional error message

        Returns:
            True if update successful, False otherwise
        """
        try:
            log_entry = self.db.query(ApiRequestLog).filter(ApiRequestLog.id == log_id).first()

            if not log_entry:
                logger.warning(f"Request log entry not found: {log_id}")
                return False

            log_entry.update_response(
                response_status=response_status,
                response_code=response_code,
                processing_time_ms=processing_time_ms,
                response_data=response_data,
                error_message=error_message
            )

            self.db.commit()
            logger.debug(f"Updated request log entry: {log_id} with response data")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error updating request log {log_id}: {str(e)}")
            self.db.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating request log {log_id}: {str(e)}")
            self.db.rollback()
            return False

    def get_request_log_by_id(self, log_id: str) -> Optional[ApiRequestLog]:
        """
        Get request log by ID

        Args:
            log_id: ID of the log entry

        Returns:
            ApiRequestLog object or None if not found
        """
        try:
            return self.db.query(ApiRequestLog).filter(ApiRequestLog.id == log_id).first()

        except SQLAlchemyError as e:
            logger.error(f"Database error getting request log {log_id}: {str(e)}")
            return None

    def get_request_logs_by_dealer(
        self,
        dealer_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Get request logs for a specific dealer

        Args:
            dealer_id: Dealer ID
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of ApiRequestLog objects
        """
        try:
            return (
                self.db.query(ApiRequestLog)
                .filter(ApiRequestLog.dealer_id == dealer_id)
                .order_by(ApiRequestLog.request_timestamp.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting request logs for dealer {dealer_id}: {str(e)}")
            return []

    def get_request_logs_by_name(
        self,
        request_name: str,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Get request logs by request name

        Args:
            request_name: Name of the request type
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of ApiRequestLog objects
        """
        try:
            return (
                self.db.query(ApiRequestLog)
                .filter(ApiRequestLog.request_name == request_name)
                .order_by(ApiRequestLog.request_timestamp.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting request logs for {request_name}: {str(e)}")
            return []

    def get_today_request_logs(self, indonesia_date=None) -> list:
        """
        Get all API request logs from today (no pagination)

        Args:
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            List of ApiRequestLog objects from today
        """
        try:
            from datetime import date, datetime

            # Get today's date range (00:00:00 to 23:59:59)
            # Use provided Indonesia date or fallback to system date
            today_date = indonesia_date if indonesia_date else date.today()
            today_start = datetime.combine(today_date, datetime.min.time())
            today_end = datetime.combine(today_date, datetime.max.time())

            return (
                self.db.query(ApiRequestLog)
                .filter(
                    ApiRequestLog.request_timestamp >= today_start,
                    ApiRequestLog.request_timestamp <= today_end
                )
                .order_by(ApiRequestLog.request_timestamp.desc())
                .all()
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting today's request logs: {str(e)}")
            return []

    def get_today_summary_by_dealer(self, indonesia_date=None) -> list:
        """
        Get aggregated summary of today's API requests grouped by dealer_id

        Args:
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            List of dictionaries containing dealer summaries:
            - dealer_id
            - total_requests
            - successful_requests
            - failed_requests
            - avg_processing_time_ms
            - request_count_by_type
        """
        try:
            from datetime import date, datetime
            from sqlalchemy import func, case

            # Get today's date range
            # Use provided Indonesia date or fallback to system date
            today_date = indonesia_date if indonesia_date else date.today()
            today_start = datetime.combine(today_date, datetime.min.time())
            today_end = datetime.combine(today_date, datetime.max.time())

            # Query aggregated data grouped by dealer_id
            results = (
                self.db.query(
                    ApiRequestLog.dealer_id,
                    func.count(ApiRequestLog.id).label('total_requests'),
                    func.sum(
                        case(
                            (ApiRequestLog.response_status == 'success', 1),
                            else_=0
                        )
                    ).label('successful_requests'),
                    func.sum(
                        case(
                            (ApiRequestLog.response_status == 'error', 1),
                            else_=0
                        )
                    ).label('failed_requests'),
                    func.avg(ApiRequestLog.processing_time_ms).label('avg_processing_time_ms')
                )
                .filter(
                    ApiRequestLog.request_timestamp >= today_start,
                    ApiRequestLog.request_timestamp <= today_end,
                    ApiRequestLog.dealer_id.isnot(None)  # Only include records with dealer_id
                )
                .group_by(ApiRequestLog.dealer_id)
                .order_by(ApiRequestLog.dealer_id)
                .all()
            )

            # Get request count by type for each dealer
            summaries = []
            for row in results:
                dealer_id = row.dealer_id

                # Get request count by type for this dealer
                request_types = (
                    self.db.query(
                        ApiRequestLog.request_name,
                        func.count(ApiRequestLog.id).label('count')
                    )
                    .filter(
                        ApiRequestLog.dealer_id == dealer_id,
                        ApiRequestLog.request_timestamp >= today_start,
                        ApiRequestLog.request_timestamp <= today_end
                    )
                    .group_by(ApiRequestLog.request_name)
                    .all()
                )

                request_count_by_type = {rt.request_name: rt.count for rt in request_types}

                summaries.append({
                    'dealer_id': dealer_id,
                    'total_requests': row.total_requests,
                    'successful_requests': row.successful_requests or 0,
                    'failed_requests': row.failed_requests or 0,
                    'avg_processing_time_ms': float(row.avg_processing_time_ms) if row.avg_processing_time_ms else 0.0,
                    'request_count_by_type': request_count_by_type
                })

            return summaries

        except SQLAlchemyError as e:
            logger.error(f"Database error getting today's dealer summary: {str(e)}")
            return []

    def get_weekly_summary_by_dealer(self, indonesia_date=None) -> list:
        """
        Get aggregated summary of ALL weeks' API requests grouped by week and dealer_id

        Week is defined as Monday 00:00:00 to Sunday 23:59:59 in Indonesia timezone.

        Args:
            indonesia_date: Not used, kept for backward compatibility

        Returns:
            List of dictionaries containing weekly dealer summaries:
            - week_start_date (ISO format)
            - week_end_date (ISO format)
            - dealer_id
            - total_requests
            - successful_requests
            - failed_requests
            - avg_processing_time_ms
            - request_count_by_type
        """
        try:
            from datetime import date, datetime, timedelta
            from sqlalchemy import func, case, extract

            # Query aggregated data grouped by week and dealer_id
            # Using date_trunc to group by week (Monday-based)
            results = (
                self.db.query(
                    func.date_trunc('week', ApiRequestLog.request_timestamp).label('week_start'),
                    ApiRequestLog.dealer_id,
                    func.count(ApiRequestLog.id).label('total_requests'),
                    func.sum(
                        case(
                            (ApiRequestLog.response_status == 'success', 1),
                            else_=0
                        )
                    ).label('successful_requests'),
                    func.sum(
                        case(
                            (ApiRequestLog.response_status == 'error', 1),
                            else_=0
                        )
                    ).label('failed_requests'),
                    func.avg(ApiRequestLog.processing_time_ms).label('avg_processing_time_ms')
                )
                .filter(
                    ApiRequestLog.dealer_id.isnot(None)  # Only include records with dealer_id
                )
                .group_by(func.date_trunc('week', ApiRequestLog.request_timestamp), ApiRequestLog.dealer_id)
                .order_by(func.date_trunc('week', ApiRequestLog.request_timestamp).desc(), ApiRequestLog.dealer_id)
                .all()
            )

            # Get request count by type for each week and dealer
            summaries = []
            for row in results:
                week_start_datetime = row.week_start
                dealer_id = row.dealer_id

                # Calculate week end date (Sunday)
                week_start_date = week_start_datetime.date()
                week_end_date = week_start_date + timedelta(days=6)

                week_start = datetime.combine(week_start_date, datetime.min.time())
                week_end = datetime.combine(week_end_date, datetime.max.time())

                # Get request count by type for this dealer and week
                request_types = (
                    self.db.query(
                        ApiRequestLog.request_name,
                        func.count(ApiRequestLog.id).label('count')
                    )
                    .filter(
                        ApiRequestLog.dealer_id == dealer_id,
                        ApiRequestLog.request_timestamp >= week_start,
                        ApiRequestLog.request_timestamp <= week_end
                    )
                    .group_by(ApiRequestLog.request_name)
                    .all()
                )

                request_count_by_type = {rt.request_name: rt.count for rt in request_types}

                summaries.append({
                    'week_start_date': week_start_date.isoformat(),
                    'week_end_date': week_end_date.isoformat(),
                    'dealer_id': dealer_id,
                    'total_requests': row.total_requests,
                    'successful_requests': row.successful_requests or 0,
                    'failed_requests': row.failed_requests or 0,
                    'avg_processing_time_ms': float(row.avg_processing_time_ms) if row.avg_processing_time_ms else 0.0,
                    'request_count_by_type': request_count_by_type
                })

            return summaries

        except SQLAlchemyError as e:
            logger.error(f"Database error getting weekly dealer summary: {str(e)}")
            return []