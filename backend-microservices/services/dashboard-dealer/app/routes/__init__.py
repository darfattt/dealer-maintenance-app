"""
Routes package for dashboard-dealer service
"""

from .dashboard import router as dashboard_router
from .health import router as health_router
from .admin_dashboard import router as admin_dashboard_router
from .admin_dealer import router as admin_dealer_router
from .h23_dashboard import router as h23_dashboard_router
from .excel_export import router as excel_export_router

__all__ = ["dashboard_router", "health_router", "admin_dashboard_router", "admin_dealer_router", "h23_dashboard_router", "excel_export_router"]
