"""
Customer satisfaction controller with business logic for file uploads and data retrieval
"""

import logging
import os
import pandas as pd
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.customer_satisfaction_repository import CustomerSatisfactionRepository
from app.schemas.customer_satisfaction import (
    CustomerSatisfactionUploadResponse,
    CustomerSatisfactionListResponse,
    CustomerSatisfactionStatisticsResponse,
    UploadTrackersListResponse,
    CustomerSatisfactionFilters,
    ErrorResponse
)

logger = logging.getLogger(__name__)


class CustomerSatisfactionController:
    """Controller for customer satisfaction operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CustomerSatisfactionRepository(db)
        
        # Supported file extensions
        self.supported_extensions = ['.xlsx', '.xls', '.csv']
        
        # Maximum file size (10MB)
        self.max_file_size = 10 * 1024 * 1024
    
    def _validate_file(self, filename: str, file_content: bytes) -> tuple[bool, str]:
        """Validate uploaded file"""
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.supported_extensions:
            return False, f"File format not supported. Please upload {', '.join(self.supported_extensions)} files only."
        
        # Check file size
        if len(file_content) > self.max_file_size:
            return False, f"File size too large. Maximum allowed size is {self.max_file_size // (1024*1024)}MB."
        
        # Check if file is empty
        if len(file_content) == 0:
            return False, "File is empty."
        
        return True, "File validation passed"
    
    def _process_excel_file(self, file_content: bytes, filename: str) -> tuple[bool, Any, str]:
        """Process Excel/CSV file and return DataFrame"""
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.csv':
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin1', 'cp1252']:
                    try:
                        df = pd.read_csv(
                            pd.io.common.BytesIO(file_content), 
                            encoding=encoding,
                            dtype=str  # Read all columns as string to avoid type conversion issues
                        )
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    return False, None, "Unable to read CSV file with supported encodings"
            
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(
                    pd.io.common.BytesIO(file_content),
                    dtype=str  # Read all columns as string
                )
            else:
                return False, None, "Unsupported file format"
            
            # Basic validation
            if df.empty:
                return False, None, "File contains no data"
            
            # Check if required columns exist (at least one of the main columns)
            required_columns = ['No Tiket', 'Nama Konsumen', 'No AHASS']
            has_required = any(col in df.columns for col in required_columns)
            
            if not has_required:
                return False, None, f"File must contain at least one of these columns: {', '.join(required_columns)}"
            
            # Fill NaN values with None/empty string
            df = df.fillna('')
            
            logger.info(f"Successfully processed file: {filename}, shape: {df.shape}")
            return True, df, "File processed successfully"
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            return False, None, f"Error processing file: {str(e)}"
    
    async def upload_customer_satisfaction_file(
        self, 
        file_content: bytes, 
        filename: str,
        uploaded_by: str = None,
        override_existing: bool = False
    ) -> CustomerSatisfactionUploadResponse:
        """Upload and process customer satisfaction file"""
        try:
            # Step 1: Validate file
            is_valid, validation_message = self._validate_file(filename, file_content)
            if not is_valid:
                logger.warning(f"File validation failed for {filename}: {validation_message}")
                return CustomerSatisfactionUploadResponse(
                    success=False,
                    message=validation_message,
                    data=None
                )
            
            # Step 2: Create upload tracker
            tracker = self.repository.create_upload_tracker(
                file_name=filename,
                file_size=len(file_content),
                uploaded_by=uploaded_by
            )
            
            # Step 3: Process file
            is_processed, df, process_message = self._process_excel_file(file_content, filename)
            if not is_processed:
                # Update tracker with error
                self.repository.update_upload_tracker_status(
                    tracker_id=str(tracker.id),
                    status='FAILED',
                    error_message=process_message
                )
                return CustomerSatisfactionUploadResponse(
                    success=False,
                    message=process_message,
                    data={"upload_tracker_id": str(tracker.id)}
                )
            
            # Step 4: Convert DataFrame to records
            records_data = df.to_dict('records')
            total_records = len(records_data)
            
            logger.info(f"Processing {total_records} records from file: {filename}")
            
            # Step 5: Bulk insert records with override handling
            result_counts = self.repository.bulk_create_satisfaction_records(
                records_data=records_data,
                upload_batch_id=str(tracker.id),
                created_by=uploaded_by,
                override_existing=override_existing
            )
            successful_count, failed_count, replaced_count, skipped_count = result_counts
            
            # Step 6: Update tracker with results
            final_status = 'COMPLETED' if failed_count == 0 else ('FAILED' if successful_count == 0 else 'COMPLETED')
            error_msg = f"Partial success: {failed_count} records failed" if 0 < failed_count < total_records else None
            
            self.repository.update_upload_tracker_status(
                tracker_id=str(tracker.id),
                status=final_status,
                total_records=total_records,
                successful_records=successful_count,
                failed_records=failed_count,
                error_message=error_msg
            )
            
            # Step 7: Return response
            success_rate = (successful_count / total_records * 100) if total_records > 0 else 0
            
            # Build message based on override mode
            if override_existing:
                message = f"File uploaded successfully. {successful_count} records processed, {failed_count} failed, {replaced_count} replaced."
            else:
                message = f"File uploaded successfully. {successful_count} records processed, {failed_count} failed, {skipped_count} skipped (duplicates)."
            
            return CustomerSatisfactionUploadResponse(
                success=True,
                message=message,
                data={
                    "upload_tracker_id": str(tracker.id),
                    "file_name": filename,
                    "file_size": len(file_content),
                    "total_records": total_records,
                    "successful_records": successful_count,
                    "failed_records": failed_count,
                    "replaced_records": replaced_count,
                    "skipped_records": skipped_count,
                    "success_rate": round(success_rate, 2),
                    "upload_status": final_status,
                    "override_enabled": override_existing
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in upload_customer_satisfaction_file: {str(e)}")
            return CustomerSatisfactionUploadResponse(
                success=False,
                message="Internal server error during file upload",
                data=None
            )
    
    def get_customer_satisfaction_records(
        self,
        filters: CustomerSatisfactionFilters
    ) -> CustomerSatisfactionListResponse:
        """Get customer satisfaction records with filtering and pagination"""
        try:
            # Parse date filters - always use tanggal_rating filtering
            date_from = None
            date_to = None
            
            if filters.date_from:
                try:
                    date_from = datetime.strptime(filters.date_from, '%Y-%m-%d')
                except ValueError:
                    return CustomerSatisfactionListResponse(
                        success=False,
                        message="Invalid date_from format. Use YYYY-MM-DD.",
                        data={}
                    )
            
            if filters.date_to:
                try:
                    date_to = datetime.strptime(filters.date_to, '%Y-%m-%d')
                    # Add time to include the entire day
                    date_to = date_to.replace(hour=23, minute=59, second=59)
                except ValueError:
                    return CustomerSatisfactionListResponse(
                        success=False,
                        message="Invalid date_to format. Use YYYY-MM-DD.",
                        data={}
                    )
            
            # Get paginated records with tanggal_rating filtering
            result = self.repository.get_satisfaction_records_paginated(
                page=filters.page,
                page_size=filters.page_size,
                periode_utk_suspend=filters.periode_utk_suspend,
                submit_review_date=filters.submit_review_date,
                no_ahass=filters.no_ahass,
                date_from=date_from,
                date_to=date_to
            )
            
            return CustomerSatisfactionListResponse(
                success=True,
                message=f"Retrieved {len(result['records'])} customer satisfaction records",
                data=result
            )
            
        except Exception as e:
            logger.error(f"Error getting customer satisfaction records: {str(e)}", exc_info=True)
            return CustomerSatisfactionListResponse(
                success=False,
                message=f"Internal server error while retrieving records: {str(e)}",
                data={}
            )
    
    def get_customer_satisfaction_statistics(
        self,
        filters: CustomerSatisfactionFilters
    ) -> CustomerSatisfactionStatisticsResponse:
        """Get customer satisfaction statistics"""
        try:
            # Parse date filters - always use tanggal_rating filtering
            date_from = None
            date_to = None
            
            if filters.date_from:
                date_from = datetime.strptime(filters.date_from, '%Y-%m-%d')
            
            if filters.date_to:
                date_to = datetime.strptime(filters.date_to, '%Y-%m-%d')
                date_to = date_to.replace(hour=23, minute=59, second=59)
            
            # Get statistics with tanggal_rating filtering
            stats = self.repository.get_satisfaction_statistics(
                periode_utk_suspend=filters.periode_utk_suspend,
                submit_review_date=filters.submit_review_date,
                no_ahass=filters.no_ahass,
                date_from=date_from,
                date_to=date_to
            )
            
            return CustomerSatisfactionStatisticsResponse(
                success=True,
                message="Statistics retrieved successfully",
                data=stats
            )
            
        except Exception as e:
            logger.error(f"Error getting customer satisfaction statistics: {str(e)}", exc_info=True)
            return CustomerSatisfactionStatisticsResponse(
                success=False,
                message=f"Internal server error while retrieving statistics: {str(e)}",
                data=None
            )
    
    def get_upload_trackers(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str = None
    ) -> UploadTrackersListResponse:
        """Get upload trackers with pagination"""
        try:
            result = self.repository.get_upload_trackers_paginated(
                page=page,
                page_size=page_size,
                status=status
            )
            
            return UploadTrackersListResponse(
                success=True,
                message=f"Retrieved {len(result['trackers'])} upload trackers",
                data=result
            )
            
        except Exception as e:
            logger.error(f"Error getting upload trackers: {str(e)}")
            return UploadTrackersListResponse(
                success=False,
                message="Internal server error while retrieving upload trackers",
                data={}
            )
    
    def get_upload_tracker_by_id(self, tracker_id: str) -> Dict[str, Any]:
        """Get upload tracker by ID"""
        try:
            tracker = self.repository.get_upload_tracker_by_id(tracker_id)
            
            if not tracker:
                return {
                    "success": False,
                    "message": "Upload tracker not found",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Upload tracker retrieved successfully",
                "data": tracker.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting upload tracker {tracker_id}: {str(e)}")
            return {
                "success": False,
                "message": "Internal server error while retrieving upload tracker",
                "data": None
            }
    
    def get_latest_upload_info(self) -> Dict[str, Any]:
        """Get latest upload information for quick display"""
        try:
            latest_info = self.repository.get_latest_upload_info()
            
            if not latest_info:
                return {
                    "success": True,
                    "message": "No uploads found",
                    "data": None
                }
            
            # Calculate success rate
            total_records = latest_info.get('total_records', 0)
            successful_records = latest_info.get('successful_records', 0)
            success_rate = (successful_records / total_records * 100) if total_records > 0 else 0
            
            # Add calculated fields
            latest_info['success_rate'] = round(success_rate, 2)
            
            return {
                "success": True,
                "message": "Latest upload information retrieved successfully",
                "data": latest_info
            }
            
        except Exception as e:
            logger.error(f"Error getting latest upload info: {str(e)}")
            return {
                "success": False,
                "message": "Internal server error while retrieving latest upload information",
                "data": None
            }
    
    def get_latest_upload_info_simple(self) -> Dict[str, Any]:
        """Get latest upload information by created_date (simplified)"""
        try:
            latest_info = self.repository.get_latest_upload_info_simple()
            
            if not latest_info:
                return {
                    "success": True,
                    "message": "No uploads found",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Latest upload date retrieved successfully",
                "data": latest_info
            }
            
        except Exception as e:
            logger.error(f"Error getting latest upload info simple: {str(e)}")
            return {
                "success": False,
                "message": "Internal server error while retrieving latest upload date",
                "data": None
            }
    
    def get_top_indikasi_keluhan(
        self,
        filters: CustomerSatisfactionFilters,
        limit: int = 3
    ) -> Dict[str, Any]:
        """Get top indikasi keluhan with filtering"""
        try:
            # Parse date filters - always use tanggal_rating filtering
            date_from = None
            date_to = None
            
            if filters.date_from:
                try:
                    date_from = datetime.strptime(filters.date_from, '%Y-%m-%d')
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date_from format. Use YYYY-MM-DD.",
                        "data": None
                    }
            
            if filters.date_to:
                try:
                    date_to = datetime.strptime(filters.date_to, '%Y-%m-%d')
                    # Add time to include the entire day
                    date_to = date_to.replace(hour=23, minute=59, second=59)
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date_to format. Use YYYY-MM-DD.",
                        "data": None
                    }
            
            # Get top indikasi keluhan with tanggal_rating filtering
            top_complaints = self.repository.get_top_indikasi_keluhan(
                periode_utk_suspend=filters.periode_utk_suspend,
                submit_review_date=filters.submit_review_date,
                no_ahass=filters.no_ahass,
                date_from=date_from,
                date_to=date_to,
                limit=limit
            )
            
            return {
                "success": True,
                "message": f"Top {limit} indikasi keluhan retrieved successfully",
                "data": top_complaints
            }
            
        except Exception as e:
            logger.error(f"Error getting top indikasi keluhan: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Internal server error while retrieving top indikasi keluhan: {str(e)}",
                "data": None
            }
    
    def get_overall_rating(
        self,
        filters: CustomerSatisfactionFilters,
        compare_previous_period: bool = True
    ) -> Dict[str, Any]:
        """Get overall rating with optional comparison to previous period"""
        try:
            # Parse date filters - always use tanggal_rating filtering
            tanggal_rating_from = None
            tanggal_rating_to = None
            
            if filters.date_from:
                try:
                    tanggal_rating_from = datetime.strptime(filters.date_from, '%Y-%m-%d')
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date_from format. Use YYYY-MM-DD.",
                        "data": None
                    }
            
            if filters.date_to:
                try:
                    tanggal_rating_to = datetime.strptime(filters.date_to, '%Y-%m-%d')
                    # Add time to include the entire day
                    tanggal_rating_to = tanggal_rating_to.replace(hour=23, minute=59, second=59)
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date_to format. Use YYYY-MM-DD.",
                        "data": None
                    }
            
            # Get overall rating with comparison using tanggal_rating filtering
            rating_data = self.repository.get_overall_rating_with_comparison(
                periode_utk_suspend=filters.periode_utk_suspend,
                submit_review_date=filters.submit_review_date,
                no_ahass=filters.no_ahass,
                date_from=None,  # Always use tanggal_rating fields for this method
                date_to=None,
                tanggal_rating_from=tanggal_rating_from,
                tanggal_rating_to=tanggal_rating_to,
                compare_previous_period=compare_previous_period
            )
            
            return {
                "success": True,
                "message": "Overall rating retrieved successfully",
                "data": rating_data
            }
            
        except Exception as e:
            logger.error(f"Error getting overall rating: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Internal server error while retrieving overall rating: {str(e)}",
                "data": None
            }