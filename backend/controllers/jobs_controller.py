"""
Jobs controller for manual job execution and job status management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from database import get_db, Dealer, FetchLog
from models.schemas import ManualFetchRequest, JobResponse, JobStatusResponse, FetchLogResponse, BulkJobRequest
from .base_controller import BaseController
from celery_app import celery_app
from job_queue_manager import add_job_to_queue, get_job_status as get_queue_job_status, get_queue_status, cancel_job as cancel_queue_job, clear_completed_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


# NEW: Queue-based job endpoints
@router.post("/queue", response_model=Dict[str, Any])
async def add_job_to_queue_endpoint(request: ManualFetchRequest, db: Session = Depends(get_db)):
    """Add a job to the sequential queue (RECOMMENDED - prevents database conflicts)"""
    # Validate dealer exists
    BaseController.validate_dealer_exists(db, request.dealer_id, Dealer)

    # Add job to queue
    job_id = await add_job_to_queue(
        dealer_id=request.dealer_id,
        fetch_type=request.fetch_type,
        from_time=request.from_time,
        to_time=request.to_time,
        no_po=request.no_po
    )

    BaseController.log_operation("ADD_JOB_TO_QUEUE", f"Added {request.fetch_type} job for dealer {request.dealer_id} to queue: {job_id}")

    return {
        "message": f"{request.fetch_type.title()} job added to queue",
        "job_id": job_id,
        "dealer_id": request.dealer_id,
        "fetch_type": request.fetch_type,
        "status": "queued"
    }


@router.get("/queue/status")
async def get_queue_status_endpoint():
    """Get overall queue status"""
    status = await get_queue_status()
    BaseController.log_operation("GET_QUEUE_STATUS", f"Queue status: {status['queue_length']} jobs queued, processing: {status['is_processing']}")
    return status


@router.get("/queue/{job_id}/status")
async def get_queue_job_status_endpoint(job_id: str):
    """Get status of a specific queued job"""
    status = await get_queue_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")

    BaseController.log_operation("GET_QUEUE_JOB_STATUS", f"Retrieved queue job status for {job_id}: {status['status']}")
    return status


@router.delete("/queue/{job_id}")
async def cancel_queue_job_endpoint(job_id: str):
    """Cancel a queued job"""
    success = await cancel_queue_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")

    BaseController.log_operation("CANCEL_QUEUE_JOB", f"Cancelled queue job {job_id}")
    return {"message": f"Job {job_id} cancelled", "job_id": job_id, "status": "cancelled"}


@router.delete("/queue/completed")
async def clear_completed_jobs_endpoint():
    """Clear completed jobs from queue"""
    cleared_count = await clear_completed_jobs()
    BaseController.log_operation("CLEAR_COMPLETED_JOBS", f"Cleared {cleared_count} completed jobs")
    return {"message": f"Cleared {cleared_count} completed jobs", "cleared_count": cleared_count}


@router.post("/queue/bulk")
async def add_bulk_jobs_to_queue(
    request: BulkJobRequest,
    db: Session = Depends(get_db)
):
    """Add multiple jobs to queue (RECOMMENDED for bulk operations)"""
    # Validate all dealers exist
    valid_dealers = []
    invalid_dealers = []

    for dealer_id in request.dealer_ids:
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

    # Add jobs to queue
    queued_jobs = []
    failed_jobs = []

    for dealer_id in valid_dealers:
        try:
            job_id = await add_job_to_queue(
                dealer_id=dealer_id,
                fetch_type=request.fetch_type,
                from_time=request.from_time,
                to_time=request.to_time
            )

            queued_jobs.append({
                "dealer_id": dealer_id,
                "job_id": job_id,
                "fetch_type": request.fetch_type,
                "status": "queued"
            })

        except Exception as e:
            failed_jobs.append({
                "dealer_id": dealer_id,
                "error": str(e)
            })

    BaseController.log_operation("ADD_BULK_JOBS_TO_QUEUE", f"Added {len(queued_jobs)} jobs to queue, {len(failed_jobs)} failed")

    return {
        "message": "Bulk jobs added to queue",
        "total_dealers": len(request.dealer_ids),
        "queued_jobs": len(queued_jobs),
        "failed_jobs": len(failed_jobs),
        "fetch_type": request.fetch_type,
        "jobs": queued_jobs,
        "failures": failed_jobs
    }


# LEGACY: Direct Celery execution (may cause database conflicts in parallel)
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
    elif request.fetch_type == "leasing":
        task_name = "tasks.data_fetcher_router.fetch_leasing_data"
        message = "Leasing data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po]
    elif request.fetch_type == "doch_read":
        task_name = "tasks.data_fetcher_router.fetch_document_handling_data"
        message = "Document handling data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po, ""]
    elif request.fetch_type == "uinb_read":
        task_name = "tasks.data_fetcher_router.fetch_unit_inbound_data"
        message = "Unit inbound data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po, ""]
    elif request.fetch_type == "bast_read":
        task_name = "tasks.data_fetcher_router.fetch_delivery_process_data"
        message = "Delivery process data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po, "", ""]
    elif request.fetch_type == "inv1_read":
        task_name = "tasks.data_fetcher_router.fetch_billing_process_data"
        message = "Billing process data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po, ""]
    elif request.fetch_type == "mdinvh1_read":
        task_name = "tasks.data_fetcher_router.fetch_unit_invoice_data"
        message = "Unit invoice data fetch job started"
        task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po, ""]
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
            elif fetch_type == "leasing":
                task_name = "tasks.data_fetcher_router.fetch_leasing_data"
                task_args = [dealer_id, from_time, to_time, ""]
            elif fetch_type == "doch_read":
                task_name = "tasks.data_fetcher_router.fetch_document_handling_data"
                task_args = [dealer_id, from_time, to_time, "", ""]
            elif fetch_type == "uinb_read":
                task_name = "tasks.data_fetcher_router.fetch_unit_inbound_data"
                task_args = [dealer_id, from_time, to_time, "", ""]
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
