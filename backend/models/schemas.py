"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date


# Dealer schemas
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


# Fetch Configuration schemas
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


# Prospect Data schemas
class ProspectDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    id_prospect: Optional[str]
    nama_lengkap: Optional[str]
    tanggal_prospect: Optional[date]
    status_prospect: Optional[str]
    fetched_at: datetime


# PKB Data schemas
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


# Parts Inbound Data schemas
class PartsInboundDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dealer_id: str
    no_penerimaan: Optional[str]
    tgl_penerimaan: Optional[str]
    no_shipping_list: Optional[str]
    created_time: Optional[str]
    modified_time: Optional[str]
    fetched_at: datetime


# API Configuration schemas
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


# Token schemas
class TokenGenerationRequest(BaseModel):
    api_key: str
    secret_key: str
    api_time: Optional[int] = None


class TokenGenerationResponse(BaseModel):
    api_token: str
    api_time: int
    timestamp: int
    expires_in: int


# Job schemas
class ManualFetchRequest(BaseModel):
    dealer_id: str
    from_time: Optional[str] = None
    to_time: Optional[str] = None
    fetch_type: Optional[str] = "prospect"  # prospect, pkb, or parts_inbound
    no_po: Optional[str] = ""  # For parts_inbound filtering


class JobResponse(BaseModel):
    message: str
    task_id: str
    dealer_id: str
    fetch_type: str
    status: str


class JobStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    progress: str


class QueueJobResponse(BaseModel):
    job_id: str
    dealer_id: str
    fetch_type: str
    status: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    celery_task_id: Optional[str] = None


class QueueStatusResponse(BaseModel):
    current_job: Optional[QueueJobResponse] = None
    queue_length: int
    queued_jobs: List[QueueJobResponse]
    is_processing: bool


class BulkJobRequest(BaseModel):
    dealer_ids: List[str]
    fetch_type: str = "prospect"
    from_time: Optional[str] = None
    to_time: Optional[str] = None


# Fetch Log schemas
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


# Common response schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class MessageResponse(BaseModel):
    message: str


class CountResponse(BaseModel):
    message: str
    count: int
