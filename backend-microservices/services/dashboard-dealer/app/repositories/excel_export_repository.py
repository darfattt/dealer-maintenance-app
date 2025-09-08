"""
Repository for Excel export data operations
"""

import os
import sys
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text

# Add parent directory to path for utils import
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if parent_path not in sys.path:
    sys.path.append(parent_path)

from utils.logger import setup_logger
from app.models.pkb_data import PKBData, PKBService, PKBPart
from app.models.workshop_invoice_data import WorkshopInvoiceData, WorkshopInvoiceNJB, WorkshopInvoiceNSC
from app.models.dp_hlo_data import DPHLOData, DPHLOPart

logger = setup_logger(__name__)


class ExcelExportRepository:
    """Repository for Excel export analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _build_date_conditions(self, model_class, date_from: str, date_to: str):
        """
        Build date filter conditions for created_time string field
        
        Args:
            model_class: SQLAlchemy model class
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            SQLAlchemy filter conditions
        """
        date_conditions = []
        
        # Handle YYYY-MM-DD format
        date_conditions.append(
            and_(
                func.length(model_class.created_time) >= 10,
                func.substr(model_class.created_time, 1, 10).op('~')(r'^\\d{4}-\\d{2}-\\d{2}$'),
                func.to_date(func.substr(model_class.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                func.to_date(func.substr(model_class.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
            )
        )
        
        # Handle DD/MM/YYYY format
        date_conditions.append(
            and_(
                func.length(model_class.created_time) >= 10,
                func.substr(model_class.created_time, 1, 10).op('~')(r'^\\d{2}/\\d{2}/\\d{4}$'),
                func.to_date(func.substr(model_class.created_time, 1, 10), 'DD/MM/YYYY') >= func.to_date(date_from, 'YYYY-MM-DD'),
                func.to_date(func.substr(model_class.created_time, 1, 10), 'DD/MM/YYYY') <= func.to_date(date_to, 'YYYY-MM-DD')
            )
        )
        
        return or_(*date_conditions)
    
    def get_work_order_export_data(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Get work order data for Excel export from PKB data
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            List of dictionaries containing work order data
        """
        try:
            logger.info(f"Getting work order export data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")
            
            # Build date filter conditions
            date_conditions = self._build_date_conditions(PKBData, date_from, date_to)
            
            # Query PKB data
            query = self.db.query(
                PKBData.no_work_order,
                PKBData.no_sa_form,
                PKBData.tanggal_servis,
                PKBData.no_polisi,
                PKBData.no_mesin,
                PKBData.no_rangka,
                PKBData.nama_pembawa,
                PKBData.no_telp_pembawa,
                PKBData.total_biaya_service,
                PKBData.created_time
            ).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    date_conditions
                )
            ).order_by(PKBData.created_time, PKBData.no_work_order)
            
            results = query.all()
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append({
                    'no_work_order': row.no_work_order,
                    'no_sa_form': row.no_sa_form,
                    'tanggal_servis': row.tanggal_servis,
                    'no_polisi': row.no_polisi,
                    'no_mesin': row.no_mesin,
                    'no_rangka': row.no_rangka,
                    'nama_pembawa': row.nama_pembawa,
                    'no_telp_pembawa': row.no_telp_pembawa,
                    'total_biaya_service': float(row.total_biaya_service) if row.total_biaya_service else 0.0
                })
            
            logger.info(f"Retrieved {len(data)} work order records for export")
            return data
            
        except Exception as e:
            logger.error(f"Error getting work order export data: {str(e)}")
            raise Exception(f"Failed to retrieve work order data: {str(e)}")
    
    def get_njb_nsc_export_data(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Get NJB/NSC data for Excel export from workshop invoice data
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            List of dictionaries containing NJB/NSC data
        """
        try:
            logger.info(f"Getting NJB/NSC export data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")
            
            # Build date filter conditions
            date_conditions = self._build_date_conditions(WorkshopInvoiceData, date_from, date_to)
            
            # Query workshop invoice data
            query = self.db.query(
                WorkshopInvoiceData.honda_id_sa,
                WorkshopInvoiceData.honda_id_mekanik,
                WorkshopInvoiceData.no_work_order,
                WorkshopInvoiceData.no_njb,
                WorkshopInvoiceData.tanggal_njb,
                WorkshopInvoiceData.total_harga_njb,
                WorkshopInvoiceData.no_nsc,
                WorkshopInvoiceData.tanggal_nsc,
                WorkshopInvoiceData.total_harga_nsc,
                WorkshopInvoiceData.created_time
            ).filter(
                and_(
                    WorkshopInvoiceData.dealer_id == dealer_id,
                    date_conditions
                )
            ).order_by(WorkshopInvoiceData.created_time, WorkshopInvoiceData.no_work_order)
            
            results = query.all()
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append({
                    'honda_id_sa': row.honda_id_sa,
                    'honda_id_mekanik': row.honda_id_mekanik,
                    'no_work_order': row.no_work_order,
                    'no_njb': row.no_njb,
                    'tanggal_njb': row.tanggal_njb,
                    'total_harga_njb': float(row.total_harga_njb) if row.total_harga_njb else 0.0,
                    'no_nsc': row.no_nsc,
                    'tanggal_nsc': row.tanggal_nsc,
                    'total_harga_nsc': float(row.total_harga_nsc) if row.total_harga_nsc else 0.0
                })
            
            logger.info(f"Retrieved {len(data)} NJB/NSC records for export")
            return data
            
        except Exception as e:
            logger.error(f"Error getting NJB/NSC export data: {str(e)}")
            raise Exception(f"Failed to retrieve NJB/NSC data: {str(e)}")
    
    def get_hlo_export_data(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Get HLO data for Excel export from DP HLO data with parts
        
        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            List of dictionaries containing HLO data with parts
        """
        try:
            logger.info(f"Getting HLO export data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")
            
            # Build date filter conditions for DPHLOData
            date_conditions = self._build_date_conditions(DPHLOData, date_from, date_to)
            
            # Query HLO data with parts using JOIN
            query = self.db.query(
                DPHLOData.id_hlo_document,
                DPHLOData.tanggal_pemesanan_hlo,
                DPHLOData.no_work_order,
                DPHLOData.id_customer,
                DPHLOPart.parts_number,
                DPHLOPart.kuantitas,
                DPHLOPart.total_harga_parts,
                DPHLOData.created_time
            ).join(
                DPHLOPart, DPHLOData.id == DPHLOPart.dp_hlo_data_id
            ).filter(
                and_(
                    DPHLOData.dealer_id == dealer_id,
                    DPHLOData.id_hlo_document.isnot(None),
                    date_conditions
                )
            ).order_by(DPHLOData.created_time, DPHLOData.id_hlo_document, DPHLOPart.id)
            
            results = query.all()
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append({
                    'id_hlo_document': row.id_hlo_document,
                    'tanggal_pemesanan_hlo': row.tanggal_pemesanan_hlo,
                    'no_work_order': row.no_work_order,
                    'id_customer': row.id_customer,
                    'parts_number': row.parts_number,
                    'kuantitas': row.kuantitas,
                    'total_harga_parts': float(row.total_harga_parts) if row.total_harga_parts else 0.0
                })
            
            logger.info(f"Retrieved {len(data)} HLO records (with parts) for export")
            return data
            
        except Exception as e:
            logger.error(f"Error getting HLO export data: {str(e)}")
            raise Exception(f"Failed to retrieve HLO data: {str(e)}")
    
    def get_export_data_count(
        self,
        export_type: str,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> int:
        """
        Get count of records for specific export type (for metadata)
        
        Args:
            export_type: Type of export ('work_order', 'njb_nsc', 'hlo')
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
        
        Returns:
            int: Count of records
        """
        try:
            if export_type == 'work_order':
                date_conditions = self._build_date_conditions(PKBData, date_from, date_to)
                count = self.db.query(PKBData.id).filter(
                    and_(
                        PKBData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()
                
            elif export_type == 'njb_nsc':
                date_conditions = self._build_date_conditions(WorkshopInvoiceData, date_from, date_to)
                count = self.db.query(WorkshopInvoiceData.id).filter(
                    and_(
                        WorkshopInvoiceData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()
                
            elif export_type == 'hlo':
                date_conditions = self._build_date_conditions(DPHLOData, date_from, date_to)
                count = self.db.query(DPHLOPart.id).join(
                    DPHLOData, DPHLOData.id == DPHLOPart.dp_hlo_data_id
                ).filter(
                    and_(
                        DPHLOData.dealer_id == dealer_id,
                        DPHLOData.id_hlo_document.isnot(None),
                        date_conditions
                    )
                ).count()
                
            else:
                raise ValueError(f"Invalid export type: {export_type}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting export data count: {str(e)}")
            return 0