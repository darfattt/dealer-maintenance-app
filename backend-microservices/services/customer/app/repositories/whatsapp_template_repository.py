"""
WhatsApp template repository
"""

from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func, desc
import logging
import uuid

from app.models.whatsapp_template import WhatsAppTemplate
from app.schemas.customer_reminder_request import BulkReminderCustomerData, get_target_only_categories, get_kpb_categories

logger = logging.getLogger(__name__)


class WhatsAppTemplateRepository:
    """Repository for WhatsApp template operations"""

    def __init__(self, db: Session):
        self.db = db
    
    def get_template(self, reminder_target: str, reminder_type: str, dealer_id: Optional[str] = None) -> Optional[WhatsAppTemplate]:
        """
        Get template by reminder_target and reminder_type, with optional dealer_id filtering

        Args:
            reminder_target: Target category (e.g., "KPB-1", "Non KPB")
            reminder_type: Type of reminder (e.g., "H+30 tanggal beli (by WA)", "N/A")
            dealer_id: Optional dealer ID for dealer-specific templates

        Returns:
            WhatsAppTemplate object or None if not found
        """
        try:
            # Build query with base filters
            query = self.db.query(WhatsAppTemplate).filter(
                and_(
                    WhatsAppTemplate.reminder_target == reminder_target,
                    WhatsAppTemplate.reminder_type == reminder_type
                )
            )

            # If dealer_id is provided, prioritize dealer-specific templates, then global
            if dealer_id:
                # First try dealer-specific template
                dealer_template = query.filter(WhatsAppTemplate.dealer_id == dealer_id).first()
                if dealer_template:
                    logger.debug(f"Found dealer-specific template for {reminder_target} - {reminder_type} (dealer: {dealer_id})")
                    return dealer_template

                # Fallback to global template (dealer_id is NULL)
                global_template = query.filter(WhatsAppTemplate.dealer_id.is_(None)).first()
                if global_template:
                    logger.debug(f"Found global template for {reminder_target} - {reminder_type} (fallback from dealer: {dealer_id})")
                    return global_template
            else:
                # No dealer_id specified, just get any template (preferably global)
                template = query.filter(WhatsAppTemplate.dealer_id.is_(None)).first()
                if template:
                    logger.debug(f"Found global template for {reminder_target} - {reminder_type}")
                    return template

                # If no global template, get any template
                template = query.first()
                if template:
                    logger.debug(f"Found template for {reminder_target} - {reminder_type}")
                    return template

            logger.warning(f"No template found for {reminder_target} - {reminder_type} (dealer: {dealer_id})")
            return None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting template for {reminder_target} - {reminder_type} (dealer: {dealer_id}): {str(e)}")
            return None

    def get_template_by_target_only(self, reminder_target: str, dealer_id: Optional[str] = None) -> Optional[WhatsAppTemplate]:
        """
        Get template by reminder_target only (for templates without specific reminder_type)

        Args:
            reminder_target: Target category (e.g., "Booking Servis", "Non KPB")
            dealer_id: Optional dealer ID for dealer-specific templates

        Returns:
            WhatsAppTemplate object or None if not found
        """
        try:
            # Build query with base filter
            query = self.db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.reminder_target == reminder_target
            )

            # If dealer_id is provided, prioritize dealer-specific templates, then global
            if dealer_id:
                # First try dealer-specific template
                dealer_template = query.filter(WhatsAppTemplate.dealer_id == dealer_id).first()
                if dealer_template:
                    logger.debug(f"Found dealer-specific target-only template for {reminder_target} (dealer: {dealer_id})")
                    return dealer_template

                # Fallback to global template (dealer_id is NULL)
                global_template = query.filter(WhatsAppTemplate.dealer_id.is_(None)).first()
                if global_template:
                    logger.debug(f"Found global target-only template for {reminder_target} (fallback from dealer: {dealer_id})")
                    return global_template
            else:
                # No dealer_id specified, just get any template (preferably global)
                template = query.filter(WhatsAppTemplate.dealer_id.is_(None)).first()
                if template:
                    logger.debug(f"Found global target-only template for {reminder_target}")
                    return template

                # If no global template, get any template
                template = query.first()
                if template:
                    logger.debug(f"Found target-only template for {reminder_target}")
                    return template

            logger.debug(f"No target-only template found for {reminder_target} (dealer: {dealer_id})")
            return None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting target-only template for {reminder_target} (dealer: {dealer_id}): {str(e)}")
            return None

    def get_template_with_fallback(self, reminder_target: str, reminder_type: str, dealer_id: Optional[str] = None) -> Optional[WhatsAppTemplate]:
        """
        Get template with simplified category-based logic:
        1. If target is in TARGET_ONLY_CATEGORIES → query by target only
        2. If target is in KPB_CATEGORIES → try exact match, then with "N/A"
        3. Otherwise → return None

        Args:
            reminder_target: Target category
            reminder_type: Type of reminder
            dealer_id: Optional dealer ID for dealer-specific templates

        Returns:
            WhatsAppTemplate object or None
        """
        logger.info(f"target : {reminder_target} (dealer: {dealer_id})")
        # Check if this is a target-only category
        if reminder_target in get_target_only_categories():
            logger.info(f"Using target-only query for {reminder_target} (dealer: {dealer_id})")
            return self.get_template_by_target_only(reminder_target, dealer_id)

        # Check if this is a KPB category
        if reminder_target in get_kpb_categories():
            logger.info(f"Using full query for KPB target {reminder_target} (dealer: {dealer_id})")

            # Try exact match first
            template = self.get_template(reminder_target, reminder_type, dealer_id)
            if template:
                return template

            # Try with "N/A" if not already "N/A"
            if reminder_type != "N/A":
                logger.info(f"Trying fallback with reminder_type 'N/A' for KPB target {reminder_target} (dealer: {dealer_id})")
                template = self.get_template(reminder_target, "N/A", dealer_id)
                if template:
                    return template

        # No template found for this category
        logger.warning(f"No template found for {reminder_target} - {reminder_type} (dealer: {dealer_id})")
        return None
    
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
        dealer_id: Optional[str] = None,
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
            dealer_id: Optional dealer ID for dealer-specific templates
            **additional_kwargs: Any additional template parameters

        Returns:
            Formatted message string or None if template not found
        """
        template = self.get_template_with_fallback(reminder_target, reminder_type, dealer_id)
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

            # Delete all existing templates
            deleted_count = self.db.query(WhatsAppTemplate).delete()
            logger.info(f"Deleted {deleted_count} existing templates")

            # Insert new templates
            success_count = 0
            for template_data in excel_templates_data:
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
                    result['errors'].append(str(e))
                    continue

            # Commit all changes
            self.db.commit()
            result['successfully_updated'] = success_count
            logger.info(f"Successfully replaced templates: {success_count}/{len(excel_templates_data)} inserted")

            if success_count == len(excel_templates_data):
                result['success'] = True
                result['message'] = f"Successfully updated {len(excel_templates_data)} templates from Excel"
            else:
                result['message'] = f"Partially updated: {success_count}/{len(excel_templates_data)} templates from Excel"

        except Exception as e:
            error_msg = f"Error updating templates from Excel: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['message'] = error_msg
            self.db.rollback()

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

    def get_templates_paginated(
        self,
        dealer_id: Optional[str] = None,
        reminder_target: Optional[str] = None,
        template_content: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[WhatsAppTemplate], Dict[str, Any]]:
        """
        Get paginated list of templates with optional filtering

        Args:
            dealer_id: Filter by exact dealer ID (empty string for global templates)
            reminder_target: Filter by exact reminder target
            template_content: Search in template content (contains)
            page: Page number (1-based)
            size: Page size (max 100)

        Returns:
            Tuple of (templates list, pagination metadata)
        """
        try:
            # Validate and adjust parameters
            page = max(1, page)
            size = min(100, max(1, size))
            offset = (page - 1) * size

            # Build base query
            query = self.db.query(WhatsAppTemplate)

            # Apply filters
            filters = []

            # Dealer ID filter - handle both null and specific dealer
            if dealer_id is not None:
                if dealer_id == "":
                    # Filter for global templates (dealer_id is NULL)
                    filters.append(WhatsAppTemplate.dealer_id.is_(None))
                else:
                    # Filter for specific dealer
                    filters.append(WhatsAppTemplate.dealer_id == dealer_id)

            # Reminder target filter
            if reminder_target:
                filters.append(WhatsAppTemplate.reminder_target == reminder_target)

            # Template content search (case-insensitive contains)
            if template_content:
                filters.append(WhatsAppTemplate.template.ilike(f"%{template_content}%"))

            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))

            # Get total count for pagination
            total = query.count()

            # Apply ordering and pagination
            templates = (
                query.order_by(desc(WhatsAppTemplate.last_modified_date))
                .limit(size)
                .offset(offset)
                .all()
            )

            # Calculate pagination metadata
            total_pages = (total + size - 1) // size
            has_next = page < total_pages
            has_previous = page > 1

            pagination = {
                "page": page,
                "size": size,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous
            }

            logger.debug(f"Retrieved {len(templates)} templates (page {page}/{total_pages})")
            return templates, pagination

        except SQLAlchemyError as e:
            logger.error(f"Database error getting paginated templates: {str(e)}")
            return [], {"page": 1, "size": size, "total": 0, "total_pages": 0, "has_next": False, "has_previous": False}

    def get_template_by_id(self, template_id: str) -> Optional[WhatsAppTemplate]:
        """
        Get template by ID

        Args:
            template_id: Template UUID

        Returns:
            WhatsAppTemplate object or None if not found
        """
        try:
            return self.db.query(WhatsAppTemplate).filter(WhatsAppTemplate.id == template_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting template by ID {template_id}: {str(e)}")
            return None

    def update_template_by_id(
        self,
        template_id: str,
        template: str,
        reminder_target: str,
        reminder_type: str,
        last_modified_by: str
    ) -> Optional[WhatsAppTemplate]:
        """
        Update template by ID (only allowed fields)

        Args:
            template_id: Template UUID
            template: New template content
            reminder_target: New reminder target
            reminder_type: New reminder type
            last_modified_by: User making the update

        Returns:
            Updated WhatsAppTemplate object or None if not found/failed
        """
        try:
            # Get existing template
            existing_template = self.get_template_by_id(template_id)
            if not existing_template:
                logger.warning(f"Template not found for update: {template_id}")
                return None

            # Update allowed fields
            existing_template.template = template
            existing_template.reminder_target = reminder_target
            existing_template.reminder_type = reminder_type
            existing_template.last_modified_by = last_modified_by
            existing_template.last_modified_date = datetime.utcnow()

            self.db.commit()
            self.db.refresh(existing_template)

            logger.debug(f"Updated template: {template_id}")
            return existing_template

        except SQLAlchemyError as e:
            logger.error(f"Database error updating template {template_id}: {str(e)}")
            self.db.rollback()
            return None

    def delete_template_by_id(self, template_id: str) -> bool:
        """
        Delete template by ID

        Args:
            template_id: Template UUID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get existing template to verify it exists
            existing_template = self.get_template_by_id(template_id)
            if not existing_template:
                logger.warning(f"Template not found for deletion: {template_id}")
                return False

            # Delete the template
            self.db.delete(existing_template)
            self.db.commit()

            logger.debug(f"Deleted template: {template_id}")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error deleting template {template_id}: {str(e)}")
            self.db.rollback()
            return False

    def get_templates_by_dealer_id(self, dealer_id: str) -> List[WhatsAppTemplate]:
        """
        Get all templates for a specific dealer

        Args:
            dealer_id: Dealer ID

        Returns:
            List of WhatsAppTemplate objects
        """
        try:
            return (
                self.db.query(WhatsAppTemplate)
                .filter(WhatsAppTemplate.dealer_id == dealer_id)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting templates for dealer {dealer_id}: {str(e)}")
            return []

    def copy_templates(
        self,
        source_dealer_id: str,
        target_dealer_id: str,
        overwrite_existing: bool = False,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Copy all templates from source dealer to target dealer

        Args:
            source_dealer_id: Source dealer ID
            target_dealer_id: Target dealer ID
            overwrite_existing: Whether to overwrite existing templates
            created_by: User performing the copy operation

        Returns:
            Dictionary with copy operation results
        """
        result = {
            "templates_found": 0,
            "templates_copied": 0,
            "templates_skipped": 0,
            "templates_overwritten": 0,
            "errors": []
        }

        try:
            # Get source templates
            source_templates = self.get_templates_by_dealer_id(source_dealer_id)
            result["templates_found"] = len(source_templates)

            if not source_templates:
                logger.warning(f"No templates found for source dealer: {source_dealer_id}")
                return result

            # Get existing target templates if not overwriting
            existing_target_templates = {}
            if not overwrite_existing:
                target_templates = self.get_templates_by_dealer_id(target_dealer_id)
                existing_target_templates = {
                    (t.reminder_target, t.reminder_type): t for t in target_templates
                }

            # Copy each template
            for source_template in source_templates:
                try:
                    template_key = (source_template.reminder_target, source_template.reminder_type)

                    # Check if template already exists for target dealer
                    if template_key in existing_target_templates:
                        if overwrite_existing:
                            # Update existing template
                            existing_template = existing_target_templates[template_key]
                            existing_template.template = source_template.template
                            existing_template.last_modified_by = created_by
                            existing_template.last_modified_date = datetime.utcnow()
                            result["templates_overwritten"] += 1
                        else:
                            # Skip existing template
                            result["templates_skipped"] += 1
                            continue
                    else:
                        # Create new template
                        new_template = WhatsAppTemplate(
                            id=str(uuid.uuid4()),
                            reminder_target=source_template.reminder_target,
                            reminder_type=source_template.reminder_type,
                            dealer_id=target_dealer_id,
                            template=source_template.template,
                            created_by=created_by,
                            created_date=datetime.utcnow(),
                            last_modified_by=created_by,
                            last_modified_date=datetime.utcnow()
                        )
                        self.db.add(new_template)
                        result["templates_copied"] += 1

                except Exception as e:
                    error_msg = f"Error copying template {source_template.id}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
                    continue

            # Commit all changes
            self.db.commit()
            logger.info(f"Copy operation completed: {result['templates_copied']} copied, {result['templates_skipped']} skipped, {result['templates_overwritten']} overwritten")

        except SQLAlchemyError as e:
            error_msg = f"Database error during copy operation: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            self.db.rollback()
        except Exception as e:
            error_msg = f"Unexpected error during copy operation: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            self.db.rollback()

        return result