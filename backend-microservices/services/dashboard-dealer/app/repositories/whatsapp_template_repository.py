"""
WhatsApp Template Repository for Dashboard Dealer Service
Handles template copying operations for newly registered dealers
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.logger import setup_logger
from app.models.whatsapp_template import WhatsAppTemplate

logger = setup_logger(__name__)

# Default source dealer for template copying
DEFAULT_SOURCE_DEALER_ID = "00999"


class WhatsAppTemplateRepository:
    """Repository for WhatsApp template operations in dashboard-dealer service"""

    def __init__(self, db: Session):
        self.db = db

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

    def copy_templates_from_default(
        self,
        target_dealer_id: str,
        source_dealer_id: str = DEFAULT_SOURCE_DEALER_ID,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Copy all templates from default source dealer to target dealer
        Used during dealer registration to provision initial templates

        Args:
            target_dealer_id: New dealer ID to copy templates to
            source_dealer_id: Source dealer ID (defaults to 00999)
            created_by: User/system performing the copy operation

        Returns:
            Dictionary with copy operation results:
            {
                "success": bool,
                "templates_found": int,
                "templates_copied": int,
                "templates_skipped": int,
                "errors": List[str]
            }
        """
        result = {
            "success": False,
            "templates_found": 0,
            "templates_copied": 0,
            "templates_skipped": 0,
            "errors": []
        }

        try:
            logger.info(f"Starting template copy from {source_dealer_id} to {target_dealer_id}")

            # Get source templates
            source_templates = self.get_templates_by_dealer_id(source_dealer_id)
            result["templates_found"] = len(source_templates)

            if not source_templates:
                logger.warning(f"No templates found for source dealer: {source_dealer_id}")
                result["success"] = True  # Not an error, just no templates to copy
                return result

            # Get existing target templates to avoid duplicates
            target_templates = self.get_templates_by_dealer_id(target_dealer_id)
            existing_template_keys = {
                (t.reminder_target, t.reminder_type) for t in target_templates
            }

            # Copy each template
            for source_template in source_templates:
                try:
                    template_key = (source_template.reminder_target, source_template.reminder_type)

                    # Skip if template already exists for target dealer
                    if template_key in existing_template_keys:
                        logger.debug(f"Template {template_key} already exists for dealer {target_dealer_id}, skipping")
                        result["templates_skipped"] += 1
                        continue

                    # Create new template for target dealer
                    new_template = WhatsAppTemplate(
                        id=uuid.uuid4(),
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
            result["success"] = True
            logger.info(
                f"Template copy completed for {target_dealer_id}: "
                f"{result['templates_copied']} copied, {result['templates_skipped']} skipped"
            )

        except SQLAlchemyError as e:
            error_msg = f"Database error during template copy: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["success"] = False
            self.db.rollback()
        except Exception as e:
            error_msg = f"Unexpected error during template copy: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["success"] = False
            self.db.rollback()

        return result

    def check_whatsapp_configured(
        self,
        fonnte_api_key: str = None,
        fonnte_api_url: str = None,
        phone_number: str = None
    ) -> bool:
        """
        Check if WhatsApp/Fonnte configuration is complete

        Args:
            fonnte_api_key: Fonnte API key
            fonnte_api_url: Fonnte API URL
            phone_number: WhatsApp phone number

        Returns:
            True if all WhatsApp fields are configured, False otherwise
        """
        return bool(fonnte_api_key and fonnte_api_url and phone_number)
