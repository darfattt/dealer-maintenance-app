"""
Controller for admin dealer management operations (SYSTEM_ADMIN only)
"""

import os
import sys
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.logger import setup_logger
from app.models.dealer import Dealer
from app.models.user import User, UserRole, UserDealer
from app.schemas.dealer import (
    DealerListResponse,
    DealerListItem,
    DealerResponse,
    DealerUpdateRequest,
    DealerUpdateResponse,
    DealerStatusResponse,
    DealerRegistrationRequest,
    DealerRegistrationResponse,
    BulkDealerRegistrationItem,
    BulkDealerRegistrationResponse
)
from app.repositories.whatsapp_template_repository import WhatsAppTemplateRepository
from passlib.context import CryptContext
import uuid

logger = setup_logger(__name__)


class AdminDealerController:
    """Controller for admin dealer management operations"""

    def __init__(self, db: Session):
        self.db = db

    async def get_all_dealers(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> DealerListResponse:
        """
        Get all dealers with pagination and filtering

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Search term for dealer_id or dealer_name
            is_active: Filter by active status

        Returns:
            DealerListResponse with paginated dealer list
        """
        try:
            logger.info(f"Getting all dealers - page: {page}, page_size: {page_size}, search: {search}, is_active: {is_active}")

            # Build query
            query = self.db.query(Dealer)

            # Apply filters
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (Dealer.dealer_id.ilike(search_filter)) |
                    (Dealer.dealer_name.ilike(search_filter))
                )

            if is_active is not None:
                query = query.filter(Dealer.is_active == is_active)

            # Get total count
            total_records = query.count()

            # Calculate pagination
            total_pages = (total_records + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # Execute query with pagination
            dealers = query.order_by(Dealer.dealer_name).offset(offset).limit(page_size).all()

            # Convert to response items
            dealer_items = []
            for dealer in dealers:
                # Check DGI API configuration (both api_key AND secret_key required)
                dgi_api_configured = bool(dealer.api_key and dealer.secret_key)

                # Check Google location configuration
                google_location_configured = bool(dealer.google_location_url)

                # Check WhatsApp/Fonnte API configuration (all 3 fields required)
                whatsapp_api_configured = bool(
                    dealer.phone_number and
                    dealer.fonnte_api_key and
                    dealer.fonnte_api_url
                )

                dealer_items.append(DealerListItem(
                    id=str(dealer.id),
                    dealer_id=dealer.dealer_id,
                    dealer_name=dealer.dealer_name,
                    is_active=dealer.is_active,
                    dgi_api_configured=dgi_api_configured,
                    google_location_configured=google_location_configured,
                    whatsapp_api_configured=whatsapp_api_configured,
                    created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                    updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
                ))

            logger.info(f"Found {total_records} dealers, returning page {page}/{total_pages}")

            return DealerListResponse(
                success=True,
                message="Dealers retrieved successfully",
                data=dealer_items,
                total_records=total_records,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error getting dealers: {str(e)}")
            return DealerListResponse(
                success=False,
                message=f"Error retrieving dealers: {str(e)}",
                data=[],
                total_records=0,
                page=page,
                page_size=page_size,
                total_pages=0
            )

    async def get_dealer_by_id(self, dealer_id: str) -> DealerResponse:
        """
        Get single dealer by ID

        Args:
            dealer_id: Dealer ID to retrieve

        Returns:
            DealerResponse with dealer details
        """
        try:
            logger.info(f"Getting dealer by ID: {dealer_id}")

            dealer = self.db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()

            if not dealer:
                logger.warning(f"Dealer not found: {dealer_id}")
                return None

            return DealerResponse(
                id=str(dealer.id),
                dealer_id=dealer.dealer_id,
                dealer_name=dealer.dealer_name,
                api_key=dealer.api_key,
                api_token=dealer.api_token,
                secret_key=dealer.secret_key,
                fonnte_api_key=dealer.fonnte_api_key,
                fonnte_api_url=dealer.fonnte_api_url,
                phone_number=dealer.phone_number,
                google_location_url=dealer.google_location_url,
                is_active=dealer.is_active,
                created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
            )

        except Exception as e:
            logger.error(f"Error getting dealer by ID: {str(e)}")
            return None

    async def update_dealer(
        self,
        dealer_id: str,
        update_data: DealerUpdateRequest
    ) -> DealerUpdateResponse:
        """
        Update dealer information

        Args:
            dealer_id: Dealer ID to update
            update_data: Update data

        Returns:
            DealerUpdateResponse with updated dealer
        """
        try:
            logger.info(f"Updating dealer: {dealer_id}")

            dealer = self.db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()

            if not dealer:
                logger.warning(f"Dealer not found: {dealer_id}")
                return DealerUpdateResponse(
                    success=False,
                    message=f"Dealer not found: {dealer_id}",
                    data=None
                )

            # Update fields if provided
            if update_data.dealer_name is not None:
                dealer.dealer_name = update_data.dealer_name

            if update_data.api_key is not None:
                dealer.api_key = update_data.api_key

            if update_data.api_token is not None:
                dealer.api_token = update_data.api_token

            if update_data.secret_key is not None:
                dealer.secret_key = update_data.secret_key

            if update_data.fonnte_api_key is not None:
                dealer.fonnte_api_key = update_data.fonnte_api_key

            if update_data.fonnte_api_url is not None:
                dealer.fonnte_api_url = update_data.fonnte_api_url

            if update_data.phone_number is not None:
                dealer.phone_number = update_data.phone_number

            if update_data.google_location_url is not None:
                dealer.google_location_url = update_data.google_location_url

            if update_data.is_active is not None:
                dealer.is_active = update_data.is_active

            # Update timestamp
            dealer.updated_at = datetime.utcnow()

            # Commit changes
            self.db.commit()
            self.db.refresh(dealer)

            logger.info(f"Dealer updated successfully: {dealer_id}")

            # Return updated dealer
            dealer_response = DealerResponse(
                id=str(dealer.id),
                dealer_id=dealer.dealer_id,
                dealer_name=dealer.dealer_name,
                api_key=dealer.api_key,
                api_token=dealer.api_token,
                secret_key=dealer.secret_key,
                fonnte_api_key=dealer.fonnte_api_key,
                fonnte_api_url=dealer.fonnte_api_url,
                phone_number=dealer.phone_number,
                google_location_url=dealer.google_location_url,
                is_active=dealer.is_active,
                created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
            )

            return DealerUpdateResponse(
                success=True,
                message="Dealer updated successfully",
                data=dealer_response
            )

        except Exception as e:
            logger.error(f"Error updating dealer: {str(e)}")
            self.db.rollback()
            return DealerUpdateResponse(
                success=False,
                message=f"Error updating dealer: {str(e)}",
                data=None
            )

    async def toggle_dealer_status(
        self,
        dealer_id: str,
        is_active: bool
    ) -> DealerStatusResponse:
        """
        Toggle dealer active/inactive status

        Args:
            dealer_id: Dealer ID to update
            is_active: New active status

        Returns:
            DealerStatusResponse with updated dealer
        """
        try:
            logger.info(f"Toggling dealer status: {dealer_id} -> {is_active}")

            dealer = self.db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()

            if not dealer:
                logger.warning(f"Dealer not found: {dealer_id}")
                return DealerStatusResponse(
                    success=False,
                    message=f"Dealer not found: {dealer_id}",
                    data=None
                )

            # Update status
            dealer.is_active = is_active
            dealer.updated_at = datetime.utcnow()

            # Commit changes
            self.db.commit()
            self.db.refresh(dealer)

            status_text = "activated" if is_active else "deactivated"
            logger.info(f"Dealer {status_text} successfully: {dealer_id}")

            # Return updated dealer
            dealer_response = DealerResponse(
                id=str(dealer.id),
                dealer_id=dealer.dealer_id,
                dealer_name=dealer.dealer_name,
                api_key=dealer.api_key,
                api_token=dealer.api_token,
                secret_key=dealer.secret_key,
                fonnte_api_key=dealer.fonnte_api_key,
                fonnte_api_url=dealer.fonnte_api_url,
                phone_number=dealer.phone_number,
                google_location_url=dealer.google_location_url,
                is_active=dealer.is_active,
                created_at=dealer.created_at.isoformat() if dealer.created_at else None,
                updated_at=dealer.updated_at.isoformat() if dealer.updated_at else None
            )

            return DealerStatusResponse(
                success=True,
                message=f"Dealer {status_text} successfully",
                data=dealer_response
            )

        except Exception as e:
            logger.error(f"Error toggling dealer status: {str(e)}")
            self.db.rollback()
            return DealerStatusResponse(
                success=False,
                message=f"Error updating dealer status: {str(e)}",
                data=None
            )

    async def register_dealer(
        self,
        registration_data: DealerRegistrationRequest
    ) -> DealerRegistrationResponse:
        """
        Register a new dealer with admin user
        This creates both the dealer and a DEALER_ADMIN user in one transaction

        Args:
            registration_data: Registration data including dealer info and admin user info

        Returns:
            DealerRegistrationResponse with dealer and user data
        """
        # Initialize password context
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        try:
            logger.info(f"Registering new dealer: {registration_data.dealer_id}")

            # Check if dealer already exists
            existing_dealer = self.db.query(Dealer).filter(
                Dealer.dealer_id == registration_data.dealer_id
            ).first()

            if existing_dealer:
                logger.warning(f"Dealer already exists: {registration_data.dealer_id}")
                return DealerRegistrationResponse(
                    success=False,
                    message=f"Dealer with ID {registration_data.dealer_id} already exists",
                    dealer=None,
                    admin_user=None
                )

            # Check if email already exists
            existing_user = self.db.query(User).filter(
                User.email == registration_data.admin_email
            ).first()

            if existing_user:
                logger.warning(f"User email already exists: {registration_data.admin_email}")
                return DealerRegistrationResponse(
                    success=False,
                    message=f"Email {registration_data.admin_email} is already registered",
                    dealer=None,
                    admin_user=None
                )

            # Step 1: Create dealer in dealer_integration schema
            new_dealer = Dealer(
                dealer_id=registration_data.dealer_id,
                dealer_name=registration_data.dealer_name,
                api_key=registration_data.api_key,
                secret_key=registration_data.secret_key,
                fonnte_api_key=registration_data.fonnte_api_key,
                fonnte_api_url=registration_data.fonnte_api_url or 'https://api.fonnte.com/send',
                phone_number=registration_data.phone_number,
                google_location_url=registration_data.google_location_url,
                is_active=True
            )

            self.db.add(new_dealer)

            logger.info(f"Dealer created in transaction: {registration_data.dealer_id}")

            # Step 2: Create admin user directly in account.users table
            # Truncate password to 72 bytes to comply with bcrypt limitation
            admin_password = registration_data.admin_password
            if len(admin_password.encode('utf-8')) > 72:
                admin_password = admin_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            hashed_password = pwd_context.hash(admin_password)

            new_user = User(
                id=uuid.uuid4(),
                email=registration_data.admin_email,
                full_name=registration_data.admin_full_name,
                hashed_password=hashed_password,
                role=UserRole.DEALER_USER,
                dealer_id=registration_data.dealer_id,
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(new_user)

            # Step 3: Create user-dealer relationship in users_dealer table
            new_user_dealer = UserDealer(
                id=uuid.uuid4(),
                user_id=new_user.id,
                dealer_id=registration_data.dealer_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(new_user_dealer)

            logger.info(f"Created user-dealer relationship: user_id={new_user.id}, dealer_id={registration_data.dealer_id}")

            # Commit dealer, user, and user-dealer relationship in single transaction
            self.db.commit()
            self.db.refresh(new_dealer)
            self.db.refresh(new_user)
            self.db.refresh(new_user_dealer)

            logger.info(f"Dealer, admin user, and user-dealer relationship created successfully: {registration_data.dealer_id}, {registration_data.admin_email}")

            # Step 4: Copy WhatsApp templates if WhatsApp is configured
            template_copy_result = None
            if (registration_data.fonnte_api_key and
                registration_data.fonnte_api_url and
                registration_data.phone_number):
                try:
                    logger.info(f"WhatsApp configured for dealer {registration_data.dealer_id}, copying templates from default source")
                    template_repo = WhatsAppTemplateRepository(self.db)
                    template_copy_result = template_repo.copy_templates_from_default(
                        target_dealer_id=registration_data.dealer_id,
                        created_by=registration_data.admin_email
                    )

                    if template_copy_result.get("success"):
                        logger.info(
                            f"Templates copied for dealer {registration_data.dealer_id}: "
                            f"{template_copy_result.get('templates_copied', 0)} copied, "
                            f"{template_copy_result.get('templates_skipped', 0)} skipped"
                        )
                    else:
                        logger.warning(
                            f"Template copy completed with errors for dealer {registration_data.dealer_id}: "
                            f"{template_copy_result.get('errors', [])}"
                        )
                except Exception as template_error:
                    # Don't fail registration if template copy fails
                    logger.warning(f"Template copy failed for dealer {registration_data.dealer_id}: {str(template_error)}")
                    template_copy_result = {
                        "success": False,
                        "templates_found": 0,
                        "templates_copied": 0,
                        "templates_skipped": 0,
                        "errors": [str(template_error)]
                    }
            else:
                logger.debug(f"WhatsApp not configured for dealer {registration_data.dealer_id}, skipping template copy")

            # Step 5: Prepare response
            dealer_response = DealerResponse(
                id=str(new_dealer.id),
                dealer_id=new_dealer.dealer_id,
                dealer_name=new_dealer.dealer_name,
                api_key=new_dealer.api_key,
                api_token=new_dealer.api_token,
                secret_key=new_dealer.secret_key,
                fonnte_api_key=new_dealer.fonnte_api_key,
                fonnte_api_url=new_dealer.fonnte_api_url,
                phone_number=new_dealer.phone_number,
                google_location_url=new_dealer.google_location_url,
                is_active=new_dealer.is_active,
                created_at=new_dealer.created_at.isoformat() if new_dealer.created_at else None,
                updated_at=new_dealer.updated_at.isoformat() if new_dealer.updated_at else None
            )

            admin_user_data = {
                "id": str(new_user.id),
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role.value,
                "dealer_id": new_user.dealer_id,
                "is_active": new_user.is_active,
                "is_verified": new_user.is_verified,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None
            }

            # Prepare template copy result for response
            template_copy_response = None
            if template_copy_result:
                from app.schemas.dealer import TemplateCopyResult
                template_copy_response = TemplateCopyResult(**template_copy_result)

            return DealerRegistrationResponse(
                success=True,
                message=f"Dealer {registration_data.dealer_id} and admin user created successfully",
                dealer=dealer_response,
                admin_user=admin_user_data,
                template_copy_result=template_copy_response
            )

        except Exception as e:
            logger.error(f"Error registering dealer: {str(e)}")
            self.db.rollback()
            return DealerRegistrationResponse(
                success=False,
                message=f"Error registering dealer: {str(e)}",
                dealer=None,
                admin_user=None
            )

    @staticmethod
    def parse_excel_to_dealer_list(file_content: bytes, filename: str = None) -> List[DealerRegistrationRequest]:
        """
        Parse Excel or CSV file to list of DealerRegistrationRequest

        Args:
            file_content: Excel or CSV file bytes
            filename: Original filename to detect file type

        Returns:
            List of validated DealerRegistrationRequest objects

        Raises:
            ValueError: If file format is invalid or required columns are missing
        """
        try:
            logger.info(f"Parsing file for bulk dealer registration: {filename}")

            # Detect file type and read accordingly
            file_extension = ''
            if filename:
                file_extension = filename.lower().split('.')[-1]

            # Read file based on extension
            if file_extension == 'csv':
                logger.info("Reading CSV file")
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_extension in ['xlsx', 'xls']:
                logger.info(f"Reading Excel file ({file_extension})")
                df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            else:
                # Try to detect format automatically
                try:
                    logger.info("Attempting to read as Excel file")
                    df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
                except Exception:
                    logger.info("Excel read failed, attempting to read as CSV file")
                    df = pd.read_csv(io.BytesIO(file_content))

            # Define required columns
            required_columns = ['dealer_id', 'dealer_name', 'admin_email', 'admin_full_name', 'admin_password']
            optional_columns = ['api_key', 'secret_key', 'fonnte_api_key', 'fonnte_api_url', 'phone_number', 'google_location_url']

            # Check for required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Fill NaN values in optional columns with None
            for col in optional_columns:
                if col in df.columns:
                    df[col] = df[col].where(pd.notna(df[col]), None)

            # Set default for fonnte_api_url if not provided
            if 'fonnte_api_url' not in df.columns:
                df['fonnte_api_url'] = 'https://api.fonnte.com/send'
            else:
                df['fonnte_api_url'] = df['fonnte_api_url'].fillna('https://api.fonnte.com/send')

            dealers_list = []
            errors = []

            # Parse each row
            for index, row in df.iterrows():
                try:
                    # Create DealerRegistrationRequest object
                    dealer_req = DealerRegistrationRequest(
                        dealer_id=str(row['dealer_id']).strip(),
                        dealer_name=str(row['dealer_name']).strip(),
                        api_key=str(row['api_key']).strip() if pd.notna(row.get('api_key')) and row.get('api_key') else None,
                        secret_key=str(row['secret_key']).strip() if pd.notna(row.get('secret_key')) and row.get('secret_key') else None,
                        fonnte_api_key=str(row['fonnte_api_key']).strip() if pd.notna(row.get('fonnte_api_key')) and row.get('fonnte_api_key') else None,
                        fonnte_api_url=str(row['fonnte_api_url']).strip() if pd.notna(row.get('fonnte_api_url')) and row.get('fonnte_api_url') else 'https://api.fonnte.com/send',
                        phone_number=str(row['phone_number']).strip() if pd.notna(row.get('phone_number')) and row.get('phone_number') else None,
                        google_location_url=str(row['google_location_url']).strip() if pd.notna(row.get('google_location_url')) and row.get('google_location_url') else None,
                        admin_email=str(row['admin_email']).strip(),
                        admin_full_name=str(row['admin_full_name']).strip(),
                        admin_password=str(row['admin_password']).strip()
                    )
                    dealers_list.append(dealer_req)
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

            if errors:
                error_msg = "Errors found in Excel file:\n" + "\n".join(errors)
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Successfully parsed {len(dealers_list)} dealers from file")
            return dealers_list

        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            raise ValueError(f"Invalid file format: {str(e)}")

    async def bulk_register_dealers(
        self,
        dealers_data: List[DealerRegistrationRequest]
    ) -> BulkDealerRegistrationResponse:
        """
        Bulk register dealers from list

        Args:
            dealers_data: List of dealer registration data

        Returns:
            BulkDealerRegistrationResponse with results for each dealer
        """
        try:
            logger.info(f"Starting bulk dealer registration: {len(dealers_data)} dealers")

            results = []
            total_success = 0
            total_failed = 0

            # Process each dealer
            for dealer_data in dealers_data:
                try:
                    # Call existing register_dealer method
                    response = await self.register_dealer(dealer_data)

                    if response.success:
                        total_success += 1
                    else:
                        total_failed += 1

                    # Create result item
                    result_item = BulkDealerRegistrationItem(
                        dealer_id=dealer_data.dealer_id,
                        success=response.success,
                        message=response.message,
                        dealer=response.dealer,
                        admin_user=response.admin_user,
                        template_copy_result=response.template_copy_result
                    )
                    results.append(result_item)

                except Exception as e:
                    total_failed += 1
                    logger.error(f"Error processing dealer {dealer_data.dealer_id}: {str(e)}")
                    result_item = BulkDealerRegistrationItem(
                        dealer_id=dealer_data.dealer_id,
                        success=False,
                        message=f"Unexpected error: {str(e)}",
                        dealer=None,
                        admin_user=None
                    )
                    results.append(result_item)

            # Create summary message
            summary_message = f"Bulk registration completed: {total_success}/{len(dealers_data)} succeeded"
            if total_failed > 0:
                summary_message += f", {total_failed} failed"

            logger.info(summary_message)

            return BulkDealerRegistrationResponse(
                success=total_failed == 0,  # Only true if no failures
                message=summary_message,
                total_processed=len(dealers_data),
                total_success=total_success,
                total_failed=total_failed,
                results=results
            )

        except Exception as e:
            logger.error(f"Error in bulk dealer registration: {str(e)}")
            return BulkDealerRegistrationResponse(
                success=False,
                message=f"Bulk registration failed: {str(e)}",
                total_processed=0,
                total_success=0,
                total_failed=len(dealers_data) if dealers_data else 0,
                results=[]
            )
