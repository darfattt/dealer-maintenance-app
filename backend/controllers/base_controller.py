"""
Base controller with common functionality for all controllers
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseController:
    """Base controller class with common functionality"""
    
    @staticmethod
    def convert_uuid_to_string(obj: Any) -> Any:
        """Convert UUID fields to strings for JSON serialization"""
        if hasattr(obj, 'id') and hasattr(obj.id, 'hex'):
            obj.id = str(obj.id)
        return obj
    
    @staticmethod
    def convert_list_uuids_to_strings(objects: list) -> list:
        """Convert UUIDs to strings for a list of objects"""
        for obj in objects:
            BaseController.convert_uuid_to_string(obj)
        return objects
    
    @staticmethod
    def validate_dealer_exists(db: Session, dealer_id: str, dealer_model) -> Any:
        """Validate that a dealer exists and return it"""
        dealer = db.query(dealer_model).filter(dealer_model.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail="Dealer not found")
        return dealer
    
    @staticmethod
    def handle_not_found(item_name: str, item_id: Optional[str] = None) -> HTTPException:
        """Standard not found error handler"""
        detail = f"{item_name} not found"
        if item_id:
            detail = f"{item_name} with ID {item_id} not found"
        return HTTPException(status_code=404, detail=detail)
    
    @staticmethod
    def handle_already_exists(item_name: str, identifier: Optional[str] = None) -> HTTPException:
        """Standard already exists error handler"""
        detail = f"{item_name} already exists"
        if identifier:
            detail = f"{item_name} '{identifier}' already exists"
        return HTTPException(status_code=400, detail=detail)
    
    @staticmethod
    def update_model_fields(model_instance: Any, update_data: dict) -> None:
        """Update model instance fields from dictionary"""
        for field, value in update_data.items():
            if hasattr(model_instance, field):
                setattr(model_instance, field, value)
    
    @staticmethod
    def log_operation(operation: str, details: str) -> None:
        """Log controller operations"""
        logger.info(f"{operation}: {details}")
    
    @staticmethod
    def build_query_filters(query, filters: dict):
        """Build query filters dynamically"""
        for field, value in filters.items():
            if value is not None:
                if hasattr(query.column_descriptions[0]['type'], field):
                    query = query.filter(getattr(query.column_descriptions[0]['type'], field) == value)
        return query
