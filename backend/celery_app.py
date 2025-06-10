from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "dealer_dashboard",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.data_fetcher"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Dynamic beat schedule - will be populated from database
celery_app.conf.beat_schedule = {
    # Default health check task
    'health-check': {
        'task': 'tasks.data_fetcher.health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    # Dynamic schedules will be added by the scheduler
}

if __name__ == "__main__":
    celery_app.start()
