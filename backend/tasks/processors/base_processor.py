"""
Base processor class for common data fetching functionality
"""
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Dict, Any, Optional
import logging

from database import SessionLocal, Dealer, FetchLog

logger = logging.getLogger(__name__)


class BaseDataProcessor(ABC):
    """Base class for all data processors"""
    
    def __init__(self, fetch_type: str):
        self.fetch_type = fetch_type
        self.logger = logger
    
    def get_dealer_info(self, db, dealer_id: str) -> Dealer:
        """Get dealer information and validate"""
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise ValueError(f"Dealer {dealer_id} not found")
        
        if not dealer.is_active:
            self.logger.info(f"Dealer {dealer_id} is inactive, skipping {self.fetch_type} fetch")
            raise ValueError(f"Dealer {dealer_id} is inactive")
        
        return dealer
    
    def set_default_time_range(self, from_time: Optional[str], to_time: Optional[str]) -> tuple[str, str]:
        """Set default time range if not provided"""
        if not from_time or not to_time:
            today = date.today()
            from_time = f"{today} 00:00:00"
            to_time = f"{today} 23:59:59"
        return from_time, to_time
    
    def validate_api_response(self, api_data: Dict[str, Any]) -> None:
        """Validate API response status"""
        if api_data.get("status") != 1:
            raise ValueError(f"{self.fetch_type} API returned error: {api_data.get('message', 'Unknown error')}")
    
    def ensure_list_data(self, data: Any) -> list:
        """Ensure data is a list for iteration"""
        if data is None:
            return []
        if not isinstance(data, list):
            return []
        return data
    
    def log_fetch_result(self, db, dealer_id: str, status: str, records_processed: int, 
                        duration: int, start_time: datetime, error_message: str = None) -> None:
        """Log fetch result to database"""
        fetch_log = FetchLog(
            dealer_id=dealer_id,
            fetch_type=self.fetch_type,
            status=status,
            records_fetched=records_processed,
            error_message=error_message,
            fetch_duration_seconds=duration,
            started_at=start_time,
            completed_at=datetime.utcnow()
        )
        db.add(fetch_log)
        db.commit()
    
    @abstractmethod
    def fetch_api_data(self, dealer: Dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch data from API - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process API records and save to database - must be implemented by subclasses"""
        pass
    
    def execute(self, dealer_id: str, from_time: str = None, to_time: str = None, **kwargs) -> Dict[str, Any]:
        """Main execution method - template pattern"""
        db = SessionLocal()
        start_time = datetime.utcnow()
        
        try:
            # Get dealer information
            dealer = self.get_dealer_info(db, dealer_id)
            
            # Set default time range
            from_time, to_time = self.set_default_time_range(from_time, to_time)
            
            # Fetch API data
            api_data = self.fetch_api_data(dealer, from_time, to_time, **kwargs)
            
            # Validate response
            self.validate_api_response(api_data)
            
            # Process records
            records_processed = self.process_records(db, dealer_id, api_data)
            
            # Commit all changes
            db.commit()
            
            # Log successful fetch
            duration = int((datetime.utcnow() - start_time).total_seconds())
            self.log_fetch_result(db, dealer_id, "success", records_processed, duration, start_time)
            
            self.logger.info(f"Successfully fetched {records_processed} {self.fetch_type} records for dealer {dealer_id}")
            
            return {
                "status": "success",
                "dealer_id": dealer_id,
                "records_processed": records_processed,
                "duration_seconds": duration
            }
            
        except Exception as e:
            # Log failed fetch
            duration = int((datetime.utcnow() - start_time).total_seconds())
            self.log_fetch_result(db, dealer_id, "failed", 0, duration, start_time, str(e))
            
            self.logger.error(f"Failed to fetch {self.fetch_type} data for dealer {dealer_id}: {e}")
            raise
            
        finally:
            db.close()
