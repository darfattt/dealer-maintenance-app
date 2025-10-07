"""
User controller for handling user management operations
"""

import uuid
import math
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, DealerAdminRegistration
from app.repositories.user_repository import UserRepository
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class UserController:
    """Controller for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def create_user(self, user_data: UserCreate, current_user: User) -> UserResponse:
        """
        Create a new user
        
        Args:
            user_data: User creation data
            current_user: Current authenticated user
            
        Returns:
            Created user response
            
        Raises:
            HTTPException: If user lacks permission or email already exists
        """
        # Check permissions
        if not current_user.has_permission(UserRole.SUPER_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can create users"
            )
        
        # Check if email already exists
        existing_user = self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists (if provided)
        if user_data.username:
            existing_username = self.user_repo.get_user_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create user
        try:
            user = self.user_repo.create_user(user_data)
            logger.info(f"User created: {user.email} by {current_user.email}")
            return UserResponse.from_orm(user)
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    def get_user_by_id(self, user_id: uuid.UUID, current_user: User) -> UserResponse:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            current_user: Current authenticated user
            
        Returns:
            User response
            
        Raises:
            HTTPException: If user not found or access denied
        """
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        if not self._can_access_user(current_user, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return UserResponse.from_orm(user)
    
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate, current_user: User) -> UserResponse:
        """
        Update user information
        
        Args:
            user_id: User ID
            user_data: User update data
            current_user: Current authenticated user
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found or access denied
        """
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        if not self._can_modify_user(current_user, user, user_data):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            existing_user = self.user_repo.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check username uniqueness if being updated
        if user_data.username and user_data.username != user.username:
            existing_username = self.user_repo.get_user_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user
        try:
            updated_user = self.user_repo.update_user(user_id, user_data)
            logger.info(f"User updated: {updated_user.email} by {current_user.email}")
            return UserResponse.from_orm(updated_user)
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    def delete_user(self, user_id: uuid.UUID, current_user: User) -> dict:
        """
        Delete user
        
        Args:
            user_id: User ID
            current_user: Current authenticated user
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If user not found or access denied
        """
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions (only super admin can delete users)
        if not current_user.has_permission(UserRole.SUPER_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can delete users"
            )
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Delete user
        try:
            self.user_repo.delete_user(user_id)
            logger.info(f"User deleted: {user.email} by {current_user.email}")
            return {"message": "User deleted successfully"}
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
    
    def get_users(
        self,
        current_user: User,
        page: int = 1,
        per_page: int = 20,
        role: Optional[UserRole] = None,
        dealer_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> UserListResponse:
        """
        Get users with filtering and pagination
        
        Args:
            current_user: Current authenticated user
            page: Page number (1-based)
            per_page: Items per page
            role: Filter by role
            dealer_id: Filter by dealer ID
            is_active: Filter by active status
            search: Search term
            
        Returns:
            User list response
            
        Raises:
            HTTPException: If access denied
        """
        # Check permissions
        if not current_user.has_permission(UserRole.SUPER_ADMIN):
            # Dealer admins can only see users from their dealer
            if current_user.role == UserRole.DEALER_ADMIN:
                dealer_id = current_user.dealer_id
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Calculate skip
        skip = (page - 1) * per_page
        
        # Get users
        try:
            users, total = self.user_repo.get_users(
                skip=skip,
                limit=per_page,
                role=role,
                dealer_id=dealer_id,
                is_active=is_active,
                search=search
            )
            
            # Calculate pagination info
            pages = math.ceil(total / per_page) if total > 0 else 1
            
            return UserListResponse(
                users=[UserResponse.from_orm(user) for user in users],
                total=total,
                page=page,
                per_page=per_page,
                pages=pages
            )
        except Exception as e:
            logger.error(f"Failed to get users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get users"
            )
    
    def _can_access_user(self, current_user: User, target_user: User) -> bool:
        """Check if current user can access target user"""
        # Super admin can access all users
        if current_user.has_permission(UserRole.SUPER_ADMIN):
            return True
        
        # Users can access their own profile
        if current_user.id == target_user.id:
            return True
        
        # Dealer admin can access users from same dealer
        if (current_user.role == UserRole.DEALER_ADMIN and 
            current_user.dealer_id == target_user.dealer_id):
            return True
        
        return False
    
    def _can_modify_user(self, current_user: User, target_user: User, update_data: UserUpdate) -> bool:
        """Check if current user can modify target user"""
        # Super admin can modify all users
        if current_user.has_permission(UserRole.SUPER_ADMIN):
            return True

        # Users can modify their own profile (with restrictions)
        if current_user.id == target_user.id:
            # Users cannot change their own role or dealer_id
            if update_data.role is not None or update_data.dealer_id is not None:
                return False
            return True

        return False

    def create_dealer_admin(self, user_data: DealerAdminRegistration) -> UserResponse:
        """
        Create a dealer admin user during dealer registration
        No authentication required - this is called by the backend API during dealer registration

        Args:
            user_data: Dealer admin registration data

        Returns:
            Created user response

        Raises:
            HTTPException: If email already exists or validation fails
        """
        # Check if email already exists
        existing_user = self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user_data.email} is already registered"
            )

        # Create user with DEALER_ADMIN role
        try:
            user = self.user_repo.create_user(
                email=user_data.email,
                password=user_data.password,
                full_name=user_data.full_name,
                username=None,
                role=UserRole.DEALER_ADMIN,
                dealer_id=user_data.dealer_id,
                is_active=True,
                is_verified=True
            )

            logger.info(f"Dealer admin user created: {user.email} for dealer {user_data.dealer_id}")
            return UserResponse.from_orm(user)

        except ValueError as e:
            logger.error(f"Failed to create dealer admin: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error creating dealer admin: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create dealer admin user"
            )
