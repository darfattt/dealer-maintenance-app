"""
Controller for UserDealer operations
"""

from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.repositories.user_dealer_repository import UserDealerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserDealerCreate, 
    UserDealerResponse, 
    UserDealerListResponse
)


class UserDealerController:
    """Controller for UserDealer operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_dealer_repo = UserDealerRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_user_dealer(self, user_dealer_data: UserDealerCreate, current_user_id: UUID, current_user_role: UserRole) -> UserDealerResponse:
        """Create a new user dealer relationship"""
        # Only SUPER_ADMIN and DEALER_ADMIN can create user dealer relationships
        if current_user_role not in [UserRole.SUPER_ADMIN, UserRole.DEALER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create user dealer relationships"
            )
        
        # Verify the user exists and has DEALER_USER role
        user = self.user_repo.get_by_id(UUID(user_dealer_data.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.role != UserRole.DEALER_USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have DEALER_USER role to be assigned to dealers"
            )
        
        # Check if relationship already exists
        if self.user_dealer_repo.exists(UUID(user_dealer_data.user_id), user_dealer_data.dealer_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User dealer relationship already exists"
            )
        
        try:
            user_dealer = self.user_dealer_repo.create(
                user_id=UUID(user_dealer_data.user_id),
                dealer_id=user_dealer_data.dealer_id
            )
            return UserDealerResponse.from_orm(user_dealer)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    def get_user_dealers_by_user(self, user_id: UUID, current_user_id: UUID, current_user_role: UserRole) -> UserDealerListResponse:
        """Get all dealer relationships for a user"""
        # Users can only view their own relationships, admins can view any
        if current_user_role == UserRole.DEALER_USER and current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own dealer relationships"
            )
        
        user_dealers = self.user_dealer_repo.get_by_user_id(user_id)
        return UserDealerListResponse(
            user_dealers=[UserDealerResponse.from_orm(ud) for ud in user_dealers],
            total=len(user_dealers)
        )
    
    def get_user_dealers_by_dealer(self, dealer_id: str, current_user_id: UUID, current_user_role: UserRole) -> UserDealerListResponse:
        """Get all user relationships for a dealer"""
        # Only admins can view dealer relationships
        if current_user_role not in [UserRole.SUPER_ADMIN, UserRole.DEALER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view dealer relationships"
            )
        
        user_dealers = self.user_dealer_repo.get_by_dealer_id(dealer_id)
        return UserDealerListResponse(
            user_dealers=[UserDealerResponse.from_orm(ud) for ud in user_dealers],
            total=len(user_dealers)
        )
    
    def delete_user_dealer(self, user_dealer_id: UUID, current_user_id: UUID, current_user_role: UserRole) -> dict:
        """Delete a user dealer relationship"""
        # Only SUPER_ADMIN and DEALER_ADMIN can delete relationships
        if current_user_role not in [UserRole.SUPER_ADMIN, UserRole.DEALER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete user dealer relationships"
            )
        
        if not self.user_dealer_repo.delete(user_dealer_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User dealer relationship not found"
            )
        
        return {"message": "User dealer relationship deleted successfully"}
    
    def delete_user_dealer_by_user_and_dealer(self, user_id: UUID, dealer_id: str, current_user_id: UUID, current_user_role: UserRole) -> dict:
        """Delete specific user dealer relationship"""
        # Only SUPER_ADMIN and DEALER_ADMIN can delete relationships
        if current_user_role not in [UserRole.SUPER_ADMIN, UserRole.DEALER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete user dealer relationships"
            )
        
        if not self.user_dealer_repo.delete_by_user_and_dealer(user_id, dealer_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User dealer relationship not found"
            )
        
        return {"message": "User dealer relationship deleted successfully"}
    
    def get_current_user_dealers(self, current_user_id: UUID) -> List[str]:
        """Get dealer IDs for current user (for DEALER_USER role)"""
        user_dealers = self.user_dealer_repo.get_by_user_id(current_user_id)
        return [ud.dealer_id for ud in user_dealers]
