"""
Routes package for dashboard-dealer service
"""

from .dashboard import router as dashboard_router
from .health import router as health_router
from .admin_dashboard import router as admin_dashboard_router

__all__ = ["dashboard_router", "health_router", "admin_dashboard_router"]
