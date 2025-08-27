"""
Phone number masking utilities for customer privacy
"""

def mask_phone_number(phone_number: str) -> str:
    """
    Mask phone number for privacy protection.
    
    Formats Indonesian phone numbers in the style: 081*****02
    - Shows first 3 digits
    - Masks middle digits with exactly 5 asterisks
    - Shows last 2 digits
    
    Args:
        phone_number (str): The phone number to mask
        
    Returns:
        str: Masked phone number or original if invalid format
        
    Examples:
        "08123456789" -> "081*****89"
        "6281234567890" -> "628*****90"
        "123" -> "123" (too short, return as-is)
    """
    if not phone_number or not isinstance(phone_number, str):
        return phone_number or ""
    
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone_number))
    
    # If phone number is too short (less than 6 digits), return as-is
    if len(digits_only) < 6:
        return phone_number
    
    # For longer numbers, mask middle part with exactly 5 asterisks
    # Show first 3 digits
    prefix = digits_only[:3]
    # Show last 2 digits
    suffix = digits_only[-2:]
    # Always use exactly 5 asterisks regardless of original length
    asterisks = '*' * 5
    
    return f"{prefix}{asterisks}{suffix}"