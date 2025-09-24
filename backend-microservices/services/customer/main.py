"""
Main FastAPI application for the customer service
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from app.config import settings
from app.routes.customer import router as customer_router
from app.routes.customer_reminder import router as customer_reminder_router
from app.routes.customer_satisfaction import router as customer_satisfaction_router
from app.routes.whatsapp_template import router as whatsapp_template_router
from app.routes.google_review_routes import router as google_review_router
from app.routes.health import router as health_router
from utils.database import DatabaseManager
from utils.logger import setup_logger
from sqlalchemy import text

# Setup logger
logger = setup_logger(__name__)

# Database manager
db_manager = DatabaseManager(settings.db_schema)


async def _initialize_whatsapp_templates(session):
    """Initialize WhatsApp templates in database"""
    try:
        from app.repositories.whatsapp_template_repository import WhatsAppTemplateRepository
        from utils.template_loader_utils import create_csv_template_loader
        
        template_repo = WhatsAppTemplateRepository(session)
        
        # Try to load templates from CSV file first
        csv_reader = create_csv_template_loader()
        csv_success, csv_templates, csv_message = csv_reader.read_csv_templates()
        
        if csv_success and csv_templates:
            logger.info(f"CSV file found and loaded: {csv_message}")
            
            # Update templates from CSV
            update_result = template_repo.update_templates_from_excel(csv_templates)
            
            if update_result['success']:
                logger.info(f"Templates successfully updated from CSV: {update_result['message']}")
                
                # Get current statistics
                stats = template_repo.get_template_statistics()
                logger.info(f"Template statistics: {stats['total_templates']} total templates, "
                          f"{stats['unique_targets']} targets, {stats['unique_types']} types")
                return
            else:
                logger.error(f"Failed to update templates from CSV: {update_result['message']}")
                if update_result['errors']:
                    for error in update_result['errors']:
                        logger.error(f"CSV update error: {error}")
                
                # Fall through to use hardcoded templates
                logger.info("Falling back to hardcoded template initialization")
        else:
            logger.info(f"CSV file not available or invalid: {csv_message}")
            logger.info("Using hardcoded template initialization")
        
#         # Fallback: Use hardcoded template data if Excel fails or is unavailable
        
#         # Template data based on migration file
#         templates_data = [
#             {
#                 'reminder_target': 'KPB-1',
#                 'reminder_type': 'H+30 tanggal beli (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Terima kasih telah mempercayai produk Honda. Saatnya untuk melakukan servis KPB-1 kendaraan Anda untuk menjaga performa dan garansi.

# Segera hubungi kami untuk membuat jadwal servis KPB-1.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-1',
#                 'reminder_type': 'H-7 dari expired KPB-1 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-1 kendaraan Honda Anda akan berakhir dalam 7 hari. Jangan lewatkan kesempatan untuk mendapatkan servis gratis.

# Segera hubungi kami untuk menjadwalkan servis KPB-1.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-2',
#                 'reminder_type': 'H-60 dari expired KPB-2 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-2 kendaraan Honda Anda akan berakhir dalam 60 hari. Pastikan kendaraan Anda mendapatkan perawatan terbaik.

# Hubungi kami sekarang untuk menjadwalkan servis KPB-2.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-2',
#                 'reminder_type': 'H-30 dari expired KPB-2 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-2 kendaraan Honda Anda akan berakhir dalam 30 hari. Jangan sampai terlewat untuk mendapatkan servis berkualitas.

# Segera hubungi kami untuk menjadwalkan servis KPB-2.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-2',
#                 'reminder_type': 'H-7 dari expired KPB-2 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-2 kendaraan Honda Anda akan berakhir dalam 7 hari. Ini adalah kesempatan terakhir untuk mendapatkan servis gratis.

# Segera hubungi kami untuk menjadwalkan servis KPB-2.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-3',
#                 'reminder_type': 'H-60 dari expired KPB-3 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-3 kendaraan Honda Anda akan berakhir dalam 60 hari. Pastikan kendaraan tetap dalam kondisi prima.

# Hubungi kami untuk menjadwalkan servis KPB-3.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-3',
#                 'reminder_type': 'H-30 dari expired KPB-3 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-3 kendaraan Honda Anda akan berakhir dalam 30 hari. Manfaatkan kesempatan ini untuk servis berkualitas.

# Segera hubungi kami untuk menjadwalkan servis KPB-3.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-3',
#                 'reminder_type': 'H-7 dari expired KPB-3 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-3 kendaraan Honda Anda akan berakhir dalam 7 hari. Jangan lewatkan kesempatan terakhir ini.

# Segera hubungi kami untuk menjadwalkan servis KPB-3.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-4',
#                 'reminder_type': 'H-60 dari expired KPB-4 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-4 kendaraan Honda Anda akan berakhir dalam 60 hari. Pastikan kendaraan mendapatkan perawatan terakhir yang optimal.

# Hubungi kami untuk menjadwalkan servis KPB-4.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-4',
#                 'reminder_type': 'H-30 dari expired KPB-4 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-4 kendaraan Honda Anda akan berakhir dalam 30 hari. Ini adalah servis terakhir dalam program garansi.

# Segera hubungi kami untuk menjadwalkan servis KPB-4.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'KPB-4',
#                 'reminder_type': 'H-7 dari expired KPB-4 (by WA)',
#                 'template': '''Halo {nama_pemilik},

# Garansi KPB-4 kendaraan Honda Anda akan berakhir dalam 7 hari. Ini adalah kesempatan terakhir untuk servis garansi.

# Segera hubungi kami untuk menjadwalkan servis KPB-4.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'Non KPB',
#                 'reminder_type': 'N/A',
#                 'template': '''Halo {nama_pemilik},

# Saatnya untuk melakukan servis rutin kendaraan Honda Anda. Perawatan berkala sangat penting untuk menjaga performa dan keamanan berkendara.

# Hubungi kami untuk menjadwalkan servis kendaraan Anda.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'Booking Servis',
#                 'reminder_type': 'N/A',
#                 'template': '''Halo {nama_pemilik},

# Terima kasih telah melakukan booking servis. Kami siap memberikan pelayanan terbaik untuk kendaraan Honda Anda.

# Silakan datang sesuai jadwal yang telah ditentukan.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             },
#             {
#                 'reminder_target': 'Ultah Konsumen',
#                 'reminder_type': 'N/A',
#                 'template': '''Halo {nama_pemilik},

# Selamat ulang tahun! Semoga di usia yang baru ini Anda selalu diberikan kesehatan dan keberkahan.

# Sebagai apresiasi, dapatkan promo spesial untuk servis kendaraan Honda Anda.

# Terima kasih,
# {dealer_name}''',
#                 'created_by': 'system'
#             }
#         ]
        
#         # Bulk upsert templates (hardcoded fallback)
#         success = template_repo.bulk_upsert_templates(templates_data)
#         if success:
#             logger.info("WhatsApp templates initialized successfully from hardcoded data")
            
#             # Get current statistics
#             stats = template_repo.get_template_statistics()
#             logger.info(f"Hardcoded template statistics: {stats['total_templates']} total templates, "
#                       f"{stats['unique_targets']} targets, {stats['unique_types']} types")
#         else:
#             logger.warning("Some hardcoded WhatsApp templates failed to initialize")
            
    except Exception as e:
        logger.error(f"Failed to initialize WhatsApp templates: {str(e)}")
        # Don't raise exception to avoid breaking service startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    
    # Create database schema and tables
    try:
        # Import models to register them with Base
        from app.models.customer_validation_request import CustomerValidationRequest, Base
        from app.models.customer_reminder_request import CustomerReminderRequest
        from app.models.customer_satisfaction_raw import CustomerSatisfactionRaw, CustomerSatisfactionUploadTracker
        from app.models.whatsapp_template import WhatsAppTemplate
        from app.models.whatsapp_template_logs import WhatsAppTemplateLogs
        from app.models.api_request_log import ApiRequestLog
        from app.models.google_review import GoogleReview, GoogleReviewDetail
        from app.models.google_review_scrape_tracker import GoogleReviewScrapeTracker
        
        # Create schema and tables with checkfirst=True to avoid conflicts
        logger.info("Creating database schema and tables...")
        db_manager.create_schema_tables_safe(Base.metadata)
        logger.info("Database tables created successfully")
        
        # Create customer schema if not exists
        for session in db_manager.get_session():
            session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.db_schema}"))
            session.commit()
            logger.info(f"Schema {settings.db_schema} ensured")
            
            # Initialize WhatsApp templates
            await _initialize_whatsapp_templates(session)
            break
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.service_name}")


# Create FastAPI application
app = FastAPI(
    title="Customer Service",
    description="Customer validation and reminder WhatsApp notification microservice for Dealer Dashboard",
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly in production
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "InternalServerError"
            }
        }
    )


# Include routers
app.include_router(customer_router, prefix="/api/v1")
app.include_router(customer_reminder_router, prefix="/api/v1")
app.include_router(customer_satisfaction_router, prefix="/api/v1")
app.include_router(whatsapp_template_router, prefix="/api/v1")
app.include_router(google_review_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled"
    }


# Service info endpoint
@app.get("/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_schema": settings.db_schema,
        "fonnte_api_url": settings.fonnte_default_api_url
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )