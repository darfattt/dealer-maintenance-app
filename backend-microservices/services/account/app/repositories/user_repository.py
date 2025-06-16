"""
User repository for database operations
"""

import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.auth import hash_password


class UserRepository:
    """Repository for user database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user instance
        """
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create user instance
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            dealer_id=user_data.dealer_id,
            is_active=user_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user instance or None
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        # Update fields that are provided
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Delete user
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        
        return True
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        dealer_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """
        Get users with filtering and pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Filter by role
            dealer_id: Filter by dealer ID
            is_active: Filter by active status
            search: Search in email, username, or full_name
            
        Returns:
            Tuple of (users list, total count)
        """
        query = self.db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if dealer_id:
            query = query.filter(User.dealer_id == dealer_id)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def update_last_login(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        db_user.last_login_at = datetime.utcnow()
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_password(self, user_id: uuid.UUID, new_password: str) -> Optional[User]:
        """
        Update user password
        
        Args:
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            Updated user instance or None
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        db_user.hashed_password = hash_password(new_password)
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def set_password_reset_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> Optional[User]:
        """
        Set password reset token for user
        
        Args:
            user_id: User ID
            token: Reset token
            expires_at: Token expiration time
            
        Returns:
            Updated user instance or None
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        db_user.password_reset_token = token
        db_user.password_reset_expires = expires_at
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_reset_token(self, token: str) -> Optional[User]:
        """
        Get user by password reset token
        
        Args:
            token: Reset token
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(
            and_(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        ).first()
    
    def clear_password_reset_token(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Clear password reset token
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        db_user.password_reset_token = None
        db_user.password_reset_expires = None
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
