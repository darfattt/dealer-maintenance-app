"""
Admin dashboard routes for administrative operations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.controllers.admin_dashboard_controller import AdminDashboardController
from app.schemas.dashboard import ActiveDealersResponse

router = APIRouter(tags=["admin-dashboard"])


@router.get("/admin/dealers/active", response_model=ActiveDealersResponse)
async def get_all_active_dealers(
    db: Session = Depends(get_db)
):
    """
    Get all active dealers without pagination
    
    This endpoint returns all dealers where is_active=True, ordered by dealer name.
    No pagination is applied - returns the complete list of active dealers.
    
    Returns:
        ActiveDealersResponse: Contains all active dealers with their basic information
        
    Example:
        GET /api/v1/admin/dealers/active
    """
    try:
        controller = AdminDashboardController(db)
        result = await controller.get_all_active_dealers()
        
        # If the controller returned an error, raise HTTPException
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )