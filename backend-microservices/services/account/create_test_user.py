#!/usr/bin/env python3
"""
Script to create a test user for testing login functionality
"""

import sys
import os
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import UserRole
from app.schemas.user import UserCreate

def create_test_user():
    """Create test user if it doesn't exist"""
    
    # Get database session
    db = next(get_db())
    user_repo = UserRepository(db)
    
    test_email = "dealer.user@example.com"
    
    try:
        # Check if user already exists
        existing_user = user_repo.get_user_by_email(test_email)
        if existing_user:
            print(f"✅ Test user {test_email} already exists")
            print(f"   ID: {existing_user.id}")
            print(f"   Role: {existing_user.role}")
            print(f"   Dealer ID: {existing_user.dealer_id}")
            print(f"   Active: {existing_user.is_active}")
            print(f"   Verified: {existing_user.is_verified}")
            return existing_user
        
        # Create test user
        print(f"🔄 Creating test user {test_email}...")
        
        user_data = UserCreate(
            email=test_email,
            username="dealer_user",
            full_name="Test Dealer User",
            password="Admin123!",  # Meets password requirements
            role=UserRole.DEALER_USER,
            dealer_id=None,  # DEALER_USER should not have dealer_id set directly
            is_active=True
        )
        
        new_user = user_repo.create_user(user_data)
        
        print(f"✅ Test user created successfully!")
        print(f"   ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Role: {new_user.role}")
        print(f"   Active: {new_user.is_active}")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Checking/Creating test user for login testing...")
    create_test_user()
    print("✅ Done!")