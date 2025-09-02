"""
Timezone utilities for consistent Indonesia timezone handling
Provides functions to work with Asia/Jakarta timezone (UTC+7)
"""

from datetime import datetime
from typing import Optional
import pytz

# Indonesia timezone (UTC+7)
INDONESIA_TZ = pytz.timezone('Asia/Jakarta')
UTC_TZ = pytz.UTC


def get_indonesia_datetime() -> datetime:
    """
    Get current datetime in Indonesia timezone (Asia/Jakarta)
    
    Returns:
        datetime: Current datetime in Asia/Jakarta timezone
    """
    return datetime.now(INDONESIA_TZ)


def convert_to_indonesia_timezone(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert any datetime to Indonesia timezone
    
    Args:
        dt: Datetime object (can be naive or timezone-aware)
        
    Returns:
        datetime: Datetime converted to Asia/Jakarta timezone, or None if input is None
    """
    if dt is None:
        return None
    
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = UTC_TZ.localize(dt)
    
    # Convert to Indonesia timezone
    return dt.astimezone(INDONESIA_TZ)


def format_indonesia_datetime(dt: Optional[datetime]) -> str:
    """
    Format datetime for Indonesia locale (dd/mm/yyyy HH:MM:SS)
    
    Args:
        dt: Datetime object
        
    Returns:
        str: Formatted datetime string or empty string if None
    """
    if dt is None:
        return ""
    
    # Ensure datetime is in Indonesia timezone
    indonesia_dt = convert_to_indonesia_timezone(dt)
    
    # Format as dd/mm/yyyy HH:MM:SS
    return indonesia_dt.strftime("%d/%m/%Y %H:%M:%S")


def format_indonesia_date(dt: Optional[datetime]) -> str:
    """
    Format date for Indonesia locale (dd/mm/yyyy)
    
    Args:
        dt: Datetime object
        
    Returns:
        str: Formatted date string or empty string if None
    """
    if dt is None:
        return ""
    
    # Ensure datetime is in Indonesia timezone
    indonesia_dt = convert_to_indonesia_timezone(dt)
    
    # Format as dd/mm/yyyy
    return indonesia_dt.strftime("%d/%m/%Y")


def format_indonesia_time(dt: Optional[datetime]) -> str:
    """
    Format time for Indonesia locale (HH:MM:SS)
    
    Args:
        dt: Datetime object
        
    Returns:
        str: Formatted time string or empty string if None
    """
    if dt is None:
        return ""
    
    # Ensure datetime is in Indonesia timezone
    indonesia_dt = convert_to_indonesia_timezone(dt)
    
    # Format as HH:MM:SS
    return indonesia_dt.strftime("%H:%M:%S")


def parse_datetime_indonesia_format(datetime_str: str) -> datetime:
    """
    Parse datetime string in Indonesia format (dd/mm/yyyy HH:MM:SS) to timezone-aware datetime
    
    Args:
        datetime_str: Datetime string in format 'dd/mm/yyyy HH:MM:SS'
        
    Returns:
        datetime: Timezone-aware datetime in Asia/Jakarta timezone
        
    Raises:
        ValueError: If datetime string format is invalid
    """
    try:
        # Parse the datetime string
        naive_dt = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
        
        # Localize to Indonesia timezone (assumes input is already in Indonesia timezone)
        return INDONESIA_TZ.localize(naive_dt)
        
    except ValueError as e:
        raise ValueError(f"Invalid datetime format. Expected 'dd/mm/yyyy HH:MM:SS', got: {datetime_str}") from e