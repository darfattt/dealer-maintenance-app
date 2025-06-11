from croniter import croniter
from datetime import datetime, timedelta
from database import SessionLocal, FetchConfiguration
from celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

def update_dynamic_schedules():
    """Update Celery beat schedule based on database configurations"""
    db = SessionLocal()
    
    try:
        # Get all active fetch configurations
        configs = db.query(FetchConfiguration).filter(
            FetchConfiguration.is_active == True
        ).all()
        
        # Clear existing dynamic schedules
        current_schedule = celery_app.conf.beat_schedule.copy()
        for key in list(current_schedule.keys()):
            if key.startswith('fetch_'):
                del current_schedule[key]
        
        # Add new schedules
        for config in configs:
            if config.cron_expression:
                task_name = f"fetch_{config.dealer_id}_{config.id}"
                
                # Parse cron expression
                try:
                    cron = croniter(config.cron_expression)
                    next_run = cron.get_next(datetime)
                    
                    # Update next_fetch_at in database
                    config.next_fetch_at = next_run
                    
                    # Add to beat schedule
                    current_schedule[task_name] = {
                        'task': 'tasks.data_fetcher.fetch_prospect_data',
                        'schedule': croniter(config.cron_expression),
                        'args': [config.dealer_id]
                    }
                    
                    logger.info(f"Added schedule for dealer {config.dealer_id}: {config.cron_expression}")
                    
                except ValueError as e:
                    logger.error(f"Invalid cron expression for dealer {config.dealer_id}: {e}")
        
        # Update Celery configuration
        celery_app.conf.beat_schedule = current_schedule
        db.commit()
        
        logger.info(f"Updated {len(configs)} dynamic schedules")
        
    except Exception as e:
        logger.error(f"Failed to update dynamic schedules: {e}")
        db.rollback()
    finally:
        db.close()

def calculate_next_run(cron_expression: str, base_time: datetime = None) -> datetime:
    """Calculate next run time for a cron expression"""
    if not base_time:
        base_time = datetime.utcnow()
    
    try:
        cron = croniter(cron_expression, base_time)
        return cron.get_next(datetime)
    except ValueError:
        # Fallback to 1 hour from now
        return base_time + timedelta(hours=1)

def validate_cron_expression(expression: str) -> bool:
    """Validate cron expression"""
    try:
        croniter(expression)
        return True
    except ValueError:
        return False
