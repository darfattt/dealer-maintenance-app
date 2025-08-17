from .customer import router as customer_router
from .customer_reminder import router as customer_reminder_router
from .health import router as health_router

__all__ = [
    "customer_router",
    "customer_reminder_router", 
    "health_router"
]