"""
Shared authentication utilities for microservices
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from .logger import setup_logger

logger = setup_logger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthUtils:
    """Authentication utilities class"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password

        Note:
            Bcrypt has a 72-byte limit. Passwords are truncated to ensure compatibility.
        """
        # Truncate password to 72 bytes to comply with bcrypt limitation
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise

        Note:
            Bcrypt has a 72-byte limit. Passwords are truncated to ensure compatibility.
        """
        # Truncate password to 72 bytes to comply with bcrypt limitation
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Data to encode in token
            
        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create refresh token: {str(e)}")
            raise
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to decode token: {str(e)}")
            return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Check if token is expired
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired, False otherwise
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return True
        except:
            return True
    
    @staticmethod
    def extract_user_id(token: str) -> Optional[str]:
        """
        Extract user ID from token
        
        Args:
            token: JWT token string
            
        Returns:
            User ID or None if not found
        """
        payload = AuthUtils.decode_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    @staticmethod
    def extract_user_role(token: str) -> Optional[str]:
        """
        Extract user role from token
        
        Args:
            token: JWT token string
            
        Returns:
            User role or None if not found
        """
        payload = AuthUtils.decode_token(token)
        if payload:
            return payload.get("role")
        return None


# Convenience functions
def hash_password(password: str) -> str:
    """Hash password - convenience function"""
    return AuthUtils.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - convenience function"""
    return AuthUtils.verify_password(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token - convenience function"""
    return AuthUtils.create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create refresh token - convenience function"""
    return AuthUtils.create_refresh_token(data)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode token - convenience function"""
    return AuthUtils.decode_token(token)
