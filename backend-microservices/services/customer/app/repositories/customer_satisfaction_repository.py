"""
Customer satisfaction repository for database operations
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.customer_satisfaction_raw import CustomerSatisfactionRaw, CustomerSatisfactionUploadTracker

logger = logging.getLogger(__name__)


class CustomerSatisfactionRepository:
    """Repository for customer satisfaction operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_upload_tracker(
        self, 
        file_name: str,
        file_size: int = None,
        uploaded_by: str = None
    ) -> CustomerSatisfactionUploadTracker:
        """Create a new upload tracker record"""
        try:
            tracker = CustomerSatisfactionUploadTracker(
                file_name=file_name,
                file_size=file_size,
                uploaded_by=uploaded_by,
                upload_status='PROCESSING',
                total_records=0,
                successful_records=0,
                failed_records=0
            )
            
            self.db.add(tracker)
            self.db.commit()
            self.db.refresh(tracker)
            
            logger.info(f"Created upload tracker for file: {file_name}")
            return tracker
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating upload tracker: {str(e)}")
            self.db.rollback()
            raise
    
    def update_upload_tracker_status(
        self,
        tracker_id: str,
        status: str,
        total_records: int = None,
        successful_records: int = None,
        failed_records: int = None,
        error_message: str = None
    ) -> bool:
        """Update upload tracker status and statistics"""
        try:
            tracker = self.db.query(CustomerSatisfactionUploadTracker).filter(
                CustomerSatisfactionUploadTracker.id == uuid.UUID(tracker_id)
            ).first()
            
            if not tracker:
                logger.warning(f"Upload tracker not found: {tracker_id}")
                return False
            
            tracker.upload_status = status
            if total_records is not None:
                tracker.total_records = total_records
            if successful_records is not None:
                tracker.successful_records = successful_records
            if failed_records is not None:
                tracker.failed_records = failed_records
            if error_message is not None:
                tracker.error_message = error_message
            if status in ['COMPLETED', 'FAILED']:
                tracker.completed_date = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Updated upload tracker {tracker_id} to status: {status}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating upload tracker: {str(e)}")
            self.db.rollback()
            return False
    
    def bulk_create_satisfaction_records(
        self, 
        records_data: List[Dict[str, Any]],
        upload_batch_id: str,
        created_by: str = None
    ) -> tuple[int, int]:
        """Bulk create customer satisfaction records"""
        successful_count = 0
        failed_count = 0
        
        try:
            for record_data in records_data:
                try:
                    # Create satisfaction record
                    satisfaction_record = CustomerSatisfactionRaw(
                        no_tiket=record_data.get('No Tiket'),
                        no_booking_no_order_pemesanan=record_data.get('No Booking/No order pemesanan'),
                        nama_konsumen=record_data.get('Nama Konsumen'),
                        no_hp=record_data.get('No HP'),
                        alamat_email=record_data.get('Alamat Email'),
                        source=record_data.get('Source'),
                        kota=record_data.get('Kota'),
                        fu_by_se=record_data.get('FU by SE'),
                        fu_by_sda=record_data.get('FU by SDA'),
                        no_ahass=record_data.get('No AHASS'),
                        status=record_data.get('Status'),
                        nama_ahass=record_data.get('Nama AHASS'),
                        tanggal_service=record_data.get('Tanggal Service'),
                        periode_service=record_data.get('Periode Service'),
                        tanggal_rating=record_data.get('tanggal Rating'),
                        jenis_hari=record_data.get('JENIS HARI'),
                        periode_utk_suspend=record_data.get('PERIODE UTK SUSPEND'),
                        submit_review_date_first_fu_cs=record_data.get('Submit Review Date (FIRST FU CS)'),
                        lt_tgl_rating_submit=record_data.get('LT TGL RATING - SUBMIT'),
                        sesuai_lt=record_data.get('SESUAI LT'),
                        periode_fu=record_data.get('Periode FU'),
                        inbox=record_data.get('Inbox'),
                        indikasi_keluhan=record_data.get('Indikasi Keluhan'),
                        rating=record_data.get('Rating'),
                        departemen=record_data.get('Departemen'),
                        # Handle duplicate columns (assuming they appear later in CSV)
                        no_ahass_duplicate=record_data.get('No AHASS.1'),  # Second occurrence
                        status_duplicate=record_data.get('Status.1'),      # Second occurrence
                        nama_ahass_duplicate=record_data.get('Nama AHASS.1'),  # Second occurrence
                        upload_batch_id=uuid.UUID(upload_batch_id),
                        created_by=created_by
                    )
                    
                    self.db.add(satisfaction_record)
                    successful_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating satisfaction record: {str(e)}")
                    failed_count += 1
                    continue
            
            # Commit all successful records
            self.db.commit()
            logger.info(f"Bulk created {successful_count} satisfaction records, {failed_count} failed")
            
            return successful_count, failed_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in bulk create satisfaction records: {str(e)}")
            self.db.rollback()
            return 0, len(records_data)
    
    def get_satisfaction_records_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        periode_utk_suspend: str = None,
        submit_review_date: str = None,
        no_ahass: str = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """Get paginated customer satisfaction records with filtering"""
        try:
            # Build query with filters
            query = self.db.query(CustomerSatisfactionRaw)
            
            # Apply filters
            if periode_utk_suspend:
                query = query.filter(CustomerSatisfactionRaw.periode_utk_suspend == periode_utk_suspend)
            
            if submit_review_date:
                query = query.filter(CustomerSatisfactionRaw.submit_review_date_first_fu_cs.like(f"%{submit_review_date}%"))
            
            if no_ahass:
                query = query.filter(CustomerSatisfactionRaw.no_ahass == no_ahass)
            
            if date_from:
                query = query.filter(CustomerSatisfactionRaw.created_date >= date_from)
            
            if date_to:
                query = query.filter(CustomerSatisfactionRaw.created_date <= date_to)
            
            # Order by created_date descending
            query = query.order_by(desc(CustomerSatisfactionRaw.created_date))
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            records = query.offset(offset).limit(page_size).all()
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "records": [record.to_dict() for record in records],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting paginated satisfaction records: {str(e)}")
            return {
                "records": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False
                }
            }
    
    def get_satisfaction_statistics(
        self,
        periode_utk_suspend: str = None,
        submit_review_date: str = None,
        no_ahass: str = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """Get satisfaction statistics with filtering"""
        try:
            # Build base query
            query = self.db.query(CustomerSatisfactionRaw)
            
            # Apply same filters as paginated query
            if periode_utk_suspend:
                query = query.filter(CustomerSatisfactionRaw.periode_utk_suspend == periode_utk_suspend)
            
            if submit_review_date:
                query = query.filter(CustomerSatisfactionRaw.submit_review_date_first_fu_cs.like(f"%{submit_review_date}%"))
            
            if no_ahass:
                query = query.filter(CustomerSatisfactionRaw.no_ahass == no_ahass)
            
            if date_from:
                query = query.filter(CustomerSatisfactionRaw.created_date >= date_from)
            
            if date_to:
                query = query.filter(CustomerSatisfactionRaw.created_date <= date_to)
            
            # Get basic statistics
            total_records = query.count()
            
            # Get rating distribution
            rating_stats = self.db.query(
                CustomerSatisfactionRaw.rating,
                func.count(CustomerSatisfactionRaw.rating).label('count')
            ).filter(
                query.whereclause if query.whereclause is not None else True
            ).group_by(CustomerSatisfactionRaw.rating).all()
            
            # Get AHASS distribution
            ahass_stats = self.db.query(
                CustomerSatisfactionRaw.no_ahass,
                CustomerSatisfactionRaw.nama_ahass,
                func.count(CustomerSatisfactionRaw.no_ahass).label('count')
            ).filter(
                query.whereclause if query.whereclause is not None else True
            ).group_by(
                CustomerSatisfactionRaw.no_ahass,
                CustomerSatisfactionRaw.nama_ahass
            ).order_by(func.count(CustomerSatisfactionRaw.no_ahass).desc()).limit(10).all()
            
            return {
                "total_records": total_records,
                "rating_distribution": [
                    {"rating": rating, "count": count}
                    for rating, count in rating_stats
                ],
                "top_ahass": [
                    {"no_ahass": no_ahass, "nama_ahass": nama_ahass, "count": count}
                    for no_ahass, nama_ahass, count in ahass_stats
                ]
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting satisfaction statistics: {str(e)}")
            return {
                "total_records": 0,
                "rating_distribution": [],
                "top_ahass": []
            }
    
    def get_upload_trackers_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str = None
    ) -> Dict[str, Any]:
        """Get paginated upload trackers"""
        try:
            query = self.db.query(CustomerSatisfactionUploadTracker)
            
            if status:
                query = query.filter(CustomerSatisfactionUploadTracker.upload_status == status)
            
            # Order by upload_date descending
            query = query.order_by(desc(CustomerSatisfactionUploadTracker.upload_date))
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            trackers = query.offset(offset).limit(page_size).all()
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "trackers": [tracker.to_dict() for tracker in trackers],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting paginated upload trackers: {str(e)}")
            return {
                "trackers": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False
                }
            }
    
    def get_upload_tracker_by_id(self, tracker_id: str) -> Optional[CustomerSatisfactionUploadTracker]:
        """Get upload tracker by ID"""
        try:
            return self.db.query(CustomerSatisfactionUploadTracker).filter(
                CustomerSatisfactionUploadTracker.id == uuid.UUID(tracker_id)
            ).first()
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f"Error getting upload tracker {tracker_id}: {str(e)}")
            return None