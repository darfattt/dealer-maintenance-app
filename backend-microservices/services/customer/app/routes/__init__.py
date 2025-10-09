from .customer import router as customer_router
from .customer_reminder import router as customer_reminder_router
from .health import router as health_router
from .api_request_log import router as api_request_log_router
from .tracker_activities import router as tracker_activities_router

__all__ = [
    "customer_router",
    "customer_reminder_router",
    "health_router",
    "api_request_log_router",
    "tracker_activities_router"
]