"""
Admin dealer management routes (SYSTEM_ADMIN only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from app.controllers.admin_dealer_controller import AdminDealerController
from app.schemas.dealer import (
    DealerListResponse,
    DealerResponse,
    DealerUpdateRequest,
    DealerUpdateResponse,
    DealerStatusRequest,
    DealerStatusResponse,
    DealerRegistrationRequest,
    DealerRegistrationResponse,
    BulkDealerRegistrationResponse
)

router = APIRouter(tags=["admin-dealer"])


@router.get("/admin/dealers", response_model=DealerListResponse)
async def get_all_dealers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by dealer ID or name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all dealers with pagination and filtering (SYSTEM_ADMIN only)

    This endpoint returns all dealers with support for:
    - Pagination (page, page_size)
    - Search by dealer ID or name
    - Filter by active status

    **Required Role**: SYSTEM_ADMIN

    **Query Parameters**:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Search term for dealer ID or name
    - **is_active**: Filter by active status (true/false)

    **Returns**:
        Paginated list of dealers with metadata

    **Example**:
        GET /api/v1/admin/dealers?page=1&page_size=10&search=AHASS&is_active=true
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.get_all_dealers(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/admin/dealers/{dealer_id}", response_model=DealerResponse)
async def get_dealer_by_id(
    dealer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get single dealer by ID (SYSTEM_ADMIN only)

    **Required Role**: SYSTEM_ADMIN

    **Path Parameters**:
    - **dealer_id**: Dealer ID to retrieve

    **Returns**:
        Dealer details including API credentials

    **Example**:
        GET /api/v1/admin/dealers/12345
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.get_dealer_by_id(dealer_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dealer not found: {dealer_id}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/admin/dealers/{dealer_id}", response_model=DealerUpdateResponse)
async def update_dealer(
    dealer_id: str,
    update_data: DealerUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update dealer information (SYSTEM_ADMIN only)

    **Required Role**: SYSTEM_ADMIN

    **Path Parameters**:
    - **dealer_id**: Dealer ID to update

    **Request Body**:
    - **dealer_name**: Optional dealer name
    - **api_key**: Optional API key
    - **api_token**: Optional API token
    - **secret_key**: Optional secret key
    - **is_active**: Optional active status

    **Returns**:
        Updated dealer details

    **Example**:
        PUT /api/v1/admin/dealers/12345
        {
            "dealer_name": "New Dealer Name",
            "is_active": true
        }
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.update_dealer(dealer_id, update_data)

        if not result.success:
            if "not found" in result.message:
                raise HTTPException(status_code=404, detail=result.message)
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/admin/dealers/{dealer_id}/status", response_model=DealerStatusResponse)
async def toggle_dealer_status(
    dealer_id: str,
    status_data: DealerStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Toggle dealer active/inactive status (SYSTEM_ADMIN only)

    **Required Role**: SYSTEM_ADMIN

    **Path Parameters**:
    - **dealer_id**: Dealer ID to update

    **Request Body**:
    - **is_active**: New active status (true/false)

    **Returns**:
        Updated dealer with new status

    **Example**:
        PATCH /api/v1/admin/dealers/12345/status
        {
            "is_active": false
        }
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.toggle_dealer_status(dealer_id, status_data.is_active)

        if not result.success:
            if "not found" in result.message:
                raise HTTPException(status_code=404, detail=result.message)
            raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/admin/dealers/register", response_model=DealerRegistrationResponse, status_code=201)
async def register_dealer(
    registration_data: DealerRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new dealer with admin user (SYSTEM_ADMIN only)

    This endpoint creates both a dealer and a DEALER_ADMIN user in one atomic operation.
    If the user creation fails, the dealer creation is rolled back.

    **Required Role**: SYSTEM_ADMIN

    **Request Body**:
    - **Step 1 - Dealer Info**:
        - dealer_id: Unique dealer ID (1-10 characters)
        - dealer_name: Dealer name
    - **Step 2 - DGI API Configuration** (optional):
        - api_key: DGI API key
        - secret_key: DGI secret key
    - **Step 3 - WhatsApp Configuration** (optional):
        - phone_number: WhatsApp phone number
        - fonnte_api_key: Fonnte API key
        - fonnte_api_url: Fonnte API URL (default: https://api.fonnte.com/send)
    - **Step 4 - Google Maps Configuration** (optional):
        - google_location_url: Google Maps location URL
    - **Step 5 - Admin User Info** (required):
        - admin_email: Admin user email
        - admin_full_name: Admin user full name
        - admin_password: Admin user password (min 8 characters)

    **Returns**:
        Registration response with dealer and user data

    **Example**:
        POST /api/v1/admin/dealers/register
        {
            "dealer_id": "DLR001",
            "dealer_name": "ABC Motors",
            "api_key": "your-api-key",
            "secret_key": "your-secret-key",
            "admin_email": "admin@abcmotors.com",
            "admin_full_name": "John Doe",
            "admin_password": "SecurePass123"
        }
    """
    try:
        controller = AdminDealerController(db)
        result = await controller.register_dealer(registration_data)

        if not result.success:
            # Check for specific error types
            if "already exists" in result.message:
                raise HTTPException(status_code=400, detail=result.message)
            elif "Account service unavailable" in result.message:
                raise HTTPException(status_code=503, detail=result.message)
            elif "Failed to create admin user" in result.message:
                raise HTTPException(status_code=400, detail=result.message)
            else:
                raise HTTPException(status_code=500, detail=result.message)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/admin/dealers/bulk-register", response_model=BulkDealerRegistrationResponse, status_code=201)
async def bulk_register_dealers(
    file: UploadFile = File(..., description="Excel or CSV file (.xlsx, .xls, or .csv) with dealer data"),
    db: Session = Depends(get_db)
):
    """
    Bulk register dealers from Excel or CSV file upload (SYSTEM_ADMIN only)

    This endpoint allows uploading an Excel or CSV file to register multiple dealers at once.
    Each row in the file represents one dealer registration.

    **Required Role**: SYSTEM_ADMIN

    **File Format**:

    The file (Excel or CSV) must contain the following columns:

    **Required Columns**:
    - **dealer_id**: Unique dealer ID (1-10 characters)
    - **dealer_name**: Dealer name
    - **admin_email**: Admin user email address
    - **admin_full_name**: Admin user full name
    - **admin_password**: Admin user password (min 8 characters)

    **Optional Columns**:
    - **api_key**: DGI API key
    - **secret_key**: DGI secret key
    - **fonnte_api_key**: Fonnte WhatsApp API key
    - **fonnte_api_url**: Fonnte API URL (default: https://api.fonnte.com/send)
    - **phone_number**: WhatsApp phone number
    - **google_location_url**: Google Maps location URL

    **File Requirements**:
    - Format: .xlsx, .xls, or .csv
    - Maximum file size: 10MB
    - First row must be column headers
    - Each subsequent row is one dealer registration

    **Processing Behavior**:
    - Each dealer is processed independently
    - Failed registrations do not stop the process
    - Detailed results returned for each dealer
    - Reasons for failure included in response

    **Response includes**:
    - Total dealers processed
    - Success and failure counts
    - Detailed results for each dealer (success/failure with messages)

    **Example Excel Structure**:
    ```
    | dealer_id | dealer_name | api_key | admin_email         | admin_full_name | admin_password |
    |-----------|-------------|---------|---------------------|-----------------|----------------|
    | DLR001    | ABC Motors  | key123  | admin@abc.com       | John Doe        | SecurePass123  |
    | DLR002    | XYZ Auto    | key456  | admin@xyz.com       | Jane Smith      | SecurePass456  |
    ```

    **Error Cases**:
    - Invalid file format (400)
    - Missing required columns (400)
    - Invalid data in rows (detailed in response)
    - Duplicate dealer_id in Excel (detailed in response)
    - Dealer already exists in database (detailed in response)
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only .xlsx, .xls, and .csv files are supported."
            )

        # Read file content
        file_content = await file.read()

        # Validate file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10MB limit"
            )

        controller = AdminDealerController(db)

        # Parse file to dealer list (pass filename for format detection)
        try:
            dealers_list = AdminDealerController.parse_excel_to_dealer_list(file_content, file.filename)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"File parsing error: {str(e)}"
            )

        if not dealers_list:
            raise HTTPException(
                status_code=400,
                detail="No dealers found in file"
            )

        # Perform bulk registration
        result = await controller.bulk_register_dealers(dealers_list)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
