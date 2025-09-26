"""
Controller for Excel export operations
"""

import os
import sys
from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.logger import setup_logger
from app.repositories.excel_export_repository import ExcelExportRepository
from app.services.excel_export_service import ExcelExportService
from app.schemas.excel_export import (
    ExcelExportMetadata,
    ExcelExportResponse,
    ExcelExportError,
    WORK_ORDER_COLUMNS,
    WORK_ORDER_DETAIL_COLUMNS,
    NJB_NSC_COLUMNS,
    NJB_NSC_DETAIL_COLUMNS,
    HLO_COLUMNS,
    HLO_DETAIL_COLUMNS
)

logger = setup_logger(__name__)


class ExcelExportController:
    """Controller for Excel export analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ExcelExportRepository(db)
        self.excel_service = ExcelExportService()
    
    def export_work_order_excel(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Tuple[bytes, ExcelExportMetadata]:
        """
        Export Work Order data to Excel file
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Tuple[bytes, ExcelExportMetadata]: Excel file bytes and metadata
        """
        try:
            logger.info(f"Exporting Work Order Excel for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get data from repository
            data = self.repository.get_work_order_export_data(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Generate Excel file
            excel_bytes = self.excel_service.create_excel_file(
                data=data,
                columns=WORK_ORDER_COLUMNS,
                sheet_name="Work Order Data",
                title=f"Work Order Export - Dealer {dealer_id} ({date_from} to {date_to})"
            )
            
            # Generate filename and metadata
            filename = self.excel_service.generate_filename(
                export_type="WorkOrder",
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            metadata = ExcelExportMetadata(
                filename=filename,
                total_records=len(data),
                export_type="WorkOrder",
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(excel_bytes)
            )
            
            logger.info(f"Work Order Excel export completed: {len(data)} records, {len(excel_bytes)} bytes")
            return excel_bytes, metadata
            
        except Exception as e:
            logger.error(f"Error exporting Work Order Excel: {str(e)}")
            raise Exception(f"Failed to export Work Order data: {str(e)}")
    
    def export_njb_nsc_excel(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Tuple[bytes, ExcelExportMetadata]:
        """
        Export NJB/NSC data to Excel file
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Tuple[bytes, ExcelExportMetadata]: Excel file bytes and metadata
        """
        try:
            logger.info(f"Exporting NJB/NSC Excel for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get data from repository
            data = self.repository.get_njb_nsc_export_data(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Generate Excel file
            excel_bytes = self.excel_service.create_excel_file(
                data=data,
                columns=NJB_NSC_COLUMNS,
                sheet_name="NJB NSC Data",
                title=f"NJB/NSC Export - Dealer {dealer_id} ({date_from} to {date_to})"
            )
            
            # Generate filename and metadata
            filename = self.excel_service.generate_filename(
                export_type="NJB_NSC",
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            metadata = ExcelExportMetadata(
                filename=filename,
                total_records=len(data),
                export_type="NJB_NSC",
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(excel_bytes)
            )
            
            logger.info(f"NJB/NSC Excel export completed: {len(data)} records, {len(excel_bytes)} bytes")
            return excel_bytes, metadata
            
        except Exception as e:
            logger.error(f"Error exporting NJB/NSC Excel: {str(e)}")
            raise Exception(f"Failed to export NJB/NSC data: {str(e)}")
    
    def export_hlo_excel(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Tuple[bytes, ExcelExportMetadata]:
        """
        Export HLO data to Excel file
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Tuple[bytes, ExcelExportMetadata]: Excel file bytes and metadata
        """
        try:
            logger.info(f"Exporting HLO Excel for dealer {dealer_id} from {date_from} to {date_to}")
            
            # Get data from repository
            data = self.repository.get_hlo_export_data(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            # Generate Excel file
            excel_bytes = self.excel_service.create_excel_file(
                data=data,
                columns=HLO_COLUMNS,
                sheet_name="HLO Data",
                title=f"HLO Export - Dealer {dealer_id} ({date_from} to {date_to})"
            )
            
            # Generate filename and metadata
            filename = self.excel_service.generate_filename(
                export_type="HLO",
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            metadata = ExcelExportMetadata(
                filename=filename,
                total_records=len(data),
                export_type="HLO",
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(excel_bytes)
            )
            
            logger.info(f"HLO Excel export completed: {len(data)} records, {len(excel_bytes)} bytes")
            return excel_bytes, metadata

        except Exception as e:
            logger.error(f"Error exporting HLO Excel: {str(e)}")
            raise Exception(f"Failed to export HLO data: {str(e)}")

    def export_work_order_detail_excel(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Tuple[bytes, ExcelExportMetadata]:
        """
        Export Work Order Detail data to Excel file (includes PKBData, PKBService, and PKBPart)

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Tuple[bytes, ExcelExportMetadata]: Excel file bytes and metadata
        """
        try:
            logger.info(f"Exporting Work Order Detail Excel for dealer {dealer_id} from {date_from} to {date_to}")

            # Get data from repository
            data = self.repository.get_work_order_detail_export_data(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Generate Excel file
            excel_bytes = self.excel_service.create_excel_file(
                data=data,
                columns=WORK_ORDER_DETAIL_COLUMNS,
                sheet_name="Work Order Detail Data",
                title=f"Work Order Detail Export - Dealer {dealer_id} ({date_from} to {date_to})"
            )

            # Generate filename and metadata
            filename = self.excel_service.generate_filename(
                export_type="WorkOrderDetail",
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            metadata = ExcelExportMetadata(
                filename=filename,
                total_records=len(data),
                export_type="WorkOrderDetail",
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(excel_bytes)
            )

            logger.info(f"Work Order Detail Excel export completed: {len(data)} records, {len(excel_bytes)} bytes")
            return excel_bytes, metadata

        except Exception as e:
            logger.error(f"Error exporting Work Order Detail Excel: {str(e)}")
            raise Exception(f"Failed to export Work Order Detail data: {str(e)}")

    def export_njb_nsc_detail_excel(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Tuple[bytes, ExcelExportMetadata]:
        """
        Export NJB/NSC Detail data to Excel file (includes WorkshopInvoiceData, WorkshopInvoiceNJB, and WorkshopInvoiceNSC)

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Tuple[bytes, ExcelExportMetadata]: Excel file bytes and metadata
        """
        try:
            logger.info(f"Exporting NJB/NSC Detail Excel for dealer {dealer_id} from {date_from} to {date_to}")

            # Get data from repository
            data = self.repository.get_njb_nsc_detail_export_data(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Generate Excel file
            excel_bytes = self.excel_service.create_excel_file(
                data=data,
                columns=NJB_NSC_DETAIL_COLUMNS,
                sheet_name="NJB NSC Detail Data",
                title=f"NJB/NSC Detail Export - Dealer {dealer_id} ({date_from} to {date_to})"
            )

            # Generate filename and metadata
            filename = self.excel_service.generate_filename(
                export_type="NJB_NSC_Detail",
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            metadata = ExcelExportMetadata(
                filename=filename,
                total_records=len(data),
                export_type="NJB_NSC_Detail",
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(excel_bytes)
            )

            logger.info(f"NJB/NSC Detail Excel export completed: {len(data)} records, {len(excel_bytes)} bytes")
            return excel_bytes, metadata

        except Exception as e:
            logger.error(f"Error exporting NJB/NSC Detail Excel: {str(e)}")
            raise Exception(f"Failed to export NJB/NSC Detail data: {str(e)}")

    def export_hlo_detail_excel(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Tuple[bytes, ExcelExportMetadata]:
        """
        Export HLO Detail data to Excel file (includes DPHLOData and DPHLOPart)

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Tuple[bytes, ExcelExportMetadata]: Excel file bytes and metadata
        """
        try:
            logger.info(f"Exporting HLO Detail Excel for dealer {dealer_id} from {date_from} to {date_to}")

            # Get data from repository
            data = self.repository.get_hlo_detail_export_data(
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            # Generate Excel file
            excel_bytes = self.excel_service.create_excel_file(
                data=data,
                columns=HLO_DETAIL_COLUMNS,
                sheet_name="HLO Detail Data",
                title=f"HLO Detail Export - Dealer {dealer_id} ({date_from} to {date_to})"
            )

            # Generate filename and metadata
            filename = self.excel_service.generate_filename(
                export_type="HLO_Detail",
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )

            metadata = ExcelExportMetadata(
                filename=filename,
                total_records=len(data),
                export_type="HLO_Detail",
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(excel_bytes)
            )

            logger.info(f"HLO Detail Excel export completed: {len(data)} records, {len(excel_bytes)} bytes")
            return excel_bytes, metadata

        except Exception as e:
            logger.error(f"Error exporting HLO Detail Excel: {str(e)}")
            raise Exception(f"Failed to export HLO Detail data: {str(e)}")

    def validate_export_request(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> bool:
        """
        Validate export request parameters
        
        Args:
            dealer_id: Dealer ID to validate
            date_from: Start date to validate
            date_to: End date to validate
            
        Returns:
            bool: True if valid, raises exception if invalid
        """
        try:
            # Validate dealer_id
            if not dealer_id or not dealer_id.strip():
                raise ValueError("Dealer ID is required and cannot be empty")
            
            # Validate date format
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d')
                end_date = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Date format must be YYYY-MM-DD")
            
            # Validate date range
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")
            
            # Validate date range is not too large (optional - prevent huge exports)
            date_diff = (end_date - start_date).days
            if date_diff > 365:  # More than 1 year
                logger.warning(f"Large date range requested: {date_diff} days")
            
            return True
            
        except Exception as e:
            logger.error(f"Export request validation failed: {str(e)}")
            raise ValueError(f"Invalid export request: {str(e)}")
    
    def get_export_preview(
        self,
        export_type: str,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """
        Get preview information about export (count of records, etc.)
        
        Args:
            export_type: Type of export ('work_order', 'work_order_detail', 'njb_nsc', 'njb_nsc_detail', 'hlo', 'hlo_detail')
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Dict with preview information
        """
        try:
            self.validate_export_request(dealer_id, date_from, date_to)
            
            record_count = self.repository.get_export_data_count(
                export_type=export_type,
                dealer_id=dealer_id,
                date_from=date_from,
                date_to=date_to
            )
            
            return {
                'export_type': export_type,
                'dealer_id': dealer_id,
                'date_from': date_from,
                'date_to': date_to,
                'estimated_records': record_count,
                'preview_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting export preview: {str(e)}")
            raise Exception(f"Failed to generate export preview: {str(e)}")