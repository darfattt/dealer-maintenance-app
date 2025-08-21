"""
CSV template loader utility for WhatsApp templates
"""

import os
import csv
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVTemplateLoader:
    """Service for reading WhatsApp templates from CSV files"""
    
    def __init__(self, csv_file_path: str):
        """
        Initialize CSV template loader
        
        Args:
            csv_file_path: Path to the CSV file containing templates
        """
        self.csv_file_path = csv_file_path
        self.required_columns = ['reminder_target', 'reminder_type', 'template']
        
    def _normalize_column_names(self, headers: List[str]) -> Dict[str, str]:
        """
        Create mapping for normalizing column names to match expected format
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            Dictionary mapping original headers to normalized names
        """
        column_mapping = {}
        
        # Map various possible column names to standard names
        for header in headers:
            header_lower = str(header).lower().strip()
            
            # Reminder target variations
            if header_lower in ['reminder_target', 'reminder target', 'target', 'kategori', 'category']:
                column_mapping[header] = 'reminder_target'
            
            # Reminder type variations  
            elif header_lower in ['reminder_type', 'reminder type', 'type', 'jenis', 'tipe']:
                column_mapping[header] = 'reminder_type'
            
            # Template/message variations
            elif header_lower in ['template', 'message', 'pesan', 'text', 'content', 'isi']:
                column_mapping[header] = 'template'
            
            # Created by variations
            elif header_lower in ['created_by', 'creator', 'author', 'dibuat_oleh']:
                column_mapping[header] = 'created_by'
        
        logger.info(f"Column mapping applied: {column_mapping}")
        return column_mapping
    
    def _validate_template_data(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate that the data has required columns and valid content
        
        Args:
            data: List of dictionaries representing CSV rows
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not data:
            errors.append("CSV file is empty or has no data rows")
            return False, errors
        
        # Check first row for required columns
        first_row = data[0]
        missing_columns = [col for col in self.required_columns if col not in first_row]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for required data in key columns
        empty_targets = sum(1 for row in data if not row.get('reminder_target', '').strip())
        if empty_targets > 0:
            errors.append(f"Found {empty_targets} rows with empty reminder_target")
        
        empty_types = sum(1 for row in data if not row.get('reminder_type', '').strip())
        if empty_types > 0:
            errors.append(f"Found {empty_types} rows with empty reminder_type")
        
        empty_templates = sum(1 for row in data if not row.get('template', '').strip())
        if empty_templates > 0:
            errors.append(f"Found {empty_templates} rows with empty template")
        
        return len(errors) == 0, errors
    
    def _process_reminder_types(self, reminder_type_str: str) -> List[str]:
        """
        Process reminder_type field which may contain multiple types separated by semicolons
        
        Args:
            reminder_type_str: String that may contain multiple reminder types
            
        Returns:
            List of individual reminder types
        """
        if not reminder_type_str or reminder_type_str.strip().lower() in ['n/a', 'na', 'all']:
            return ['N/A']
        
        # Split by semicolon and clean up each type
        types = [t.strip() for t in reminder_type_str.split(';') if t.strip()]
        return types if types else ['N/A']
    
    def _convert_to_template_format(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert CSV data to template format expected by repository
        
        Args:
            data: List of dictionaries representing CSV rows
            
        Returns:
            List of template dictionaries
        """
        templates_data = []
        
        for row in data:
            # Skip rows with any missing required data
            if not all(row.get(col, '').strip() for col in self.required_columns):
                continue
            
            reminder_target = str(row['reminder_target']).strip()
            reminder_types = self._process_reminder_types(str(row['reminder_type']).strip())
            template_content = str(row['template']).strip()
            created_by = str(row.get('created_by', 'csv_import')).strip()
            
            # Create separate entries for each reminder type
            for reminder_type in reminder_types:
                template_dict = {
                    'reminder_target': reminder_target,
                    'reminder_type': reminder_type,
                    'template': template_content,
                    'created_by': created_by
                }
                
                templates_data.append(template_dict)
                logger.debug(f"Processed template: {template_dict['reminder_target']} - {template_dict['reminder_type']}")
        
        return templates_data
    
    def read_csv_templates(self) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Read templates from CSV file
        
        Returns:
            Tuple of (success, templates_data, message)
        """
        # Check if file exists
        if not os.path.exists(self.csv_file_path):
            logger.warning(f"CSV file not found: {self.csv_file_path}")
            return False, [], f"CSV file not found: {self.csv_file_path}"
        
        try:
            logger.info(f"Reading CSV file: {self.csv_file_path}")
            
            data = []
            with open(self.csv_file_path, 'r', encoding='utf-8-sig', newline='') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    return False, [], "CSV file has no headers"
                
                logger.info(f"CSV file headers: {headers}")
                
                # Normalize column names
                column_mapping = self._normalize_column_names(headers)
                
                # Read all rows and apply column mapping
                for row in reader:
                    if any(row.values()):  # Skip completely empty rows
                        normalized_row = {}
                        for original_key, value in row.items():
                            normalized_key = column_mapping.get(original_key, original_key)
                            normalized_row[normalized_key] = value or ''
                        data.append(normalized_row)
            
            logger.info(f"CSV file loaded: {len(data)} rows")
            
            # Validate data
            is_valid, errors = self._validate_template_data(data)
            if not is_valid:
                error_msg = "CSV validation errors: " + "; ".join(errors)
                logger.error(error_msg)
                return False, [], error_msg
            
            # Convert to template format
            templates_data = self._convert_to_template_format(data)
            
            if not templates_data:
                return False, [], "No valid template data found in CSV file"
            
            logger.info(f"Successfully processed {len(templates_data)} templates from CSV file")
            return True, templates_data, f"Successfully loaded {len(templates_data)} templates"
            
        except Exception as e:
            error_msg = f"Error reading CSV file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, [], error_msg
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the CSV file
        
        Returns:
            Dictionary with file information
        """
        info = {
            'file_path': self.csv_file_path,
            'exists': os.path.exists(self.csv_file_path),
            'size': None,
            'modified_time': None
        }
        
        if info['exists']:
            try:
                stat = os.stat(self.csv_file_path)
                info['size'] = stat.st_size
                info['modified_time'] = stat.st_mtime
            except Exception as e:
                logger.error(f"Error getting file info: {str(e)}")
        
        return info


def create_csv_template_loader(base_path: str = None) -> CSVTemplateLoader:
    """
    Factory function to create CSVTemplateLoader with standard file path
    
    Args:
        base_path: Base directory path. If None, uses current working directory
        
    Returns:
        CSVTemplateLoader instance
    """
    if base_path is None:
        base_path = os.getcwd()
    
    csv_file_path = os.path.join(base_path, 'files', 'reminder_template_v1.csv')
    return CSVTemplateLoader(csv_file_path)