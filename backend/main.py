from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, create_tables, Dealer, FetchConfiguration, ProspectData, FetchLog, PKBData, PKBService, PKBPart, APIConfiguration
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date
import logging
from celery_app import celery_app
from croniter import croniter
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to convert UUID to string
def convert_uuid_to_string(obj):
    """Convert UUID fields to strings for JSON serialization"""
    if hasattr(obj, 'id') and hasattr(obj.id, 'hex'):
        obj.id = str(obj.id)
    return obj

# Create FastAPI app
app = FastAPI(
    title="Dealer Dashboard API",
    description="API for managing dealer data fetching and analytics",
    version="1.0.0"
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

# Pydantic models
class DealerCreate(BaseModel):
    dealer_id: str
    dealer_name: str
    api_key: Optional[str] = None
    api_token: Optional[str] = None
    secret_key: Optional[str] = None

class DealerUpdate(BaseModel):
    dealer_name: Optional[str] = None
    api_key: Optional[str] = None
    api_token: Optional[str] = None
    secret_key: Optional[str] = None
    is_active: Optional[bool] = None

class DealerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    dealer_name: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    is_active: bool
    created_at: datetime

class FetchConfigurationCreate(BaseModel):
    dealer_id: str
    schedule_type: str  # hourly, daily, custom
    cron_expression: Optional[str] = None

class FetchConfigurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    schedule_type: str
    cron_expression: Optional[str]
    is_active: bool
    last_fetch_at: Optional[datetime]
    next_fetch_at: Optional[datetime]

class ProspectDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    id_prospect: Optional[str]
    nama_lengkap: Optional[str]
    tanggal_prospect: Optional[date]
    status_prospect: Optional[str]
    fetched_at: datetime

class FetchLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    fetch_type: str
    status: str
    records_fetched: int
    error_message: Optional[str]
    fetch_duration_seconds: Optional[int]
    completed_at: datetime

class PKBDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    no_work_order: str
    no_sa_form: Optional[str]
    tanggal_servis: Optional[str]
    nama_pemilik: Optional[str]
    no_polisi: Optional[str]
    kode_tipe_unit: Optional[str]
    status_work_order: Optional[str]
    total_biaya_service: Optional[float]
    fetched_at: datetime

class APIConfigurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    config_name: str
    base_url: str
    description: Optional[str]
    is_active: bool
    timeout_seconds: int
    retry_attempts: int
    created_at: datetime
    updated_at: datetime

class APIConfigurationCreate(BaseModel):
    config_name: str
    base_url: str
    description: Optional[str] = None
    is_active: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3

class APIConfigurationUpdate(BaseModel):
    base_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None

class TokenGenerationRequest(BaseModel):
    api_key: str
    secret_key: str
    api_time: Optional[int] = None

class TokenGenerationResponse(BaseModel):
    api_token: str
    api_time: int
    timestamp: int
    expires_in: int

class ManualFetchRequest(BaseModel):
    dealer_id: str
    from_time: Optional[str] = None
    to_time: Optional[str] = None
    fetch_type: Optional[str] = "prospect"  # prospect or pkb

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Dealer Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Dealer endpoints
@app.post("/dealers/", response_model=DealerResponse)
async def create_dealer(dealer: DealerCreate, db: Session = Depends(get_db)):
    # Check if dealer already exists
    existing_dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer.dealer_id).first()
    if existing_dealer:
        raise HTTPException(status_code=400, detail="Dealer already exists")

    db_dealer = Dealer(**dealer.dict())
    db.add(db_dealer)
    db.commit()
    db.refresh(db_dealer)
    convert_uuid_to_string(db_dealer)
    return db_dealer

@app.get("/dealers/", response_model=List[DealerResponse])
async def get_dealers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dealers = db.query(Dealer).offset(skip).limit(limit).all()
    # Convert UUIDs to strings
    for dealer in dealers:
        convert_uuid_to_string(dealer)
    return dealers

@app.get("/dealers/{dealer_id}", response_model=DealerResponse)
async def get_dealer(dealer_id: str, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    convert_uuid_to_string(dealer)
    return dealer

@app.put("/dealers/{dealer_id}", response_model=DealerResponse)
async def update_dealer(dealer_id: str, dealer_update: DealerUpdate, db: Session = Depends(get_db)):
    # Find existing dealer
    db_dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not db_dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")

    # Update dealer fields
    update_data = dealer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_dealer, field):
            setattr(db_dealer, field, value)

    db.commit()
    db.refresh(db_dealer)
    convert_uuid_to_string(db_dealer)
    return db_dealer

# Fetch configuration endpoints
@app.post("/fetch-configurations/", response_model=FetchConfigurationResponse)
async def create_fetch_configuration(config: FetchConfigurationCreate, db: Session = Depends(get_db)):
    # Validate dealer exists
    dealer = db.query(Dealer).filter(Dealer.dealer_id == config.dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    
    # Validate cron expression if custom schedule
    if config.schedule_type == "custom" and config.cron_expression:
        try:
            croniter(config.cron_expression)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid cron expression")
    elif config.schedule_type == "hourly":
        config.cron_expression = "0 * * * *"  # Every hour
    elif config.schedule_type == "daily":
        config.cron_expression = "0 0 * * *"  # Every day at midnight
    
    # Deactivate existing configurations for this dealer
    db.query(FetchConfiguration).filter(
        FetchConfiguration.dealer_id == config.dealer_id
    ).update({"is_active": False})
    
    db_config = FetchConfiguration(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    convert_uuid_to_string(db_config)
    return db_config

@app.get("/fetch-configurations/", response_model=List[FetchConfigurationResponse])
async def get_fetch_configurations(dealer_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FetchConfiguration)
    if dealer_id:
        query = query.filter(FetchConfiguration.dealer_id == dealer_id)
    configurations = query.all()
    for config in configurations:
        convert_uuid_to_string(config)
    return configurations

@app.get("/fetch-configurations/{config_id}", response_model=FetchConfigurationResponse)
async def get_fetch_configuration(config_id: str, db: Session = Depends(get_db)):
    config = db.query(FetchConfiguration).filter(FetchConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    convert_uuid_to_string(config)
    return config

# Prospect data endpoints
@app.get("/prospect-data/", response_model=List[ProspectDataResponse])
async def get_prospect_data(
    dealer_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ProspectData)

    if dealer_id:
        query = query.filter(ProspectData.dealer_id == dealer_id)
    if from_date:
        query = query.filter(ProspectData.tanggal_prospect >= from_date)
    if to_date:
        query = query.filter(ProspectData.tanggal_prospect <= to_date)

    prospects = query.offset(skip).limit(limit).all()
    for prospect in prospects:
        convert_uuid_to_string(prospect)
    return prospects

@app.get("/prospect-data/analytics/{dealer_id}")
async def get_prospect_analytics(dealer_id: str, db: Session = Depends(get_db)):
    # Validate dealer exists
    dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    
    # Get prospect data grouped by date
    from sqlalchemy import func
    
    daily_counts = db.query(
        ProspectData.tanggal_prospect,
        func.count(ProspectData.id).label('count')
    ).filter(
        ProspectData.dealer_id == dealer_id,
        ProspectData.tanggal_prospect.isnot(None)
    ).group_by(
        ProspectData.tanggal_prospect
    ).order_by(
        ProspectData.tanggal_prospect
    ).all()
    
    # Get status distribution
    status_counts = db.query(
        ProspectData.status_prospect,
        func.count(ProspectData.id).label('count')
    ).filter(
        ProspectData.dealer_id == dealer_id,
        ProspectData.status_prospect.isnot(None)
    ).group_by(
        ProspectData.status_prospect
    ).all()
    
    # Get total counts
    total_prospects = db.query(func.count(ProspectData.id)).filter(
        ProspectData.dealer_id == dealer_id
    ).scalar()
    
    return {
        "dealer_id": dealer_id,
        "total_prospects": total_prospects,
        "daily_counts": [
            {"date": str(row.tanggal_prospect), "count": row.count}
            for row in daily_counts
        ],
        "status_distribution": [
            {"status": row.status_prospect, "count": row.count}
            for row in status_counts
        ]
    }

# PKB data endpoints
@app.get("/pkb-data/", response_model=List[PKBDataResponse])
async def get_pkb_data(
    dealer_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(PKBData)

    if dealer_id:
        query = query.filter(PKBData.dealer_id == dealer_id)
    if from_date:
        # Parse tanggal_servis string to date for comparison
        query = query.filter(PKBData.tanggal_servis.isnot(None))
    if to_date:
        query = query.filter(PKBData.tanggal_servis.isnot(None))

    pkb_records = query.offset(skip).limit(limit).all()
    for record in pkb_records:
        convert_uuid_to_string(record)
    return pkb_records

@app.get("/pkb-data/analytics/{dealer_id}")
async def get_pkb_analytics(dealer_id: str, db: Session = Depends(get_db)):
    # Validate dealer exists
    dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")

    # Get PKB data analytics
    from sqlalchemy import func

    # Count by status
    status_counts = db.query(
        PKBData.status_work_order,
        func.count(PKBData.id).label('count')
    ).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.status_work_order.isnot(None)
    ).group_by(
        PKBData.status_work_order
    ).all()

    # Count by unit type
    unit_counts = db.query(
        PKBData.kode_tipe_unit,
        func.count(PKBData.id).label('count')
    ).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.kode_tipe_unit.isnot(None)
    ).group_by(
        PKBData.kode_tipe_unit
    ).all()

    # Get total counts
    total_pkb = db.query(func.count(PKBData.id)).filter(
        PKBData.dealer_id == dealer_id
    ).scalar()

    # Average service cost
    avg_service_cost = db.query(func.avg(PKBData.total_biaya_service)).filter(
        PKBData.dealer_id == dealer_id,
        PKBData.total_biaya_service.isnot(None)
    ).scalar()

    return {
        "dealer_id": dealer_id,
        "total_pkb": total_pkb,
        "avg_service_cost": float(avg_service_cost) if avg_service_cost else 0,
        "status_distribution": [
            {"status": row.status_work_order, "count": row.count}
            for row in status_counts
        ],
        "unit_distribution": [
            {"unit": row.kode_tipe_unit, "count": row.count}
            for row in unit_counts
        ]
    }

# API Configuration endpoints
@app.get("/api-configurations/", response_model=List[APIConfigurationResponse])
async def get_api_configurations(db: Session = Depends(get_db)):
    configs = db.query(APIConfiguration).all()
    for config in configs:
        convert_uuid_to_string(config)
    return configs

@app.post("/api-configurations/", response_model=APIConfigurationResponse)
async def create_api_configuration(config: APIConfigurationCreate, db: Session = Depends(get_db)):
    # Check if config name already exists
    existing = db.query(APIConfiguration).filter(APIConfiguration.config_name == config.config_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Configuration name already exists")

    db_config = APIConfiguration(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    convert_uuid_to_string(db_config)
    return db_config

@app.put("/api-configurations/{config_id}", response_model=APIConfigurationResponse)
async def update_api_configuration(config_id: str, config: APIConfigurationUpdate, db: Session = Depends(get_db)):
    db_config = db.query(APIConfiguration).filter(APIConfiguration.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="API configuration not found")

    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)

    db_config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_config)
    convert_uuid_to_string(db_config)
    return db_config

@app.delete("/api-configurations/{config_id}")
async def delete_api_configuration(config_id: str, db: Session = Depends(get_db)):
    db_config = db.query(APIConfiguration).filter(APIConfiguration.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="API configuration not found")

    db.delete(db_config)
    db.commit()
    return {"message": "API configuration deleted successfully"}

@app.post("/api-configurations/initialize")
async def initialize_api_configurations(db: Session = Depends(get_db)):
    # Check if configurations already exist
    existing_count = db.query(APIConfiguration).count()
    if existing_count > 0:
        return {"message": "API configurations already exist", "count": existing_count}

    # Create default configurations
    default_configs = [
        APIConfiguration(
            config_name="dgi_prospect_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Prospect Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_pkb_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for PKB (Service Record) Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        )
    ]

    for config in default_configs:
        db.add(config)

    db.commit()
    return {"message": "Default API configurations initialized successfully", "count": len(default_configs)}

# Token generation endpoint
@app.post("/generate-token", response_model=TokenGenerationResponse)
async def generate_dgi_token(request: TokenGenerationRequest):
    """Generate DGI API token using API key and secret key"""
    from utils.dgi_token_generator import generate_api_token

    token_data = generate_api_token(
        api_key=request.api_key,
        secret_key=request.secret_key,
        api_time=request.api_time
    )

    return TokenGenerationResponse(**token_data)

@app.post("/refresh-token", response_model=TokenGenerationResponse)
async def refresh_dgi_token(request: TokenGenerationRequest):
    """Refresh DGI API token with current timestamp"""
    from utils.dgi_token_generator import refresh_token

    token_data = refresh_token(
        api_key=request.api_key,
        secret_key=request.secret_key
    )

    return TokenGenerationResponse(**token_data)

# Fetch logs endpoints
@app.get("/fetch-logs/", response_model=List[FetchLogResponse])
async def get_fetch_logs(
    dealer_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(FetchLog)

    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)
    if status:
        query = query.filter(FetchLog.status == status)

    logs = query.order_by(FetchLog.completed_at.desc()).offset(skip).limit(limit).all()
    for log in logs:
        convert_uuid_to_string(log)
    return logs

# Manual job execution endpoint
@app.post("/jobs/run")
async def run_job(request: ManualFetchRequest, db: Session = Depends(get_db)):
    # Validate dealer exists
    dealer = db.query(Dealer).filter(Dealer.dealer_id == request.dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")

    # Determine which task to run based on fetch_type
    if request.fetch_type == "pkb":
        task_name = "tasks.data_fetcher.fetch_pkb_data"
        message = "PKB data fetch job started"
    else:
        task_name = "tasks.data_fetcher.fetch_prospect_data"
        message = "Prospect data fetch job started"

    # Trigger Celery task
    task = celery_app.send_task(
        task_name,
        args=[request.dealer_id, request.from_time, request.to_time]
    )

    return {
        "message": message,
        "task_id": task.id,
        "dealer_id": request.dealer_id,
        "fetch_type": request.fetch_type,
        "status": "running"
    }

@app.get("/jobs/{task_id}/status")
async def get_job_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None,
        "progress": "completed" if task.ready() else "running"
    }

# Get all jobs for a dealer
@app.get("/jobs/")
async def get_jobs(dealer_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FetchLog)
    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)

    jobs = query.order_by(FetchLog.completed_at.desc()).limit(50).all()
    for job in jobs:
        convert_uuid_to_string(job)
    return jobs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
