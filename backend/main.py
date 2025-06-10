from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, create_tables, Dealer, FetchConfiguration, ProspectData, FetchLog
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

class DealerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    dealer_name: str
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

class ManualFetchRequest(BaseModel):
    dealer_id: str
    from_time: Optional[str] = None
    to_time: Optional[str] = None

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
async def update_dealer(dealer_id: str, dealer_update: DealerCreate, db: Session = Depends(get_db)):
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

    # Trigger Celery task
    task = celery_app.send_task(
        "tasks.data_fetcher.fetch_prospect_data",
        args=[request.dealer_id, request.from_time, request.to_time]
    )

    return {
        "message": "Data fetch job started",
        "task_id": task.id,
        "dealer_id": request.dealer_id,
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
