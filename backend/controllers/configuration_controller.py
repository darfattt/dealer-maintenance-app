"""
Configuration controller for fetch configurations and API configurations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from croniter import croniter

from database import get_db, Dealer, FetchConfiguration, APIConfiguration
from models.schemas import (
    FetchConfigurationCreate, FetchConfigurationResponse,
    APIConfigurationCreate, APIConfigurationUpdate, APIConfigurationResponse,
    CountResponse
)
from .base_controller import BaseController

router = APIRouter(tags=["configuration"])


# Fetch Configuration endpoints
@router.post("/fetch-configurations/", response_model=FetchConfigurationResponse)
async def create_fetch_configuration(config: FetchConfigurationCreate, db: Session = Depends(get_db)):
    """Create a new fetch configuration"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, config.dealer_id, Dealer)
    
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
    
    BaseController.convert_uuid_to_string(db_config)
    BaseController.log_operation("CREATE_FETCH_CONFIG", f"Created fetch config for dealer {config.dealer_id}")
    
    return db_config


@router.get("/fetch-configurations/", response_model=List[FetchConfigurationResponse])
async def get_fetch_configurations(dealer_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get fetch configurations with optional dealer filter"""
    query = db.query(FetchConfiguration)
    if dealer_id:
        query = query.filter(FetchConfiguration.dealer_id == dealer_id)
    
    configurations = query.all()
    BaseController.convert_list_uuids_to_strings(configurations)
    
    BaseController.log_operation("GET_FETCH_CONFIGS", f"Retrieved {len(configurations)} fetch configurations")
    return configurations


@router.get("/fetch-configurations/{config_id}", response_model=FetchConfigurationResponse)
async def get_fetch_configuration(config_id: str, db: Session = Depends(get_db)):
    """Get a specific fetch configuration"""
    config = db.query(FetchConfiguration).filter(FetchConfiguration.id == config_id).first()
    if not config:
        raise BaseController.handle_not_found("Fetch Configuration", config_id)
    
    BaseController.convert_uuid_to_string(config)
    BaseController.log_operation("GET_FETCH_CONFIG", f"Retrieved fetch config {config_id}")
    
    return config


# API Configuration endpoints
@router.get("/api-configurations/", response_model=List[APIConfigurationResponse])
async def get_api_configurations(db: Session = Depends(get_db)):
    """Get all API configurations"""
    configs = db.query(APIConfiguration).all()
    BaseController.convert_list_uuids_to_strings(configs)
    
    BaseController.log_operation("GET_API_CONFIGS", f"Retrieved {len(configs)} API configurations")
    return configs


@router.post("/api-configurations/", response_model=APIConfigurationResponse)
async def create_api_configuration(config: APIConfigurationCreate, db: Session = Depends(get_db)):
    """Create a new API configuration"""
    # Check if config name already exists
    existing = db.query(APIConfiguration).filter(APIConfiguration.config_name == config.config_name).first()
    if existing:
        raise BaseController.handle_already_exists("API Configuration", config.config_name)

    db_config = APIConfiguration(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    BaseController.convert_uuid_to_string(db_config)
    BaseController.log_operation("CREATE_API_CONFIG", f"Created API config {config.config_name}")
    
    return db_config


@router.put("/api-configurations/{config_id}", response_model=APIConfigurationResponse)
async def update_api_configuration(config_id: str, config: APIConfigurationUpdate, db: Session = Depends(get_db)):
    """Update an API configuration"""
    db_config = db.query(APIConfiguration).filter(APIConfiguration.id == config_id).first()
    if not db_config:
        raise BaseController.handle_not_found("API Configuration", config_id)

    update_data = config.dict(exclude_unset=True)
    BaseController.update_model_fields(db_config, update_data)
    db_config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_config)
    
    BaseController.convert_uuid_to_string(db_config)
    BaseController.log_operation("UPDATE_API_CONFIG", f"Updated API config {config_id}")
    
    return db_config


@router.delete("/api-configurations/{config_id}")
async def delete_api_configuration(config_id: str, db: Session = Depends(get_db)):
    """Delete an API configuration"""
    db_config = db.query(APIConfiguration).filter(APIConfiguration.id == config_id).first()
    if not db_config:
        raise BaseController.handle_not_found("API Configuration", config_id)

    db.delete(db_config)
    db.commit()
    
    BaseController.log_operation("DELETE_API_CONFIG", f"Deleted API config {config_id}")
    return {"message": "API configuration deleted successfully"}


@router.post("/api-configurations/initialize", response_model=CountResponse)
async def initialize_api_configurations(db: Session = Depends(get_db)):
    """Initialize default API configurations"""
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
        ),
        APIConfiguration(
            config_name="dgi_parts_inbound_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Parts Inbound Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_leasing_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Leasing Requirement Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_document_handling_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Document Handling Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_unit_inbound_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Unit Inbound from Purchase Order Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_delivery_process_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Delivery Process Data (BAST)",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_billing_process_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Billing Process Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_unit_invoice_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Unit Invoice (MD to Dealer) Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_parts_sales_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Parts Sales Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_dp_hlo_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for DP HLO Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_workshop_invoice_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Workshop Invoice (NJB & NSC) Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_unpaid_hlo_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Unpaid HLO Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        ),
        APIConfiguration(
            config_name="dgi_parts_invoice_api",
            base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
            description="DGI API for Parts Invoice (MD to Dealer) Data",
            is_active=True,
            timeout_seconds=30,
            retry_attempts=3
        )
    ]

    for config in default_configs:
        db.add(config)

    db.commit()
    
    BaseController.log_operation("INIT_API_CONFIGS", f"Initialized {len(default_configs)} default API configurations")
    return {"message": "Default API configurations initialized successfully", "count": len(default_configs)}


@router.post("/api-configurations/force-reinitialize", response_model=CountResponse)
async def force_reinitialize_api_configurations(db: Session = Depends(get_db)):
    """Force re-initialization of API configurations (deletes existing and recreates)"""
    try:
        # Delete all existing configurations
        deleted_count = db.query(APIConfiguration).delete()

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
            ),
            APIConfiguration(
                config_name="dgi_parts_inbound_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Parts Inbound Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_leasing_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Leasing Requirement Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_document_handling_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Document Handling Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unit_inbound_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Unit Inbound from Purchase Order Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_delivery_process_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Delivery Process Data (BAST)",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_billing_process_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Billing Process Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unit_invoice_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Unit Invoice (MD to Dealer) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_parts_sales_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Parts Sales Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_dp_hlo_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for DP HLO Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_workshop_invoice_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Workshop Invoice (NJB & NSC) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_unpaid_hlo_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Unpaid HLO Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            ),
            APIConfiguration(
                config_name="dgi_parts_invoice_api",
                base_url="https://dev-gvt-gateway.eksad.com/dgi-api/v1.3",
                description="DGI API for Parts Invoice (MD to Dealer) Data",
                is_active=True,
                timeout_seconds=30,
                retry_attempts=3
            )
        ]

        for config in default_configs:
            db.add(config)

        db.commit()

        BaseController.log_operation("FORCE_REINIT_API_CONFIGS", f"Force re-initialized {len(default_configs)} API configurations (deleted {deleted_count} existing)")
        return {"message": f"API configurations force re-initialized successfully (deleted {deleted_count}, created {len(default_configs)})", "count": len(default_configs)}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to force re-initialize API configurations: {str(e)}")
