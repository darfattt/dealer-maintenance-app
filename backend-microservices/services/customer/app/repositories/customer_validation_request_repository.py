"""
Customer validation request repository
"""

from typing import Optional, List
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.customer_validation_request import CustomerValidationRequest
from app.schemas.customer_validation_request import CustomerValidationRequestCreate


class CustomerValidationRequestRepository:
    """Repository for customer validation request operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, request_data: CustomerValidationRequestCreate, created_by: Optional[str] = None) -> CustomerValidationRequest:
        """Create a new customer validation request"""
        try:
            # Parse the datetime strings or use current time as default
            current_time = datetime.utcnow()
            
            if request_data.createdTime:
                created_datetime = datetime.strptime(request_data.createdTime, '%d/%m/%Y %H:%M:%S')
            else:
                created_datetime = current_time
                
            if request_data.modifiedTime:
                modified_datetime = datetime.strptime(request_data.modifiedTime, '%d/%m/%Y %H:%M:%S')
            else:
                modified_datetime = current_time
            
            # Create the model instance
            db_request = CustomerValidationRequest(
                dealer_id=request_data.dealerId,
                request_date=created_datetime.date(),
                request_time=created_datetime.time(),
                nama_pembawa=request_data.namaPembawa,
                no_telp=request_data.noTelp,
                tipe_unit=request_data.tipeUnit,
                no_pol=request_data.noPol,
                kode_ahass=request_data.kodeAhass,
                nama_ahass=request_data.namaAhass,
                alamat_ahass=request_data.alamatAhass,
                nomor_mesin=request_data.noMesin,
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
    
    def get_by_id(self, request_id: str) -> Optional[CustomerValidationRequest]:
        """Get customer validation request by ID"""
        return self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.id == request_id
        ).first()
    
    def get_by_dealer_id(self, dealer_id: str, limit: int = 100) -> List[CustomerValidationRequest]:
        """Get customer validation requests by dealer ID"""
        return self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.dealer_id == dealer_id
        ).order_by(CustomerValidationRequest.created_date.desc()).limit(limit).all()
    
    def update_status(
        self, 
        request_id: str, 
        request_status: Optional[str] = None,
        whatsapp_status: Optional[str] = None,
        whatsapp_message: Optional[str] = None,
        fonnte_response: Optional[dict] = None,
        modified_by: Optional[str] = None
    ) -> Optional[CustomerValidationRequest]:
        """Update customer validation request status and WhatsApp message"""
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
            
            db_request.last_modified_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_request)
            
            return db_request
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_requests_by_status(self, status: str, limit: int = 100) -> List[CustomerValidationRequest]:
        """Get customer validation requests by status"""
        return self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.request_status == status
        ).order_by(CustomerValidationRequest.created_date.desc()).limit(limit).all()
    
    def get_requests_by_phone(self, phone_number: str) -> List[CustomerValidationRequest]:
        """Get customer validation requests by phone number"""
        return self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.no_telp == phone_number
        ).order_by(CustomerValidationRequest.created_date.desc()).all()
    
    def count_requests_by_dealer(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> int:
        """Count customer validation requests by dealer and date range"""
        query = self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerValidationRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerValidationRequest.request_date <= date_to)
        
        return query.count()
    
    def get_whatsapp_status_stats(self, dealer_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> dict:
        """Get WhatsApp status statistics for a dealer"""
        from sqlalchemy import func
        
        query = self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerValidationRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerValidationRequest.request_date <= date_to)
        
        # Count total requests
        total_requests = query.count()
        
        # Count by WhatsApp status
        delivered_count = query.filter(CustomerValidationRequest.whatsapp_status == 'SENT').count()
        failed_count = query.filter(CustomerValidationRequest.whatsapp_status == 'FAILED').count()
        
        # Calculate delivery percentage
        delivery_percentage = round((delivered_count / total_requests * 100) if total_requests > 0 else 0, 2)
        
        return {
            'total_requests': total_requests,
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'delivery_percentage': delivery_percentage
        }
    
    def get_paginated_requests_by_dealer(
        self, 
        dealer_id: str, 
        page: int = 1, 
        page_size: int = 10,
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> dict:
        """Get paginated customer validation requests by dealer with date filtering"""
        query = self.db.query(CustomerValidationRequest).filter(
            CustomerValidationRequest.dealer_id == dealer_id
        )
        
        if date_from:
            query = query.filter(CustomerValidationRequest.request_date >= date_from)
        
        if date_to:
            query = query.filter(CustomerValidationRequest.request_date <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * page_size
        requests = query.order_by(
            CustomerValidationRequest.request_date.desc(),
            CustomerValidationRequest.request_time.desc()
        ).offset(offset).limit(page_size).all()
        
        return {
            'items': [request.to_dict() for request in requests],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def delete(self, request_id: str) -> bool:
        """Delete customer validation request"""
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