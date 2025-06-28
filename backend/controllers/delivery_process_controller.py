"""
Delivery Process Controller

This module provides REST API endpoints for delivery process data management.
It handles CRUD operations and data retrieval for delivery process information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, DeliveryProcessData, DeliveryProcessDetail, Dealer
from tasks.processors.delivery_process_processor import DeliveryProcessDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/delivery_process", tags=["delivery_process"])


@router.get("/")
async def get_delivery_process_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in delivery document ID, SO number, SPK ID, customer ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get delivery process data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(DeliveryProcessData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(DeliveryProcessData.dealer_id == dealer_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    DeliveryProcessData.delivery_document_id.ilike(search_term),
                    DeliveryProcessData.id_driver.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        delivery_data = query.order_by(desc(DeliveryProcessData.fetched_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for delivery in delivery_data:
            # Get delivery details
            details = db.query(DeliveryProcessDetail).filter(
                DeliveryProcessDetail.delivery_process_data_id == delivery.id
            ).all()
            
            delivery_dict = {
                "id": str(delivery.id),
                "dealer_id": delivery.dealer_id,
                "dealer_name": delivery.dealer.dealer_name,
                "delivery_document_id": delivery.delivery_document_id,
                "tanggal_pengiriman": delivery.tanggal_pengiriman,
                "id_driver": delivery.id_driver,
                "status_delivery_document": delivery.status_delivery_document,
                "created_time": delivery.created_time,
                "modified_time": delivery.modified_time,
                "fetched_at": delivery.fetched_at.isoformat() if delivery.fetched_at else None,
                "details": [
                    {
                        "id": str(detail.id),
                        "no_so": detail.no_so,
                        "id_spk": detail.id_spk,
                        "no_mesin": detail.no_mesin,
                        "no_rangka": detail.no_rangka,
                        "id_customer": detail.id_customer,
                        "waktu_pengiriman": detail.waktu_pengiriman,
                        "checklist_kelengkapan": detail.checklist_kelengkapan,
                        "lokasi_pengiriman": detail.lokasi_pengiriman,
                        "latitude": detail.latitude,
                        "longitude": detail.longitude,
                        "nama_penerima": detail.nama_penerima,
                        "no_kontak_penerima": detail.no_kontak_penerima,
                        "created_time": detail.created_time,
                        "modified_time": detail.modified_time
                    }
                    for detail in details
                ]
            }
            result.append(delivery_dict)
        
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
        logger.error(f"Error fetching delivery process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching delivery process data: {str(e)}")


@router.get("/summary")
async def get_delivery_process_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get delivery process summary statistics"""
    try:
        processor = DeliveryProcessDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting delivery process summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_delivery_process_data(db: Session = Depends(get_db)):
    """Get list of dealers that have delivery process data"""
    try:
        dealers = db.query(Dealer).join(DeliveryProcessData).distinct().all()
        
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
        logger.error(f"Error fetching dealers with delivery process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_delivery_process_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    delivery_document_id: Optional[str] = Query("", description="Delivery document ID filter"),
    id_spk: Optional[str] = Query("", description="SPK ID filter"),
    id_customer: Optional[str] = Query("", description="Customer ID filter"),
    db: Session = Depends(get_db)
):
    """Test delivery process API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")
        
        # Test fetch
        processor = DeliveryProcessDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            delivery_document_id=delivery_document_id,
            id_spk=id_spk,
            id_customer=id_customer
        )
        
        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error testing delivery process fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_delivery_process_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search delivery process data across multiple fields"""
    try:
        # Base query
        query = db.query(DeliveryProcessData).join(Dealer)
        
        # Apply dealer filter
        if dealer_id:
            query = query.filter(DeliveryProcessData.dealer_id == dealer_id)
        
        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                DeliveryProcessData.delivery_document_id.ilike(search_term),
                DeliveryProcessData.id_driver.ilike(search_term)
            )
        )
        
        # Also search in delivery details
        detail_query = db.query(DeliveryProcessDetail).filter(
            or_(
                DeliveryProcessDetail.no_so.ilike(search_term),
                DeliveryProcessDetail.id_spk.ilike(search_term),
                DeliveryProcessDetail.no_mesin.ilike(search_term),
                DeliveryProcessDetail.no_rangka.ilike(search_term),
                DeliveryProcessDetail.id_customer.ilike(search_term),
                DeliveryProcessDetail.nama_penerima.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Get delivery IDs from detail search
        delivery_ids_from_details = [detail.delivery_process_data_id for detail in detail_query]
        
        # Combine results
        if delivery_ids_from_details:
            query = query.filter(
                or_(
                    DeliveryProcessData.id.in_(delivery_ids_from_details),
                    # Original delivery-level search conditions already applied
                )
            )
        
        deliveries = query.limit(limit).all()
        
        result = [
            {
                "id": str(delivery.id),
                "dealer_id": delivery.dealer_id,
                "dealer_name": delivery.dealer.dealer_name,
                "delivery_document_id": delivery.delivery_document_id,
                "tanggal_pengiriman": delivery.tanggal_pengiriman,
                "id_driver": delivery.id_driver,
                "status_delivery_document": delivery.status_delivery_document
            }
            for delivery in deliveries
        ]
        
        return {
            "success": True,
            "results": result,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error searching delivery process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")


@router.get("/dashboard/status-counts")
async def get_delivery_process_status_counts(
    response: Response,
    dealer_id: str = Query(..., description="Dealer ID to filter by"),
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get delivery process data count grouped by status_delivery_document for dashboard visualization

    This endpoint returns statistics about delivery process data grouped by delivery document status
    for a specific dealer within a date range. The data is suitable for delivery process widgets.

    Args:
        dealer_id: The dealer ID to filter records
        date_from: Start date for filtering (YYYY-MM-DD format)
        date_to: End date for filtering (YYYY-MM-DD format)

    Returns:
        JSON response with delivery status counts and total records

    Example:
        GET /delivery_process/dashboard/status-counts?dealer_id=12284&date_from=2024-01-01&date_to=2024-12-31
    """
    try:
        from datetime import datetime

        # Set cache control headers to prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        # Validate date format
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format."
            )

        # Validate date range
        if date_from > date_to:
            raise HTTPException(
                status_code=400,
                detail="date_from must be less than or equal to date_to"
            )

        # Status mapping for delivery process
        status_mapping = {
            '1': 'Ready',
            '2': 'In Progress',
            '3': 'Back to Dealer',
            '4': 'Completed'
        }

        # Query to get counts grouped by status_delivery_document
        # Convert VARCHAR tanggal_pengiriman (DD/MM/YYYY format) to DATE for proper filtering
        query = db.query(
            DeliveryProcessData.status_delivery_document,
            func.count(DeliveryProcessData.id).label('count')
        ).filter(
            DeliveryProcessData.dealer_id == dealer_id,
            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= date_from,
            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= date_to
        ).group_by(DeliveryProcessData.status_delivery_document)

        result = query.all()

        logger.info(f"Found {len(result)} different delivery statuses for dealer {dealer_id}")

        # Get total records
        total_records = db.query(func.count(DeliveryProcessData.id)).filter(
            DeliveryProcessData.dealer_id == dealer_id,
            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') >= date_from,
            func.to_date(DeliveryProcessData.tanggal_pengiriman, 'DD/MM/YYYY') <= date_to
        ).scalar() or 0

        # Convert to response format with status labels
        status_items = []
        for row in result:
            status_label = status_mapping.get(row.status_delivery_document, row.status_delivery_document or 'Unknown')

            status_items.append({
                "status_delivery_document": row.status_delivery_document,
                "status_label": status_label,
                "count": row.count
            })

        return {
            "success": True,
            "message": "Delivery process status statistics retrieved successfully",
            "data": status_items,
            "total_records": total_records
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting delivery process status statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
