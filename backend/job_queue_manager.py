"""
Job Queue Manager for Sequential Job Execution
Prevents database transaction conflicts by running jobs one at a time
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueuedJob:
    """Represents a job in the queue"""
    id: str
    dealer_id: str
    fetch_type: str
    from_time: Optional[str] = None
    to_time: Optional[str] = None
    no_po: Optional[str] = None
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    celery_task_id: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, JobStatus):
                data[key] = value.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueuedJob':
        """Create from dictionary"""
        # Convert ISO strings back to datetime objects
        for key in ['created_at', 'started_at', 'completed_at']:
            if data.get(key):
                data[key] = datetime.fromisoformat(data[key])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = JobStatus(data['status'])
        
        return cls(**data)


class JobQueueManager:
    """Manages sequential job execution to prevent database conflicts"""
    
    def __init__(self):
        self.job_queue: List[QueuedJob] = []
        self.current_job: Optional[QueuedJob] = None
        self.is_processing = False
        self._lock = asyncio.Lock()
        
    async def add_job(self, dealer_id: str, fetch_type: str, from_time: str = None, 
                     to_time: str = None, no_po: str = None) -> str:
        """Add a job to the queue"""
        async with self._lock:
            job_id = str(uuid.uuid4())
            job = QueuedJob(
                id=job_id,
                dealer_id=dealer_id,
                fetch_type=fetch_type,
                from_time=from_time,
                to_time=to_time,
                no_po=no_po
            )
            
            self.job_queue.append(job)
            logger.info(f"Added job {job_id} to queue: {fetch_type} for dealer {dealer_id}")
            
            # Start processing if not already running
            if not self.is_processing:
                asyncio.create_task(self._process_queue())
            
            return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        async with self._lock:
            # Check current job
            if self.current_job and self.current_job.id == job_id:
                return self.current_job.to_dict()
            
            # Check queue
            for job in self.job_queue:
                if job.id == job_id:
                    return job.to_dict()
            
            return None
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        async with self._lock:
            return {
                "current_job": self.current_job.to_dict() if self.current_job else None,
                "queue_length": len(self.job_queue),
                "queued_jobs": [job.to_dict() for job in self.job_queue],
                "is_processing": self.is_processing
            }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued job (cannot cancel running job)"""
        async with self._lock:
            for i, job in enumerate(self.job_queue):
                if job.id == job_id:
                    job.status = JobStatus.CANCELLED
                    job.completed_at = datetime.utcnow()
                    job.error_message = "Job cancelled by user"
                    self.job_queue.pop(i)
                    logger.info(f"Cancelled job {job_id}")
                    return True
            return False
    
    async def clear_completed_jobs(self) -> int:
        """Clear completed/failed jobs from history"""
        async with self._lock:
            initial_count = len(self.job_queue)
            self.job_queue = [job for job in self.job_queue 
                            if job.status in [JobStatus.QUEUED, JobStatus.RUNNING]]
            cleared_count = initial_count - len(self.job_queue)
            logger.info(f"Cleared {cleared_count} completed jobs")
            return cleared_count
    
    async def _process_queue(self):
        """Process jobs in the queue sequentially"""
        if self.is_processing:
            return
        
        self.is_processing = True
        logger.info("Started job queue processing")
        
        try:
            while True:
                async with self._lock:
                    if not self.job_queue:
                        break
                    
                    # Get next job
                    self.current_job = self.job_queue.pop(0)
                    self.current_job.status = JobStatus.RUNNING
                    self.current_job.started_at = datetime.utcnow()
                
                logger.info(f"Processing job {self.current_job.id}: {self.current_job.fetch_type} for dealer {self.current_job.dealer_id}")
                
                # Execute the job
                await self._execute_job(self.current_job)
                
                # Mark job as completed
                async with self._lock:
                    self.current_job.completed_at = datetime.utcnow()
                    if self.current_job.status == JobStatus.RUNNING:
                        self.current_job.status = JobStatus.COMPLETED
                    
                    logger.info(f"Completed job {self.current_job.id} with status {self.current_job.status.value}")
                    self.current_job = None
                
                # Small delay between jobs to prevent overwhelming the system
                await asyncio.sleep(1)
        
        finally:
            self.is_processing = False
            logger.info("Stopped job queue processing")
    
    async def _execute_job(self, job: QueuedJob):
        """Execute a single job using Celery"""
        from celery_app import celery_app
        
        try:
            # Determine task name and arguments
            if job.fetch_type == "pkb":
                task_name = "tasks.data_fetcher_router.fetch_pkb_data"
                task_args = [job.dealer_id, job.from_time, job.to_time]
            elif job.fetch_type == "parts_inbound":
                task_name = "tasks.data_fetcher_router.fetch_parts_inbound_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or ""]
            elif job.fetch_type == "leasing":
                task_name = "tasks.data_fetcher_router.fetch_leasing_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or ""]
            elif job.fetch_type == "doch_read":
                task_name = "tasks.data_fetcher_router.fetch_document_handling_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            elif job.fetch_type == "uinb_read":
                task_name = "tasks.data_fetcher_router.fetch_unit_inbound_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            elif job.fetch_type == "bast_read":
                task_name = "tasks.data_fetcher_router.fetch_delivery_process_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", "", ""]
            elif job.fetch_type == "inv1_read":
                task_name = "tasks.data_fetcher_router.fetch_billing_process_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            elif job.fetch_type == "mdinvh1_read":
                task_name = "tasks.data_fetcher_router.fetch_unit_invoice_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            elif job.fetch_type == "prsl_read":
                task_name = "tasks.data_fetcher_router.fetch_parts_sales_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or ""]
            elif job.fetch_type == "dphlo_read":
                task_name = "tasks.data_fetcher_router.fetch_dp_hlo_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            elif job.fetch_type == "inv2_read":
                task_name = "tasks.data_fetcher_router.fetch_workshop_invoice_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or ""]
            elif job.fetch_type == "unpaidhlo_read":
                task_name = "tasks.data_fetcher_router.fetch_unpaid_hlo_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            elif job.fetch_type == "mdinvh3_read":
                task_name = "tasks.data_fetcher_router.fetch_parts_invoice_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or ""]
            elif job.fetch_type == "spk_read":
                task_name = "tasks.data_fetcher_router.fetch_spk_dealing_process_data"
                task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
            else:  # prospect
                task_name = "tasks.data_fetcher_router.fetch_prospect_data"
                task_args = [job.dealer_id, job.from_time, job.to_time]
            
            # Execute Celery task synchronously (wait for completion)
            task = celery_app.send_task(task_name, args=task_args)
            job.celery_task_id = task.id
            
            # Wait for task completion
            result = task.get(timeout=300)  # 5 minute timeout
            
            job.result = result
            job.status = JobStatus.COMPLETED
            logger.info(f"Job {job.id} completed successfully: {result}")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Job {job.id} failed: {e}")


# Global job queue manager instance
job_queue_manager = JobQueueManager()


# Convenience functions for easy access
async def add_job_to_queue(dealer_id: str, fetch_type: str, from_time: str = None, 
                          to_time: str = None, no_po: str = None) -> str:
    """Add a job to the global queue"""
    return await job_queue_manager.add_job(dealer_id, fetch_type, from_time, to_time, no_po)


async def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a specific job"""
    return await job_queue_manager.get_job_status(job_id)


async def get_queue_status() -> Dict[str, Any]:
    """Get overall queue status"""
    return await job_queue_manager.get_queue_status()


async def cancel_job(job_id: str) -> bool:
    """Cancel a queued job"""
    return await job_queue_manager.cancel_job(job_id)


async def clear_completed_jobs() -> int:
    """Clear completed jobs"""
    return await job_queue_manager.clear_completed_jobs()
