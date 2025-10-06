"""
WhatsApp Template API Routes
RESTful endpoints for template management with CRUD operations and audit logging
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.controllers.whatsapp_template_controller import WhatsAppTemplateController
from app.schemas.whatsapp_template_schemas import (
    WhatsAppTemplateListRequest,
    WhatsAppTemplateListResponse,
    WhatsAppTemplateUpdateRequest,
    WhatsAppTemplateUpdateResponse,
    WhatsAppTemplateDeleteResponse,
    WhatsAppTemplateCopyRequest,
    WhatsAppTemplateCopyResponse,
    WhatsAppTemplateLogsResponse
)
from app.dependencies import get_db, get_current_user, UserContext

router = APIRouter(prefix="/whatsapp-templates", tags=["WhatsApp Templates"])


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return client_ip, user_agent


@router.get("", response_model=WhatsAppTemplateListResponse, summary="Get WhatsApp Templates")
async def get_templates(
    dealer_id: Optional[str] = None,
    reminder_target: Optional[str] = None,
    template: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Get paginated list of WhatsApp templates with optional filtering

    - **dealer_id**: Filter by dealer ID (empty string for global templates)
    - **reminder_target**: Filter by reminder target (exact match)
    - **template**: Search in template content (contains, case-insensitive)
    - **page**: Page number (1-based, default: 1)
    - **size**: Page size (1-100, default: 10)
    """
    try:
        # Get client information
        client_ip, user_agent = get_client_info(request)

        # Create request object
        list_request = WhatsAppTemplateListRequest(
            dealer_id=dealer_id,
            reminder_target=reminder_target,
            template=template,
            page=page,
            size=size
        )

        # Get templates
        controller = WhatsAppTemplateController(db)
        return controller.get_templates(
            request=list_request,
            user_email=current_user.email,
            client_ip=client_ip,
            user_agent=user_agent
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}"
        )


@router.put("/{template_id}", response_model=WhatsAppTemplateUpdateResponse, summary="Update WhatsApp Template")
async def update_template(
    template_id: str,
    request_data: WhatsAppTemplateUpdateRequest,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Update a WhatsApp template by ID

    - **template_id**: Template UUID
    - **template**: New template content (required, max 2000 chars)
    - **reminder_target**: New reminder target (required, max 50 chars)
    - **reminder_type**: New reminder type (required, max 100 chars)

    Only these fields can be updated. Other fields like dealer_id and timestamps are managed automatically.
    """
    try:
        # Get client information
        client_ip, user_agent = get_client_info(request)

        # Update template
        controller = WhatsAppTemplateController(db)
        return controller.update_template(
            template_id=template_id,
            request=request_data,
            user_email=current_user.email,
            client_ip=client_ip,
            user_agent=user_agent
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}", response_model=WhatsAppTemplateDeleteResponse, summary="Delete WhatsApp Template")
async def delete_template(
    template_id: str,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Delete a WhatsApp template by ID

    - **template_id**: Template UUID

    This operation creates an audit log entry and permanently removes the template.
    """
    try:
        # Get client information
        client_ip, user_agent = get_client_info(request)

        # Delete template
        controller = WhatsAppTemplateController(db)
        return controller.delete_template(
            template_id=template_id,
            user_email=current_user.email,
            client_ip=client_ip,
            user_agent=user_agent
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )


@router.post("/copy", response_model=WhatsAppTemplateCopyResponse, summary="Copy WhatsApp Templates")
async def copy_templates(
    request_data: WhatsAppTemplateCopyRequest,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Copy all templates from source dealer to target dealer

    - **source_dealer_id**: Source dealer ID (required, max 50 chars)
    - **target_dealer_id**: Target dealer ID (required, max 50 chars, must be different from source)
    - **overwrite_existing**: Whether to overwrite existing templates (default: false)

    This operation:
    1. Gets all templates from source dealer
    2. For each template, either creates a new one or overwrites existing (if overwrite_existing=true)
    3. Creates audit log entries for the copy operation
    4. Returns statistics about the operation
    """
    try:
        # Get client information
        client_ip, user_agent = get_client_info(request)

        # Copy templates
        controller = WhatsAppTemplateController(db)
        return controller.copy_templates(
            request=request_data,
            user_email=current_user.email,
            client_ip=client_ip,
            user_agent=user_agent
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to copy templates: {str(e)}"
        )


@router.get("/logs", response_model=WhatsAppTemplateLogsResponse, summary="Get Template Audit Logs")
async def get_template_logs(
    template_id: Optional[str] = None,
    dealer_id: Optional[str] = None,
    operation: Optional[str] = None,
    user_email_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Get template audit logs with optional filtering

    - **template_id**: Filter by specific template UUID
    - **dealer_id**: Filter by dealer ID (includes source/target dealer for copy operations)
    - **operation**: Filter by operation type (CREATE, UPDATE, DELETE, COPY)
    - **user_email_filter**: Filter by user who performed the operation
    - **limit**: Maximum number of records (1-100, default: 50)
    - **offset**: Number of records to skip (default: 0)

    Returns audit logs in reverse chronological order (newest first).
    If no filters are specified, returns recent operations from the last 24 hours.
    """
    try:
        # Get template logs
        controller = WhatsAppTemplateController(db)
        return controller.get_template_logs(
            template_id=template_id,
            dealer_id=dealer_id,
            operation=operation,
            limit=min(100, max(1, limit)),
            offset=max(0, offset),
            user_email=user_email_filter
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template logs: {str(e)}"
        )