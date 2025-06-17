"""
Pydantic schemas for user-related operations
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: Optional[str] = None
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.DEALER_USER
    dealer_id: Optional[str] = Field(None, max_length=10)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v
    
    @validator('dealer_id')
    def validate_dealer_id(cls, v, values):
        """Validate dealer_id requirements based on role"""
        role = values.get('role')
        if role == UserRole.DEALER_ADMIN and not v:
            raise ValueError('dealer_id is required for DEALER_ADMIN role')
        if role == UserRole.SUPER_ADMIN and v:
            raise ValueError('dealer_id should not be set for SUPER_ADMIN role')
        if role == UserRole.DEALER_USER and v:
            raise ValueError('dealer_id should not be set for DEALER_USER role (use users_dealer table instead)')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    dealer_id: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    username: Optional[str]
    full_name: str
    role: UserRole
    dealer_id: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class UserListResponse(BaseModel):
    """Schema for user list response"""
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int


# UserDealer schemas
class UserDealerBase(BaseModel):
    """Base user dealer schema"""
    dealer_id: str = Field(..., max_length=10)


class UserDealerCreate(UserDealerBase):
    """Schema for creating a new user dealer relationship"""
    user_id: str


class UserDealerResponse(BaseModel):
    """Schema for user dealer response"""
    id: str
    user_id: str
    dealer_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDealerListResponse(BaseModel):
    """Schema for user dealer list response"""
    user_dealers: list[UserDealerResponse]
    total: int
