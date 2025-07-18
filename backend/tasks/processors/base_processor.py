"""
Base processor class for common data fetching functionality
"""
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Dict, Any, Optional
import logging
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
import psycopg2.errors
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError

from database import SessionLocal, Dealer, FetchLog

logger = logging.getLogger(__name__)


class BaseDataProcessor(ABC):
    """Base class for all data processors"""
    
    def __init__(self, fetch_type: str):
        self.fetch_type = fetch_type
        self.logger = logger
    
    def _is_transaction_aborted(self, db) -> bool:
        """Check if PostgreSQL transaction is in aborted state"""
        try:
            # Try to execute a simple query to test transaction state
            db.execute(text("SELECT 1"))
            return False
        except (psycopg2.errors.InFailedSqlTransaction, DatabaseError) as e:
            self.logger.debug(f"Transaction is in aborted state: {e}")
            return True
        except Exception:
            # Other errors don't necessarily mean aborted transaction
            return False
    
    def _safe_rollback(self, db) -> bool:
        """Safely rollback transaction with PostgreSQL error handling"""
        try:
            if self._is_transaction_aborted(db):
                self.logger.info("Transaction already aborted, forcing rollback")
            db.rollback()
            self.logger.info("Database transaction rolled back successfully")
            return True
        except Exception as rollback_error:
            self.logger.error(f"Error during rollback: {rollback_error}")
            try:
                # Force close the session if rollback fails
                db.close()
                self.logger.info("Session closed after rollback failure")
                return False
            except Exception:
                pass
            return False
    
    def get_dealer_info(self, db, dealer_id: str) -> Dealer:
        """Get dealer information and validate with PostgreSQL error handling"""
        try:
            # Check if transaction is already aborted
            if self._is_transaction_aborted(db):
                self.logger.warning("Transaction aborted before dealer lookup, attempting recovery")
                self._safe_rollback(db)

            dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
            if not dealer:
                raise ValueError(f"Dealer {dealer_id} not found")

            if not dealer.is_active:
                self.logger.info(f"Dealer {dealer_id} is inactive, skipping {self.fetch_type} fetch")
                raise ValueError(f"Dealer {dealer_id} is inactive")

            return dealer
            
        except (psycopg2.errors.InFailedSqlTransaction, DatabaseError) as pg_error:
            self.logger.error(f"PostgreSQL transaction error getting dealer info for {dealer_id}: {pg_error}")
            # Force rollback for PostgreSQL transaction errors
            if self._safe_rollback(db):
                try:
                    # Retry after rollback
                    dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
                    if not dealer:
                        raise ValueError(f"Dealer {dealer_id} not found")
                    if not dealer.is_active:
                        raise ValueError(f"Dealer {dealer_id} is inactive")
                    return dealer
                except Exception as retry_error:
                    self.logger.error(f"Retry failed after PostgreSQL error for dealer {dealer_id}: {retry_error}")
                    raise ValueError(f"Failed to get dealer info after PostgreSQL error for {dealer_id}: {pg_error}")
            else:
                raise ValueError(f"Failed to recover from PostgreSQL error for dealer {dealer_id}: {pg_error}")
                
        except Exception as e:
            self.logger.error(f"General error getting dealer info for {dealer_id}: {e}")
            # Try to rollback and retry for other errors
            if self._safe_rollback(db):
                try:
                    dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
                    if not dealer:
                        raise ValueError(f"Dealer {dealer_id} not found")
                    if not dealer.is_active:
                        raise ValueError(f"Dealer {dealer_id} is inactive")
                    return dealer
                except Exception as retry_error:
                    self.logger.error(f"Retry failed for dealer {dealer_id}: {retry_error}")
                    raise ValueError(f"Failed to get dealer info for {dealer_id}: {e}")
            else:
                raise ValueError(f"Failed to get dealer info for {dealer_id}: {e}")
    
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
        """Log fetch result to database with transaction safety"""
        try:
            # Check if transaction is aborted before logging
            if self._is_transaction_aborted(db):
                self.logger.warning("Transaction aborted before logging fetch result")
                if not self._safe_rollback(db):
                    raise DatabaseError("Failed to recover from aborted transaction for logging")
            
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
            
        except (psycopg2.errors.InFailedSqlTransaction, DatabaseError) as pg_error:
            self.logger.error(f"PostgreSQL error logging fetch result: {pg_error}")
            # Try to recover and log again
            if self._safe_rollback(db):
                try:
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
                except Exception as retry_error:
                    self.logger.error(f"Failed to log fetch result after recovery: {retry_error}")
                    raise
            else:
                raise
                
        except Exception as e:
            self.logger.error(f"Error logging fetch result: {e}")
            raise

    def bulk_upsert(self, db, model_class, records: list, conflict_columns: list, batch_size: int = 1000):
        """Perform bulk upsert operation using PostgreSQL ON CONFLICT with enhanced error handling"""
        if not records:
            return 0

        total_processed = 0

        # Process records in batches to manage memory
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            try:
                # Check transaction state before batch operation
                if self._is_transaction_aborted(db):
                    self.logger.warning("Transaction aborted before bulk upsert, attempting recovery")
                    if not self._safe_rollback(db):
                        raise DatabaseError("Failed to recover from aborted transaction")

                # Use PostgreSQL's INSERT ... ON CONFLICT ... DO UPDATE
                stmt = insert(model_class).values(batch)

                # Create update dict for all columns except conflict columns
                update_dict = {
                    col.name: stmt.excluded[col.name]
                    for col in model_class.__table__.columns
                    if col.name not in conflict_columns and col.name != 'id'
                }

                # Add fetched_at update
                if hasattr(model_class, 'fetched_at'):
                    update_dict['fetched_at'] = datetime.utcnow()

                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_=update_dict
                )

                result = db.execute(stmt)
                total_processed += len(batch)

                self.logger.debug(f"Processed batch of {len(batch)} records for {model_class.__name__}")

            except (psycopg2.errors.InFailedSqlTransaction, psycopg2.errors.IntegrityError) as pg_error:
                self.logger.error(f"PostgreSQL error in bulk upsert batch: {pg_error}")
                # Force rollback and retry with individual inserts
                if self._safe_rollback(db):
                    total_processed += self._fallback_individual_inserts(
                        db, model_class, batch, conflict_columns, update_dict
                    )
                else:
                    self.logger.error(f"Failed to recover from PostgreSQL error in batch for {model_class.__name__}")
                    raise
                    
            except Exception as e:
                self.logger.error(f"General error in bulk upsert batch: {e}")
                # Try individual inserts for this batch as fallback
                total_processed += self._fallback_individual_inserts(
                    db, model_class, batch, conflict_columns, None
                )

        return total_processed
    
    def _fallback_individual_inserts(self, db, model_class, batch: list, conflict_columns: list, update_dict: dict = None):
        """Fallback to individual inserts when batch operations fail"""
        processed = 0
        
        for record in batch:
            try:
                # Check transaction state before each insert
                if self._is_transaction_aborted(db):
                    if not self._safe_rollback(db):
                        self.logger.error("Failed to recover transaction state for individual insert")
                        continue
                
                stmt = insert(model_class).values(record)
                
                # Recreate update_dict if not provided
                if update_dict is None:
                    update_dict = {
                        col.name: stmt.excluded[col.name]
                        for col in model_class.__table__.columns
                        if col.name not in conflict_columns and col.name != 'id'
                    }
                    if hasattr(model_class, 'fetched_at'):
                        update_dict['fetched_at'] = datetime.utcnow()
                
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_=update_dict
                )
                db.execute(stmt)
                processed += 1
                
            except (psycopg2.errors.InFailedSqlTransaction, psycopg2.errors.IntegrityError) as pg_error:
                self.logger.error(f"PostgreSQL error in individual insert: {pg_error}")
                # Try to recover transaction state
                self._safe_rollback(db)
                continue
                
            except Exception as individual_error:
                self.logger.error(f"Failed to insert individual record: {individual_error}")
                continue
                
        return processed

    def process_in_chunks(self, data: list, chunk_size: int = 100):
        """Generator to process data in chunks for memory efficiency"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def safe_numeric(self, value, default=None):
        """Convert value to numeric, return None for empty strings or invalid values"""
        if value is None or value == '' or value == 'null':
            return default
        try:
            return float(value) if '.' in str(value) else int(value)
        except (ValueError, TypeError):
            return default

    def safe_int(self, value, default=None):
        """Convert value to integer, return None for empty strings or invalid values"""
        if value is None or value == '' or value == 'null':
            return default
        try:
            return int(float(value))  # Handle string floats like "1.0"
        except (ValueError, TypeError):
            return default

    def safe_string(self, value, default=None):
        """Convert value to string, return None for empty strings"""
        if value is None or value == '' or value == 'null':
            return default
        return str(value)
    
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
        db = None
        start_time = datetime.utcnow()

        try:
            # Create database session with retry logic
            db = self._create_db_session()

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

        except (psycopg2.errors.InFailedSqlTransaction, psycopg2.errors.IntegrityError, DatabaseError) as pg_error:
            # PostgreSQL-specific error handling with potential retry
            self.logger.error(f"PostgreSQL error in execution for dealer {dealer_id}: {pg_error}")
            
            if db:
                session_recovered = self._safe_rollback(db)
                if not session_recovered:
                    try:
                        db.close()
                        db = None
                    except Exception:
                        pass

            # Log failed fetch with a new session
            duration = int((datetime.utcnow() - start_time).total_seconds())
            self._log_error_safely(dealer_id, duration, start_time, str(pg_error))

            self.logger.error(f"Failed to fetch {self.fetch_type} data for dealer {dealer_id} due to PostgreSQL error: {pg_error}")
            raise
            
        except Exception as e:
            # General error handling
            if db:
                session_recovered = self._safe_rollback(db)
                if not session_recovered:
                    try:
                        db.close()
                        db = None
                    except Exception:
                        pass

            # Log failed fetch with a new session if needed
            duration = int((datetime.utcnow() - start_time).total_seconds())
            self._log_error_safely(dealer_id, duration, start_time, str(e))

            self.logger.error(f"Failed to fetch {self.fetch_type} data for dealer {dealer_id}: {e}")
            raise

        finally:
            if db:
                try:
                    db.close()
                    self.logger.debug("Database session closed successfully")
                except Exception as close_error:
                    self.logger.error(f"Error closing database session: {close_error}")

    def _create_db_session(self):
        """Create database session with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db = SessionLocal()
                # Test the connection with a simple query
                result = db.execute(text("SELECT 1"))
                result.fetchone()  # Ensure the query actually executes
                return db
            except Exception as e:
                self.logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                try:
                    if 'db' in locals():
                        db.close()
                except Exception:
                    pass
                if attempt == max_retries - 1:
                    raise
                # Wait before retry
                import time
                time.sleep(1)

    def _log_error_safely(self, dealer_id: str, duration: int, start_time: datetime, error_message: str):
        """Log error with a separate database session and PostgreSQL error handling"""
        error_db = None
        max_retries = 2

        for attempt in range(max_retries):
            try:
                error_db = SessionLocal()
                # Test connection first
                error_db.execute(text("SELECT 1")).fetchone()

                # Log the error using the enhanced log_fetch_result method
                self.log_fetch_result(error_db, dealer_id, "failed", 0, duration, start_time, error_message)
                break  # Success, exit retry loop

            except (psycopg2.errors.InFailedSqlTransaction, DatabaseError) as pg_error:
                self.logger.error(f"PostgreSQL error logging to database (attempt {attempt + 1}): {pg_error}")
                if error_db:
                    try:
                        self._safe_rollback(error_db)
                        error_db.close()
                    except Exception:
                        pass
                    error_db = None

                if attempt == max_retries - 1:
                    self.logger.error(f"Giving up on error logging after {max_retries} attempts due to PostgreSQL errors")
                else:
                    import time
                    time.sleep(0.5)  # Brief wait before retry
                    
            except Exception as log_error:
                self.logger.error(f"General error logging to database (attempt {attempt + 1}): {log_error}")
                if error_db:
                    try:
                        error_db.rollback()
                        error_db.close()
                    except Exception:
                        pass
                    error_db = None

                if attempt == max_retries - 1:
                    self.logger.error(f"Giving up on error logging after {max_retries} attempts")
                else:
                    import time
                    time.sleep(0.5)  # Brief wait before retry
            finally:
                if error_db and attempt == max_retries - 1:
                    try:
                        error_db.close()
                    except Exception:
                        pass
