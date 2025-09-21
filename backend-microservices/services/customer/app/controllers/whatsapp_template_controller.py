"""
WhatsApp Template Controller
Handles CRUD operations for WhatsApp templates with audit logging
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.whatsapp_template_repository import WhatsAppTemplateRepository
from app.repositories.whatsapp_template_logs_repository import WhatsAppTemplateLogsRepository
from app.schemas.whatsapp_template_schemas import (
    WhatsAppTemplateListRequest,
    WhatsAppTemplateListResponse,
    WhatsAppTemplateResponse,
    WhatsAppTemplateUpdateRequest,
    WhatsAppTemplateUpdateResponse,
    WhatsAppTemplateDeleteResponse,
    WhatsAppTemplateCopyRequest,
    WhatsAppTemplateCopyResponse,
    WhatsAppTemplateLogsResponse,
    TemplateOperation
)

logger = logging.getLogger(__name__)


class WhatsAppTemplateController:
    """Controller for WhatsApp template management operations"""

    def __init__(self, db: Session):
        self.db = db
        self.template_repo = WhatsAppTemplateRepository(db)
        self.logs_repo = WhatsAppTemplateLogsRepository(db)

    def get_templates(
        self,
        request: WhatsAppTemplateListRequest,
        user_email: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> WhatsAppTemplateListResponse:
        """
        Get paginated list of templates with filtering

        Args:
            request: List request parameters
            user_email: Email of requesting user
            client_ip: Client IP address
            user_agent: User agent string

        Returns:
            WhatsAppTemplateListResponse with templates and pagination
        """
        try:
            # Get paginated templates
            templates, pagination = self.template_repo.get_templates_paginated(
                dealer_id=request.dealer_id,
                reminder_target=request.reminder_target,
                template_content=request.template,
                page=request.page,
                size=request.size
            )

            # Convert to response format
            template_responses = []
            for template in templates:
                template_responses.append(WhatsAppTemplateResponse(
                    id=str(template.id),
                    reminder_target=template.reminder_target,
                    reminder_type=template.reminder_type,
                    dealer_id=template.dealer_id,
                    template=template.template,
                    created_by=template.created_by,
                    created_date=template.created_date.isoformat() if template.created_date else None,
                    last_modified_by=template.last_modified_by,
                    last_modified_date=template.last_modified_date.isoformat() if template.last_modified_date else None
                ))

            logger.info(f"Retrieved {len(template_responses)} templates for user {user_email}")

            return WhatsAppTemplateListResponse(
                success=True,
                data=template_responses,
                pagination=pagination
            )

        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve templates"
            )

    def update_template(
        self,
        template_id: str,
        request: WhatsAppTemplateUpdateRequest,
        user_email: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> WhatsAppTemplateUpdateResponse:
        """
        Update template by ID

        Args:
            template_id: Template UUID
            request: Update request data
            user_email: Email of requesting user
            client_ip: Client IP address
            user_agent: User agent string

        Returns:
            WhatsAppTemplateUpdateResponse with update result
        """
        try:
            # Get existing template for audit logging
            existing_template = self.template_repo.get_template_by_id(template_id)
            if not existing_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )

            # Store old data for audit log
            old_data = {
                "template": existing_template.template,
                "reminder_target": existing_template.reminder_target,
                "reminder_type": existing_template.reminder_type
            }

            # Update template
            updated_template = self.template_repo.update_template_by_id(
                template_id=template_id,
                template=request.template,
                reminder_target=request.reminder_target,
                reminder_type=request.reminder_type,
                last_modified_by=user_email
            )

            if not updated_template:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update template"
                )

            # Create audit log
            new_data = {
                "template": updated_template.template,
                "reminder_target": updated_template.reminder_target,
                "reminder_type": updated_template.reminder_type
            }

            self.logs_repo.create_log(
                operation=TemplateOperation.UPDATE,
                user_email=user_email,
                template_id=str(updated_template.id),
                old_data=old_data,
                new_data=new_data,
                dealer_id=updated_template.dealer_id,
                client_ip=client_ip,
                user_agent=user_agent,
                operation_notes=f"Updated template fields: template, reminder_target, reminder_type"
            )

            # Prepare response
            template_response = WhatsAppTemplateResponse(
                id=str(updated_template.id),
                reminder_target=updated_template.reminder_target,
                reminder_type=updated_template.reminder_type,
                dealer_id=updated_template.dealer_id,
                template=updated_template.template,
                created_by=updated_template.created_by,
                created_date=updated_template.created_date.isoformat() if updated_template.created_date else None,
                last_modified_by=updated_template.last_modified_by,
                last_modified_date=updated_template.last_modified_date.isoformat() if updated_template.last_modified_date else None
            )

            logger.info(f"Updated template {template_id} by user {user_email}")

            return WhatsAppTemplateUpdateResponse(
                success=True,
                message="Template updated successfully",
                data=template_response
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update template"
            )

    def delete_template(
        self,
        template_id: str,
        user_email: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> WhatsAppTemplateDeleteResponse:
        """
        Delete template by ID

        Args:
            template_id: Template UUID
            user_email: Email of requesting user
            client_ip: Client IP address
            user_agent: User agent string

        Returns:
            WhatsAppTemplateDeleteResponse with deletion result
        """
        try:
            # Get existing template for audit logging
            existing_template = self.template_repo.get_template_by_id(template_id)
            if not existing_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )

            # Store template data for audit log
            template_data = {
                "template": existing_template.template,
                "reminder_target": existing_template.reminder_target,
                "reminder_type": existing_template.reminder_type,
                "dealer_id": existing_template.dealer_id
            }

            # Delete template
            if not self.template_repo.delete_template_by_id(template_id):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete template"
                )

            # Create audit log
            self.logs_repo.create_log(
                operation=TemplateOperation.DELETE,
                user_email=user_email,
                template_id=template_id,
                old_data=template_data,
                new_data=None,
                dealer_id=existing_template.dealer_id,
                client_ip=client_ip,
                user_agent=user_agent,
                operation_notes=f"Deleted template: {existing_template.reminder_target} - {existing_template.reminder_type}"
            )

            logger.info(f"Deleted template {template_id} by user {user_email}")

            return WhatsAppTemplateDeleteResponse(
                success=True,
                message="Template deleted successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete template"
            )

    def copy_templates(
        self,
        request: WhatsAppTemplateCopyRequest,
        user_email: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> WhatsAppTemplateCopyResponse:
        """
        Copy templates from source dealer to target dealer

        Args:
            request: Copy request data
            user_email: Email of requesting user
            client_ip: Client IP address
            user_agent: User agent string

        Returns:
            WhatsAppTemplateCopyResponse with copy operation results
        """
        try:
            # Perform copy operation
            copy_result = self.template_repo.copy_templates(
                source_dealer_id=request.source_dealer_id,
                target_dealer_id=request.target_dealer_id,
                overwrite_existing=request.overwrite_existing,
                created_by=user_email
            )

            # Create audit log for copy operation
            operation_data = {
                "source_dealer_id": request.source_dealer_id,
                "target_dealer_id": request.target_dealer_id,
                "overwrite_existing": request.overwrite_existing,
                "copy_result": copy_result
            }

            self.logs_repo.create_log(
                operation=TemplateOperation.COPY,
                user_email=user_email,
                template_id=None,
                old_data=None,
                new_data=operation_data,
                dealer_id=request.target_dealer_id,
                source_dealer_id=request.source_dealer_id,
                target_dealer_id=request.target_dealer_id,
                client_ip=client_ip,
                user_agent=user_agent,
                operation_notes=f"Copied {copy_result['templates_copied']} templates from {request.source_dealer_id} to {request.target_dealer_id}"
            )

            # Prepare response data
            response_data = {
                "source_dealer_id": request.source_dealer_id,
                "target_dealer_id": request.target_dealer_id,
                "templates_found": copy_result["templates_found"],
                "templates_copied": copy_result["templates_copied"],
                "templates_skipped": copy_result["templates_skipped"],
                "templates_overwritten": copy_result.get("templates_overwritten", 0),
                "overwrite_existing": request.overwrite_existing,
                "copy_timestamp": datetime.utcnow().isoformat()
            }

            # Add errors if any
            if copy_result.get("errors"):
                response_data["errors"] = copy_result["errors"]

            success = copy_result["templates_copied"] > 0 or copy_result["templates_overwritten"] > 0
            message = f"Successfully copied {copy_result['templates_copied']} templates"

            if copy_result["templates_skipped"] > 0:
                message += f" ({copy_result['templates_skipped']} skipped)"

            if copy_result.get("templates_overwritten", 0) > 0:
                message += f" ({copy_result['templates_overwritten']} overwritten)"

            logger.info(f"Copy operation completed by user {user_email}: {message}")

            return WhatsAppTemplateCopyResponse(
                success=success,
                message=message,
                data=response_data
            )

        except Exception as e:
            logger.error(f"Error copying templates: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to copy templates"
            )

    def get_template_logs(
        self,
        template_id: Optional[str] = None,
        dealer_id: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_email: Optional[str] = None
    ) -> WhatsAppTemplateLogsResponse:
        """
        Get template audit logs with filtering

        Args:
            template_id: Filter by template ID
            dealer_id: Filter by dealer ID
            operation: Filter by operation type
            limit: Maximum number of records
            offset: Number of records to skip
            user_email: Filter by user email

        Returns:
            WhatsAppTemplateLogsResponse with log entries
        """
        try:
            logs = []

            if template_id:
                logs = self.logs_repo.get_logs_by_template_id(template_id, limit, offset)
            elif dealer_id:
                logs = self.logs_repo.get_logs_by_dealer_id(dealer_id, operation, limit, offset)
            elif user_email:
                logs = self.logs_repo.get_logs_by_user(user_email, limit, offset)
            else:
                # Get recent operations
                logs = self.logs_repo.get_recent_operations(hours=24, limit=limit)

            # Convert to response format
            log_responses = []
            for log in logs:
                log_responses.append({
                    "id": str(log.id),
                    "template_id": str(log.template_id) if log.template_id else None,
                    "operation": log.operation,
                    "old_data": log.old_data,
                    "new_data": log.new_data,
                    "dealer_id": log.dealer_id,
                    "user_email": log.user_email,
                    "source_dealer_id": log.source_dealer_id,
                    "target_dealer_id": log.target_dealer_id,
                    "operation_timestamp": log.operation_timestamp.isoformat() if log.operation_timestamp else None,
                    "operation_notes": log.operation_notes
                })

            return WhatsAppTemplateLogsResponse(
                success=True,
                data=log_responses,
                pagination={
                    "page": (offset // limit) + 1 if limit > 0 else 1,
                    "size": limit,
                    "total": len(log_responses),
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": offset > 0
                }
            )

        except Exception as e:
            logger.error(f"Error getting template logs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve template logs"
            )