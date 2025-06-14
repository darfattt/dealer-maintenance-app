"""
Unpaid HLO Controller

This module provides REST API endpoints for unpaid HLO data management.
It handles CRUD operations and data retrieval for unpaid HLO information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, UnpaidHLOData, UnpaidHLOPart, Dealer
from tasks.processors.unpaid_hlo_processor import UnpaidHLODataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/unpaid_hlo", tags=["unpaid_hlo"])


@router.get("/")
async def get_unpaid_hlo_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in HLO document, work order, customer name, KTP, vehicle details"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get unpaid HLO data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(UnpaidHLOData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(UnpaidHLOData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join with parts to search in parts data
            query = query.join(UnpaidHLOPart, UnpaidHLOData.id == UnpaidHLOPart.unpaid_hlo_data_id, isouter=True)
            search_filter = or_(
                UnpaidHLOData.id_hlo_document.ilike(search_term),
                UnpaidHLOData.no_work_order.ilike(search_term),
                UnpaidHLOData.nama_customer.ilike(search_term),
                UnpaidHLOData.no_ktp.ilike(search_term),
                UnpaidHLOData.kode_tipe_unit.ilike(search_term),
                UnpaidHLOData.no_mesin.ilike(search_term),
                UnpaidHLOData.no_rangka.ilike(search_term),
                UnpaidHLOPart.parts_number.ilike(search_term)
            )
            query = query.filter(search_filter).distinct()
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        hlo_records = query.order_by(desc(UnpaidHLOData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for hlo in hlo_records:
            # Get parts for this HLO document
            parts = db.query(UnpaidHLOPart).filter(
                UnpaidHLOPart.unpaid_hlo_data_id == hlo.id
            ).all()
            
            hlo_dict = {
                "id": str(hlo.id),
                "dealer_id": hlo.dealer_id,
                "dealer_name": hlo.dealer.dealer_name,
                "id_hlo_document": hlo.id_hlo_document,
                "tanggal_pemesanan_hlo": hlo.tanggal_pemesanan_hlo,
                "no_work_order": hlo.no_work_order,
                "no_buku_claim_c2": hlo.no_buku_claim_c2,
                "no_ktp": hlo.no_ktp,
                "nama_customer": hlo.nama_customer,
                "alamat": hlo.alamat,
                "kode_propinsi": hlo.kode_propinsi,
                "kode_kota": hlo.kode_kota,
                "kode_kecamatan": hlo.kode_kecamatan,
                "kode_kelurahan": hlo.kode_kelurahan,
                "kode_pos": hlo.kode_pos,
                "no_kontak": hlo.no_kontak,
                "kode_tipe_unit": hlo.kode_tipe_unit,
                "tahun_motor": hlo.tahun_motor,
                "no_mesin": hlo.no_mesin,
                "no_rangka": hlo.no_rangka,
                "flag_numbering": hlo.flag_numbering,
                "vehicle_off_road": hlo.vehicle_off_road,
                "job_return": hlo.job_return,
                "created_time": hlo.created_time,
                "modified_time": hlo.modified_time,
                "fetched_at": hlo.fetched_at.isoformat() if hlo.fetched_at else None,
                "parts_count": len(parts),
                "parts": [
                    {
                        "id": str(part.id),
                        "parts_number": part.parts_number,
                        "kuantitas": part.kuantitas,
                        "harga_parts": float(part.harga_parts) if part.harga_parts else None,
                        "total_harga_parts": float(part.total_harga_parts) if part.total_harga_parts else None,
                        "uang_muka": float(part.uang_muka) if part.uang_muka else None,
                        "sisa_bayar": float(part.sisa_bayar) if part.sisa_bayar else None,
                        "created_time": part.created_time,
                        "modified_time": part.modified_time
                    }
                    for part in parts
                ]
            }
            result.append(hlo_dict)
        
        return {
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching unpaid HLO data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching unpaid HLO data: {str(e)}")


@router.get("/summary")
async def get_unpaid_hlo_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get unpaid HLO summary statistics"""
    try:
        processor = UnpaidHLODataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting unpaid HLO summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_unpaid_hlo_data(db: Session = Depends(get_db)):
    """Get list of dealers that have unpaid HLO data"""
    try:
        dealers = db.query(Dealer).join(UnpaidHLOData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with unpaid HLO data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_unpaid_hlo_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    no_work_order: Optional[str] = Query("", description="Work order number filter"),
    id_hlo_document: Optional[str] = Query("", description="HLO document ID filter"),
    db: Session = Depends(get_db)
):
    """Test unpaid HLO API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = UnpaidHLODataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            no_work_order=no_work_order,
            id_hlo_document=id_hlo_document
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing unpaid HLO fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_unpaid_hlo_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search unpaid HLO data across multiple fields"""
    try:
        # Base query
        query = db.query(UnpaidHLOData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(UnpaidHLOData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                UnpaidHLOData.id_hlo_document.ilike(search_term),
                UnpaidHLOData.no_work_order.ilike(search_term),
                UnpaidHLOData.nama_customer.ilike(search_term),
                UnpaidHLOData.no_ktp.ilike(search_term),
                UnpaidHLOData.kode_tipe_unit.ilike(search_term),
                UnpaidHLOData.no_mesin.ilike(search_term),
                UnpaidHLOData.no_rangka.ilike(search_term)
            )
        )
        
        hlo_documents = query.limit(limit).all()
        
        result = [
            {
                "id": str(hlo.id),
                "dealer_id": hlo.dealer_id,
                "dealer_name": hlo.dealer.dealer_name,
                "id_hlo_document": hlo.id_hlo_document,
                "no_work_order": hlo.no_work_order,
                "nama_customer": hlo.nama_customer,
                "kode_tipe_unit": hlo.kode_tipe_unit,
                "tahun_motor": hlo.tahun_motor,
                "no_mesin": hlo.no_mesin,
                "no_rangka": hlo.no_rangka
            }
            for hlo in hlo_documents
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching unpaid HLO data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
