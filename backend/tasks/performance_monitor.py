"""
Performance Monitoring for Batch Processing
Comprehensive monitoring, metrics collection, and performance analysis
"""

import time
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import psutil
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class JobPerformanceData:
    """Performance data for a specific job"""
    job_id: str
    dealer_id: str
    job_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    records_processed: int = 0
    records_per_second: Optional[float] = None
    memory_usage_mb: List[float] = field(default_factory=list)
    cpu_usage_percent: List[float] = field(default_factory=list)
    database_operations: int = 0
    api_calls: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        
        # Metrics storage
        self.metrics: deque = deque(maxlen=max_metrics_history)
        self.job_performance: Dict[str, JobPerformanceData] = {}
        
        # Aggregated statistics
        self.stats = {
            'total_jobs': 0,
            'successful_jobs': 0,
            'failed_jobs': 0,
            'average_duration': 0.0,
            'average_throughput': 0.0,  # records per second
            'peak_memory_usage': 0.0,
            'peak_cpu_usage': 0.0,
            'total_records_processed': 0,
            'total_api_calls': 0,
            'total_database_operations': 0
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_job_duration': 3600,  # 1 hour
            'min_throughput': 10,      # records per second
            'max_memory_usage': 80,    # percent
            'max_cpu_usage': 90,       # percent
            'max_error_rate': 5        # percent
        }
        
        # Background monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """Start background performance monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
            self.monitor_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def start_job_monitoring(self, job_id: str, dealer_id: str, job_type: str) -> JobPerformanceData:
        """Start monitoring a specific job"""
        job_data = JobPerformanceData(
            job_id=job_id,
            dealer_id=dealer_id,
            job_type=job_type,
            start_time=datetime.now(timezone.utc)
        )
        
        with self.lock:
            self.job_performance[job_id] = job_data
            self.stats['total_jobs'] += 1
        
        logger.info(f"Started monitoring job {job_id} ({job_type}) for dealer {dealer_id}")
        return job_data
    
    def end_job_monitoring(self, job_id: str, success: bool = True, 
                          records_processed: int = 0, errors: List[str] = None,
                          warnings: List[str] = None):
        """End monitoring for a specific job"""
        with self.lock:
            job_data = self.job_performance.get(job_id)
            if not job_data:
                logger.warning(f"Job {job_id} not found in performance monitoring")
                return
            
            # Update job completion data
            job_data.end_time = datetime.now(timezone.utc)
            job_data.duration_seconds = (job_data.end_time - job_data.start_time).total_seconds()
            job_data.records_processed = records_processed
            
            if job_data.duration_seconds > 0:
                job_data.records_per_second = records_processed / job_data.duration_seconds
            
            if errors:
                job_data.errors.extend(errors)
            if warnings:
                job_data.warnings.extend(warnings)
            
            # Update global statistics
            if success:
                self.stats['successful_jobs'] += 1
            else:
                self.stats['failed_jobs'] += 1
            
            self.stats['total_records_processed'] += records_processed
            
            # Update averages
            total_completed = self.stats['successful_jobs'] + self.stats['failed_jobs']
            if total_completed > 0:
                # Update average duration
                current_avg_duration = self.stats['average_duration']
                self.stats['average_duration'] = (
                    (current_avg_duration * (total_completed - 1) + job_data.duration_seconds) 
                    / total_completed
                )
                
                # Update average throughput
                if job_data.records_per_second:
                    current_avg_throughput = self.stats['average_throughput']
                    self.stats['average_throughput'] = (
                        (current_avg_throughput * (total_completed - 1) + job_data.records_per_second) 
                        / total_completed
                    )
        
        logger.info(f"Completed monitoring job {job_id}: "
                   f"{records_processed} records in {job_data.duration_seconds:.2f}s "
                   f"({job_data.records_per_second:.2f} records/sec)")
    
    def record_metric(self, metric_name: str, value: float, unit: str = "", 
                     tags: Dict[str, str] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now(timezone.utc),
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
        
        # Update peak values
        if metric_name == "memory_usage_percent" and value > self.stats['peak_memory_usage']:
            self.stats['peak_memory_usage'] = value
        elif metric_name == "cpu_usage_percent" and value > self.stats['peak_cpu_usage']:
            self.stats['peak_cpu_usage'] = value
    
    def record_job_resource_usage(self, job_id: str, memory_mb: float, cpu_percent: float):
        """Record resource usage for a specific job"""
        with self.lock:
            job_data = self.job_performance.get(job_id)
            if job_data:
                job_data.memory_usage_mb.append(memory_mb)
                job_data.cpu_usage_percent.append(cpu_percent)
    
    def record_database_operation(self, job_id: str, operation_count: int = 1):
        """Record database operations for a job"""
        with self.lock:
            job_data = self.job_performance.get(job_id)
            if job_data:
                job_data.database_operations += operation_count
                self.stats['total_database_operations'] += operation_count
    
    def record_api_call(self, job_id: str, call_count: int = 1):
        """Record API calls for a job"""
        with self.lock:
            job_data = self.job_performance.get(job_id)
            if job_data:
                job_data.api_calls += call_count
                self.stats['total_api_calls'] += call_count
    
    def _monitor_system(self):
        """Background system monitoring"""
        while self.monitoring_active:
            try:
                # Get system metrics
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                disk = psutil.disk_usage('/')
                
                # Record system metrics
                self.record_metric("memory_usage_percent", memory.percent, "%")
                self.record_metric("memory_available_gb", memory.available / (1024**3), "GB")
                self.record_metric("cpu_usage_percent", cpu_percent, "%")
                self.record_metric("disk_usage_percent", disk.percent, "%")
                
                # Check for performance issues
                self._check_performance_thresholds()
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(5)
    
    def _check_performance_thresholds(self):
        """Check if performance thresholds are exceeded"""
        current_time = datetime.now(timezone.utc)
        
        # Check running jobs for performance issues
        with self.lock:
            for job_id, job_data in self.job_performance.items():
                if job_data.end_time is None:  # Job is still running
                    duration = (current_time - job_data.start_time).total_seconds()
                    
                    # Check job duration
                    if duration > self.thresholds['max_job_duration']:
                        logger.warning(f"Job {job_id} has been running for {duration:.0f}s "
                                     f"(threshold: {self.thresholds['max_job_duration']}s)")
                    
                    # Check throughput (if we have processed records)
                    if job_data.records_processed > 0 and duration > 60:  # At least 1 minute
                        current_throughput = job_data.records_processed / duration
                        if current_throughput < self.thresholds['min_throughput']:
                            logger.warning(f"Job {job_id} throughput is {current_throughput:.2f} records/sec "
                                         f"(threshold: {self.thresholds['min_throughput']} records/sec)")
    
    def get_job_performance(self, job_id: str) -> Optional[JobPerformanceData]:
        """Get performance data for a specific job"""
        return self.job_performance.get(job_id)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        with self.lock:
            # Calculate error rate
            total_completed = self.stats['successful_jobs'] + self.stats['failed_jobs']
            error_rate = (self.stats['failed_jobs'] / total_completed * 100) if total_completed > 0 else 0
            
            # Get recent system metrics
            recent_metrics = list(self.metrics)[-10:] if self.metrics else []
            current_memory = next((m.value for m in reversed(recent_metrics) 
                                 if m.metric_name == "memory_usage_percent"), 0)
            current_cpu = next((m.value for m in reversed(recent_metrics) 
                              if m.metric_name == "cpu_usage_percent"), 0)
            
            return {
                'statistics': dict(self.stats),
                'error_rate_percent': error_rate,
                'current_system': {
                    'memory_usage_percent': current_memory,
                    'cpu_usage_percent': current_cpu
                },
                'active_jobs': len([j for j in self.job_performance.values() if j.end_time is None]),
                'total_jobs_tracked': len(self.job_performance),
                'performance_issues': self._get_performance_issues()
            }
    
    def _get_performance_issues(self) -> List[str]:
        """Get list of current performance issues"""
        issues = []
        
        # Check error rate
        total_completed = self.stats['successful_jobs'] + self.stats['failed_jobs']
        if total_completed > 0:
            error_rate = self.stats['failed_jobs'] / total_completed * 100
            if error_rate > self.thresholds['max_error_rate']:
                issues.append(f"High error rate: {error_rate:.1f}%")
        
        # Check system resources
        if self.stats['peak_memory_usage'] > self.thresholds['max_memory_usage']:
            issues.append(f"High memory usage: {self.stats['peak_memory_usage']:.1f}%")
        
        if self.stats['peak_cpu_usage'] > self.thresholds['max_cpu_usage']:
            issues.append(f"High CPU usage: {self.stats['peak_cpu_usage']:.1f}%")
        
        # Check throughput
        if (self.stats['average_throughput'] > 0 and 
            self.stats['average_throughput'] < self.thresholds['min_throughput']):
            issues.append(f"Low throughput: {self.stats['average_throughput']:.2f} records/sec")
        
        return issues
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': self.get_performance_summary(),
            'job_performance': {
                job_id: {
                    'job_id': job_data.job_id,
                    'dealer_id': job_data.dealer_id,
                    'job_type': job_data.job_type,
                    'start_time': job_data.start_time.isoformat(),
                    'end_time': job_data.end_time.isoformat() if job_data.end_time else None,
                    'duration_seconds': job_data.duration_seconds,
                    'records_processed': job_data.records_processed,
                    'records_per_second': job_data.records_per_second,
                    'avg_memory_usage_mb': sum(job_data.memory_usage_mb) / len(job_data.memory_usage_mb) if job_data.memory_usage_mb else 0,
                    'avg_cpu_usage_percent': sum(job_data.cpu_usage_percent) / len(job_data.cpu_usage_percent) if job_data.cpu_usage_percent else 0,
                    'database_operations': job_data.database_operations,
                    'api_calls': job_data.api_calls,
                    'error_count': len(job_data.errors),
                    'warning_count': len(job_data.warnings)
                }
                for job_id, job_data in self.job_performance.items()
            }
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
