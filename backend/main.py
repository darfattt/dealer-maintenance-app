"""
Main FastAPI application with modular controller architecture

This file now acts as the main application entry point that registers
all the modular controllers for better separation of concerns and maintainability.

Architecture:
- main.py (this file): FastAPI app setup and controller registration
- controllers/: Modular controllers for different API concerns
- models/schemas.py: Pydantic models for request/response schemas
- database.py: Database models and connection
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import database setup
from database import create_tables, get_db

# Import all controllers
from controllers.common_controller import router as common_router
from controllers.dealers_controller import router as dealers_router
from controllers.configuration_controller import router as configuration_router
from controllers.prospect_controller import router as prospect_router
from controllers.pkb_controller import router as pkb_router
from controllers.parts_inbound_controller import router as parts_inbound_router
from controllers.leasing_controller import router as leasing_router
from controllers.document_handling_controller import router as document_handling_router
from controllers.unit_inbound_controller import router as unit_inbound_router
from controllers.delivery_process_controller import router as delivery_process_router
from controllers.billing_process_controller import router as billing_process_router
from controllers.unit_invoice_controller import router as unit_invoice_router
from controllers.parts_sales_controller import router as parts_sales_router
from controllers.dp_hlo_controller import router as dp_hlo_router
from controllers.workshop_invoice_controller import router as workshop_invoice_router
from controllers.unpaid_hlo_controller import router as unpaid_hlo_router
from controllers.parts_invoice_controller import router as parts_invoice_router
from controllers.token_controller import router as token_router
from controllers.logs_controller import router as logs_router
from controllers.jobs_controller import router as jobs_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dealer Dashboard API",
    description="API for managing dealer data fetching and analytics - Modular Architecture",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created/verified")
    logger.info("Dealer Dashboard API started with modular controller architecture")

# Register all routers
app.include_router(common_router)                    # Root and health endpoints
app.include_router(dealers_router)                  # Dealer management
app.include_router(configuration_router)            # Configurations (fetch & API)
app.include_router(prospect_router)                 # Prospect data and analytics
app.include_router(pkb_router)                      # PKB data and analytics
app.include_router(parts_inbound_router)            # Parts Inbound data and analytics
app.include_router(leasing_router)                  # Leasing data and analytics
app.include_router(document_handling_router)        # Document handling data and analytics
app.include_router(unit_inbound_router)              # Unit inbound data and analytics
app.include_router(delivery_process_router)         # Delivery process data and analytics
app.include_router(billing_process_router)          # Billing process data and analytics
app.include_router(unit_invoice_router)             # Unit invoice data and analytics
app.include_router(parts_sales_router)              # Parts sales data and analytics
app.include_router(dp_hlo_router)                   # DP HLO data and analytics
app.include_router(workshop_invoice_router)         # Workshop invoice data and analytics
app.include_router(unpaid_hlo_router)               # Unpaid HLO data and analytics
app.include_router(parts_invoice_router)            # Parts invoice data and analytics
app.include_router(token_router)                    # Token generation and management
app.include_router(logs_router)                     # Logs and monitoring
app.include_router(jobs_router)                     # Job execution and management

# Legacy endpoints for backward compatibility
@app.post("/generate-token")
async def generate_token_legacy(request):
    """Legacy endpoint - redirects to /token/generate"""
    from controllers.token_controller import generate_dgi_token
    return await generate_dgi_token(request)

@app.post("/refresh-token")
async def refresh_token_legacy(request):
    """Legacy endpoint - redirects to /token/refresh"""
    from controllers.token_controller import refresh_dgi_token
    return await refresh_dgi_token(request)

@app.get("/fetch-logs/")
async def get_fetch_logs_legacy(
    dealer_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db)
):
    """Legacy endpoint - redirects to /logs/fetch-logs/"""
    from controllers.logs_controller import get_fetch_logs
    return await get_fetch_logs(dealer_id, status, None, skip, limit, db)

# Application metadata
@app.get("/api/info")
async def get_api_info():
    """Get API information and available endpoints"""
    return {
        "title": "Dealer Dashboard API",
        "version": "2.0.0",
        "architecture": "Modular Controller Architecture",
        "controllers": {
            "common": "Root and health endpoints",
            "dealers": "Dealer management (CRUD operations)",
            "configuration": "Fetch and API configurations",
            "prospect": "Prospect data and analytics",
            "pkb": "PKB (Service Record) data and analytics",
            "parts_inbound": "Parts Inbound data and analytics",
            "leasing": "Leasing requirement data and analytics",
        "document_handling": "Document handling data and analytics",
        "unit_inbound": "Unit inbound from purchase order data and analytics",
        "delivery_process": "Delivery process data and analytics",
        "billing_process": "Billing process data and analytics",
        "unit_invoice": "Unit invoice (MD to Dealer) data and analytics",
        "parts_sales": "Parts sales data and analytics",
        "dp_hlo": "DP HLO data and analytics",
        "workshop_invoice": "Workshop invoice (NJB & NSC) data and analytics",
        "unpaid_hlo": "Unpaid HLO data and analytics",
        "parts_invoice": "Parts invoice (MD to Dealer) data and analytics",
            "token": "DGI API token generation and management",
            "logs": "Fetch logs and system monitoring",
            "jobs": "Manual job execution and status"
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "dealers": "/dealers/",
            "prospect_data": "/prospect-data/",
            "pkb_data": "/pkb-data/",
            "parts_inbound_data": "/parts-inbound-data/",
            "leasing_data": "/leasing/",
        "document_handling_data": "/document_handling/",
        "unit_inbound_data": "/unit_inbound/",
        "delivery_process_data": "/delivery_process/",
        "billing_process_data": "/billing_process/",
        "unit_invoice_data": "/unit_invoice/",
        "parts_sales_data": "/parts_sales/",
        "dp_hlo_data": "/dp_hlo/",
        "workshop_invoice_data": "/workshop_invoice/",
        "unpaid_hlo_data": "/unpaid_hlo/",
        "parts_invoice_data": "/parts_invoice/",
            "token_generation": "/token/generate",
            "job_execution": "/jobs/run",
            "logs": "/logs/fetch-logs/"
        },
        "features": [
            "Modular controller architecture",
            "Comprehensive API documentation",
            "Dealer management with CRUD operations",
            "Multi-API data fetching (Prospect, PKB, Parts Inbound, Leasing)",
            "Real-time job execution and monitoring",
            "Advanced analytics and reporting",
            "Token-based authentication support",
            "Comprehensive logging and error tracking",
            "Bulk operations support",
            "Performance monitoring and metrics"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
