"""
WhatsApp template model for customer service
"""

import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, Union
from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WhatsAppTemplate(Base):
    """WhatsApp message template model"""
    
    __tablename__ = "whatsapp_template"
    __table_args__ = (
        {"schema": "customer"}
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Template categorization
    reminder_target = Column(String(50), nullable=False, index=True)  # e.g., "KPB-1", "KPB-2", "Non KPB"
    reminder_type = Column(String(100), nullable=False, index=True)   # e.g., "H+30 tanggal beli (by WA)", "N/A"
    
    # Template content
    template = Column(Text, nullable=False)  # Message template with placeholders like {nama_pemilik}, {dealer_name}
    
    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified_by = Column(String(100), nullable=True)
    last_modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<WhatsAppTemplate(id={self.id}, reminder_target={self.reminder_target}, reminder_type={self.reminder_type})>"
    
    def to_dict(self):
        """Convert WhatsApp template to dictionary"""
        return {
            "id": str(self.id),
            "reminder_target": self.reminder_target,
            "reminder_type": self.reminder_type,
            "template": self.template,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_by": self.last_modified_by,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
        }
    
    @staticmethod
    def _format_date(date_value: Optional[Union[date, str]], default: str = "Tidak diketahui") -> str:
        """
        Format date to Indonesian readable format
        
        Args:
            date_value: Date object or string
            default: Default value if date is None or invalid
            
        Returns:
            Formatted date string
        """
        if date_value is None:
            return default
            
        try:
            if isinstance(date_value, str):
                # Try to parse string date
                try:
                    date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    return default
                    
            if isinstance(date_value, date):
                # Indonesian month names
                months = [
                    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
                ]
                return f"{date_value.day} {months[date_value.month - 1]} {date_value.year}"
                
        except (ValueError, IndexError, AttributeError):
            pass
            
        return default
    
    @staticmethod
    def _mask_phone(phone: Optional[str]) -> str:
        """
        Mask phone number for privacy if needed
        
        Args:
            phone: Phone number string
            
        Returns:
            Masked phone number
        """
        if not phone:
            return "Tidak tersedia"
            
        # Keep first 4 and last 2 digits, mask middle
        if len(phone) > 6:
            return f"{phone[:4]}****{phone[-2:]}"
        return phone
    
    @staticmethod 
    def _prepare_template_variables(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Prepare template variables with proper formatting and safe defaults
        
        Args:
            data: Raw data dictionary
            
        Returns:
            Processed template variables
        """
        # Safe getter function
        def safe_get(key: str, default: str = "") -> str:
            value = data.get(key)
            if value is None:
                return default
            return str(value).strip() if str(value).strip() else default
        
        # Prepare all possible template variables
        template_vars = {
            # Customer information
            'nama_pemilik': safe_get('nama_pemilik', 'Bpk/Ibu'),
            'nama_pembawa': safe_get('nama_pembawa', 'Tidak tersedia'),
            'nomor_telepon_pelanggan': safe_get('nomor_telepon_pelanggan', 'Tidak tersedia'),
            'no_telepon_pembawa': safe_get('no_telepon_pembawa', 'Tidak tersedia'),
            
            # Vehicle information
            'nomor_polisi': safe_get('nomor_polisi', 'Tidak tersedia'),
            'tipe_unit': safe_get('tipe_unit', 'Kendaraan Honda'),
            'nomor_mesin': safe_get('nomor_mesin', 'Tidak tersedia'),
            
            # Date information with special formatting
            'tanggal_beli': WhatsAppTemplate._format_date(data.get('tanggal_beli')),
            'tanggal_expired_kpb': WhatsAppTemplate._format_date(data.get('tanggal_expired_kpb')),
            
            # AHASS information
            'kode_ahass': safe_get('kode_ahass', 'Tidak tersedia'),
            'nama_ahass': safe_get('nama_ahass', 'AHASS'),
            'alamat_ahass': safe_get('alamat_ahass', 'Tidak tersedia'),
            
            # Dealer information
            'dealer_name': safe_get('dealer_name', 'Dealer Honda'),
            
            # Additional derived variables
            'customer_name': safe_get('nama_pemilik', 'Bpk/Ibu'),  # Alias for compatibility
            'unit_type': safe_get('tipe_unit', 'Kendaraan Honda'),  # Alias for compatibility
            'license_plate': safe_get('nomor_polisi', 'Tidak tersedia'),  # Alias for compatibility
        }
        
        return template_vars
    
    def format_template(self, **kwargs) -> str:
        """
        Format template with enhanced variable support
        
        Args:
            **kwargs: Template parameters including customer data, dates, etc.
            
        Returns:
            Formatted message string with all variables properly processed
        """
        try:
            # Prepare comprehensive template variables
            template_vars = self._prepare_template_variables(kwargs)
            
            # Try to format with prepared variables
            return self.template.format(**template_vars)
            
        except KeyError as e:
            # Handle missing template parameters gracefully
            missing_param = str(e).strip("'")
            
            # Add missing parameter with safe default
            template_vars = self._prepare_template_variables(kwargs)
            if missing_param not in template_vars:
                template_vars[missing_param] = f"[{missing_param}]"
            
            try:
                return self.template.format(**template_vars)
            except Exception:
                # Final fallback - replace all unmatched braces
                result = self.template
                for key, value in template_vars.items():
                    result = result.replace(f"{{{key}}}", str(value))
                return result
                
        except Exception as e:
            # Ultimate fallback - return template with error note
            return f"{self.template}\n\n[Error formatting template: {str(e)}]"