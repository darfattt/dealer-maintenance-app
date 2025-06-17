"""
Status mapping utilities for unit inbound data
"""

from typing import Dict, Optional


class UnitInboundStatusMapper:
    """Mapper for unit inbound status codes to human-readable labels"""
    
    # Status mapping based on API specification
    STATUS_MAPPING = {
        '0': 'Belum Diterima',
        '1': 'Sudah Diterima',
        '2': 'Sudah Diterima',  # Assuming 2 is also "received" based on data
        # Fallback for text statuses (test data)
        'DELIVERED': 'Sudah Diterima',
        'PENDING': 'Belum Diterima', 
        'IN_TRANSIT': 'Dalam Perjalanan',
        'CANCELLED': 'Dibatalkan'
    }
    
    @classmethod
    def get_mapped_status(cls, original_status: Optional[str]) -> str:
        """
        Get the mapped status label for a given original status
        
        Args:
            original_status: The original status code/text
            
        Returns:
            Mapped status label in Indonesian
        """
        if not original_status:
            return 'Unknown'
            
        return cls.STATUS_MAPPING.get(str(original_status), original_status)
    
    @classmethod
    def get_all_mappings(cls) -> Dict[str, str]:
        """Get all status mappings"""
        return cls.STATUS_MAPPING.copy()
