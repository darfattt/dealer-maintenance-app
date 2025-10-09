"""
User management routes
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, DealerAdminRegistration
)
from app.models.user import UserRole
from app.controllers.user_controller import UserController
from app.dependencies import get_db, get_current_user
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (Super Admin only)
    """
    user_controller = UserController(db)
    return user_controller.create_user(user_data, current_user)


@router.get("", response_model=UserListResponse)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in email, username, or full name"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get users with filtering and pagination
    """
    user_controller = UserController(db)
    return user_controller.get_users(
        current_user=current_user,
        page=page,
        per_page=per_page,
        role=role,
        dealer_id=dealer_id,
        is_active=is_active,
        search=search
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    """
    user_controller = UserController(db)
    return user_controller.get_user_by_id(user_id, current_user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user information
    """
    user_controller = UserController(db)
    return user_controller.update_user(user_id, user_data, current_user)


@router.delete("/{user_id}")
def delete_user(
    user_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (Super Admin only)
    """
    user_controller = UserController(db)
    return user_controller.delete_user(user_id, current_user)


@router.post("/dealer-admin", response_model=UserResponse, status_code=201)
def create_dealer_admin(
    user_data: DealerAdminRegistration,
    db: Session = Depends(get_db)
):
    """
    Create a dealer admin user (used during dealer registration)
    This endpoint is called by the backend API during dealer registration
    """
    user_controller = UserController(db)
    return user_controller.create_dealer_admin(user_data)
