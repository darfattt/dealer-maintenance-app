"""
Excel template reader service for WhatsApp templates
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)


class ExcelTemplateReader:
    """Service for reading WhatsApp templates from Excel files"""
    
    def __init__(self, excel_file_path: str):
        """
        Initialize Excel template reader
        
        Args:
            excel_file_path: Path to the Excel file containing templates
        """
        self.excel_file_path = excel_file_path
        self.required_columns = ['reminder_target', 'reminder_type', 'template']
        
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        if pd is None:
            logger.error("pandas is not installed. Please install pandas and openpyxl to use Excel template reading.")
            return False
        return True
    
    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to match expected format
        
        Args:
            df: DataFrame with potentially different column names
            
        Returns:
            DataFrame with normalized column names
        """
        # Create mapping for common column name variations
        column_mapping = {}
        
        # Map various possible column names to standard names
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            # Reminder target variations
            if col_lower in ['reminder_target', 'reminder target', 'target', 'kategori', 'category']:
                column_mapping[col] = 'reminder_target'
            
            # Reminder type variations  
            elif col_lower in ['reminder_type', 'reminder type', 'type', 'jenis', 'tipe']:
                column_mapping[col] = 'reminder_type'
            
            # Template/message variations
            elif col_lower in ['template', 'message', 'pesan', 'text', 'content', 'isi']:
                column_mapping[col] = 'template'
            
            # Created by variations
            elif col_lower in ['created_by', 'creator', 'author', 'dibuat_oleh']:
                column_mapping[col] = 'created_by'
        
        # Rename columns
        df_normalized = df.rename(columns=column_mapping)
        
        logger.info(f"Column mapping applied: {column_mapping}")
        return df_normalized
    
    def _validate_template_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that the DataFrame has required columns and valid data
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty dataframe
        if df.empty:
            errors.append("Excel file is empty or has no data rows")
        
        # Check for required data in key columns
        if 'reminder_target' in df.columns:
            empty_targets = df['reminder_target'].isna().sum()
            if empty_targets > 0:
                errors.append(f"Found {empty_targets} rows with empty reminder_target")
        
        if 'reminder_type' in df.columns:
            empty_types = df['reminder_type'].isna().sum()
            if empty_types > 0:
                errors.append(f"Found {empty_types} rows with empty reminder_type")
        
        if 'template' in df.columns:
            empty_templates = df['template'].isna().sum()
            if empty_templates > 0:
                errors.append(f"Found {empty_templates} rows with empty template")
        
        return len(errors) == 0, errors
    
    def _convert_to_template_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to template format expected by repository
        
        Args:
            df: Validated DataFrame with template data
            
        Returns:
            List of template dictionaries
        """
        templates_data = []
        
        for _, row in df.iterrows():
            # Skip rows with any missing required data
            if pd.isna(row['reminder_target']) or pd.isna(row['reminder_type']) or pd.isna(row['template']):
                continue
            
            template_dict = {
                'reminder_target': str(row['reminder_target']).strip(),
                'reminder_type': str(row['reminder_type']).strip(),
                'template': str(row['template']).strip(),
                'created_by': str(row.get('created_by', 'excel_import')).strip()
            }
            
            # Ensure template is not empty after stripping
            if template_dict['template']:
                templates_data.append(template_dict)
                logger.debug(f"Processed template: {template_dict['reminder_target']} - {template_dict['reminder_type']}")
        
        return templates_data
    
    def read_excel_templates(self) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Read templates from Excel file
        
        Returns:
            Tuple of (success, templates_data, message)
        """
        # Check dependencies
        if not self._check_dependencies():
            return False, [], "Missing required dependencies (pandas, openpyxl)"
        
        # Check if file exists
        if not os.path.exists(self.excel_file_path):
            logger.warning(f"Excel file not found: {self.excel_file_path}")
            return False, [], f"Excel file not found: {self.excel_file_path}"
        
        try:
            logger.info(f"Reading Excel file: {self.excel_file_path}")
            
            # Read Excel file - try different sheet names
            df = None
            sheet_names_to_try = [0, 'Sheet1', 'Templates', 'Reminder Templates', 'Data']
            
            for sheet_name in sheet_names_to_try:
                try:
                    df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
                    logger.info(f"Successfully read sheet: {sheet_name}")
                    break
                except Exception as e:
                    logger.debug(f"Could not read sheet '{sheet_name}': {str(e)}")
                    continue
            
            if df is None:
                return False, [], "Could not read any sheet from Excel file"
            
            logger.info(f"Excel file loaded: {len(df)} rows, columns: {list(df.columns)}")
            
            # Normalize column names
            df = self._normalize_column_names(df)
            
            # Validate data
            is_valid, errors = self._validate_template_data(df)
            if not is_valid:
                error_msg = "Excel validation errors: " + "; ".join(errors)
                logger.error(error_msg)
                return False, [], error_msg
            
            # Convert to template format
            templates_data = self._convert_to_template_format(df)
            
            if not templates_data:
                return False, [], "No valid template data found in Excel file"
            
            logger.info(f"Successfully processed {len(templates_data)} templates from Excel file")
            return True, templates_data, f"Successfully loaded {len(templates_data)} templates"
            
        except Exception as e:
            error_msg = f"Error reading Excel file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, [], error_msg
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the Excel file
        
        Returns:
            Dictionary with file information
        """
        info = {
            'file_path': self.excel_file_path,
            'exists': os.path.exists(self.excel_file_path),
            'size': None,
            'modified_time': None
        }
        
        if info['exists']:
            try:
                stat = os.stat(self.excel_file_path)
                info['size'] = stat.st_size
                info['modified_time'] = stat.st_mtime
            except Exception as e:
                logger.error(f"Error getting file info: {str(e)}")
        
        return info


def create_excel_template_reader(base_path: str = None) -> ExcelTemplateReader:
    """
    Factory function to create ExcelTemplateReader with standard file path
    
    Args:
        base_path: Base directory path. If None, uses current working directory
        
    Returns:
        ExcelTemplateReader instance
    """
    if base_path is None:
        base_path = os.getcwd()
    
    excel_file_path = os.path.join(base_path, 'files', 'reminder_template_v1.xlsx')
    return ExcelTemplateReader(excel_file_path)