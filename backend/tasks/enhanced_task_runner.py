"""
Enhanced Task Runner for Batch Processing
Integrates all performance improvements: job queue, monitoring, bulk operations
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from .job_queue_manager import job_queue_manager, JobPriority
from .performance_monitor import performance_monitor
from .batch_config import BatchProcessingConfig, get_processor_config
from .processors.base_processor import BaseDataProcessor

# Import all processors
from .processors.prospect_processor import ProspectDataProcessor
from .processors.pkb_processor import PKBDataProcessor
from .processors.parts_inbound_processor import PartsInboundDataProcessor
from .processors.leasing_processor import LeasingDataProcessor
from .processors.document_handling_processor import DocumentHandlingDataProcessor
from .processors.unit_inbound_processor import UnitInboundDataProcessor
from .processors.delivery_process_processor import DeliveryProcessDataProcessor
from .processors.billing_process_processor import BillingProcessDataProcessor
from .processors.unit_invoice_processor import UnitInvoiceDataProcessor
from .processors.parts_sales_processor import PartsSalesDataProcessor
from .processors.dp_hlo_processor import DPHLODataProcessor
from .processors.workshop_invoice_processor import WorkshopInvoiceDataProcessor
from .processors.unpaid_hlo_processor import UnpaidHLODataProcessor
from .processors.parts_invoice_processor import PartsInvoiceDataProcessor

logger = logging.getLogger(__name__)

class EnhancedTaskRunner:
    """Enhanced task runner with performance optimizations"""
    
    def __init__(self):
        self.processors = {
            'prospect': ProspectDataProcessor(),
            'pkb': PKBDataProcessor(),
            'parts_inbound': PartsInboundDataProcessor(),
            'leasing': LeasingDataProcessor(),
            'document_handling': DocumentHandlingDataProcessor(),
            'unit_inbound': UnitInboundDataProcessor(),
            'delivery_process': DeliveryProcessDataProcessor(),
            'billing_process': BillingProcessDataProcessor(),
            'unit_invoice': UnitInvoiceDataProcessor(),
            'parts_sales': PartsSalesDataProcessor(),
            'dp_hlo': DPHLODataProcessor(),
            'workshop_invoice': WorkshopInvoiceDataProcessor(),
            'unpaid_hlo': UnpaidHLODataProcessor(),
            'parts_invoice': PartsInvoiceDataProcessor()
        }
        
        # Start monitoring
        performance_monitor.start_monitoring()
        
        logger.info("Enhanced Task Runner initialized with performance optimizations")
    
    def run_single_task(self, processor_type: str, dealer_id: str, 
                       from_time: str = None, to_time: str = None, 
                       priority: str = "normal", **kwargs) -> Dict[str, Any]:
        """Run a single batch processing task with enhanced monitoring"""
        
        # Validate processor type
        if processor_type not in self.processors:
            raise ValueError(f"Unknown processor type: {processor_type}")
        
        # Generate unique job ID
        job_id = f"{processor_type}_{dealer_id}_{uuid.uuid4().hex[:8]}"
        
        # Get processor configuration
        processor_config = get_processor_config(processor_type)
        
        # Convert priority string to enum
        priority_map = {
            "low": JobPriority.LOW,
            "normal": JobPriority.NORMAL,
            "high": JobPriority.HIGH,
            "critical": JobPriority.CRITICAL
        }
        job_priority = priority_map.get(priority.lower(), JobPriority.NORMAL)
        
        # Submit job to queue
        success = job_queue_manager.submit_job(
            job_id=job_id,
            dealer_id=dealer_id,
            job_type=processor_type,
            job_function=self._execute_processor_job,
            job_args=(processor_type, dealer_id, from_time, to_time, job_id),
            job_kwargs=kwargs,
            priority=job_priority,
            estimated_duration=processor_config.get("estimated_duration", 600)
        )
        
        if not success:
            return {
                "success": False,
                "error": "Failed to submit job to queue (dealer may have too many running jobs)",
                "job_id": job_id
            }
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Job {job_id} submitted successfully",
            "estimated_duration": processor_config.get("estimated_duration", 600)
        }
    
    def _execute_processor_job(self, processor_type: str, dealer_id: str, 
                              from_time: str, to_time: str, job_id: str, **kwargs) -> Dict[str, Any]:
        """Execute a processor job with performance monitoring"""
        
        # Start performance monitoring
        job_perf = performance_monitor.start_job_monitoring(job_id, dealer_id, processor_type)
        
        processor = self.processors[processor_type]
        errors = []
        warnings = []
        records_processed = 0
        
        try:
            logger.info(f"Starting enhanced batch job {job_id} ({processor_type}) for dealer {dealer_id}")
            
            # Execute the processor
            result = processor.execute(dealer_id, from_time, to_time, **kwargs)
            
            # Extract results
            if isinstance(result, dict):
                records_processed = result.get('records_processed', 0)
                if result.get('errors'):
                    errors.extend(result['errors'])
                if result.get('warnings'):
                    warnings.extend(result['warnings'])
            else:
                records_processed = result if isinstance(result, int) else 0
            
            # Record successful completion
            performance_monitor.end_job_monitoring(
                job_id, 
                success=True, 
                records_processed=records_processed,
                errors=errors,
                warnings=warnings
            )
            
            logger.info(f"Completed batch job {job_id}: {records_processed} records processed")
            
            return {
                "success": True,
                "records_processed": records_processed,
                "errors": errors,
                "warnings": warnings,
                "duration_seconds": job_perf.duration_seconds
            }
            
        except Exception as e:
            error_msg = str(e)
            errors.append(error_msg)
            
            # Record failed completion
            performance_monitor.end_job_monitoring(
                job_id, 
                success=False, 
                records_processed=records_processed,
                errors=errors,
                warnings=warnings
            )
            
            logger.error(f"Batch job {job_id} failed: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "records_processed": records_processed,
                "errors": errors,
                "warnings": warnings
            }
    
    def run_multiple_tasks(self, tasks: List[Dict[str, Any]], 
                          max_concurrent: int = None) -> Dict[str, Any]:
        """Run multiple batch processing tasks concurrently"""
        
        if max_concurrent is None:
            max_concurrent = BatchProcessingConfig.MAX_CONCURRENT_JOBS
        
        results = {}
        submitted_jobs = []
        
        # Submit all jobs
        for task in tasks:
            processor_type = task.get('processor_type')
            dealer_id = task.get('dealer_id')
            from_time = task.get('from_time')
            to_time = task.get('to_time')
            priority = task.get('priority', 'normal')
            
            if not processor_type or not dealer_id:
                results[f"invalid_task_{len(results)}"] = {
                    "success": False,
                    "error": "Missing processor_type or dealer_id"
                }
                continue
            
            result = self.run_single_task(
                processor_type, dealer_id, from_time, to_time, priority, 
                **task.get('kwargs', {})
            )
            
            if result['success']:
                submitted_jobs.append(result['job_id'])
            
            results[result['job_id']] = result
        
        return {
            "submitted_jobs": submitted_jobs,
            "total_submitted": len(submitted_jobs),
            "total_failed_to_submit": len(tasks) - len(submitted_jobs),
            "results": results
        }
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a specific job"""
        
        # Get job queue status
        queue_status = job_queue_manager.get_job_status(job_id)
        
        # Get performance data
        perf_data = performance_monitor.get_job_performance(job_id)
        
        if not queue_status and not perf_data:
            return {"error": f"Job {job_id} not found"}
        
        result = {}
        
        if queue_status:
            result.update({
                "job_id": queue_status.job_id,
                "dealer_id": queue_status.dealer_id,
                "job_type": queue_status.job_type,
                "status": queue_status.status.value,
                "priority": queue_status.priority.name,
                "created_at": queue_status.created_at.isoformat(),
                "started_at": queue_status.started_at.isoformat() if queue_status.started_at else None,
                "completed_at": queue_status.completed_at.isoformat() if queue_status.completed_at else None,
                "error_message": queue_status.error_message,
                "progress": queue_status.progress
            })
        
        if perf_data:
            result.update({
                "performance": {
                    "records_processed": perf_data.records_processed,
                    "records_per_second": perf_data.records_per_second,
                    "duration_seconds": perf_data.duration_seconds,
                    "database_operations": perf_data.database_operations,
                    "api_calls": perf_data.api_calls,
                    "avg_memory_usage_mb": (
                        sum(perf_data.memory_usage_mb) / len(perf_data.memory_usage_mb) 
                        if perf_data.memory_usage_mb else 0
                    ),
                    "avg_cpu_usage_percent": (
                        sum(perf_data.cpu_usage_percent) / len(perf_data.cpu_usage_percent) 
                        if perf_data.cpu_usage_percent else 0
                    ),
                    "error_count": len(perf_data.errors),
                    "warning_count": len(perf_data.warnings)
                }
            })
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        
        # Get queue status
        queue_status = job_queue_manager.get_queue_status()
        
        # Get performance summary
        perf_summary = performance_monitor.get_performance_summary()
        
        return {
            "queue_status": queue_status,
            "performance_summary": perf_summary,
            "processors_available": list(self.processors.keys()),
            "configuration": {
                "max_concurrent_jobs": BatchProcessingConfig.MAX_CONCURRENT_JOBS,
                "max_jobs_per_dealer": BatchProcessingConfig.MAX_JOBS_PER_DEALER,
                "memory_threshold": BatchProcessingConfig.MEMORY_THRESHOLD_PERCENT,
                "cpu_threshold": BatchProcessingConfig.CPU_THRESHOLD_PERCENT
            }
        }
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a job"""
        success = job_queue_manager.cancel_job(job_id)
        
        return {
            "success": success,
            "message": f"Job {job_id} {'cancelled' if success else 'could not be cancelled'}"
        }
    
    def shutdown(self):
        """Shutdown the task runner"""
        logger.info("Shutting down Enhanced Task Runner...")
        
        # Stop monitoring
        performance_monitor.stop_monitoring()
        
        # Shutdown job queue manager
        job_queue_manager.shutdown()
        
        logger.info("Enhanced Task Runner shutdown complete")

# Global instance
enhanced_task_runner = EnhancedTaskRunner()
