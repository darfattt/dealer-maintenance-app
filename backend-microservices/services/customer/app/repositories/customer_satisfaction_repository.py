"""
Customer satisfaction repository for database operations
"""

import logging
import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, text
from sqlalchemy.exc import SQLAlchemyError

from app.models.customer_satisfaction_raw import CustomerSatisfactionRaw, CustomerSatisfactionUploadTracker

logger = logging.getLogger(__name__)


class CustomerSatisfactionRepository:
    """Repository for customer satisfaction operations"""
    
    # Indonesian month names mapping
    INDONESIAN_MONTHS = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
        'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }
    
    ENGLISH_TO_INDONESIAN_MONTHS = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def _parse_indonesian_date(self, indo_date_str: str) -> Optional[datetime]:
        """
        Parse Indonesian date string like '24 Desember 2024' to datetime object
        
        Args:
            indo_date_str: Indonesian date string
            
        Returns:
            datetime object or None if parsing fails
        """
        if not indo_date_str or not isinstance(indo_date_str, str):
            return None
        
        try:
            # Clean and normalize the string
            clean_date = indo_date_str.strip()
            
            # Pattern: DD Month YYYY or D Month YYYY
            pattern = r'^(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})$'
            match = re.match(pattern, clean_date)
            
            if not match:
                logger.warning(f"Invalid Indonesian date format: {indo_date_str}")
                return None
            
            day_str, month_str, year_str = match.groups()
            
            # Convert to lowercase for lookup
            month_lower = month_str.lower()
            
            if month_lower not in self.INDONESIAN_MONTHS:
                logger.warning(f"Unknown Indonesian month: {month_str}")
                return None
            
            day = int(day_str)
            month = self.INDONESIAN_MONTHS[month_lower]
            year = int(year_str)
            
            return datetime(year, month, day)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing Indonesian date '{indo_date_str}': {str(e)}")
            return None
    
    def _datetime_to_indonesian_date(self, dt: datetime) -> str:
        """
        Convert datetime object to Indonesian date string
        
        Args:
            dt: datetime object
            
        Returns:
            Indonesian date string like '24 Desember 2024'
        """
        if not dt:
            return None
        
        try:
            day = dt.day
            month_name = self.ENGLISH_TO_INDONESIAN_MONTHS.get(dt.month, f"Month{dt.month}")
            year = dt.year
            
            return f"{day} {month_name} {year}"
            
        except Exception as e:
            logger.warning(f"Error converting datetime to Indonesian date: {str(e)}")
            return None
    
    def _build_tanggal_rating_date_filter(self, query, date_from: datetime = None, date_to: datetime = None):
        """
        Build date filter for tanggal_rating field using Indonesian date parsing
        
        Args:
            query: SQLAlchemy query object
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            Updated query with date filters
        """
        if not date_from and not date_to:
            return query
        
        try:
            # We'll use a subquery approach to parse Indonesian dates and compare them
            date_conditions = []
            
            if date_from:
                # Create SQL condition to parse Indonesian date and compare with date_from
                date_from_str = date_from.strftime('%Y-%m-%d')
                date_conditions.append(f"""
                    CASE 
                        WHEN tanggal_rating ~ '^[0-9]{{1,2}} [A-Za-z]+ [0-9]{{4}}$' THEN
                            CASE LOWER(SPLIT_PART(tanggal_rating, ' ', 2))
                                WHEN 'januari' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-01-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'februari' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-02-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'maret' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-03-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'april' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-04-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'mei' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-05-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'juni' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-06-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'juli' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-07-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'agustus' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-08-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'september' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-09-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'oktober' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-10-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'november' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-11-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'desember' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-12-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                ELSE NULL
                            END >= TO_DATE('{date_from_str}', 'YYYY-MM-DD')
                        ELSE FALSE
                    END
                """)
            
            if date_to:
                date_to_str = date_to.strftime('%Y-%m-%d')
                date_conditions.append(f"""
                    CASE 
                        WHEN tanggal_rating ~ '^[0-9]{{1,2}} [A-Za-z]+ [0-9]{{4}}$' THEN
                            CASE LOWER(SPLIT_PART(tanggal_rating, ' ', 2))
                                WHEN 'januari' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-01-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'februari' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-02-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'maret' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-03-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'april' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-04-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'mei' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-05-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'juni' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-06-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'juli' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-07-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'agustus' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-08-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'september' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-09-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'oktober' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-10-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'november' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-11-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                WHEN 'desember' THEN TO_DATE(SPLIT_PART(tanggal_rating, ' ', 3) || '-12-' || LPAD(SPLIT_PART(tanggal_rating, ' ', 1), 2, '0'), 'YYYY-MM-DD')
                                ELSE NULL
                            END <= TO_DATE('{date_to_str}', 'YYYY-MM-DD')
                        ELSE FALSE
                    END
                """)
            
            # Combine conditions with AND
            if date_conditions:
                combined_condition = " AND ".join(date_conditions)
                query = query.filter(text(combined_condition))
            
            return query
            
        except Exception as e:
            logger.error(f"Error building tanggal_rating date filter: {str(e)}")
            # Return unfiltered query if there's an error
            return query
    
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
        created_by: str = None,
        override_existing: bool = False
    ) -> tuple[int, int, int, int]:
        """Bulk create customer satisfaction records with override support
        
        Returns: (successful_count, failed_count, replaced_count, skipped_count)
        """
        successful_count = 0
        failed_count = 0
        replaced_count = 0
        skipped_count = 0
        
        try:
            for record_data in records_data:
                try:
                    no_tiket = record_data.get('No Tiket')
                    
                    # Skip records without no_tiket (cannot check for duplicates)
                    if not no_tiket or str(no_tiket).strip() == '':
                        logger.warning("Skipping record without No Tiket")
                        failed_count += 1
                        continue
                    
                    # Check if record with same no_tiket already exists
                    existing_record = self.db.query(CustomerSatisfactionRaw).filter_by(no_tiket=str(no_tiket).strip()).first()
                    
                    if existing_record:
                        if override_existing:
                            # Delete existing record and create new one
                            logger.info(f"Overriding existing record with no_tiket: {no_tiket}")
                            self.db.delete(existing_record)
                            self.db.flush()  # Ensure deletion is processed before insert
                            replaced_count += 1
                        else:
                            # Skip duplicate record
                            logger.info(f"Skipping duplicate record with no_tiket: {no_tiket}")
                            failed_count += 1
                            skipped_count += 1
                            continue
                    
                    # Create new satisfaction record
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
                    logger.error(f"Error processing satisfaction record with no_tiket {record_data.get('No Tiket', 'N/A')}: {str(e)}")
                    failed_count += 1
                    continue
            
            # Commit all successful records
            self.db.commit()
            logger.info(f"Bulk processed satisfaction records: {successful_count} successful, {failed_count} failed, {replaced_count} replaced, {skipped_count} skipped")
            
            return successful_count, failed_count, replaced_count, skipped_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error in bulk create satisfaction records: {str(e)}")
            self.db.rollback()
            return 0, len(records_data), 0, 0
    
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
            
            # Apply tanggal_rating date filtering using Indonesian date parsing
            query = self._build_tanggal_rating_date_filter(query, date_from, date_to)
            
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
            
            # Apply tanggal_rating date filtering using Indonesian date parsing
            query = self._build_tanggal_rating_date_filter(query, date_from, date_to)
            
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
    
    def get_latest_upload_info(self) -> Optional[Dict[str, Any]]:
        """Get the latest upload information for quick display"""
        try:
            # Get the most recent upload tracker
            latest_tracker = self.db.query(CustomerSatisfactionUploadTracker).order_by(
                desc(CustomerSatisfactionUploadTracker.upload_date)
            ).first()
            
            if not latest_tracker:
                return None
            
            # Calculate processing time if completed
            processing_time = None
            if latest_tracker.completed_date and latest_tracker.upload_date:
                processing_time = (latest_tracker.completed_date - latest_tracker.upload_date).total_seconds()
            
            return {
                "upload_date": latest_tracker.upload_date.isoformat() if latest_tracker.upload_date else None,
                "uploaded_by": latest_tracker.uploaded_by,
                "file_name": latest_tracker.file_name,
                "file_size": latest_tracker.file_size,
                "total_records": latest_tracker.total_records or 0,
                "successful_records": latest_tracker.successful_records or 0,
                "failed_records": latest_tracker.failed_records or 0,
                "upload_status": latest_tracker.upload_status,
                "error_message": latest_tracker.error_message,
                "processing_time_seconds": int(processing_time) if processing_time else None,
                "completed_date": latest_tracker.completed_date.isoformat() if latest_tracker.completed_date else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting latest upload info: {str(e)}")
            return None
    
    def get_latest_upload_info_simple(self) -> Optional[Dict[str, Any]]:
        """Get the latest upload information by created_date from records (simplified version) with sentiment processing status"""
        try:
            # Get the most recent record by created_date
            latest_record = self.db.query(CustomerSatisfactionRaw).order_by(
                desc(CustomerSatisfactionRaw.created_date)
            ).first()
            
            if not latest_record:
                return None
            
            # Convert UTC datetime to Indonesia timezone (UTC+7)
            indonesia_tz = pytz.timezone('Asia/Jakarta')
            if latest_record.created_date:
                # Assume the stored datetime is in UTC
                utc_dt = latest_record.created_date.replace(tzinfo=pytz.UTC) if latest_record.created_date.tzinfo is None else latest_record.created_date
                indonesia_dt = utc_dt.astimezone(indonesia_tz)
                latest_upload_date = indonesia_dt.isoformat()
            else:
                latest_upload_date = None
            
            # Check sentiment analysis processing status
            # Only check for records uploaded in the last 24 hours to avoid unnecessary processing
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            # Count total records from recent uploads
            total_recent_records = self.db.query(CustomerSatisfactionRaw).filter(
                CustomerSatisfactionRaw.created_date >= twenty_four_hours_ago
            ).count()
            
            # Count processed records (those with sentiment analysis)
            processed_records = self.db.query(CustomerSatisfactionRaw).filter(
                and_(
                    CustomerSatisfactionRaw.created_date >= twenty_four_hours_ago,
                    CustomerSatisfactionRaw.sentiment.isnot(None)
                )
            ).count()
            
            # Count pending records (those without sentiment analysis)
            pending_records = total_recent_records - processed_records
            
            # Get last processed timestamp
            last_processed_record = self.db.query(CustomerSatisfactionRaw).filter(
                and_(
                    CustomerSatisfactionRaw.created_date >= twenty_four_hours_ago,
                    CustomerSatisfactionRaw.sentiment_analyzed_at.isnot(None)
                )
            ).order_by(desc(CustomerSatisfactionRaw.sentiment_analyzed_at)).first()
            
            last_processed_at = None
            if last_processed_record and last_processed_record.sentiment_analyzed_at:
                utc_processed_dt = last_processed_record.sentiment_analyzed_at.replace(tzinfo=pytz.UTC) if last_processed_record.sentiment_analyzed_at.tzinfo is None else last_processed_record.sentiment_analyzed_at
                indonesia_processed_dt = utc_processed_dt.astimezone(indonesia_tz)
                last_processed_at = indonesia_processed_dt.isoformat()
            
            # Calculate processing progress
            processing_progress = 0.0
            is_processing = False
            
            if total_recent_records > 0:
                processing_progress = round((processed_records / total_recent_records) * 100, 1)
                # Consider processing active if there are pending records and some progress has been made
                is_processing = pending_records > 0 and (processed_records > 0 or total_recent_records > processed_records)
            
            # Prepare sentiment analysis status
            sentiment_analysis = None
            if total_recent_records > 0:  # Only include if there are recent records
                sentiment_analysis = {
                    "is_processing": is_processing,
                    "total_records": total_recent_records,
                    "processed_records": processed_records,
                    "pending_records": pending_records,
                    "processing_progress": processing_progress,
                    "last_processed_at": last_processed_at
                }
            
            result = {
                "latest_upload_date": latest_upload_date
            }
            
            # Only include sentiment_analysis if there's relevant data
            if sentiment_analysis:
                result["sentiment_analysis"] = sentiment_analysis
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting latest upload info simple: {str(e)}")
            return None
    
    def get_top_indikasi_keluhan(
        self,
        periode_utk_suspend: str = None,
        submit_review_date: str = None,
        no_ahass: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get top indikasi keluhan with filtering"""
        try:
            # Build base query
            query = self.db.query(CustomerSatisfactionRaw)
            
            # Apply same filters as other methods
            if periode_utk_suspend:
                query = query.filter(CustomerSatisfactionRaw.periode_utk_suspend == periode_utk_suspend)
            
            if submit_review_date:
                query = query.filter(CustomerSatisfactionRaw.submit_review_date_first_fu_cs.like(f"%{submit_review_date}%"))
            
            if no_ahass:
                query = query.filter(CustomerSatisfactionRaw.no_ahass == no_ahass)
            
            # Apply tanggal_rating date filtering using Indonesian date parsing
            query = self._build_tanggal_rating_date_filter(query, date_from, date_to)
            
            # Get total count for percentage calculation
            total_records = query.count()
            
            if total_records == 0:
                return []
            
            # Get top indikasi keluhan with counts
            complaint_stats = self.db.query(
                CustomerSatisfactionRaw.indikasi_keluhan,
                func.count(CustomerSatisfactionRaw.indikasi_keluhan).label('count')
            ).filter(
                query.whereclause if query.whereclause is not None else True
            ).filter(
                CustomerSatisfactionRaw.indikasi_keluhan.isnot(None),
                CustomerSatisfactionRaw.indikasi_keluhan != ''
            ).group_by(
                CustomerSatisfactionRaw.indikasi_keluhan
            ).order_by(
                func.count(CustomerSatisfactionRaw.indikasi_keluhan).desc()
            ).limit(limit).all()
            
            # Calculate percentages and format results
            results = []
            for indikasi_keluhan, count in complaint_stats:
                percentage = round((count / total_records) * 100, 1)
                results.append({
                    "indikasi_keluhan": indikasi_keluhan,
                    "count": count,
                    "percentage": percentage
                })
            
            return results
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting top indikasi keluhan: {str(e)}")
            return []
    
    def get_overall_rating_with_comparison(
        self,
        periode_utk_suspend: str = None,
        submit_review_date: str = None,
        no_ahass: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        tanggal_rating_from: datetime = None,
        tanggal_rating_to: datetime = None,
        compare_previous_period: bool = True
    ) -> Dict[str, Any]:
        """Get overall rating with optional comparison to previous period"""
        try:
            # Helper function to build base query with filters
            def build_query():
                query = self.db.query(CustomerSatisfactionRaw)
                
                # Apply filters
                if periode_utk_suspend:
                    query = query.filter(CustomerSatisfactionRaw.periode_utk_suspend == periode_utk_suspend)
                
                if submit_review_date:
                    query = query.filter(CustomerSatisfactionRaw.submit_review_date_first_fu_cs.like(f"%{submit_review_date}%"))
                
                if no_ahass:
                    query = query.filter(CustomerSatisfactionRaw.no_ahass == no_ahass)
                
                return query
            
            # Helper function to calculate average rating from query with date filters
            def calculate_rating_for_period(query, date_from_param=None, date_to_param=None, tanggal_rating_from_param=None, tanggal_rating_to_param=None):
                period_query = query
                
                # Apply date filters - always use tanggal_rating Indonesian date filtering
                if tanggal_rating_from_param or tanggal_rating_to_param:
                    # Use Indonesian date filtering for tanggal_rating field
                    period_query = self._build_tanggal_rating_date_filter(period_query, tanggal_rating_from_param, tanggal_rating_to_param)
                elif date_from_param or date_to_param:
                    # Also use tanggal_rating filtering for date_from/date_to parameters
                    period_query = self._build_tanggal_rating_date_filter(period_query, date_from_param, date_to_param)
                
                # Get all ratings for the period, excluding empty/null ratings
                ratings_data = period_query.filter(
                    CustomerSatisfactionRaw.rating.isnot(None),
                    CustomerSatisfactionRaw.rating != ''
                ).all()
                
                if not ratings_data:
                    return None, 0
                
                # Calculate average rating
                valid_ratings = []
                for record in ratings_data:
                    try:
                        rating_value = float(record.rating)
                        if 0 <= rating_value <= 5:  # Validate rating is in expected range
                            valid_ratings.append(rating_value)
                    except (ValueError, TypeError):
                        continue
                
                if not valid_ratings:
                    return None, 0
                
                avg_rating = sum(valid_ratings) / len(valid_ratings)
                return round(avg_rating, 2), len(valid_ratings)
            
            # Build base query
            base_query = build_query()
            
            # Calculate current period rating
            current_rating, current_count = calculate_rating_for_period(
                base_query, 
                date_from, 
                date_to, 
                tanggal_rating_from, 
                tanggal_rating_to
            )
            
            result = {
                "current_rating": current_rating,
                "total_ratings": current_count,
                "previous_rating": None,
                "change": None,
                "change_direction": None,
                "period_label": "selected period"
            }
            
            # Calculate previous period for comparison if requested and current period has data
            if compare_previous_period and current_rating is not None:
                try:
                    # Calculate previous period dates
                    if tanggal_rating_from and tanggal_rating_to:
                        # Calculate period length for tanggal_rating
                        period_length = (tanggal_rating_to - tanggal_rating_from).days
                        prev_to = tanggal_rating_from - timedelta(days=1)
                        prev_from = prev_to - timedelta(days=period_length)
                        
                        prev_rating, prev_count = calculate_rating_for_period(
                            base_query,
                            tanggal_rating_from_param=prev_from,
                            tanggal_rating_to_param=prev_to
                        )
                        
                        result["period_label"] = "selected tanggal rating period"
                        
                    elif date_from and date_to:
                        # Calculate period length for created_date
                        period_length = (date_to - date_from).days
                        prev_to = date_from - timedelta(days=1)
                        prev_from = prev_to - timedelta(days=period_length)
                        
                        prev_rating, prev_count = calculate_rating_for_period(
                            base_query,
                            date_from_param=prev_from,
                            date_to_param=prev_to
                        )
                        
                        result["period_label"] = "selected date period"
                    
                    else:
                        # Default to current month vs previous month if no specific dates provided
                        now = datetime.now()
                        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        
                        # Previous month calculation
                        if current_month_start.month == 1:
                            prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
                        else:
                            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)
                        
                        # Get last day of previous month
                        if prev_month_start.month == 12:
                            next_month = prev_month_start.replace(year=prev_month_start.year + 1, month=1)
                        else:
                            next_month = prev_month_start.replace(month=prev_month_start.month + 1)
                        
                        prev_month_end = next_month - timedelta(days=1)
                        prev_month_end = prev_month_end.replace(hour=23, minute=59, second=59)
                        
                        prev_rating, prev_count = calculate_rating_for_period(
                            base_query,
                            date_from_param=prev_month_start,
                            date_to_param=prev_month_end
                        )
                        
                        result["period_label"] = "current period"
                    
                    # Calculate change
                    if prev_rating is not None:
                        result["previous_rating"] = prev_rating
                        change = current_rating - prev_rating
                        result["change"] = round(change, 2)
                        
                        if change > 0:
                            result["change_direction"] = "increase"
                        elif change < 0:
                            result["change_direction"] = "decrease"
                        else:
                            result["change_direction"] = "no_change"
                            
                except Exception as e:
                    logger.warning(f"Error calculating previous period rating: {str(e)}")
                    # Continue without comparison data
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting overall rating with comparison: {str(e)}")
            return {
                "current_rating": None,
                "total_ratings": 0,
                "previous_rating": None,
                "change": None,
                "change_direction": None,
                "period_label": "error"
            }
    
    # Sentiment Analysis Methods
    
    def get_unanalyzed_records(self, limit: int = 50, upload_batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get customer satisfaction records that need sentiment analysis
        
        Args:
            limit: Maximum number of records to return
            upload_batch_id: Optional filter by specific upload batch
            
        Returns:
            List of records with id, no_tiket, and review (from inbox) fields
        """
        try:
            query = self.db.query(CustomerSatisfactionRaw).filter(
                and_(
                    CustomerSatisfactionRaw.sentiment.is_(None),  # Not analyzed yet
                    CustomerSatisfactionRaw.inbox.isnot(None),   # Has review content
                    func.trim(CustomerSatisfactionRaw.inbox) != ''  # Review is not empty
                )
            )
            
            if upload_batch_id:
                query = query.filter(CustomerSatisfactionRaw.upload_batch_id == upload_batch_id)
            
            records = query.limit(limit).all()
            
            # Format records for sentiment analysis
            formatted_records = []
            for record in records:
                formatted_records.append({
                    "id": str(record.id),
                    "no_tiket": record.no_tiket or "",
                    "review": record.inbox or ""
                })
            
            logger.info(f"Found {len(formatted_records)} unanalyzed records")
            return formatted_records
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting unanalyzed records: {str(e)}")
            return []
    
    def update_sentiment_analysis(self, record_id: str, sentiment_data: Dict[str, Any]) -> bool:
        """
        Update sentiment analysis results for a single record
        
        Args:
            record_id: UUID of the record to update
            sentiment_data: Dictionary containing sentiment analysis results
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            record = self.db.query(CustomerSatisfactionRaw).filter(
                CustomerSatisfactionRaw.id == record_id
            ).first()
            
            if not record:
                logger.warning(f"Record with ID {record_id} not found")
                return False
            
            # Update sentiment fields
            record.sentiment = sentiment_data.get('sentiment')
            record.sentiment_score = sentiment_data.get('sentiment_score')
            record.sentiment_reasons = sentiment_data.get('sentiment_reasons')
            record.sentiment_suggestion = sentiment_data.get('sentiment_suggestion')
            record.sentiment_themes = sentiment_data.get('sentiment_themes')
            record.sentiment_analyzed_at = sentiment_data.get('sentiment_analyzed_at')
            record.sentiment_batch_id = sentiment_data.get('sentiment_batch_id')
            
            # Update modification timestamp
            record.last_modified_date = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Updated sentiment analysis for record {record_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating sentiment analysis for record {record_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def bulk_update_sentiment_analysis(self, sentiment_results: List[Dict[str, Any]], batch_id: Optional[str] = None) -> Dict[str, int]:
        """
        Bulk update sentiment analysis results for multiple records
        
        Args:
            sentiment_results: List of sentiment analysis results
            batch_id: Optional batch ID for tracking
            
        Returns:
            Dictionary with update statistics
        """
        updated_count = 0
        failed_count = 0
        
        try:
            for result in sentiment_results:
                try:
                    record_id = result.get('id')
                    if not record_id:
                        failed_count += 1
                        continue
                    
                    # Add batch_id if provided
                    if batch_id:
                        result['sentiment_batch_id'] = batch_id
                    
                    success = self.update_sentiment_analysis(record_id, result)
                    if success:
                        updated_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing sentiment result for ID {result.get('id', 'unknown')}: {str(e)}")
                    failed_count += 1
            
            logger.info(f"Bulk sentiment update completed: {updated_count} updated, {failed_count} failed")
            
            return {
                "updated_count": updated_count,
                "failed_count": failed_count,
                "total_processed": len(sentiment_results)
            }
            
        except Exception as e:
            logger.error(f"Error in bulk sentiment analysis update: {str(e)}")
            return {
                "updated_count": updated_count,
                "failed_count": failed_count + len(sentiment_results) - updated_count,
                "total_processed": len(sentiment_results)
            }
    
    def get_sentiment_statistics(
        self,
        periode_utk_suspend: Optional[str] = None,
        submit_review_date: Optional[str] = None,
        no_ahass: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get sentiment analysis statistics
        
        Args:
            periode_utk_suspend: Filter by periode untuk suspend
            submit_review_date: Filter by submit review date
            no_ahass: Filter by No AHASS
            date_from: Filter by date from
            date_to: Filter by date to
            
        Returns:
            Dictionary containing sentiment statistics
        """
        try:
            # Build base query with sentiment analysis data
            query = self.db.query(CustomerSatisfactionRaw).filter(
                CustomerSatisfactionRaw.sentiment.isnot(None)
            )
            
            # Apply filters (same logic as other methods)
            if periode_utk_suspend:
                query = query.filter(CustomerSatisfactionRaw.periode_utk_suspend.ilike(f"%{periode_utk_suspend}%"))
            
            if submit_review_date:
                query = query.filter(CustomerSatisfactionRaw.submit_review_date_first_fu_cs.ilike(f"%{submit_review_date}%"))
            
            if no_ahass:
                query = query.filter(CustomerSatisfactionRaw.no_ahass == no_ahass)
            
            # Apply tanggal_rating date filtering using Indonesian date parsing
            query = self._build_tanggal_rating_date_filter(query, date_from, date_to)
            
            # Get sentiment distribution
            sentiment_distribution = self.db.query(
                CustomerSatisfactionRaw.sentiment,
                func.count(CustomerSatisfactionRaw.id).label('count')
            ).filter(
                query.filter(CustomerSatisfactionRaw.sentiment.isnot(None))
                .statement.whereclause
            ).group_by(
                CustomerSatisfactionRaw.sentiment
            ).all()
            
            # Get average sentiment score
            avg_score = self.db.query(
                func.avg(CustomerSatisfactionRaw.sentiment_score).label('avg_score')
            ).filter(
                query.filter(CustomerSatisfactionRaw.sentiment_score.isnot(None))
                .statement.whereclause
            ).scalar()
            
            # Get total analyzed records
            total_analyzed = query.count()
            
            # Get top themes (this would require parsing the JSON themes field)
            # For now, we'll return a simple count
            themes_count = self.db.query(
                func.count(CustomerSatisfactionRaw.id).label('count')
            ).filter(
                and_(
                    query.filter(CustomerSatisfactionRaw.sentiment_themes.isnot(None))
                    .statement.whereclause,
                    CustomerSatisfactionRaw.sentiment_themes != ''
                )
            ).scalar() or 0
            
            # Format results with percentage calculations
            sentiment_dist = []
            for item in sentiment_distribution:
                count = item[1]
                percentage = round((count / total_analyzed * 100), 1) if total_analyzed > 0 else 0.0
                sentiment_dist.append({
                    "sentiment": item[0],
                    "count": count,
                    "percentage": percentage
                })
            
            return {
                "total_analyzed_records": total_analyzed,
                "average_sentiment_score": float(avg_score) if avg_score else None,
                "sentiment_distribution": sentiment_dist,
                "records_with_themes": themes_count,
                "analysis_summary": {
                    "positive_count": next((item["count"] for item in sentiment_dist if item["sentiment"] == "Positive"), 0),
                    "negative_count": next((item["count"] for item in sentiment_dist if item["sentiment"] == "Negative"), 0),
                    "neutral_count": next((item["count"] for item in sentiment_dist if item["sentiment"] == "Neutral"), 0)
                }
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting sentiment statistics: {str(e)}")
            return {
                "total_analyzed_records": 0,
                "average_sentiment_score": None,
                "sentiment_distribution": [],
                "records_with_themes": 0,
                "analysis_summary": {
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0
                }
            }
    
    def get_records_by_sentiment(
        self,
        sentiment: str,
        page: int = 1,
        page_size: int = 10,
        periode_utk_suspend: Optional[str] = None,
        submit_review_date: Optional[str] = None,
        no_ahass: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get customer satisfaction records filtered by sentiment
        
        Args:
            sentiment: Sentiment to filter by (Positive/Negative/Neutral)
            page: Page number (1-based)
            page_size: Number of records per page
            periode_utk_suspend: Filter by periode untuk suspend
            submit_review_date: Filter by submit review date
            no_ahass: Filter by No AHASS
            
        Returns:
            Dictionary containing paginated records and metadata
        """
        try:
            # Build base query
            query = self.db.query(CustomerSatisfactionRaw).filter(
                CustomerSatisfactionRaw.sentiment == sentiment
            )
            
            # Apply additional filters
            if periode_utk_suspend:
                query = query.filter(CustomerSatisfactionRaw.periode_utk_suspend.ilike(f"%{periode_utk_suspend}%"))
            
            if submit_review_date:
                query = query.filter(CustomerSatisfactionRaw.submit_review_date_first_fu_cs.ilike(f"%{submit_review_date}%"))
            
            if no_ahass:
                query = query.filter(CustomerSatisfactionRaw.no_ahass == no_ahass)
            
            # Get total count
            total_count = query.count()
            
            # Calculate pagination
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated records
            records = query.order_by(desc(CustomerSatisfactionRaw.sentiment_analyzed_at))\
                          .offset(offset)\
                          .limit(page_size)\
                          .all()
            
            # Convert to dictionaries
            records_data = [record.to_dict() for record in records]
            
            return {
                "records": records_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting records by sentiment '{sentiment}': {str(e)}")
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