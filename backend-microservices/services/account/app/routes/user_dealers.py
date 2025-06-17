"""
Routes for UserDealer operations
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.controllers.user_dealer_controller import UserDealerController
from app.models.user import User
from app.schemas.user import (
    UserDealerCreate,
    UserDealerResponse,
    UserDealerListResponse
)

router = APIRouter(prefix="/user-dealers", tags=["user-dealers"])


@router.post("/", response_model=UserDealerResponse, status_code=status.HTTP_201_CREATED)
async def create_user_dealer(
    user_dealer_data: UserDealerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user dealer relationship"""
    controller = UserDealerController(db)
    return controller.create_user_dealer(
        user_dealer_data=user_dealer_data,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.get("/user/{user_id}", response_model=UserDealerListResponse)
async def get_user_dealers_by_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all dealer relationships for a user"""
    controller = UserDealerController(db)
    return controller.get_user_dealers_by_user(
        user_id=user_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.get("/dealer/{dealer_id}", response_model=UserDealerListResponse)
async def get_user_dealers_by_dealer(
    dealer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all user relationships for a dealer"""
    controller = UserDealerController(db)
    return controller.get_user_dealers_by_dealer(
        dealer_id=dealer_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.delete("/{user_dealer_id}")
async def delete_user_dealer(
    user_dealer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user dealer relationship"""
    controller = UserDealerController(db)
    return controller.delete_user_dealer(
        user_dealer_id=user_dealer_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.delete("/user/{user_id}/dealer/{dealer_id}")
async def delete_user_dealer_by_user_and_dealer(
    user_id: UUID,
    dealer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete specific user dealer relationship"""
    controller = UserDealerController(db)
    return controller.delete_user_dealer_by_user_and_dealer(
        user_id=user_id,
        dealer_id=dealer_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.get("/me/dealers", response_model=List[str])
async def get_my_dealers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dealer IDs for current user (for DEALER_USER role)"""
    controller = UserDealerController(db)
    return controller.get_current_user_dealers(current_user_id=current_user.id)
