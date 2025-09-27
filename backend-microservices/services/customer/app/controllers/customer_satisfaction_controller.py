"""
Customer satisfaction controller with business logic for file uploads and data retrieval
"""

import logging
import os
import pandas as pd
import re
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, BinaryIO, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.customer_satisfaction_repository import CustomerSatisfactionRepository
from app.services.sentiment_analysis_service import SentimentAnalysisService
from app.utils.timezone_utils import get_indonesia_utc_now
from app.schemas.customer_satisfaction import (
    CustomerSatisfactionUploadResponse,
    CustomerSatisfactionListResponse,
    CustomerSatisfactionStatisticsResponse,
    UploadTrackersListResponse,
    CustomerSatisfactionFilters,
    SentimentAnalysisResponse,
    BulkSentimentAnalysisResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)


class CustomerSatisfactionController:
    """Controller for customer satisfaction operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CustomerSatisfactionRepository(db)
        self.sentiment_service = SentimentAnalysisService()

        # Thread pool for background sentiment analysis
        self.thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="sentiment_analysis")

        # Supported file extensions
        self.supported_extensions = ['.xlsx', '.xls', '.csv']

        # Maximum file size (10MB)
        self.max_file_size = 10 * 1024 * 1024
        
        # Indonesian month names mapping (same as repository)
        self.INDONESIAN_MONTHS = {
            'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
            'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
            'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
        }
    
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
    
    def _validate_indonesian_date(self, date_str: str) -> Tuple[bool, str]:
        """
        Strictly validate Indonesian date string format: EXACTLY 'DD Month YYYY' or 'D Month YYYY'
        
        Rejects all numeric formats (24-12-2025, 24/12/2025, etc.) and time components.
        Only accepts Indonesian month names with exactly one space between components.
        
        Args:
            date_str: Indonesian date string to validate
            
        Returns:
            (is_valid, error_message): Validation result and error message if invalid
        """
        if not date_str or not isinstance(date_str, str):
            return True, ""  # Allow empty dates
        
        # Clean and normalize the string
        clean_date = date_str.strip()
        if not clean_date:
            return True, ""  # Allow empty dates after stripping
        
        try:
            # Explicit rejection of common invalid formats BEFORE regex
            
            # Reject any format with dashes (DD-MM-YYYY or YYYY-MM-DD)
            if re.search(r'\d{1,2}-\d{1,2}-\d{4}', clean_date):
                return False, f"Numeric date format with dashes not allowed. Expected: 'DD Month YYYY' (e.g., '24 Desember 2024'), got '{date_str}'"
            
            if re.search(r'\d{4}-\d{1,2}-\d{1,2}', clean_date):
                return False, f"ISO date format (YYYY-MM-DD) not allowed. Expected: 'DD Month YYYY' (e.g., '24 Desember 2024'), got '{date_str}'"
            
            # Reject any format with slashes (DD/MM/YYYY or YYYY/MM/DD)
            if re.search(r'\d{1,2}/\d{1,2}/\d{4}', clean_date):
                return False, f"Numeric date format with slashes not allowed. Expected: 'DD Month YYYY' (e.g., '24 Desember 2024'), got '{date_str}'"
            
            if re.search(r'\d{4}/\d{1,2}/\d{1,2}', clean_date):
                return False, f"ISO date format with slashes not allowed. Expected: 'DD Month YYYY' (e.g., '24 Desember 2024'), got '{date_str}'"
            
            # Reject any format with dots (DD.MM.YYYY)
            if re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', clean_date):
                return False, f"Numeric date format with dots not allowed. Expected: 'DD Month YYYY' (e.g., '24 Desember 2024'), got '{date_str}'"
            
            # Reject any format with time components (containing colon)
            if ':' in clean_date:
                return False, f"Time components not allowed. Expected: 'DD Month YYYY' (e.g., '24 Desember 2024'), got '{date_str}'"
            
            # Reject any format that contains only numbers and separators (no letters)
            if re.match(r'^[\d\s\-/\.]+$', clean_date):
                return False, f"Numeric-only date format not allowed. Expected: 'DD Month YYYY' with Indonesian month name (e.g., '24 Desember 2024'), got '{date_str}'"
            
            # STRICT Pattern: DD Month YYYY or D Month YYYY (exactly ONE space between components)
            pattern = r'^(\d{1,2})\s([a-zA-Z]+)\s(\d{4})$'
            match = re.match(pattern, clean_date)
            
            if not match:
                return False, f"Invalid date format. Expected exactly 'DD Month YYYY' with single spaces (e.g., '24 Desember 2024'), got '{date_str}'"
            
            day_str, month_str, year_str = match.groups()
            
            # Convert to lowercase for lookup
            month_lower = month_str.lower()
            
            if month_lower not in self.INDONESIAN_MONTHS:
                valid_months = ', '.join(self.INDONESIAN_MONTHS.keys())
                return False, f"Invalid Indonesian month '{month_str}'. Must use Indonesian month name. Valid months: {valid_months}"
            
            try:
                day = int(day_str)
                month = self.INDONESIAN_MONTHS[month_lower]
                year = int(year_str)
                
                # Validate date logic
                test_date = datetime(year, month, day)
                
                # Additional validation for reasonable ranges
                if year < 1900 or year > 2100:
                    return False, f"Year {year} is out of reasonable range (1900-2100). Expected: 'DD Month YYYY' format"
                
                if day < 1 or day > 31:
                    return False, f"Day {day} is invalid. Expected: 'DD Month YYYY' format"
                
                return True, ""
                
            except ValueError as e:
                return False, f"Invalid date values in '{date_str}': {str(e)}. Expected: 'DD Month YYYY' format (e.g., '24 Desember 2024')"
            
        except Exception as e:
            return False, f"Error validating date '{date_str}': {str(e)}. Expected: 'DD Month YYYY' format (e.g., '24 Desember 2024')"
    
    def _validate_data_records(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data records for critical fields before bulk insert
        
        Args:
            df: DataFrame containing records to validate
            
        Returns:
            Dict containing validation results and statistics
        """
        validation_results = {
            "total_records": len(df),
            "valid_records": 0,
            "invalid_records": 0,
            "validation_errors": [],
            "invalid_tanggal_rating_count": 0,
            "invalid_rating_count": 0,
            "missing_no_tiket_count": 0,
            "error_summary": {}
        }
        
        error_types = {
            "tanggal_rating_format": 0,
            "rating_format": 0, 
            "missing_no_tiket": 0
        }
        
        for index, row in df.iterrows():
            record_errors = []
            row_number = index + 2  # +2 because pandas is 0-indexed and Excel has header row
            
            # Validate no_tiket (required for duplicate checking)
            no_tiket = row.get('No Tiket', '')
            if not no_tiket or str(no_tiket).strip() == '' or str(no_tiket).lower() == 'nan':
                record_errors.append(f"Row {row_number}: Missing or empty 'No Tiket' field (required)")
                validation_results["missing_no_tiket_count"] += 1
                error_types["missing_no_tiket"] += 1
            
            # Validate tanggal_rating format
            tanggal_rating = row.get('tanggal Rating', '') or row.get('tanggal_rating', '')
            if tanggal_rating and str(tanggal_rating).strip() and str(tanggal_rating).lower() != 'nan':
                is_valid_date, date_error = self._validate_indonesian_date(str(tanggal_rating))
                if not is_valid_date:
                    record_errors.append(f"Row {row_number}: tanggal_rating - {date_error}")
                    validation_results["invalid_tanggal_rating_count"] += 1
                    error_types["tanggal_rating_format"] += 1
            
            # Validate rating format (if present)
            rating = row.get('Rating', '')
            if rating and str(rating).strip() and str(rating).lower() != 'nan':
                try:
                    rating_value = float(str(rating).strip())
                    if not (0 <= rating_value <= 5):
                        record_errors.append(f"Row {row_number}: Rating must be between 0 and 5, got {rating_value}")
                        validation_results["invalid_rating_count"] += 1
                        error_types["rating_format"] += 1
                except (ValueError, TypeError):
                    record_errors.append(f"Row {row_number}: Rating must be numeric, got '{rating}'")
                    validation_results["invalid_rating_count"] += 1
                    error_types["rating_format"] += 1
            
            # Track record validity
            if record_errors:
                validation_results["invalid_records"] += 1
                validation_results["validation_errors"].extend(record_errors)
            else:
                validation_results["valid_records"] += 1
        
        # Create error summary
        validation_results["error_summary"] = {
            "tanggal_rating_format_errors": error_types["tanggal_rating_format"],
            "rating_format_errors": error_types["rating_format"], 
            "missing_no_tiket_errors": error_types["missing_no_tiket"]
        }
        
        # Limit validation_errors to prevent overwhelming response
        if len(validation_results["validation_errors"]) > 50:
            validation_results["validation_errors"] = validation_results["validation_errors"][:50]
            validation_results["validation_errors"].append("... (showing first 50 errors only)")
        
        logger.info(f"Data validation completed: {validation_results['valid_records']} valid, {validation_results['invalid_records']} invalid records")
        
        return validation_results
    
    def _has_validation_errors(self, record_dict: Dict[str, Any], row_number: int) -> Tuple[bool, List[str]]:
        """
        Check if an individual record has validation errors
        
        Args:
            record_dict: Dictionary containing record data
            row_number: Row number in the file (for error reporting)
            
        Returns:
            (has_errors, error_list): Boolean indicating if errors exist and list of error messages
        """
        record_errors = []
        
        # Check no_tiket (required for duplicate checking)
        no_tiket = record_dict.get('No Tiket', '')
        if not no_tiket or str(no_tiket).strip() == '' or str(no_tiket).lower() == 'nan':
            record_errors.append(f"Row {row_number}: Missing or empty 'No Tiket' field (required)")
        
        # Check tanggal_rating format
        tanggal_rating = record_dict.get('tanggal Rating', '') or record_dict.get('tanggal_rating', '')
        if tanggal_rating and str(tanggal_rating).strip() and str(tanggal_rating).lower() != 'nan':
            is_valid_date, date_error = self._validate_indonesian_date(str(tanggal_rating))
            if not is_valid_date:
                record_errors.append(f"Row {row_number}: tanggal_rating - {date_error}")
        
        # Check rating format (if present)
        rating = record_dict.get('Rating', '')
        if rating and str(rating).strip() and str(rating).lower() != 'nan':
            try:
                rating_value = float(str(rating).strip())
                if not (0 <= rating_value <= 5):
                    record_errors.append(f"Row {row_number}: Rating must be between 0 and 5, got {rating_value}")
            except (ValueError, TypeError):
                record_errors.append(f"Row {row_number}: Rating must be numeric, got '{rating}'")
        
        return len(record_errors) > 0, record_errors
    
    def _reformat_tanggal_rating(self, date_str: str) -> Tuple[str, bool]:
        """
        Attempt to reformat various date formats to Indonesian format: 'DD Month YYYY'
        
        Handles common formats:
        - DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY → DD Month YYYY
        - YYYY-MM-DD, YYYY/MM/DD → DD Month YYYY  
        - D-M-YYYY, D/M/YYYY → D Month YYYY
        - English month names → Indonesian month names
        - Removes time components
        - Handles 2-digit years (assumes 20xx)
        
        Args:
            date_str: Original date string to reformat
            
        Returns:
            (reformatted_date, was_reformatted): Tuple of reformatted string and boolean indicating if changes were made
        """
        if not date_str or not isinstance(date_str, str):
            return date_str, False
        
        original_date = date_str
        clean_date = date_str.strip()
        
        if not clean_date:
            return date_str, False
        
        try:
            # Remove time components (anything after space followed by time pattern)
            # Patterns: "10:30", "10:30:45", "T10:30:00"
            clean_date = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?$', '', clean_date)
            clean_date = re.sub(r'T\d{1,2}:\d{2}(:\d{2})?.*$', '', clean_date)
            
            # English to Indonesian month mapping
            english_to_indonesian = {
                'january': 'januari', 'jan': 'januari',
                'february': 'februari', 'feb': 'februari', 
                'march': 'maret', 'mar': 'maret',
                'april': 'april', 'apr': 'april',
                'may': 'mei',
                'june': 'juni', 'jun': 'juni',
                'july': 'juli', 'jul': 'juli',
                'august': 'agustus', 'aug': 'agustus',
                'september': 'september', 'sep': 'september',
                'october': 'oktober', 'oct': 'oktober',
                'november': 'november', 'nov': 'november',
                'december': 'desember', 'dec': 'desember'
            }
            
            # Month number to Indonesian name
            month_num_to_indonesian = {
                1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
                5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
                9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
            }
            
            reformatted_date = clean_date
            was_reformatted = False
            
            # Pattern 1: DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
            pattern1 = r'^(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{2,4})$'
            match1 = re.match(pattern1, clean_date)
            if match1:
                day, month, year = match1.groups()
                
                # Handle 2-digit years (assume 20xx)
                if len(year) == 2:
                    year = '20' + year
                
                try:
                    month_num = int(month)
                    if 1 <= month_num <= 12:
                        indonesian_month = month_num_to_indonesian[month_num]
                        reformatted_date = f"{int(day)} {indonesian_month} {year}"
                        was_reformatted = True
                except (ValueError, KeyError):
                    pass
            
            # Pattern 2: YYYY-MM-DD, YYYY/MM/DD (ISO format)  
            if not was_reformatted:
                pattern2 = r'^(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})$'
                match2 = re.match(pattern2, clean_date)
                if match2:
                    year, month, day = match2.groups()
                    
                    try:
                        month_num = int(month)
                        if 1 <= month_num <= 12:
                            indonesian_month = month_num_to_indonesian[month_num]
                            reformatted_date = f"{int(day)} {indonesian_month} {year}"
                            was_reformatted = True
                    except (ValueError, KeyError):
                        pass
            
            # Pattern 3: DD Month YYYY with English month names
            if not was_reformatted:
                pattern3 = r'^(\d{1,2})\s+([a-zA-Z]+)\s+(\d{2,4})$'
                match3 = re.match(pattern3, clean_date)
                if match3:
                    day, month_str, year = match3.groups()
                    
                    # Handle 2-digit years
                    if len(year) == 2:
                        year = '20' + year
                    
                    month_lower = month_str.lower()
                    if month_lower in english_to_indonesian:
                        indonesian_month = english_to_indonesian[month_lower].capitalize()
                        reformatted_date = f"{int(day)} {indonesian_month} {year}"
                        was_reformatted = True
            
            # Pattern 4: Already in Indonesian format but may need time removal or case fixing
            if not was_reformatted:
                pattern4 = r'^(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})$'
                match4 = re.match(pattern4, clean_date)
                if match4:
                    day, month_str, year = match4.groups()
                    month_lower = month_str.lower()
                    
                    # Check if it's already Indonesian month
                    if month_lower in self.INDONESIAN_MONTHS:
                        # Fix capitalization 
                        proper_month = month_str.capitalize()
                        reformatted_date = f"{int(day)} {proper_month} {year}"
                        # Only mark as reformatted if we actually changed something
                        was_reformatted = (reformatted_date != original_date)
            
            # If we removed time components but didn't reformat the date part
            if not was_reformatted and reformatted_date != original_date:
                was_reformatted = True
            
            return reformatted_date, was_reformatted
            
        except Exception as e:
            # If reformatting fails, return original
            logger.warning(f"Error reformatting date '{date_str}': {str(e)}")
            return original_date, False
    
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
        override_existing: bool = False,
        reformat_tanggal_rating: bool = False
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
            
            # Step 3.5: Apply reformatting if enabled
            reformatted_count = 0
            if reformat_tanggal_rating and 'tanggal_rating' in df.columns:
                logger.info("Applying tanggal_rating reformatting before validation")
                for index in df.index:
                    original_value = df.at[index, 'tanggal_rating']
                    if original_value and str(original_value).strip():
                        reformatted_value, was_reformatted = self._reformat_tanggal_rating(str(original_value).strip())
                        if was_reformatted:
                            df.at[index, 'tanggal_rating'] = reformatted_value
                            reformatted_count += 1
                logger.info(f"Reformatted {reformatted_count} tanggal_rating values")
            
            # Step 4: Validate data records
            validation_results = self._validate_data_records(df)
            
            # Step 5: Convert DataFrame to records and filter valid vs invalid
            all_records_data = df.to_dict('records')
            total_records = len(all_records_data)
            
            # Separate valid and invalid records
            valid_records = []
            invalid_records = []
            invalid_record_errors = []
            
            for index, record_dict in enumerate(all_records_data):
                row_number = index + 2  # +2 because pandas is 0-indexed and Excel has header row
                has_errors, error_list = self._has_validation_errors(record_dict, row_number)
                
                if has_errors:
                    invalid_records.append(record_dict)
                    invalid_record_errors.extend(error_list)
                else:
                    valid_records.append(record_dict)
            
            validation_failed_count = len(invalid_records)
            valid_count = len(valid_records)
            
            logger.info(f"Processing {total_records} records from file: {filename}")
            logger.info(f"Validation filtering: {valid_count} valid, {validation_failed_count} invalid (excluded from database)")
            
            # Step 6: Only process valid records through database
            if valid_records:
                result_counts = self.repository.bulk_create_satisfaction_records(
                    records_data=valid_records,  # Only send valid records
                    upload_batch_id=str(tracker.id),
                    created_by=uploaded_by,
                    override_existing=override_existing
                )
                successful_count, db_failed_count, replaced_count, skipped_count = result_counts
            else:
                # No valid records to process
                successful_count, db_failed_count, replaced_count, skipped_count = 0, 0, 0, 0
                logger.warning("No valid records to process after validation filtering")
            
            # Calculate total failures (validation + database)
            total_failed_count = validation_failed_count + db_failed_count
            
            # Step 7: Update tracker with comprehensive results
            final_status = 'COMPLETED' if total_failed_count == 0 else ('FAILED' if successful_count == 0 else 'COMPLETED')
            
            # Build comprehensive error message
            error_msg_parts = []
            if validation_failed_count > 0:
                error_msg_parts.append(f"Validation failures: {validation_failed_count}")
            if db_failed_count > 0:
                error_msg_parts.append(f"Database failures: {db_failed_count}")
            
            error_msg = "; ".join(error_msg_parts) if error_msg_parts else None
            
            if total_failed_count > 0 and successful_count > 0:
                error_msg = f"Partial success: {error_msg}"
            
            self.repository.update_upload_tracker_status(
                tracker_id=str(tracker.id),
                status=final_status,
                total_records=total_records,
                successful_records=successful_count,
                failed_records=total_failed_count,  # Total failures (validation + database)
                error_message=error_msg
            )
            
            # Step 8: Return response
            success_rate = (successful_count / total_records * 100) if total_records > 0 else 0
            
            # Build comprehensive message
            base_message = f"File uploaded successfully. {successful_count} records processed, {total_failed_count} failed"
            
            # Add reformatting details
            if reformatted_count > 0:
                base_message += f", {reformatted_count} dates reformatted"
            
            # Add database operation details if any valid records were processed
            if valid_count > 0:
                if override_existing:
                    base_message += f", {replaced_count} replaced"
                else:
                    base_message += f", {skipped_count} skipped (duplicates)"
            
            base_message += "."
            
            # Initialize validation issue counters (always define these variables)
            tanggal_rating_issues = 0
            rating_issues = 0
            no_tiket_issues = 0
            
            # Add validation failure details
            if validation_failed_count > 0:
                base_message += f" Validation excluded {validation_failed_count} invalid records from database."
                
                # Count specific validation issues from filtered records
                tanggal_rating_issues = sum(1 for error in invalid_record_errors if 'tanggal_rating' in error)
                rating_issues = sum(1 for error in invalid_record_errors if 'Rating must be' in error)
                no_tiket_issues = sum(1 for error in invalid_record_errors if 'No Tiket' in error)
                
                issue_details = []
                if tanggal_rating_issues > 0:
                    issue_details.append(f"{tanggal_rating_issues} tanggal_rating format errors")
                if rating_issues > 0:
                    issue_details.append(f"{rating_issues} rating format errors")
                if no_tiket_issues > 0:
                    issue_details.append(f"{no_tiket_issues} missing no_tiket errors")
                
                if issue_details:
                    base_message += f" Issues: {', '.join(issue_details)}."
            
            response = CustomerSatisfactionUploadResponse(
                success=True,
                message=base_message,
                data={
                    "upload_tracker_id": str(tracker.id),
                    "file_name": filename,
                    "file_size": len(file_content),
                    "total_records": total_records,
                    "successful_records": successful_count,
                    "failed_records": total_failed_count,
                    "replaced_records": replaced_count,
                    "skipped_records": skipped_count,
                    "success_rate": round(success_rate, 2),
                    "upload_status": final_status,
                    "override_enabled": override_existing,
                    "reformat_enabled": reformat_tanggal_rating,
                    "reformatted_records": reformatted_count,
                    # Enhanced failure breakdown
                    "failure_breakdown": {
                        "validation_failures": validation_failed_count,
                        "database_failures": db_failed_count,
                        "duplicate_skipped": skipped_count
                    },
                    "validation_details": {
                        "total_validated": total_records,
                        "valid_sent_to_database": valid_count,
                        "invalid_excluded": validation_failed_count,
                        "tanggal_rating_format_failures": tanggal_rating_issues,
                        "rating_format_failures": rating_issues,
                        "missing_no_tiket_failures": no_tiket_issues
                    },
                    "validation_errors": invalid_record_errors[:50],  # Limit to first 50 errors
                    "format_requirements": {
                        "tanggal_rating_format": "Indonesian date format: 'DD Month YYYY' (e.g., '24 Desember 2024')",
                        "valid_months": list(self.INDONESIAN_MONTHS.keys()),
                        "rating_format": "Numeric value between 0 and 5",
                        "required_fields": ["No Tiket"]
                    },
                    "processing_summary": {
                        "records_received": total_records,
                        "records_validated": total_records,
                        "records_passed_validation": valid_count,
                        "records_sent_to_database": valid_count,
                        "records_successfully_stored": successful_count,
                        "records_failed_validation": validation_failed_count,
                        "records_failed_database": db_failed_count
                    }
                }
            )
            
            # Trigger background sentiment analysis for successful uploads (completely non-blocking)
            if successful_count > 0:
                try:
                    # Create a completely isolated background task that cannot affect the upload response
                    task = asyncio.create_task(
                        self._safe_background_sentiment_analysis(str(tracker.id))
                    )
                    # Don't await the task - let it run completely independently
                    task.add_done_callback(lambda t: self._log_background_task_completion(t, str(tracker.id)))
                    logger.info(f"Started background sentiment analysis for upload batch {tracker.id}")
                except Exception as bg_error:
                    # Even task creation failures should not affect file upload success
                    logger.warning(f"Failed to start background sentiment analysis (non-blocking): {str(bg_error)}")
                    logger.info("File upload completed successfully despite sentiment analysis startup failure")
            
            return response
            
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
    
    # Sentiment Analysis Methods
    
    def _log_background_task_completion(self, task: asyncio.Task, upload_batch_id: str) -> None:
        """
        Log the completion of background sentiment analysis task
        
        Args:
            task: The completed asyncio task
            upload_batch_id: UUID of the upload batch that was analyzed
        """
        try:
            if task.exception():
                logger.error(f"Background sentiment analysis failed for batch {upload_batch_id}: {str(task.exception())}")
            else:
                logger.info(f"Background sentiment analysis completed successfully for batch {upload_batch_id}")
        except Exception as e:
            logger.error(f"Error logging background task completion for batch {upload_batch_id}: {str(e)}")

    async def _safe_background_sentiment_analysis(self, upload_batch_id: str) -> None:
        """
        Safe wrapper for background sentiment analysis that catches all exceptions
        
        Args:
            upload_batch_id: UUID of the upload batch to analyze
        """
        try:
            await self._background_sentiment_analysis(upload_batch_id)
        except Exception as e:
            # Catch all exceptions to prevent them from bubbling up
            logger.error(f"Safe wrapper caught error in background sentiment analysis for batch {upload_batch_id}: {str(e)}", exc_info=True)

    async def _background_sentiment_analysis(self, upload_batch_id: str) -> None:
        """
        Background task to perform sentiment analysis on uploaded records
        
        Args:
            upload_batch_id: UUID of the upload batch to analyze
        """
        try:
            logger.info(f"Starting background sentiment analysis for batch {upload_batch_id}")
            
            # Get unanalyzed records from this upload batch
            unanalyzed_records = self.repository.get_unanalyzed_records(
                limit=100,  # Process in batches
                upload_batch_id=upload_batch_id
            )
            
            if not unanalyzed_records:
                logger.info(f"No unanalyzed records found for batch {upload_batch_id}")
                return
            
            # Process records in smaller batches to avoid overwhelming the API
            batch_size = 10
            batch_id = str(uuid.uuid4())
            total_processed = 0
            total_successful = 0
            total_failed = 0
            
            for i in range(0, len(unanalyzed_records), batch_size):
                batch = unanalyzed_records[i:i + batch_size]
                
                logger.info(f"Processing sentiment analysis batch {i//batch_size + 1} with {len(batch)} records")
                
                # Analyze sentiments for this batch
                try:
                    sentiment_results, errors = await self.sentiment_service.analyze_sentiments(batch)
                    
                    if sentiment_results:
                        # Update database with results
                        update_stats = self.repository.bulk_update_sentiment_analysis(
                            sentiment_results, 
                            batch_id=batch_id
                        )
                        
                        total_successful += update_stats["updated_count"]
                        total_failed += update_stats["failed_count"]
                        
                        if errors:
                            logger.warning(f"Batch {i//batch_size + 1} had {len(errors)} errors: {errors[:3]}")  # Log first 3 errors
                    else:
                        logger.warning(f"No sentiment results for batch {i//batch_size + 1}")
                        if errors:
                            logger.error(f"Sentiment analysis errors for batch {i//batch_size + 1}: {errors[:3]}")  # Log first 3 errors
                        total_failed += len(batch)
                        
                except Exception as batch_error:
                    logger.error(f"Unexpected error processing sentiment analysis batch {i//batch_size + 1}: {str(batch_error)}")
                    total_failed += len(batch)
                
                total_processed += len(batch)
                
                # Small delay between batches to be respectful to the API
                if i + batch_size < len(unanalyzed_records):
                    await asyncio.sleep(2)  # Increased delay to reduce API pressure
            
            logger.info(f"Background sentiment analysis completed for batch {upload_batch_id}: "
                       f"{total_successful} successful, {total_failed} failed, {total_processed} total")
            
        except Exception as e:
            logger.error(f"Error in background sentiment analysis for batch {upload_batch_id}: {str(e)}", exc_info=True)
    
    async def analyze_record_sentiment(self, record_id: str) -> SentimentAnalysisResponse:
        """
        Analyze sentiment for a single record
        
        Args:
            record_id: UUID of the record to analyze
            
        Returns:
            SentimentAnalysisResponse with analysis results
        """
        try:
            # Get the record
            records = self.repository.get_unanalyzed_records(limit=1)
            record = None
            
            # Find the specific record 
            from app.models.customer_satisfaction_raw import CustomerSatisfactionRaw
            
            all_records = self.db.query(CustomerSatisfactionRaw).filter(
                CustomerSatisfactionRaw.id == record_id
            ).first()
            
            if not all_records:
                return SentimentAnalysisResponse(
                    success=False,
                    message=f"Record with ID {record_id} not found",
                    data=None
                )
            
            # Check if record has review content
            if not all_records.inbox or not all_records.inbox.strip():
                return SentimentAnalysisResponse(
                    success=False,
                    message="Record does not have review content for sentiment analysis",
                    data=None
                )
            
            # Format record for analysis
            record_data = {
                "id": str(all_records.id),
                "no_tiket": all_records.no_tiket or "",
                "review": all_records.inbox
            }
            
            # Analyze sentiment
            result, error = await self.sentiment_service.analyze_single_record(record_data)
            
            if error:
                return SentimentAnalysisResponse(
                    success=False,
                    message=f"Sentiment analysis failed: {error}",
                    data=None
                )
            
            if result:
                # Update database
                success = self.repository.update_sentiment_analysis(record_id, result)
                
                if success:
                    return SentimentAnalysisResponse(
                        success=True,
                        message="Sentiment analysis completed successfully",
                        data={
                            "record_id": record_id,
                            "sentiment": result["sentiment"],
                            "sentiment_score": result["sentiment_score"],
                            "sentiment_reasons": result["sentiment_reasons"],
                            "sentiment_suggestion": result["sentiment_suggestion"],
                            "sentiment_themes": result["sentiment_themes"],
                            "analyzed_at": result["sentiment_analyzed_at"].isoformat() if result.get("sentiment_analyzed_at") else None
                        }
                    )
                else:
                    return SentimentAnalysisResponse(
                        success=False,
                        message="Failed to update sentiment analysis in database",
                        data=None
                    )
            
            return SentimentAnalysisResponse(
                success=False,
                message="No sentiment analysis result received",
                data=None
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for record {record_id}: {str(e)}", exc_info=True)
            return SentimentAnalysisResponse(
                success=False,
                message=f"Internal server error during sentiment analysis: {str(e)}",
                data=None
            )
    
    async def bulk_analyze_sentiment(
        self,
        limit: int = 50,
        upload_batch_id: Optional[str] = None
    ) -> BulkSentimentAnalysisResponse:
        """
        Perform bulk sentiment analysis on unanalyzed records using background processing

        Args:
            limit: Maximum number of records to analyze
            upload_batch_id: Optional filter by specific upload batch

        Returns:
            BulkSentimentAnalysisResponse with background processing status
        """
        try:
            started_at = get_indonesia_utc_now()

            # Get unanalyzed records count
            unanalyzed_records = self.repository.get_unanalyzed_records(
                limit=limit,
                upload_batch_id=upload_batch_id
            )

            if not unanalyzed_records:
                return BulkSentimentAnalysisResponse(
                    success=True,
                    message="No unanalyzed records found for sentiment analysis",
                    data={
                        "batch_id": None,
                        "total_records": 0,
                        "analyzed_records": 0,
                        "failed_records": 0,
                        "status": "COMPLETED",
                        "started_at": started_at.isoformat(),
                        "completed_at": get_indonesia_utc_now().isoformat()
                    }
                )

            try:
                # Start background sentiment analysis using thread pool
                loop = asyncio.get_event_loop()
                loop.run_in_executor(
                    self.thread_pool,
                    self._run_bulk_sentiment_analysis_background,
                    limit,
                    upload_batch_id or "",
                    None  # tracker_id - can be implemented later
                )

                # Return immediately with processing status
                batch_id = str(uuid.uuid4())

                return BulkSentimentAnalysisResponse(
                    success=True,
                    message=f"Bulk sentiment analysis started in background for {len(unanalyzed_records)} records",
                    data={
                        "batch_id": batch_id,
                        "total_records": len(unanalyzed_records),
                        "analyzed_records": 0,  # Will be updated by background process
                        "failed_records": 0,    # Will be updated by background process
                        "status": "PROCESSING",
                        "started_at": started_at.isoformat(),
                        "completed_at": None,   # Will be set by background process
                        "message": "Processing in background - check logs for completion status"
                    }
                )

            except Exception as e:
                logger.error(f"Failed to start background bulk sentiment analysis: {str(e)}")

                return BulkSentimentAnalysisResponse(
                    success=False,
                    message=f"Failed to start background sentiment analysis: {str(e)}",
                    data=None
                )

        except Exception as e:
            logger.error(f"Error in bulk sentiment analysis setup: {str(e)}", exc_info=True)
            return BulkSentimentAnalysisResponse(
                success=False,
                message=f"Internal server error during bulk sentiment analysis setup: {str(e)}",
                data=None
            )
    
    def get_sentiment_analysis_statistics(self, filters: CustomerSatisfactionFilters) -> Dict[str, Any]:
        """
        Get sentiment analysis statistics with filtering
        
        Args:
            filters: Filter parameters
            
        Returns:
            Dictionary containing sentiment statistics
        """
        try:
            # Parse date filters
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
                    date_to = date_to.replace(hour=23, minute=59, second=59)
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date_to format. Use YYYY-MM-DD.",
                        "data": None
                    }
            
            # Get sentiment statistics
            stats = self.repository.get_sentiment_statistics(
                periode_utk_suspend=filters.periode_utk_suspend,
                submit_review_date=filters.submit_review_date,
                no_ahass=filters.no_ahass,
                date_from=date_from,
                date_to=date_to
            )
            
            return {
                "success": True,
                "message": "Sentiment analysis statistics retrieved successfully",
                "data": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment statistics: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Internal server error while retrieving sentiment statistics: {str(e)}",
                "data": None
            }
    
    def get_sentiment_themes_statistics(self, filters: CustomerSatisfactionFilters) -> Dict[str, Any]:
        """
        Get sentiment themes statistics with filtering - counts and groups by sentiment_themes
        
        Args:
            filters: Filter parameters including date range, no_ahass, etc.
            
        Returns:
            Dictionary containing sentiment themes statistics
        """
        try:
            # Parse date filters
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
                    date_to = date_to.replace(hour=23, minute=59, second=59)
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date_to format. Use YYYY-MM-DD.",
                        "data": None
                    }
            
            # Get sentiment themes statistics from repository
            stats = self.repository.get_sentiment_themes_statistics(
                periode_utk_suspend=filters.periode_utk_suspend,
                submit_review_date=filters.submit_review_date,
                no_ahass=filters.no_ahass,
                date_from=date_from,
                date_to=date_to
            )
            
            return {
                "success": True,
                "message": "Sentiment themes statistics retrieved successfully",
                "data": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment themes statistics: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Internal server error while retrieving sentiment themes statistics: {str(e)}",
                "data": None
            }

    def _run_bulk_sentiment_analysis_background(self, limit: int, upload_batch_id: str, tracker_id: str = None) -> None:
        """
        Run bulk sentiment analysis in background thread

        Args:
            limit: Maximum number of records to analyze
            upload_batch_id: Upload batch ID to filter records (optional)
            tracker_id: Tracker ID for monitoring progress (optional)
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            analysis_start_time = get_indonesia_utc_now()
            logger.info(f"Starting background bulk sentiment analysis (limit: {limit}, batch: {upload_batch_id})")

            # Create new database session for background thread
            from app.dependencies import db_manager
            background_db = next(db_manager.get_session())

            try:
                # Initialize background controller with background db session
                background_controller = CustomerSatisfactionController(background_db)

                # Get unanalyzed records
                unanalyzed_records = background_controller.repository.get_unanalyzed_records(
                    limit=limit,
                    upload_batch_id=upload_batch_id
                )

                if not unanalyzed_records:
                    logger.info(f"No unanalyzed records found for background analysis")
                    return

                # Run sentiment analysis synchronously in background thread
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # Generate batch ID for this analysis
                    batch_id = str(uuid.uuid4())
                    logger.info(f"Processing {len(unanalyzed_records)} records in background (batch {batch_id})")

                    # Analyze sentiments
                    sentiment_results, errors = loop.run_until_complete(
                        background_controller.sentiment_service.analyze_sentiments(unanalyzed_records)
                    )

                    # Update database with results
                    analyzed_count = 0
                    failed_count = len(unanalyzed_records)

                    if sentiment_results:
                        update_stats = background_controller.repository.bulk_update_sentiment_analysis(
                            sentiment_results,
                            batch_id=batch_id
                        )

                        analyzed_count = update_stats["updated_count"]
                        failed_count = update_stats["failed_count"] + len(errors)

                    analysis_duration = int((get_indonesia_utc_now() - analysis_start_time).total_seconds())

                    logger.info(f"Background bulk sentiment analysis completed: "
                              f"{analyzed_count} analyzed, {failed_count} failed, {analysis_duration}s duration")

                finally:
                    loop.close()

            finally:
                background_db.close()

        except Exception as e:
            logger.error(f"Critical error in background bulk sentiment analysis: {str(e)}", exc_info=True)

    def __del__(self):
        """Cleanup thread pool executor on object deletion"""
        if hasattr(self, 'thread_pool') and self.thread_pool:
            self.thread_pool.shutdown(wait=False)