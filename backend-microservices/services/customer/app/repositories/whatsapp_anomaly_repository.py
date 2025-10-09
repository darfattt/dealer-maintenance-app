"""
WhatsApp Anomaly repository for database operations
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_, union_all, select, literal
from sqlalchemy.exc import SQLAlchemyError

from app.models.customer_validation_request import CustomerValidationRequest
from app.models.customer_reminder_request import CustomerReminderRequest
from app.utils.phone_masking import mask_phone_number

logger = logging.getLogger(__name__)


class WhatsAppAnomalyRepository:
    """Repository for WhatsApp integration anomaly operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_combined_failures(
        self,
        page: int = 1,
        per_page: int = 10,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        whatsapp_status: Optional[str] = None,
        request_type: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get combined WhatsApp failures from both validation and reminder tables

        Args:
            page: Page number (1-based)
            per_page: Items per page
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            whatsapp_status: Optional status filter (FAILED, ERROR, REJECTED)
            request_type: Optional request type filter (VALIDATION, REMINDER, ALL)

        Returns:
            Tuple of (list of failure records, total count)
        """
        try:
            # Failed statuses to filter
            failed_statuses = ['FAILED', 'ERROR', 'REJECTED', 'NOT_SENT']

            # Build validation query
            validation_query = (
                select(
                    CustomerValidationRequest.id,
                    CustomerValidationRequest.dealer_id,
                    literal('VALIDATION').label('request_type'),
                    CustomerValidationRequest.request_date,
                    CustomerValidationRequest.request_time,
                    CustomerValidationRequest.nama_pembawa.label('customer_name'),
                    CustomerValidationRequest.nomor_telepon_pembawa.label('phone_number'),
                    CustomerValidationRequest.whatsapp_status,
                    CustomerValidationRequest.whatsapp_message,
                    CustomerValidationRequest.fonnte_response,
                    CustomerValidationRequest.created_date
                )
                .where(CustomerValidationRequest.whatsapp_status.in_(failed_statuses))
            )

            # Build reminder query
            reminder_query = (
                select(
                    CustomerReminderRequest.id,
                    CustomerReminderRequest.dealer_id,
                    literal('REMINDER').label('request_type'),
                    CustomerReminderRequest.request_date,
                    CustomerReminderRequest.request_time,
                    CustomerReminderRequest.nama_pelanggan.label('customer_name'),
                    CustomerReminderRequest.nomor_telepon_pelanggan.label('phone_number'),
                    CustomerReminderRequest.whatsapp_status,
                    CustomerReminderRequest.whatsapp_message,
                    CustomerReminderRequest.fonnte_response,
                    CustomerReminderRequest.created_date
                )
                .where(CustomerReminderRequest.whatsapp_status.in_(failed_statuses))
            )

            # Apply filters based on request_type
            if request_type and request_type != 'ALL':
                if request_type == 'VALIDATION':
                    # Only use validation query
                    combined_query = validation_query
                elif request_type == 'REMINDER':
                    # Only use reminder query
                    combined_query = reminder_query
            else:
                # Union both queries
                combined_query = union_all(validation_query, reminder_query)

            # Create subquery for filtering and pagination
            subquery = combined_query.subquery()

            # Build main query with filters
            main_query = select(subquery)

            # Apply dealer_id filter
            if dealer_id:
                main_query = main_query.where(subquery.c.dealer_id == dealer_id)

            # Apply date range filter
            if date_from:
                main_query = main_query.where(subquery.c.request_date >= date_from)
            if date_to:
                main_query = main_query.where(subquery.c.request_date <= date_to)

            # Apply status filter
            if whatsapp_status:
                main_query = main_query.where(subquery.c.whatsapp_status == whatsapp_status)

            # Get total count
            count_query = select(func.count()).select_from(main_query.subquery())
            total_count = self.db.execute(count_query).scalar() or 0

            # Apply ordering
            main_query = main_query.order_by(subquery.c.created_date.desc())

            # Apply pagination
            offset = (page - 1) * per_page
            main_query = main_query.offset(offset).limit(per_page)

            # Execute query
            results = self.db.execute(main_query).fetchall()

            # Format results
            failures = []
            for row in results:
                # Extract error details from fonnte_response
                error_details = None
                if row.fonnte_response:
                    if isinstance(row.fonnte_response, dict):
                        error_details = (
                            row.fonnte_response.get('reason') or
                            row.fonnte_response.get('detail') or
                            row.fonnte_response.get('message') or
                            str(row.fonnte_response.get('status', ''))
                        )

                failures.append({
                    'id': str(row.id),
                    'dealer_id': row.dealer_id,
                    'request_type': row.request_type,
                    'request_date': row.request_date.isoformat() if row.request_date else None,
                    'request_time': row.request_time.isoformat() if row.request_time else None,
                    'customer_name': row.customer_name,
                    'phone_number': mask_phone_number(row.phone_number) if row.phone_number else None,
                    'whatsapp_status': row.whatsapp_status,
                    'whatsapp_message': row.whatsapp_message,
                    'fonnte_response': row.fonnte_response,
                    'error_details': error_details,
                    'created_date': row.created_date.isoformat() if row.created_date else None
                })

            return failures, total_count

        except SQLAlchemyError as e:
            logger.error(f"Database error getting combined WhatsApp failures: {str(e)}")
            return [], 0

    def get_daily_summary(self, dealer_id: Optional[str] = None, indonesia_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get daily summary of WhatsApp failures for today

        Args:
            dealer_id: Optional dealer ID filter
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            Dictionary with daily failure statistics
        """
        try:
            # Get today's date range
            today_date = indonesia_date if indonesia_date else date.today()

            # Failed statuses
            failed_statuses = ['FAILED', 'ERROR', 'REJECTED', 'NOT_SENT']

            # Count validation failures
            validation_count_query = (
                self.db.query(func.count(CustomerValidationRequest.id))
                .filter(
                    CustomerValidationRequest.request_date == today_date,
                    CustomerValidationRequest.whatsapp_status.in_(failed_statuses)
                )
            )
            if dealer_id:
                validation_count_query = validation_count_query.filter(
                    CustomerValidationRequest.dealer_id == dealer_id
                )
            validation_failed = validation_count_query.scalar() or 0

            # Count reminder failures
            reminder_count_query = (
                self.db.query(func.count(CustomerReminderRequest.id))
                .filter(
                    CustomerReminderRequest.request_date == today_date,
                    CustomerReminderRequest.whatsapp_status.in_(failed_statuses)
                )
            )
            if dealer_id:
                reminder_count_query = reminder_count_query.filter(
                    CustomerReminderRequest.dealer_id == dealer_id
                )
            reminder_failed = reminder_count_query.scalar() or 0

            # Total failures
            total_failed = validation_failed + reminder_failed

            # Count total requests for today
            validation_total_query = (
                self.db.query(func.count(CustomerValidationRequest.id))
                .filter(CustomerValidationRequest.request_date == today_date)
            )
            if dealer_id:
                validation_total_query = validation_total_query.filter(
                    CustomerValidationRequest.dealer_id == dealer_id
                )
            validation_total = validation_total_query.scalar() or 0

            reminder_total_query = (
                self.db.query(func.count(CustomerReminderRequest.id))
                .filter(CustomerReminderRequest.request_date == today_date)
            )
            if dealer_id:
                reminder_total_query = reminder_total_query.filter(
                    CustomerReminderRequest.dealer_id == dealer_id
                )
            reminder_total = reminder_total_query.scalar() or 0

            total_requests = validation_total + reminder_total

            # Calculate failure rate
            failure_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0

            return {
                'date': today_date.isoformat(),
                'total_failed': total_failed,
                'validation_failed': validation_failed,
                'reminder_failed': reminder_failed,
                'total_requests': total_requests,
                'failure_rate': round(failure_rate, 2)
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting daily WhatsApp summary: {str(e)}")
            return {
                'date': date.today().isoformat(),
                'total_failed': 0,
                'validation_failed': 0,
                'reminder_failed': 0,
                'total_requests': 0,
                'failure_rate': 0.0
            }

    def get_weekly_summary(self, dealer_id: Optional[str] = None, indonesia_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get weekly summary of WhatsApp failures for past 7 days

        Args:
            dealer_id: Optional dealer ID filter
            indonesia_date: Optional date object representing today in Indonesia timezone

        Returns:
            Dictionary with weekly failure statistics
        """
        try:
            # Get date range for past 7 days
            today_date = indonesia_date if indonesia_date else date.today()
            week_ago = today_date - timedelta(days=7)

            # Failed statuses
            failed_statuses = ['FAILED', 'ERROR', 'REJECTED', 'NOT_SENT']

            # Count validation failures
            validation_count_query = (
                self.db.query(func.count(CustomerValidationRequest.id))
                .filter(
                    CustomerValidationRequest.request_date >= week_ago,
                    CustomerValidationRequest.request_date <= today_date,
                    CustomerValidationRequest.whatsapp_status.in_(failed_statuses)
                )
            )
            if dealer_id:
                validation_count_query = validation_count_query.filter(
                    CustomerValidationRequest.dealer_id == dealer_id
                )
            validation_failed = validation_count_query.scalar() or 0

            # Count reminder failures
            reminder_count_query = (
                self.db.query(func.count(CustomerReminderRequest.id))
                .filter(
                    CustomerReminderRequest.request_date >= week_ago,
                    CustomerReminderRequest.request_date <= today_date,
                    CustomerReminderRequest.whatsapp_status.in_(failed_statuses)
                )
            )
            if dealer_id:
                reminder_count_query = reminder_count_query.filter(
                    CustomerReminderRequest.dealer_id == dealer_id
                )
            reminder_failed = reminder_count_query.scalar() or 0

            # Total failures
            total_failed = validation_failed + reminder_failed

            # Count total requests for week
            validation_total_query = (
                self.db.query(func.count(CustomerValidationRequest.id))
                .filter(
                    CustomerValidationRequest.request_date >= week_ago,
                    CustomerValidationRequest.request_date <= today_date
                )
            )
            if dealer_id:
                validation_total_query = validation_total_query.filter(
                    CustomerValidationRequest.dealer_id == dealer_id
                )
            validation_total = validation_total_query.scalar() or 0

            reminder_total_query = (
                self.db.query(func.count(CustomerReminderRequest.id))
                .filter(
                    CustomerReminderRequest.request_date >= week_ago,
                    CustomerReminderRequest.request_date <= today_date
                )
            )
            if dealer_id:
                reminder_total_query = reminder_total_query.filter(
                    CustomerReminderRequest.dealer_id == dealer_id
                )
            reminder_total = reminder_total_query.scalar() or 0

            total_requests = validation_total + reminder_total

            # Calculate failure rate
            failure_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0

            return {
                'date_from': week_ago.isoformat(),
                'date_to': today_date.isoformat(),
                'total_failed': total_failed,
                'validation_failed': validation_failed,
                'reminder_failed': reminder_failed,
                'total_requests': total_requests,
                'failure_rate': round(failure_rate, 2)
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting weekly WhatsApp summary: {str(e)}")
            today_date = date.today()
            week_ago = today_date - timedelta(days=7)
            return {
                'date_from': week_ago.isoformat(),
                'date_to': today_date.isoformat(),
                'total_failed': 0,
                'validation_failed': 0,
                'reminder_failed': 0,
                'total_requests': 0,
                'failure_rate': 0.0
            }

    def get_failure_statistics(
        self,
        dealer_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive failure statistics with breakdown by status and type

        Args:
            dealer_id: Optional dealer ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            Dictionary with failure statistics and breakdowns
        """
        try:
            # Failed statuses
            failed_statuses = ['FAILED', 'ERROR', 'REJECTED', 'NOT_SENT']

            # Build base filters
            validation_filters = [CustomerValidationRequest.whatsapp_status.in_(failed_statuses)]
            reminder_filters = [CustomerReminderRequest.whatsapp_status.in_(failed_statuses)]

            if dealer_id:
                validation_filters.append(CustomerValidationRequest.dealer_id == dealer_id)
                reminder_filters.append(CustomerReminderRequest.dealer_id == dealer_id)

            if date_from:
                validation_filters.append(CustomerValidationRequest.request_date >= date_from)
                reminder_filters.append(CustomerReminderRequest.request_date >= date_from)

            if date_to:
                validation_filters.append(CustomerValidationRequest.request_date <= date_to)
                reminder_filters.append(CustomerReminderRequest.request_date <= date_to)

            # Get status breakdown from validation
            validation_status_breakdown = (
                self.db.query(
                    CustomerValidationRequest.whatsapp_status,
                    func.count(CustomerValidationRequest.id).label('count')
                )
                .filter(and_(*validation_filters))
                .group_by(CustomerValidationRequest.whatsapp_status)
                .all()
            )

            # Get status breakdown from reminder
            reminder_status_breakdown = (
                self.db.query(
                    CustomerReminderRequest.whatsapp_status,
                    func.count(CustomerReminderRequest.id).label('count')
                )
                .filter(and_(*reminder_filters))
                .group_by(CustomerReminderRequest.whatsapp_status)
                .all()
            )

            # Combine status breakdowns
            status_counts = {}
            for status, count in validation_status_breakdown:
                status_counts[status] = status_counts.get(status, 0) + count
            for status, count in reminder_status_breakdown:
                status_counts[status] = status_counts.get(status, 0) + count

            # Calculate total failed
            total_failed = sum(status_counts.values())

            # Format status breakdown with percentages
            breakdown_by_status = []
            for status, count in status_counts.items():
                percentage = (count / total_failed * 100) if total_failed > 0 else 0.0
                breakdown_by_status.append({
                    'status': status,
                    'count': count,
                    'percentage': round(percentage, 2)
                })

            # Sort by count descending
            breakdown_by_status.sort(key=lambda x: x['count'], reverse=True)

            # Get type breakdown
            validation_count = sum(count for _, count in validation_status_breakdown)
            reminder_count = sum(count for _, count in reminder_status_breakdown)

            breakdown_by_type = {
                'VALIDATION': validation_count,
                'REMINDER': reminder_count
            }

            return {
                'total_failed': total_failed,
                'breakdown_by_status': breakdown_by_status,
                'breakdown_by_type': breakdown_by_type
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting WhatsApp failure statistics: {str(e)}")
            return {
                'total_failed': 0,
                'breakdown_by_status': [],
                'breakdown_by_type': {
                    'VALIDATION': 0,
                    'REMINDER': 0
                }
            }
