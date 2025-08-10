"""
Dealer configuration repository
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.dealer_config import DealerConfig


class DealerConfigRepository:
    """Repository for dealer configuration operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_dealer_id(self, dealer_id: str) -> Optional[DealerConfig]:
        """Get dealer configuration by dealer ID"""
        return self.db.query(DealerConfig).filter(
            DealerConfig.dealer_id == dealer_id,
            DealerConfig.is_active == True
        ).first()
    
    def get_active_dealers(self) -> List[DealerConfig]:
        """Get all active dealers"""
        return self.db.query(DealerConfig).filter(
            DealerConfig.is_active == True
        ).all()
    
    def get_dealers_with_fonnte_config(self) -> List[DealerConfig]:
        """Get all dealers with Fonnte configuration"""
        return self.db.query(DealerConfig).filter(
            DealerConfig.is_active == True,
            DealerConfig.fonnte_api_key.isnot(None),
            DealerConfig.fonnte_api_key != ""
        ).all()
    
    def get_fonnte_config(self, dealer_id: str) -> Optional[dict]:
        """Get Fonnte configuration for a dealer"""
        dealer = self.get_by_dealer_id(dealer_id)
        
        if not dealer or not dealer.has_fonnte_configuration():
            return None
        
        return {
            "api_key": dealer.fonnte_api_key,
            "api_url": dealer.fonnte_api_url or "https://api.fonnte.com/send",
            "dealer_name": dealer.dealer_name
        }
    
    def update_fonnte_config(
        self, 
        dealer_id: str, 
        fonnte_api_key: Optional[str] = None,
        fonnte_api_url: Optional[str] = None
    ) -> Optional[DealerConfig]:
        """Update Fonnte configuration for a dealer"""
        try:
            dealer = self.get_by_dealer_id(dealer_id)
            if not dealer:
                return None
            
            if fonnte_api_key is not None:
                dealer.fonnte_api_key = fonnte_api_key
            
            if fonnte_api_url is not None:
                dealer.fonnte_api_url = fonnte_api_url
            
            self.db.commit()
            self.db.refresh(dealer)
            
            return dealer
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def validate_dealer_exists(self, dealer_id: str) -> bool:
        """Validate if dealer exists and is active"""
        dealer = self.get_by_dealer_id(dealer_id)
        return dealer is not None
    
    def validate_dealer_fonnte_config(self, dealer_id: str) -> tuple[bool, Optional[str]]:
        """Validate if dealer has Fonnte configuration"""
        dealer = self.get_by_dealer_id(dealer_id)
        
        if not dealer:
            return False, "Dealer not found or inactive"
        
        if not dealer.has_fonnte_configuration():
            return False, "Dealer does not have Fonnte WhatsApp configuration"
        
        return True, None
    
    def get_dealer_stats(self, dealer_id: str) -> Optional[dict]:
        """Get dealer statistics"""
        dealer = self.get_by_dealer_id(dealer_id)
        
        if not dealer:
            return None
        
        return {
            "dealer_id": dealer.dealer_id,
            "dealer_name": dealer.dealer_name,
            "is_active": dealer.is_active,
            "has_fonnte_config": dealer.has_fonnte_configuration(),
            "created_at": dealer.created_at.isoformat() if dealer.created_at else None,
            "updated_at": dealer.updated_at.isoformat() if dealer.updated_at else None,
        }