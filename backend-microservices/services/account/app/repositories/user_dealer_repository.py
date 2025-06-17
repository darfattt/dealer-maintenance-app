"""
Repository for UserDealer operations
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import UserDealer


class UserDealerRepository:
    """Repository for UserDealer operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: UUID, dealer_id: str) -> UserDealer:
        """Create a new user dealer relationship"""
        try:
            user_dealer = UserDealer(
                user_id=user_id,
                dealer_id=dealer_id
            )
            self.db.add(user_dealer)
            self.db.commit()
            self.db.refresh(user_dealer)
            return user_dealer
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User dealer relationship already exists or invalid user_id: {user_id}")
    
    def get_by_id(self, user_dealer_id: UUID) -> Optional[UserDealer]:
        """Get user dealer by ID"""
        return self.db.query(UserDealer).filter(UserDealer.id == user_dealer_id).first()
    
    def get_by_user_id(self, user_id: UUID) -> List[UserDealer]:
        """Get all dealer relationships for a user"""
        return self.db.query(UserDealer).filter(UserDealer.user_id == user_id).all()
    
    def get_by_dealer_id(self, dealer_id: str) -> List[UserDealer]:
        """Get all user relationships for a dealer"""
        return self.db.query(UserDealer).filter(UserDealer.dealer_id == dealer_id).all()
    
    def get_by_user_and_dealer(self, user_id: UUID, dealer_id: str) -> Optional[UserDealer]:
        """Get specific user dealer relationship"""
        return self.db.query(UserDealer).filter(
            UserDealer.user_id == user_id,
            UserDealer.dealer_id == dealer_id
        ).first()
    
    def delete(self, user_dealer_id: UUID) -> bool:
        """Delete user dealer relationship"""
        user_dealer = self.get_by_id(user_dealer_id)
        if user_dealer:
            self.db.delete(user_dealer)
            self.db.commit()
            return True
        return False
    
    def delete_by_user_and_dealer(self, user_id: UUID, dealer_id: str) -> bool:
        """Delete specific user dealer relationship"""
        user_dealer = self.get_by_user_and_dealer(user_id, dealer_id)
        if user_dealer:
            self.db.delete(user_dealer)
            self.db.commit()
            return True
        return False
    
    def delete_all_by_user(self, user_id: UUID) -> int:
        """Delete all dealer relationships for a user"""
        count = self.db.query(UserDealer).filter(UserDealer.user_id == user_id).count()
        self.db.query(UserDealer).filter(UserDealer.user_id == user_id).delete()
        self.db.commit()
        return count
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserDealer]:
        """Get all user dealer relationships with pagination"""
        return self.db.query(UserDealer).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Get total count of user dealer relationships"""
        return self.db.query(UserDealer).count()
    
    def exists(self, user_id: UUID, dealer_id: str) -> bool:
        """Check if user dealer relationship exists"""
        return self.db.query(UserDealer).filter(
            UserDealer.user_id == user_id,
            UserDealer.dealer_id == dealer_id
        ).first() is not None
