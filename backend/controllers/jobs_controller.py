"""
Jobs controller for manual job execution and job status management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db, Dealer, FetchLog
from models.schemas import ManualFetchRequest, JobResponse, JobStatusResponse, FetchLogResponse
from .base_controller import BaseController
from celery_app import celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/run", response_model=JobResponse)
async def run_job(request: ManualFetchRequest, db: Session = Depends(get_db)):
    """Execute a manual data fetch job"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, request.dealer_id, Dealer)

    # Determine which task to run based on fetch_type
    if request.fetch_type == "pkb":
        task_name = "tasks.data_fetcher_router.fetch_pkb_data"
        message = "PKB data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time]
    elif request.fetch_type == "parts_inbound":
        task_name = "tasks.data_fetcher_router.fetch_parts_inbound_data"
        message = "Parts Inbound data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po]
    else:
        task_name = "tasks.data_fetcher_router.fetch_prospect_data"
        message = "Prospect data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time]

    # Trigger Celery task
    task = celery_app.send_task(
        task_name,
        args=task_args
    )
    
    BaseController.log_operation("RUN_JOB", f"Started {request.fetch_type} job for dealer {request.dealer_id}, task_id: {task.id}")

    return JobResponse(
        message=message,
        task_id=task.id,
        dealer_id=request.dealer_id,
        fetch_type=request.fetch_type,
        status="running"
    )


@router.get("/{task_id}/status", response_model=JobStatusResponse)
async def get_job_status(task_id: str):
    """Get the status of a specific job"""
    task = celery_app.AsyncResult(task_id)

    # Handle result safely
    result = None
    if task.ready():
        try:
            result = task.result
            # Ensure result is a dict or convert to dict
            if not isinstance(result, dict):
                if hasattr(result, '__dict__'):
                    result = result.__dict__
                else:
                    result = {"value": str(result)}
        except Exception as e:
            result = {"error": str(e)}

    status_response = JobStatusResponse(
        task_id=task_id,
        status=task.status,
        result=result,
        progress="completed" if task.ready() else "running"
    )

    BaseController.log_operation("GET_JOB_STATUS", f"Retrieved status for task {task_id}: {task.status}")
    return status_response


@router.get("/", response_model=List[FetchLogResponse])
async def get_jobs(dealer_id: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    """Get recent jobs with optional dealer filter"""
    query = db.query(FetchLog)
    if dealer_id:
        query = query.filter(FetchLog.dealer_id == dealer_id)

    jobs = query.order_by(FetchLog.completed_at.desc()).limit(limit).all()
    BaseController.convert_list_uuids_to_strings(jobs)
    
    BaseController.log_operation("GET_JOBS", f"Retrieved {len(jobs)} recent jobs")
    return jobs


@router.post("/run-bulk")
async def run_bulk_jobs(
    dealer_ids: List[str],
    fetch_type: str = "prospect",
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Run jobs for multiple dealers"""
    # Validate all dealers exist
    valid_dealers = []
    invalid_dealers = []
    
    for dealer_id in dealer_ids:
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if dealer:
            valid_dealers.append(dealer_id)
        else:
            invalid_dealers.append(dealer_id)
    
    if invalid_dealers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid dealer IDs: {', '.join(invalid_dealers)}"
        )
    
    # Start jobs for all valid dealers
    started_jobs = []
    failed_jobs = []
    
    for dealer_id in valid_dealers:
        try:
            # Determine task name
            if fetch_type == "pkb":
                task_name = "tasks.data_fetcher_router.fetch_pkb_data"
                task_args = [dealer_id, from_time, to_time]
            elif fetch_type == "parts_inbound":
                task_name = "tasks.data_fetcher_router.fetch_parts_inbound_data"
                task_args = [dealer_id, from_time, to_time, ""]
            else:
                task_name = "tasks.data_fetcher_router.fetch_prospect_data"
                task_args = [dealer_id, from_time, to_time]
            
            # Start task
            task = celery_app.send_task(task_name, args=task_args)
            
            started_jobs.append({
                "dealer_id": dealer_id,
                "task_id": task.id,
                "fetch_type": fetch_type,
                "status": "started"
            })
            
        except Exception as e:
            failed_jobs.append({
                "dealer_id": dealer_id,
                "error": str(e)
            })
    
    BaseController.log_operation("RUN_BULK_JOBS", f"Started {len(started_jobs)} jobs, {len(failed_jobs)} failed")
    
    return {
        "message": f"Bulk job execution completed",
        "total_dealers": len(dealer_ids),
        "started_jobs": len(started_jobs),
        "failed_jobs": len(failed_jobs),
        "fetch_type": fetch_type,
        "jobs": started_jobs,
        "failures": failed_jobs
    }


@router.get("/active")
async def get_active_jobs():
    """Get currently active/running jobs"""
    # Get active tasks from Celery
    inspect = celery_app.control.inspect()
    
    try:
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        all_active = []
        
        # Process active tasks
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    all_active.append({
                        "task_id": task["id"],
                        "task_name": task["name"],
                        "worker": worker,
                        "status": "active",
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {})
                    })
        
        # Process scheduled tasks
        if scheduled_tasks:
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    all_active.append({
                        "task_id": task["request"]["id"],
                        "task_name": task["request"]["task"],
                        "worker": worker,
                        "status": "scheduled",
                        "eta": task.get("eta"),
                        "args": task["request"].get("args", []),
                        "kwargs": task["request"].get("kwargs", {})
                    })
        
        # Process reserved tasks
        if reserved_tasks:
            for worker, tasks in reserved_tasks.items():
                for task in tasks:
                    all_active.append({
                        "task_id": task["id"],
                        "task_name": task["name"],
                        "worker": worker,
                        "status": "reserved",
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {})
                    })
        
        BaseController.log_operation("GET_ACTIVE_JOBS", f"Retrieved {len(all_active)} active jobs")
        
        return {
            "active_jobs_count": len(all_active),
            "jobs": all_active
        }
        
    except Exception as e:
        BaseController.log_operation("GET_ACTIVE_JOBS_ERROR", f"Failed to retrieve active jobs: {str(e)}")
        return {
            "error": "Failed to retrieve active jobs",
            "message": str(e),
            "active_jobs_count": 0,
            "jobs": []
        }


@router.delete("/{task_id}/cancel")
async def cancel_job(task_id: str):
    """Cancel a running job"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        
        BaseController.log_operation("CANCEL_JOB", f"Cancelled job {task_id}")
        
        return {
            "message": f"Job {task_id} cancellation requested",
            "task_id": task_id,
            "status": "cancelled"
        }
        
    except Exception as e:
        BaseController.log_operation("CANCEL_JOB_ERROR", f"Failed to cancel job {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get("/health")
async def get_job_system_health():
    """Get job system health status"""
    try:
        # Check Celery workers
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        worker_count = len(stats) if stats else 0
        workers_online = list(stats.keys()) if stats else []
        
        # Get queue lengths (if available)
        reserved = inspect.reserved()
        active = inspect.active()
        
        total_reserved = sum(len(tasks) for tasks in reserved.values()) if reserved else 0
        total_active = sum(len(tasks) for tasks in active.values()) if active else 0
        
        health_status = {
            "status": "healthy" if worker_count > 0 else "unhealthy",
            "worker_count": worker_count,
            "workers_online": workers_online,
            "total_active_jobs": total_active,
            "total_reserved_jobs": total_reserved,
            "celery_available": True
        }
        
        BaseController.log_operation("GET_JOB_HEALTH", f"Job system health check: {worker_count} workers online")
        
        return health_status
        
    except Exception as e:
        BaseController.log_operation("GET_JOB_HEALTH_ERROR", f"Job system health check failed: {str(e)}")
        
        return {
            "status": "unhealthy",
            "error": str(e),
            "celery_available": False,
            "worker_count": 0,
            "workers_online": [],
            "total_active_jobs": 0,
            "total_reserved_jobs": 0
        }
