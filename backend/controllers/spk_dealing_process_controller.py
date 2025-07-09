"""
SPK Dealing Process Controller

This module provides REST API endpoints for SPK dealing process data management.
It handles CRUD operations and data retrieval for SPK dealing process information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, SPKDealingProcessData, SPKDealingProcessUnit, SPKDealingProcessFamilyMember, Dealer
from tasks.processors.spk_dealing_process_processor import SPKDealingProcessDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/spk_dealing_process", tags=["spk_dealing_process"])


@router.get("/")
async def get_spk_dealing_process_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in SPK ID, prospect ID, customer name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get SPK dealing process data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(SPKDealingProcessData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(SPKDealingProcessData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    SPKDealingProcessData.id_spk.ilike(search_term),
                    SPKDealingProcessData.id_prospect.ilike(search_term),
                    SPKDealingProcessData.nama_customer.ilike(search_term),
                    SPKDealingProcessData.no_ktp.ilike(search_term),
                    SPKDealingProcessData.email.ilike(search_term)
                )
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        spk_data = query.order_by(desc(SPKDealingProcessData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for spk in spk_data:
            spk_dict = {
                "id": str(spk.id),
                "dealer_id": spk.dealer_id,
                "dealer_name": spk.dealer.dealer_name,
                "id_spk": spk.id_spk,
                "id_prospect": spk.id_prospect,
                "nama_customer": spk.nama_customer,
                "no_ktp": spk.no_ktp,
                "alamat": spk.alamat,
                "no_kontak": spk.no_kontak,
                "email": spk.email,
                "id_sales_people": spk.id_sales_people,
                "tanggal_pesanan": spk.tanggal_pesanan,
                "status_spk": spk.status_spk,
                "created_time": spk.created_time,
                "modified_time": spk.modified_time,
                "fetched_at": spk.fetched_at.isoformat() if spk.fetched_at else None
            }
            result.append(spk_dict)
        
        return {
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching SPK dealing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.get("/summary")
async def get_spk_dealing_process_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get SPK dealing process summary statistics"""
    try:
        processor = SPKDealingProcessDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting SPK dealing process summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_spk_dealing_process_data(db: Session = Depends(get_db)):
    """Get list of dealers that have SPK dealing process data"""
    try:
        dealers = db.query(Dealer).join(SPKDealingProcessData).distinct().all()
        
        result = [
            {
                "dealer_id": dealer.dealer_id,
                "dealer_name": dealer.dealer_name
            }
            for dealer in dealers
        ]
        
        return {
            "success": True,
            "dealers": result
        }
        
    except Exception as e:
        logger.error(f"Error fetching dealers with SPK dealing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_spk_dealing_process_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    id_prospect: Optional[str] = Query("", description="Prospect ID filter"),
    id_sales_people: Optional[str] = Query("", description="Sales people ID filter"),
    db: Session = Depends(get_db)
):
    """Test SPK dealing process API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = SPKDealingProcessDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            id_prospect=id_prospect,
            id_sales_people=id_sales_people
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing SPK dealing process fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_spk_dealing_process_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search SPK dealing process data across multiple fields"""
    try:
        # Base query
        query = db.query(SPKDealingProcessData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(SPKDealingProcessData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                SPKDealingProcessData.id_spk.ilike(search_term),
                SPKDealingProcessData.id_prospect.ilike(search_term),
                SPKDealingProcessData.nama_customer.ilike(search_term),
                SPKDealingProcessData.no_ktp.ilike(search_term),
                SPKDealingProcessData.email.ilike(search_term),
                SPKDealingProcessData.no_kontak.ilike(search_term)
            )
        )
        
        spk_data = query.limit(limit).all()
        
        result = [
            {
                "id": str(spk.id),
                "dealer_id": spk.dealer_id,
                "dealer_name": spk.dealer.dealer_name,
                "id_spk": spk.id_spk,
                "id_prospect": spk.id_prospect,
                "nama_customer": spk.nama_customer,
                "no_ktp": spk.no_ktp,
                "status_spk": spk.status_spk
            }
            for spk in spk_data
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching SPK dealing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching data: {str(e)}")


@router.get("/{spk_id}/details")
async def get_spk_dealing_process_details(
    spk_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed SPK dealing process data including units and family members"""
    try:
        # Get SPK data
        spk = db.query(SPKDealingProcessData).filter(SPKDealingProcessData.id == spk_id).first()
        if not spk:
            raise HTTPException(status_code=404, detail=f"SPK dealing process data {spk_id} not found")
        
        # Get units
        units = db.query(SPKDealingProcessUnit).filter(
            SPKDealingProcessUnit.spk_dealing_process_data_id == spk.id
        ).all()
        
        # Get family members
        family_members = db.query(SPKDealingProcessFamilyMember).filter(
            SPKDealingProcessFamilyMember.spk_dealing_process_data_id == spk.id
        ).all()
        
        result = {
            "id": str(spk.id),
            "dealer_id": spk.dealer_id,
            "dealer_name": spk.dealer.dealer_name,
            "id_spk": spk.id_spk,
            "id_prospect": spk.id_prospect,
            "nama_customer": spk.nama_customer,
            "no_ktp": spk.no_ktp,
            "alamat": spk.alamat,
            "email": spk.email,
            "no_kontak": spk.no_kontak,
            "status_spk": spk.status_spk,
            "tanggal_pesanan": spk.tanggal_pesanan,
            "units": [
                {
                    "id": str(unit.id),
                    "kode_tipe_unit": unit.kode_tipe_unit,
                    "kode_warna": unit.kode_warna,
                    "quantity": unit.quantity,
                    "harga_jual": float(unit.harga_jual) if unit.harga_jual else None,
                    "diskon": float(unit.diskon) if unit.diskon else None,
                    "tipe_pembayaran": unit.tipe_pembayaran,
                    "tanggal_pengiriman": unit.tanggal_pengiriman
                }
                for unit in units
            ],
            "family_members": [
                {
                    "id": str(member.id),
                    "anggota_kk": member.anggota_kk,
                    "created_time": member.created_time,
                    "modified_time": member.modified_time
                }
                for member in family_members
            ]
        }
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error fetching SPK dealing process details: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching details: {str(e)}")
