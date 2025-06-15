"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.schemas.user import (
    UserLogin, TokenResponse, RefreshTokenRequest, 
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
    UserResponse
)
from app.controllers.auth_controller import AuthController
from app.dependencies import get_db, get_current_user
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access and refresh tokens
    """
    auth_controller = AuthController(db)
    return auth_controller.login(login_data)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_controller = AuthController(db)
    return auth_controller.refresh_token(refresh_request)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return UserResponse.from_orm(current_user)


@router.post("/password-reset/request")
def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset email
    """
    auth_controller = AuthController(db)
    return auth_controller.request_password_reset(reset_request)


@router.post("/password-reset/confirm")
def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token
    """
    auth_controller = AuthController(db)
    return auth_controller.confirm_password_reset(reset_confirm)


@router.post("/change-password")
def change_password(
    change_request: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    auth_controller = AuthController(db)
    return auth_controller.change_password(current_user, change_request)


@router.post("/logout")
def logout():
    """
    Logout user (client should discard tokens)
    """
    return {"message": "Successfully logged out"}
