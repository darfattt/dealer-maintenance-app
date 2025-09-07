"""
Customer reminder request repository
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.customer_reminder_request import CustomerReminderRequest
from app.schemas.customer_reminder_request import CustomerReminderRequestCreate, BulkReminderCustomerData
from app.utils.timezone_utils import get_indonesia_datetime, parse_datetime_indonesia_format

logger = logging.getLogger(__name__)


class CustomerReminderRequestRepository:
    """Repository for customer reminder request operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, request_data: CustomerReminderRequestCreate, created_by: Optional[str] = None) -> CustomerReminderRequest:
        """Create a new customer reminder request"""
        try:
            # Parse the datetime strings or use current time as default
            current_time = get_indonesia_datetime()
            
            if request_data.created_time:
                created_datetime = parse_datetime_indonesia_format(request_data.created_time)
            else:
                created_datetime = current_time
                
            if request_data.modified_time:
                modified_datetime = parse_datetime_indonesia_format(request_data.modified_time)
            else:
                modified_datetime = current_time
            
            # Create the model instance
            db_request = CustomerReminderRequest(
                dealer_id=request_data.dealer_id,
                request_date=created_datetime.date(),
                request_time=created_datetime.time(),
                nama_pelanggan=request_data.nama_pelanggan,
                nomor_telepon_pelanggan=request_data.nomor_telepon_pelanggan,
                reminder_type=request_data.reminder_type,
                request_status='PENDING',
                whatsapp_status='NOT_SENT',
                created_by=created_by or 'system',
                created_date=created_datetime,
                last_modified_by=created_by or 'system',
                last_modified_date=modified_datetime
            )
            
            self.db.add(db_request)
            self.db.commit()
            self.db.refresh(db_request)
            
            return db_request
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def create_bulk_reminder(
        self, 
        customer_data: BulkReminderCustomerData, 
        ahass_data: Dict[str, Any],
        reminder_target: str,
        reminder_type: str,
        dealer_id: str,
        transaction_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> CustomerReminderRequest:
        """Create a new customer reminder request from bulk data"""
        try:
            current_time = get_indonesia_datetime()
            
            # Parse date strings
            tanggal_beli = None
            tanggal_expired_kpb = None
            
            try:
                tanggal_beli = datetime.strptime(customer_data.tanggal_beli, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Invalid tanggal_beli format: {customer_data.tanggal_beli}")
            
            try:
                tanggal_expired_kpb = datetime.strptime(customer_data.tanggal_expired_kpb, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Invalid tanggal_expired_kpb format: {customer_data.tanggal_expired_kpb}")
            
            # Create the model instance
            db_request = CustomerReminderRequest(
                dealer_id=dealer_id,
                request_date=current_time.date(),
                request_time=current_time.time(),
                nama_pelanggan=customer_data.nama_pelanggan,
                nomor_telepon_pelanggan=customer_data.nomor_telepon_pelanggan,
                nomor_mesin=customer_data.nomor_mesin,
                nomor_polisi=customer_data.nomor_polisi,
                tipe_unit=customer_data.tipe_unit,
                tanggal_beli=tanggal_beli,
                tanggal_expired_kpb=tanggal_expired_kpb,
                kode_ahass=ahass_data.get('kode_ahass'),
                nama_ahass=ahass_data.get('nama_ahass'),
                alamat_ahass=ahass_data.get('alamat_ahass'),
                reminder_target=reminder_target,
                reminder_type=reminder_type,
                transaction_id=transaction_id,
                request_status='PENDING',
                whatsapp_status='NOT_SENT',
                created_by=created_by or 'system',
                created_date=current_time,
                last_modified_by=created_by or 'system',
                last_modified_date=current_time
            )
            
            self.db.add(db_request)
            self.db.commit()
            self.db.refresh(db_request)
            
            return db_request
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_by_id(self, request_id: str) -> Optional[CustomerReminderRequest]:
        """Get customer reminder request by ID"""
        return self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.id == request_id
        ).first()
    
    def get_by_dealer_id(self, dealer_id: str, limit: int = 100) -> List[CustomerReminderRequest]:
        """Get customer reminder requests by dealer ID"""
        return self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        ).order_by(CustomerReminderRequest.created_date.desc()).limit(limit).all()
    
    def update_status(
        self, 
        request_id: str, 
        request_status: Optional[str] = None,
        whatsapp_status: Optional[str] = None,
        whatsapp_message: Optional[str] = None,
        fonnte_response: Optional[dict] = None,
        modified_by: Optional[str] = None
    ) -> Optional[CustomerReminderRequest]:
        """Update customer reminder request status and WhatsApp message"""
        try:
            db_request = self.get_by_id(request_id)
            if not db_request:
                return None
            
            if request_status:
                db_request.request_status = request_status
            
            if whatsapp_status:
                db_request.whatsapp_status = whatsapp_status
            
            if whatsapp_message:
                db_request.whatsapp_message = whatsapp_message
            
            if fonnte_response:
                db_request.fonnte_response = fonnte_response
            
            if modified_by:
                db_request.last_modified_by = modified_by
            
            db_request.last_modified_date = get_indonesia_datetime()
            
            self.db.commit()
            self.db.refresh(db_request)
            
            return db_request
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_requests_by_status(self, status: str, limit: int = 100) -> List[CustomerReminderRequest]:
        """Get customer reminder requests by status"""
        return self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.request_status == status
        ).order_by(CustomerReminderRequest.created_date.desc()).limit(limit).all()
    
    def get_requests_by_reminder_type(self, reminder_type: str, limit: int = 100) -> List[CustomerReminderRequest]:
        """Get customer reminder requests by reminder type"""
        return self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.reminder_type == reminder_type
        ).order_by(CustomerReminderRequest.created_date.desc()).limit(limit).all()
    
    def get_requests_by_phone(self, phone_number: str) -> List[CustomerReminderRequest]:
        """Get customer reminder requests by phone number"""
        return self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.nomor_telepon_pelanggan == phone_number
        ).order_by(CustomerReminderRequest.created_date.desc()).all()
    
    def count_requests_by_dealer(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> int:
        """Count customer reminder requests by dealer and date range"""
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        return query.count()
    
    def get_whatsapp_status_stats(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None, reminder_target: Optional[str] = None) -> dict:
        """Get WhatsApp status statistics for a dealer"""
        from sqlalchemy import func
        
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        if reminder_target:
            query = query.filter(CustomerReminderRequest.reminder_target == reminder_target)
        
        # Count total requests
        total_requests = query.count()
        
        # Count by WhatsApp status
        delivered_count = query.filter(CustomerReminderRequest.whatsapp_status == 'SENT').count()
        failed_count = query.filter(CustomerReminderRequest.whatsapp_status == 'FAILED').count()
        pending_count = query.filter(CustomerReminderRequest.whatsapp_status == 'NOT_SENT').count()
        
        # Calculate delivery percentage
        delivery_percentage = round((delivered_count / total_requests * 100) if total_requests > 0 else 0, 2)
        
        return {
            'total_requests': total_requests,
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'pending_count': pending_count,
            'delivery_percentage': delivery_percentage
        }
    
    def get_reminder_type_stats(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None, reminder_target: Optional[str] = None) -> dict:
        """Get reminder type statistics for a dealer"""
        from sqlalchemy import func
        
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        if reminder_target:
            query = query.filter(CustomerReminderRequest.reminder_target == reminder_target)
        
        # Count by reminder type
        reminder_stats = query.with_entities(
            CustomerReminderRequest.reminder_type,
            func.count(CustomerReminderRequest.id).label('count')
        ).group_by(CustomerReminderRequest.reminder_type).all()
        
        return {reminder_type: count for reminder_type, count in reminder_stats}
    
    def get_reminder_target_stats(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None, reminder_target: Optional[str] = None) -> dict:
        """Get reminder target statistics for a dealer"""
        from sqlalchemy import func
        
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        if reminder_target:
            query = query.filter(CustomerReminderRequest.reminder_target == reminder_target)
        
        # Count by reminder target
        reminder_target_stats = query.with_entities(
            CustomerReminderRequest.reminder_target,
            func.count(CustomerReminderRequest.id).label('count')
        ).group_by(CustomerReminderRequest.reminder_target).all()
        
        return {target or 'Unknown': count for target, count in reminder_target_stats}
    
    def get_paginated_requests_by_dealer(
        self, 
        dealer_id: str, 
        page: int = 1, 
        page_size: int = 10,
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None,
        reminder_target: Optional[str] = None
    ) -> dict:
        """Get paginated customer reminder requests by dealer with date and target filtering"""
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        if reminder_target:
            query = query.filter(CustomerReminderRequest.reminder_target == reminder_target)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * page_size
        requests = query.order_by(
            CustomerReminderRequest.request_date.desc(),
            CustomerReminderRequest.request_time.desc()
        ).offset(offset).limit(page_size).all()
        
        return {
            'items': [request.to_safe_dict() for request in requests],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def get_reminders_by_transaction_id(self, transaction_id: str) -> dict:
        """Get customer reminder requests by transaction ID without pagination"""
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.transaction_id == transaction_id
        )
        
        # Get total count
        total = query.count()
        
        # Get all requests ordered by creation date
        requests = query.order_by(
            CustomerReminderRequest.request_date.desc(),
            CustomerReminderRequest.request_time.desc()
        ).all()
        
        return {
            'items': [request.to_safe_dict() for request in requests],
            'total': total,
            'transaction_id': transaction_id
        }
    
    def get_reminder_type_whatsapp_status_stats(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None, reminder_target: Optional[str] = None) -> dict:
        """Get statistics grouped by reminder_type and whatsapp_status (cross-tabulation)"""
        from sqlalchemy import func
        
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        if reminder_target:
            query = query.filter(CustomerReminderRequest.reminder_target == reminder_target)
        
        # Get cross-tabulation of reminder_type and whatsapp_status
        results = query.with_entities(
            CustomerReminderRequest.reminder_type,
            CustomerReminderRequest.reminder_target,
            CustomerReminderRequest.whatsapp_status,
            func.count(CustomerReminderRequest.id).label('count')
        ).group_by(
            CustomerReminderRequest.reminder_type,
            CustomerReminderRequest.reminder_target,
            CustomerReminderRequest.whatsapp_status
        ).all()
        
        # Structure the results as nested dictionary with fallback logic
        stats = {}
        for reminder_type, reminder_target, whatsapp_status, count in results:
            # Use reminder_target as fallback if reminder_type is null
            type_key = reminder_type if reminder_type else reminder_target
            
            if type_key not in stats:
                stats[type_key] = {}
            stats[type_key][whatsapp_status] = count
        
        return stats
    
    def get_tipe_unit_stats(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None, reminder_target: Optional[str] = None) -> dict:
        """Get statistics grouped by tipe_unit (vehicle type)"""
        from sqlalchemy import func
        
        query = self.db.query(CustomerReminderRequest).filter(
            CustomerReminderRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerReminderRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerReminderRequest.request_date <= date_to)
        
        if reminder_target:
            query = query.filter(CustomerReminderRequest.reminder_target == reminder_target)
        
        # Count by tipe_unit
        tipe_unit_stats = query.with_entities(
            CustomerReminderRequest.tipe_unit,
            func.count(CustomerReminderRequest.id).label('count')
        ).group_by(CustomerReminderRequest.tipe_unit).all()
        
        return {tipe_unit or 'Unknown': count for tipe_unit, count in tipe_unit_stats}
    
    def delete(self, request_id: str) -> bool:
        """Delete customer reminder request"""
        try:
            db_request = self.get_by_id(request_id)
            if not db_request:
                return False
            
            self.db.delete(db_request)
            self.db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e