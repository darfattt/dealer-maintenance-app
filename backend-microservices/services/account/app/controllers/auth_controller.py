"""
Authentication controller for handling auth-related operations
"""

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserLogin, TokenResponse, RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest
from app.repositories.user_repository import UserRepository
import sys
import os

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils.auth import verify_password, create_access_token, create_refresh_token, decode_token, hash_password
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthController:
    """Controller for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def login(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and return tokens
        
        Args:
            login_data: User login credentials
            
        Returns:
            Token response with access and refresh tokens
            
        Raises:
            HTTPException: If authentication fails
        """
        # Get user by email
        user = self.user_repo.get_user_by_email(login_data.email)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        self.user_repo.update_last_login(user.id)
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "dealer_id": user.dealer_id
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        logger.info(f"Successful login for user: {login_data.email}")
        
        # Convert User model to UserResponse
        from app.schemas.user import UserResponse
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            dealer_id=user.dealer_id,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes
            user=user_response
        )
    
    def refresh_token(self, refresh_request: RefreshTokenRequest) -> TokenResponse:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_request: Refresh token request
            
        Returns:
            New token response
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = self.user_repo.get_user_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "dealer_id": user.dealer_id
        }
        
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        # Convert User model to UserResponse
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            dealer_id=user.dealer_id,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes
            user=user_response
        )
    
    def get_current_user(self, token: str) -> User:
        """
        Get current user from access token
        
        Args:
            token: JWT access token
            
        Returns:
            Current user
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Decode token
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        user = self.user_repo.get_user_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
    
    def request_password_reset(self, reset_request: PasswordResetRequest) -> dict:
        """
        Request password reset
        
        Args:
            reset_request: Password reset request
            
        Returns:
            Success message
        """
        user = self.user_repo.get_user_by_email(reset_request.email)
        if not user:
            # Don't reveal if email exists or not
            logger.warning(f"Password reset requested for non-existent email: {reset_request.email}")
            return {"message": "If the email exists, a password reset link has been sent"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        # Save reset token
        self.user_repo.set_password_reset_token(user.id, reset_token, expires_at)
        
        # TODO: Send email with reset link
        # For now, just log the token (in production, send email)
        logger.info(f"Password reset token for {reset_request.email}: {reset_token}")
        
        return {"message": "If the email exists, a password reset link has been sent"}
    
    def confirm_password_reset(self, reset_confirm: PasswordResetConfirm) -> dict:
        """
        Confirm password reset with token
        
        Args:
            reset_confirm: Password reset confirmation
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        user = self.user_repo.get_user_by_reset_token(reset_confirm.token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        self.user_repo.update_password(user.id, reset_confirm.new_password)
        
        # Clear reset token
        self.user_repo.clear_password_reset_token(user.id)
        
        logger.info(f"Password reset completed for user: {user.email}")
        
        return {"message": "Password has been reset successfully"}
    
    def change_password(self, user: User, change_request: ChangePasswordRequest) -> dict:
        """
        Change user password
        
        Args:
            user: Current user
            change_request: Password change request
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(change_request.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        self.user_repo.update_password(user.id, change_request.new_password)
        
        logger.info(f"Password changed for user: {user.email}")
        
        return {"message": "Password has been changed successfully"}
