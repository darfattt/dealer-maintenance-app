"""
WhatsApp template repository
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
import logging

from app.models.whatsapp_template import WhatsAppTemplate
from app.schemas.customer_reminder_request import BulkReminderCustomerData

logger = logging.getLogger(__name__)


class WhatsAppTemplateRepository:
    """Repository for WhatsApp template operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_template(self, reminder_target: str, reminder_type: str) -> Optional[WhatsAppTemplate]:
        """
        Get template by reminder_target and reminder_type
        
        Args:
            reminder_target: Target category (e.g., "KPB-1", "Non KPB")
            reminder_type: Type of reminder (e.g., "H+30 tanggal beli (by WA)", "N/A")
            
        Returns:
            WhatsAppTemplate object or None if not found
        """
        try:
            template = self.db.query(WhatsAppTemplate).filter(
                and_(
                    WhatsAppTemplate.reminder_target == reminder_target,
                    WhatsAppTemplate.reminder_type == reminder_type
                )
            ).first()
            
            if template:
                logger.debug(f"Found template for {reminder_target} - {reminder_type}")
            else:
                logger.warning(f"No template found for {reminder_target} - {reminder_type}")
                
            return template
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting template for {reminder_target} - {reminder_type}: {str(e)}")
            return None
    
    def get_template_with_fallback(self, reminder_target: str, reminder_type: str) -> Optional[WhatsAppTemplate]:
        """
        Get template with fallback logic:
        1. Try exact match (reminder_target + reminder_type)
        2. If not found and reminder_type is "N/A", try reminder_target + "N/A"
        3. If still not found, try generic template
        
        Args:
            reminder_target: Target category
            reminder_type: Type of reminder
            
        Returns:
            WhatsAppTemplate object or None
        """
        # Try exact match first
        template = self.get_template(reminder_target, reminder_type)
        if template:
            return template
        
        # If reminder_type is not "N/A", try with "N/A" for the same target
        if reminder_type != "N/A":
            logger.info(f"Trying fallback with reminder_type 'N/A' for target {reminder_target}")
            template = self.get_template(reminder_target, "N/A")
            if template:
                return template
        
        # Try generic fallback templates
        fallback_targets = ["Non KPB", "Booking Service"]
        for fallback_target in fallback_targets:
            logger.info(f"Trying fallback target: {fallback_target}")
            template = self.get_template(fallback_target, "N/A")
            if template:
                return template
        
        logger.error(f"No template found even with fallbacks for {reminder_target} - {reminder_type}")
        return None
    
    def get_all_templates(self) -> List[WhatsAppTemplate]:
        """Get all WhatsApp templates"""
        try:
            return self.db.query(WhatsAppTemplate).order_by(
                WhatsAppTemplate.reminder_target,
                WhatsAppTemplate.reminder_type
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting all templates: {str(e)}")
            return []
    
    def upsert_template(
        self,
        reminder_target: str,
        reminder_type: str,
        template: str,
        modified_by: Optional[str] = None
    ) -> Optional[WhatsAppTemplate]:
        """
        Insert or update template data
        
        Args:
            reminder_target: Target category
            reminder_type: Type of reminder
            template: Template content
            modified_by: User who modified the template
            
        Returns:
            WhatsAppTemplate object or None on error
        """
        try:
            # Check if template already exists
            existing_template = self.get_template(reminder_target, reminder_type)
            
            if existing_template:
                # Update existing template
                existing_template.template = template
                existing_template.last_modified_by = modified_by or 'system'
                existing_template.last_modified_date = datetime.utcnow()
                
                self.db.commit()
                logger.info(f"Updated template for {reminder_target} - {reminder_type}")
                return existing_template
            else:
                # Create new template
                new_template = WhatsAppTemplate(
                    reminder_target=reminder_target,
                    reminder_type=reminder_type,
                    template=template,
                    created_by=modified_by or 'system',
                    last_modified_by=modified_by or 'system'
                )
                
                self.db.add(new_template)
                self.db.commit()
                self.db.refresh(new_template)
                
                logger.info(f"Created new template for {reminder_target} - {reminder_type}")
                return new_template
                
        except SQLAlchemyError as e:
            logger.error(f"Database error upserting template for {reminder_target} - {reminder_type}: {str(e)}")
            self.db.rollback()
            return None
    
    def bulk_upsert_templates(self, templates_data: List[Dict[str, str]]) -> bool:
        """
        Bulk upsert multiple templates
        
        Args:
            templates_data: List of dictionaries with template data
                Each dict should have: reminder_target, reminder_type, template
                
        Returns:
            True if successful, False otherwise
        """
        try:
            success_count = 0
            for template_data in templates_data:
                result = self.upsert_template(
                    reminder_target=template_data['reminder_target'],
                    reminder_type=template_data['reminder_type'],
                    template=template_data['template'],
                    modified_by=template_data.get('created_by', 'system')
                )
                if result:
                    success_count += 1
            
            logger.info(f"Bulk upsert completed: {success_count}/{len(templates_data)} templates processed")
            return success_count == len(templates_data)
            
        except Exception as e:
            logger.error(f"Error in bulk upsert templates: {str(e)}")
            return False
    
    def get_templates_by_target(self, reminder_target: str) -> List[WhatsAppTemplate]:
        """Get all templates for a specific reminder target"""
        try:
            return self.db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.reminder_target == reminder_target
            ).order_by(WhatsAppTemplate.reminder_type).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting templates for target {reminder_target}: {str(e)}")
            return []
    
    def delete_template(self, reminder_target: str, reminder_type: str) -> bool:
        """Delete a specific template"""
        try:
            template = self.get_template(reminder_target, reminder_type)
            if template:
                self.db.delete(template)
                self.db.commit()
                logger.info(f"Deleted template for {reminder_target} - {reminder_type}")
                return True
            else:
                logger.warning(f"Template not found for deletion: {reminder_target} - {reminder_type}")
                return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting template: {str(e)}")
            self.db.rollback()
            return False
    
    @staticmethod
    def _extract_customer_data_dict(customer_data: Union[BulkReminderCustomerData, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract customer data into a dictionary for template formatting
        
        Args:
            customer_data: Customer data object or dictionary
            
        Returns:
            Dictionary with all customer data fields
        """
        if isinstance(customer_data, BulkReminderCustomerData):
            # Extract from Pydantic model
            return {
                'nama_pelanggan': customer_data.nama_pelanggan,
                'nomor_telepon_pelanggan': customer_data.nomor_telepon_pelanggan,
                'nomor_mesin': customer_data.nomor_mesin,
                'nomor_polisi': customer_data.nomor_polisi,
                'tipe_unit': customer_data.tipe_unit,
                'tanggal_beli': customer_data.tanggal_beli,
                'tanggal_expired_kpb': customer_data.tanggal_expired_kpb,
            }
        elif isinstance(customer_data, dict):
            # Return dictionary as-is but ensure all expected keys exist
            return {
                'nama_pelanggan': customer_data.get('nama_pelanggan'),
                'nomor_telepon_pelanggan': customer_data.get('nomor_telepon_pelanggan'),
                'nomor_mesin': customer_data.get('nomor_mesin'),
                'nomor_polisi': customer_data.get('nomor_polisi'),
                'tipe_unit': customer_data.get('tipe_unit'),
                'tanggal_beli': customer_data.get('tanggal_beli'),
                'tanggal_expired_kpb': customer_data.get('tanggal_expired_kpb'),
            }
        else:
            logger.warning(f"Unexpected customer_data type: {type(customer_data)}")
            return {}
    
    def format_template_with_customer_data(
        self,
        reminder_target: str,
        reminder_type: str,
        customer_data: Union[BulkReminderCustomerData, Dict[str, Any]],
        ahass_data: Optional[Dict[str, Any]] = None,
        dealer_name: Optional[str] = None,
        **additional_kwargs
    ) -> Optional[str]:
        """
        Get and format template with comprehensive customer data
        
        Args:
            reminder_target: Target category
            reminder_type: Type of reminder  
            customer_data: Customer data object or dictionary
            ahass_data: AHASS information dictionary
            dealer_name: Dealer name
            **additional_kwargs: Any additional template parameters
            
        Returns:
            Formatted message string or None if template not found
        """
        template = self.get_template_with_fallback(reminder_target, reminder_type)
        if not template:
            return None
        
        # Extract customer data
        extracted_data = self._extract_customer_data_dict(customer_data)
        
        # Add AHASS data if provided
        if ahass_data:
            extracted_data.update({
                'kode_ahass': ahass_data.get('kode_ahass'),
                'nama_ahass': ahass_data.get('nama_ahass'),
                'alamat_ahass': ahass_data.get('alamat_ahass'),
            })
        
        # Add dealer information
        if dealer_name:
            extracted_data['dealer_name'] = dealer_name
        
        # Add any additional parameters
        extracted_data.update(additional_kwargs)
        
        try:
            return template.format_template(**extracted_data)
        except Exception as e:
            logger.error(f"Error formatting template with customer data: {str(e)}")
            return None
    
    def format_template(
        self,
        reminder_target: str,
        reminder_type: str,
        **kwargs
    ) -> Optional[str]:
        """
        Get and format template with provided parameters (legacy method)
        
        Args:
            reminder_target: Target category
            reminder_type: Type of reminder
            **kwargs: Template parameters (e.g., nama_pemilik, dealer_name)
            
        Returns:
            Formatted message string or None if template not found
        """
        template = self.get_template_with_fallback(reminder_target, reminder_type)
        if template:
            return template.format_template(**kwargs)
        return None
    
    def backup_existing_templates(self) -> List[Dict[str, Any]]:
        """
        Create backup of existing templates before replacement
        
        Returns:
            List of existing templates as dictionaries
        """
        try:
            existing_templates = self.get_all_templates()
            backup_data = [template.to_dict() for template in existing_templates]
            logger.info(f"Backed up {len(backup_data)} existing templates")
            return backup_data
        except Exception as e:
            logger.error(f"Error backing up templates: {str(e)}")
            return []
    
    def replace_all_templates(self, templates_data: List[Dict[str, str]], backup_first: bool = True) -> bool:
        """
        Replace all existing templates with new template data
        
        Args:
            templates_data: List of template dictionaries
            backup_first: Whether to backup existing templates first
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Backup existing templates if requested
            backup_data = []
            if backup_first:
                backup_data = self.backup_existing_templates()
            
            # Delete all existing templates
            deleted_count = self.db.query(WhatsAppTemplate).delete()
            logger.info(f"Deleted {deleted_count} existing templates")
            
            # Insert new templates
            success_count = 0
            for template_data in templates_data:
                try:
                    new_template = WhatsAppTemplate(
                        reminder_target=template_data['reminder_target'],
                        reminder_type=template_data['reminder_type'],
                        template=template_data['template'],
                        created_by=template_data.get('created_by', 'excel_import')
                    )
                    
                    self.db.add(new_template)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error inserting template {template_data.get('reminder_target', 'Unknown')} - {template_data.get('reminder_type', 'Unknown')}: {str(e)}")
                    continue
            
            # Commit all changes
            self.db.commit()
            logger.info(f"Successfully replaced templates: {success_count}/{len(templates_data)} inserted")
            
            return success_count == len(templates_data)
            
        except Exception as e:
            logger.error(f"Error replacing templates: {str(e)}")
            self.db.rollback()
            
            # If backup exists, could potentially restore here
            if backup_data:
                logger.info(f"Backup available with {len(backup_data)} templates for manual recovery")
            
            return False
    
    def update_templates_from_excel(self, excel_templates_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Update templates from Excel data with detailed reporting
        
        Args:
            excel_templates_data: Template data from Excel file
            
        Returns:
            Dictionary with update results and statistics
        """
        result = {
            'success': False,
            'total_processed': len(excel_templates_data),
            'successfully_updated': 0,
            'errors': [],
            'backup_created': False,
            'message': ''
        }
        
        try:
            logger.info(f"Starting template update from Excel with {len(excel_templates_data)} templates")
            
            # Create backup
            backup_data = self.backup_existing_templates()
            result['backup_created'] = len(backup_data) > 0
            
            # Replace all templates
            success = self.replace_all_templates(excel_templates_data, backup_first=False)  # Already backed up
            
            if success:
                result['success'] = True
                result['successfully_updated'] = len(excel_templates_data)
                result['message'] = f"Successfully updated {len(excel_templates_data)} templates from Excel"
                logger.info(result['message'])
            else:
                result['message'] = "Failed to update some templates from Excel"
                result['errors'].append("Not all templates were successfully updated")
            
        except Exception as e:
            error_msg = f"Error updating templates from Excel: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['message'] = error_msg
        
        return result
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about current templates in database
        
        Returns:
            Dictionary with template statistics
        """
        try:
            total_templates = self.db.query(WhatsAppTemplate).count()
            
            # Count by reminder target
            target_stats = {}
            targets = self.db.query(WhatsAppTemplate.reminder_target).distinct().all()
            for (target,) in targets:
                count = self.db.query(WhatsAppTemplate).filter(
                    WhatsAppTemplate.reminder_target == target
                ).count()
                target_stats[target] = count
            
            # Count by reminder type  
            type_stats = {}
            types = self.db.query(WhatsAppTemplate.reminder_type).distinct().all()
            for (reminder_type,) in types:
                count = self.db.query(WhatsAppTemplate).filter(
                    WhatsAppTemplate.reminder_type == reminder_type
                ).count()
                type_stats[reminder_type] = count
            
            return {
                'total_templates': total_templates,
                'targets': target_stats,
                'types': type_stats,
                'unique_targets': len(target_stats),
                'unique_types': len(type_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting template statistics: {str(e)}")
            return {
                'total_templates': 0,
                'targets': {},
                'types': {},
                'unique_targets': 0,
                'unique_types': 0,
                'error': str(e)
            }