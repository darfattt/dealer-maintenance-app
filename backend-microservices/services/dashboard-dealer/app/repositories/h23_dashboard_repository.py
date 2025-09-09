"""
Repository for H23 dashboard data operations
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text, case

# Import dateutil for date calculations
try:
    from dateutil.relativedelta import relativedelta
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    relativedelta = None

# Add parent directory to path for utils import
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if parent_path not in sys.path:
    sys.path.append(parent_path)

from utils.logger import setup_logger
from app.models.pkb_data import PKBData
from app.models.workshop_invoice_data import WorkshopInvoiceData
from app.models.dp_hlo_data import DPHLOData, DPHLOPart
from app.schemas.h23_dashboard import WorkOrderStatusItem

logger = setup_logger(__name__)


class H23DashboardRepository:
    """Repository for H23 dashboard analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_total_unit_entry_with_trend(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """
        Get total unit entry count with trend indicator from PKB data
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date for filtering (string format)
            date_to: End date for filtering (string format)
        
        Returns:
            Dict containing current count, previous count, trend, and percentage
        """
        try:
            logger.info(f"Getting total unit entry with trend for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")
            
            # Helper function to build date filter conditions
            def build_date_conditions(date_from_str: str, date_to_str: str):
                return or_(
                    # Handle YYYY-MM-DD format
                    and_(
                        func.length(PKBData.created_time) >= 10,
                        func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                        func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from_str, 'YYYY-MM-DD'),
                        func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to_str, 'YYYY-MM-DD')
                    ),
                    # Handle DD/MM/YYYY format
                    and_(
                        func.length(PKBData.created_time) >= 10,
                        func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                        func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from_str, 'YYYY-MM-DD'),
                        func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to_str, 'YYYY-MM-DD')
                    )
                )

            # Get current period count
            current_conditions = build_date_conditions(date_from, date_to)
            
            current_query = self.db.query(
                func.count(func.distinct(PKBData.no_work_order)).label('count')
            ).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    PKBData.no_work_order.isnot(None),
                    current_conditions
                )
            )

            current_result = current_query.first()
            current_count = int(current_result.count or 0) if current_result else 0

            # Calculate previous period dates (minus 1 month)
            try:
                if not DATEUTIL_AVAILABLE:
                    raise ImportError("python-dateutil not available")

                date_from_obj = datetime.strptime(date_from[:10], '%Y-%m-%d')
                date_to_obj = datetime.strptime(date_to[:10], '%Y-%m-%d')

                # Subtract 1 month from both dates
                prev_date_from_obj = date_from_obj - relativedelta(months=1)
                prev_date_to_obj = date_to_obj - relativedelta(months=1)

                prev_date_from = prev_date_from_obj.strftime('%Y-%m-%d')
                prev_date_to = prev_date_to_obj.strftime('%Y-%m-%d')

                # Get previous period count
                prev_conditions = build_date_conditions(prev_date_from, prev_date_to)

                prev_query = self.db.query(
                    func.count(func.distinct(PKBData.no_work_order)).label('count')
                ).filter(
                    and_(
                        PKBData.dealer_id == dealer_id,
                        PKBData.no_work_order.isnot(None),
                        prev_conditions
                    )
                )

                prev_result = prev_query.first()
                prev_count = int(prev_result.count or 0) if prev_result else 0

            except Exception as e:
                logger.warning(f"Error calculating previous period: {e}")
                prev_count = 0

            # Calculate trend and percentage
            if prev_count == 0:
                if current_count > 0:
                    trend = 'up'
                    percentage = 100.0
                else:
                    trend = 'stable'
                    percentage = 0.0
            else:
                percentage_change = ((current_count - prev_count) / prev_count) * 100
                percentage = round(abs(percentage_change), 1)

                if percentage_change > 0:
                    trend = 'up'
                elif percentage_change < 0:
                    trend = 'down'
                else:
                    trend = 'stable'

            logger.info(f"Total unit entry count: current={current_count}, previous={prev_count}, trend={trend}, percentage={percentage}")

            return {
                'count': current_count,
                'previous_count': prev_count,
                'trend': trend,
                'percentage': percentage
            }

        except Exception as e:
            logger.error(f"Error getting total unit entry with trend: {e}")
            return {
                'count': 0,
                'previous_count': 0,
                'trend': 'stable',
                'percentage': 0.0
            }

    def get_work_order_revenue(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """
        Get total revenue from work orders (PKB data)
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            Dictionary with total_revenue and total_records
        """
        try:
            logger.info(f"Getting work order revenue for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions for created_time string field
            date_conditions = []

            # Handle YYYY-MM-DD format
            date_conditions.append(
                and_(
                    func.length(PKBData.created_time) >= 10,
                    func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Handle DD/MM/YYYY format
            date_conditions.append(
                and_(
                    func.length(PKBData.created_time) >= 10,
                    func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Get total revenue
            revenue_query = self.db.query(
                func.coalesce(func.sum(PKBData.total_biaya_service), 0).label('total_revenue')
            ).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    PKBData.total_biaya_service.isnot(None),
                    or_(*date_conditions)
                )
            )

            revenue_result = revenue_query.first()
            total_revenue = float(revenue_result.total_revenue) if revenue_result and revenue_result.total_revenue else 0.0

            # Get total records count
            count_query = self.db.query(
                func.count(PKBData.id).label('total_records')
            ).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    or_(*date_conditions)
                )
            )

            count_result = count_query.first()
            total_records = count_result.total_records if count_result else 0

            logger.info(f"Work order revenue for dealer {dealer_id}: total_revenue={total_revenue}, total_records={total_records}")

            return {
                'total_revenue': total_revenue,
                'total_records': total_records
            }

        except Exception as e:
            logger.error(f"Error calculating work order revenue: {str(e)}")
            return {
                'total_revenue': 0.0,
                'total_records': 0
            }

    def get_work_order_status_counts(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[WorkOrderStatusItem]:
        """
        Get count of PKB data grouped by status_work_order
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            List of WorkOrderStatusItem with status and count
        """
        try:
            logger.info(f"Querying work order status for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Status mapping for work order
            status_mapping = {
                '1': 'Start',
                '2': 'Pause',
                '3': 'Pending',
                '4': 'Finish',
                '5': 'Cancel'
            }

            # Build date filter conditions
            date_conditions = []

            # Handle YYYY-MM-DD format
            date_conditions.append(
                and_(
                    func.length(PKBData.created_time) >= 10,
                    func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Handle DD/MM/YYYY format
            date_conditions.append(
                and_(
                    func.length(PKBData.created_time) >= 10,
                    func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Query to get counts grouped by status_work_order
            query = self.db.query(
                PKBData.status_work_order,
                func.count(PKBData.id).label('count')
            ).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    PKBData.status_work_order.isnot(None),
                    or_(*date_conditions)
                )
            ).group_by(PKBData.status_work_order)

            results = query.all()
            logger.info(f"Found {len(results)} different work order statuses")

            # Convert to schema objects with status mapping
            status_items = []
            for status, count in results:
                status_label = status_mapping.get(status, status or 'Unknown')
                
                status_items.append(WorkOrderStatusItem(
                    status_work_order=status,
                    status_label=status_label,
                    count=count
                ))

            # Ensure all statuses are represented (with 0 count if needed)
            existing_statuses = {item.status_work_order for item in status_items}
            for status_code, status_label in status_mapping.items():
                if status_code not in existing_statuses:
                    status_items.append(WorkOrderStatusItem(
                        status_work_order=status_code,
                        status_label=status_label,
                        count=0
                    ))

            # Sort by status code for consistent ordering
            status_items.sort(key=lambda x: x.status_work_order or '0')

            return status_items

        except Exception as e:
            logger.error(f"Error getting work order status counts: {str(e)}")
            raise Exception(f"Error getting work order status counts: {str(e)}")

    def get_total_work_order_records(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get total count of PKB records for the given filters
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            Total number of records
        """
        try:
            # Build date filter conditions
            date_conditions = []

            # Handle YYYY-MM-DD format
            date_conditions.append(
                and_(
                    func.length(PKBData.created_time) >= 10,
                    func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Handle DD/MM/YYYY format
            date_conditions.append(
                and_(
                    func.length(PKBData.created_time) >= 10,
                    func.substr(PKBData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(PKBData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            total = self.db.query(func.count(PKBData.id)).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    or_(*date_conditions)
                )
            ).scalar()

            return total or 0

        except Exception as e:
            raise Exception(f"Error getting total work order records: {str(e)}")

    def get_njb_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """
        Get NJB (Nota Jasa Bengkel) statistics from workshop_invoice_data
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            Dictionary with total_amount and total_records for NJB
        """
        try:
            logger.info(f"Getting NJB statistics for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions for created_time string field
            date_conditions = []

            # Handle YYYY-MM-DD format
            date_conditions.append(
                and_(
                    func.length(WorkshopInvoiceData.created_time) >= 10,
                    func.substr(WorkshopInvoiceData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Handle DD/MM/YYYY format
            date_conditions.append(
                and_(
                    func.length(WorkshopInvoiceData.created_time) >= 10,
                    func.substr(WorkshopInvoiceData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Query for NJB statistics where no_njb is not null
            query = self.db.query(
                func.coalesce(func.sum(WorkshopInvoiceData.total_harga_njb), 0).label('total_amount'),
                func.count(WorkshopInvoiceData.no_njb).label('total_records')
            ).filter(
                and_(
                    WorkshopInvoiceData.dealer_id == dealer_id,
                    WorkshopInvoiceData.no_njb.isnot(None),
                    or_(*date_conditions)
                )
            )

            result = query.first()
            total_amount = float(result.total_amount) if result and result.total_amount else 0.0
            total_records = int(result.total_records) if result and result.total_records else 0

            logger.info(f"NJB statistics: total_amount={total_amount}, total_records={total_records}")

            return {
                'total_amount': total_amount,
                'total_records': total_records
            }

        except Exception as e:
            logger.error(f"Error getting NJB statistics: {str(e)}")
            return {
                'total_amount': 0.0,
                'total_records': 0
            }

    def get_nsc_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """
        Get NSC (Nota Suku Cadang) statistics from workshop_invoice_data
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            Dictionary with total_amount and total_records for NSC
        """
        try:
            logger.info(f"Getting NSC statistics for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions for created_time string field
            date_conditions = []

            # Handle YYYY-MM-DD format
            date_conditions.append(
                and_(
                    func.length(WorkshopInvoiceData.created_time) >= 10,
                    func.substr(WorkshopInvoiceData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Handle DD/MM/YYYY format
            date_conditions.append(
                and_(
                    func.length(WorkshopInvoiceData.created_time) >= 10,
                    func.substr(WorkshopInvoiceData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(WorkshopInvoiceData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Query for NSC statistics where no_nsc is not null
            # Sum total_harga_njb + total_harga_nsc as per requirements
            query = self.db.query(
                func.coalesce(func.sum(
                    func.coalesce(WorkshopInvoiceData.total_harga_njb, 0) + 
                    func.coalesce(WorkshopInvoiceData.total_harga_nsc, 0)
                ), 0).label('total_amount'),
                func.count(WorkshopInvoiceData.no_nsc).label('total_records')
            ).filter(
                and_(
                    WorkshopInvoiceData.dealer_id == dealer_id,
                    WorkshopInvoiceData.no_nsc.isnot(None),
                    or_(*date_conditions)
                )
            )

            result = query.first()
            total_amount = float(result.total_amount) if result and result.total_amount else 0.0
            total_records = int(result.total_records) if result and result.total_records else 0

            logger.info(f"NSC statistics: total_amount={total_amount}, total_records={total_records}")

            return {
                'total_amount': total_amount,
                'total_records': total_records
            }

        except Exception as e:
            logger.error(f"Error getting NSC statistics: {str(e)}")
            return {
                'total_amount': 0.0,
                'total_records': 0
            }

    def get_hlo_statistics(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """
        Get HLO (Honda Layanan Otomotif) statistics from dp_hlo_data
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            Dictionary with total_hlo_documents, total_parts and total_records for HLO
        """
        try:
            logger.info(f"Getting HLO statistics for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions for created_time string field
            date_conditions = []

            # Handle YYYY-MM-DD format
            date_conditions.append(
                and_(
                    func.length(DPHLOData.created_time) >= 10,
                    func.substr(DPHLOData.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                    func.to_date(func.substr(DPHLOData.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(DPHLOData.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Handle DD/MM/YYYY format
            date_conditions.append(
                and_(
                    func.length(DPHLOData.created_time) >= 10,
                    func.substr(DPHLOData.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
                    func.to_date(func.substr(DPHLOData.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                    func.to_date(func.substr(DPHLOData.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
                )
            )

            # Query for HLO documents count where id_hlo_document is not null
            hlo_documents_query = self.db.query(
                func.count(func.distinct(DPHLOData.id_hlo_document)).label('total_hlo_documents')
            ).filter(
                and_(
                    DPHLOData.dealer_id == dealer_id,
                    DPHLOData.id_hlo_document.isnot(None),
                    or_(*date_conditions)
                )
            )

            hlo_documents_result = hlo_documents_query.first()
            total_hlo_documents = int(hlo_documents_result.total_hlo_documents) if hlo_documents_result and hlo_documents_result.total_hlo_documents else 0

            # Query for parts count from dp_hlo_parts via JOIN with dp_hlo_data
            parts_count_query = self.db.query(
                func.count(DPHLOPart.id).label('total_parts')
            ).join(
                DPHLOData, DPHLOPart.dp_hlo_data_id == DPHLOData.id
            ).filter(
                and_(
                    DPHLOData.dealer_id == dealer_id,
                    DPHLOData.id_hlo_document.isnot(None),
                    or_(*date_conditions)
                )
            )

            parts_result = parts_count_query.first()
            total_parts = int(parts_result.total_parts) if parts_result and parts_result.total_parts else 0

            # Query for total HLO records count
            total_records_query = self.db.query(
                func.count(DPHLOData.id).label('total_records')
            ).filter(
                and_(
                    DPHLOData.dealer_id == dealer_id,
                    or_(*date_conditions)
                )
            )

            records_result = total_records_query.first()
            total_records = int(records_result.total_records) if records_result and records_result.total_records else 0

            logger.info(f"HLO statistics: total_hlo_documents={total_hlo_documents}, total_parts={total_parts}, total_records={total_records}")

            return {
                'total_hlo_documents': total_hlo_documents,
                'total_parts': total_parts,
                'total_records': total_records
            }

        except Exception as e:
            logger.error(f"Error getting HLO statistics: {str(e)}")
            return {
                'total_hlo_documents': 0,
                'total_parts': 0,
                'total_records': 0
            }