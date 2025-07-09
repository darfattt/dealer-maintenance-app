"""
Job Queue Manager for Batch Processing
Manages concurrent job execution, resource monitoring, and job prioritization
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import psutil
import queue

logger = logging.getLogger(__name__)

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JobInfo:
    """Information about a batch job"""
    job_id: str
    dealer_id: str
    job_type: str
    priority: JobPriority
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    error_message: Optional[str] = None
    progress: float = 0.0
    estimated_duration: Optional[int] = None  # seconds
    actual_duration: Optional[int] = None  # seconds
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.memory_threshold_percent = 80  # Stop new jobs if memory > 80%
        self.cpu_threshold_percent = 90     # Stop new jobs if CPU > 90%
    
    def get_system_stats(self) -> Dict[str, float]:
        """Get current system resource usage"""
        return {
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_percent': psutil.cpu_percent(interval=1),
            'disk_percent': psutil.disk_usage('/').percent,
            'available_memory_gb': psutil.virtual_memory().available / (1024**3)
        }
    
    def can_start_new_job(self) -> bool:
        """Check if system resources allow starting a new job"""
        stats = self.get_system_stats()
        
        if stats['memory_percent'] > self.memory_threshold_percent:
            logger.warning(f"Memory usage too high: {stats['memory_percent']:.1f}%")
            return False
        
        if stats['cpu_percent'] > self.cpu_threshold_percent:
            logger.warning(f"CPU usage too high: {stats['cpu_percent']:.1f}%")
            return False
        
        return True

class JobQueueManager:
    """Manages batch job execution with resource monitoring and concurrency control"""
    
    def __init__(self, max_concurrent_jobs: int = 3, max_jobs_per_dealer: int = 1):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_jobs_per_dealer = max_jobs_per_dealer
        
        # Job tracking
        self.jobs: Dict[str, JobInfo] = {}
        self.job_queue = queue.PriorityQueue()
        self.running_jobs: Dict[str, threading.Thread] = {}
        self.dealer_job_count: Dict[str, int] = {}
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        
        # Thread management
        self.shutdown_event = threading.Event()
        self.queue_processor_thread = None
        self.monitor_thread = None
        
        # Statistics
        self.stats = {
            'total_jobs_processed': 0,
            'total_jobs_failed': 0,
            'average_job_duration': 0.0,
            'peak_concurrent_jobs': 0
        }
        
        self._start_background_threads()
    
    def _start_background_threads(self):
        """Start background threads for queue processing and monitoring"""
        self.queue_processor_thread = threading.Thread(
            target=self._process_job_queue, 
            daemon=True
        )
        self.queue_processor_thread.start()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_jobs, 
            daemon=True
        )
        self.monitor_thread.start()
    
    def submit_job(self, job_id: str, dealer_id: str, job_type: str, 
                   job_function: Callable, job_args: tuple = (), 
                   job_kwargs: dict = None, priority: JobPriority = JobPriority.NORMAL,
                   estimated_duration: int = None) -> bool:
        """Submit a job to the queue"""
        
        if job_kwargs is None:
            job_kwargs = {}
        
        # Check if dealer already has too many jobs
        if self.dealer_job_count.get(dealer_id, 0) >= self.max_jobs_per_dealer:
            logger.warning(f"Dealer {dealer_id} already has {self.max_jobs_per_dealer} jobs running")
            return False
        
        # Create job info
        job_info = JobInfo(
            job_id=job_id,
            dealer_id=dealer_id,
            job_type=job_type,
            priority=priority,
            estimated_duration=estimated_duration
        )
        
        self.jobs[job_id] = job_info
        
        # Add to priority queue (lower number = higher priority)
        priority_value = 5 - priority.value  # Invert priority for queue
        self.job_queue.put((priority_value, time.time(), job_id, job_function, job_args, job_kwargs))
        
        logger.info(f"Job {job_id} submitted for dealer {dealer_id} with priority {priority.name}")
        return True
    
    def _process_job_queue(self):
        """Background thread to process the job queue"""
        while not self.shutdown_event.is_set():
            try:
                # Check if we can start new jobs
                if (len(self.running_jobs) >= self.max_concurrent_jobs or 
                    not self.resource_monitor.can_start_new_job()):
                    time.sleep(5)  # Wait before checking again
                    continue
                
                # Get next job from queue (with timeout to allow shutdown)
                try:
                    priority, timestamp, job_id, job_function, job_args, job_kwargs = \
                        self.job_queue.get(timeout=5)
                except queue.Empty:
                    continue
                
                # Start the job
                self._start_job(job_id, job_function, job_args, job_kwargs)
                
            except Exception as e:
                logger.error(f"Error in job queue processor: {e}")
                time.sleep(1)
    
    def _start_job(self, job_id: str, job_function: Callable, job_args: tuple, job_kwargs: dict):
        """Start executing a job"""
        job_info = self.jobs.get(job_id)
        if not job_info:
            logger.error(f"Job {job_id} not found in jobs registry")
            return
        
        # Update job status
        job_info.status = JobStatus.RUNNING
        job_info.started_at = datetime.now(timezone.utc)
        
        # Update dealer job count
        self.dealer_job_count[job_info.dealer_id] = \
            self.dealer_job_count.get(job_info.dealer_id, 0) + 1
        
        # Create and start job thread
        job_thread = threading.Thread(
            target=self._execute_job,
            args=(job_id, job_function, job_args, job_kwargs),
            daemon=True
        )
        
        self.running_jobs[job_id] = job_thread
        job_thread.start()
        
        # Update peak concurrent jobs stat
        current_concurrent = len(self.running_jobs)
        if current_concurrent > self.stats['peak_concurrent_jobs']:
            self.stats['peak_concurrent_jobs'] = current_concurrent
        
        logger.info(f"Started job {job_id} ({current_concurrent}/{self.max_concurrent_jobs} concurrent)")
    
    def _execute_job(self, job_id: str, job_function: Callable, job_args: tuple, job_kwargs: dict):
        """Execute a job and handle completion"""
        job_info = self.jobs.get(job_id)
        if not job_info:
            return
        
        try:
            # Execute the job function
            result = job_function(*job_args, **job_kwargs)
            
            # Mark job as completed
            job_info.status = JobStatus.COMPLETED
            job_info.completed_at = datetime.now(timezone.utc)
            
            if job_info.started_at:
                duration = (job_info.completed_at - job_info.started_at).total_seconds()
                job_info.actual_duration = int(duration)
            
            self.stats['total_jobs_processed'] += 1
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            # Mark job as failed
            job_info.status = JobStatus.FAILED
            job_info.completed_at = datetime.now(timezone.utc)
            job_info.error_message = str(e)
            
            self.stats['total_jobs_failed'] += 1
            logger.error(f"Job {job_id} failed: {e}")
        
        finally:
            # Clean up
            self._cleanup_job(job_id)
    
    def _cleanup_job(self, job_id: str):
        """Clean up after job completion"""
        job_info = self.jobs.get(job_id)
        if job_info:
            # Update dealer job count
            self.dealer_job_count[job_info.dealer_id] = \
                max(0, self.dealer_job_count.get(job_info.dealer_id, 0) - 1)
        
        # Remove from running jobs
        if job_id in self.running_jobs:
            del self.running_jobs[job_id]
        
        logger.debug(f"Cleaned up job {job_id}")
    
    def _monitor_jobs(self):
        """Background thread to monitor running jobs"""
        while not self.shutdown_event.is_set():
            try:
                current_time = datetime.now(timezone.utc)
                
                # Monitor resource usage for running jobs
                for job_id in list(self.running_jobs.keys()):
                    job_info = self.jobs.get(job_id)
                    if job_info and job_info.status == JobStatus.RUNNING:
                        # Update resource usage (simplified)
                        stats = self.resource_monitor.get_system_stats()
                        job_info.memory_usage_mb = stats.get('available_memory_gb', 0) * 1024
                        job_info.cpu_usage_percent = stats.get('cpu_percent', 0)
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in job monitor: {e}")
                time.sleep(5)
    
    def get_job_status(self, job_id: str) -> Optional[JobInfo]:
        """Get status of a specific job"""
        return self.jobs.get(job_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        return {
            'queued_jobs': self.job_queue.qsize(),
            'running_jobs': len(self.running_jobs),
            'total_jobs': len(self.jobs),
            'system_resources': self.resource_monitor.get_system_stats(),
            'statistics': self.stats
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        job_info = self.jobs.get(job_id)
        if not job_info:
            return False
        
        if job_info.status == JobStatus.PENDING:
            job_info.status = JobStatus.CANCELLED
            return True
        elif job_info.status == JobStatus.RUNNING:
            # Note: Cannot forcefully stop running threads in Python
            # This would require cooperation from the job function
            logger.warning(f"Cannot cancel running job {job_id} - requires job cooperation")
            return False
        
        return False
    
    def shutdown(self):
        """Shutdown the job queue manager"""
        logger.info("Shutting down job queue manager...")
        self.shutdown_event.set()
        
        # Wait for background threads to finish
        if self.queue_processor_thread:
            self.queue_processor_thread.join(timeout=10)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        logger.info("Job queue manager shutdown complete")

# Global instance
job_queue_manager = JobQueueManager()
