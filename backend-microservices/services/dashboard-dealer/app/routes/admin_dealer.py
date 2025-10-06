"""
Admin dealer management routes (SYSTEM_ADMIN only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from app.controllers.admin_dealer_controller import AdminDealerController
from app.schemas.dealer import (
    DealerListResponse,
    DealerResponse,
    DealerUpdateRequest,
    DealerUpdateResponse,
    DealerStatusRequest,
    DealerStatusResponse
)

router = APIRouter(tags=["admin-dealer"])


@router.get("/admin/dealers", response_model=DealerListResponse)
async def get_all_dealers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by dealer ID or name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all dealers with pagination and filtering (SYSTEM_ADMIN only)

    This endpoint returns all dealers with support for:
    - Pagination (page, page_size)
    - Search by dealer ID or name
    - Filter by active status

    **Required Role**: SYSTEM_ADMIN

    **Query Parameters**:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Search term for dealer ID or name
    - **is_active**: Filter by active status (true/false)

    **Returns**:
        Paginated list of dealers with metadata

    **Example**:
        GET /api/v1/admin/dealers?page=1&page_size=10&search=AHASS&is_active=true
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.get_all_dealers(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/admin/dealers/{dealer_id}", response_model=DealerResponse)
async def get_dealer_by_id(
    dealer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get single dealer by ID (SYSTEM_ADMIN only)

    **Required Role**: SYSTEM_ADMIN

    **Path Parameters**:
    - **dealer_id**: Dealer ID to retrieve

    **Returns**:
        Dealer details including API credentials

    **Example**:
        GET /api/v1/admin/dealers/12345
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.get_dealer_by_id(dealer_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dealer not found: {dealer_id}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/admin/dealers/{dealer_id}", response_model=DealerUpdateResponse)
async def update_dealer(
    dealer_id: str,
    update_data: DealerUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update dealer information (SYSTEM_ADMIN only)

    **Required Role**: SYSTEM_ADMIN

    **Path Parameters**:
    - **dealer_id**: Dealer ID to update

    **Request Body**:
    - **dealer_name**: Optional dealer name
    - **api_key**: Optional API key
    - **api_token**: Optional API token
    - **secret_key**: Optional secret key
    - **is_active**: Optional active status

    **Returns**:
        Updated dealer details

    **Example**:
        PUT /api/v1/admin/dealers/12345
        {
            "dealer_name": "New Dealer Name",
            "is_active": true
        }
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.update_dealer(dealer_id, update_data)

        if not result.success:
            if "not found" in result.message:
                raise HTTPException(status_code=404, detail=result.message)
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/admin/dealers/{dealer_id}/status", response_model=DealerStatusResponse)
async def toggle_dealer_status(
    dealer_id: str,
    status_data: DealerStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Toggle dealer active/inactive status (SYSTEM_ADMIN only)

    **Required Role**: SYSTEM_ADMIN

    **Path Parameters**:
    - **dealer_id**: Dealer ID to update

    **Request Body**:
    - **is_active**: New active status (true/false)

    **Returns**:
        Updated dealer with new status

    **Example**:
        PATCH /api/v1/admin/dealers/12345/status
        {
            "is_active": false
        }
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.toggle_dealer_status(dealer_id, status_data.is_active)

        if not result.success:
            if "not found" in result.message:
                raise HTTPException(status_code=404, detail=result.message)
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
