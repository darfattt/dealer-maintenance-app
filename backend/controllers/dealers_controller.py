"""
Dealers controller for dealer management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db, Dealer
from models.schemas import DealerCreate, DealerUpdate, DealerResponse
from .base_controller import BaseController

router = APIRouter(prefix="/dealers", tags=["dealers"])


@router.post("/", response_model=DealerResponse)
async def create_dealer(dealer: DealerCreate, db: Session = Depends(get_db)):
    """Create a new dealer"""
    # Check if dealer already exists
    existing_dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer.dealer_id).first()
    if existing_dealer:
        raise BaseController.handle_already_exists("Dealer", dealer.dealer_id)

    db_dealer = Dealer(**dealer.dict())
    db.add(db_dealer)
    db.commit()
    db.refresh(db_dealer)
    
    BaseController.convert_uuid_to_string(db_dealer)
    BaseController.log_operation("CREATE_DEALER", f"Created dealer {dealer.dealer_id}")
    
    return db_dealer


@router.get("/", response_model=List[DealerResponse])
async def get_dealers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all dealers with pagination"""
    dealers = db.query(Dealer).offset(skip).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(dealers)
    
    BaseController.log_operation("GET_DEALERS", f"Retrieved {len(dealers)} dealers")
    return dealers


@router.get("/{dealer_id}", response_model=DealerResponse)
async def get_dealer(dealer_id: str, db: Session = Depends(get_db)):
    """Get a specific dealer by ID"""
    dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not dealer:
        raise BaseController.handle_not_found("Dealer", dealer_id)
    
    BaseController.convert_uuid_to_string(dealer)
    BaseController.log_operation("GET_DEALER", f"Retrieved dealer {dealer_id}")
    
    return dealer


@router.put("/{dealer_id}", response_model=DealerResponse)
async def update_dealer(dealer_id: str, dealer_update: DealerUpdate, db: Session = Depends(get_db)):
    """Update a dealer"""
    # Find existing dealer
    db_dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not db_dealer:
        raise BaseController.handle_not_found("Dealer", dealer_id)

    # Update dealer fields
    update_data = dealer_update.dict(exclude_unset=True)
    BaseController.update_model_fields(db_dealer, update_data)

    db.commit()
    db.refresh(db_dealer)
    
    BaseController.convert_uuid_to_string(db_dealer)
    BaseController.log_operation("UPDATE_DEALER", f"Updated dealer {dealer_id}")
    
    return db_dealer


@router.delete("/{dealer_id}")
async def delete_dealer(dealer_id: str, db: Session = Depends(get_db)):
    """Delete a dealer"""
    db_dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not db_dealer:
        raise BaseController.handle_not_found("Dealer", dealer_id)

    db.delete(db_dealer)
    db.commit()
    
    BaseController.log_operation("DELETE_DEALER", f"Deleted dealer {dealer_id}")
    return {"message": f"Dealer {dealer_id} deleted successfully"}
