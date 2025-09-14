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
                func.substr(model_class.created_time, 1, 10).op('~')(r'^\d{4}-\d{2}-\d{2}$'),
                func.to_date(func.substr(model_class.created_time, 1, 10), 'YYYY-MM-DD') >= func.to_date(date_from, 'YYYY-MM-DD'),
                func.to_date(func.substr(model_class.created_time, 1, 10), 'YYYY-MM-DD') <= func.to_date(date_to, 'YYYY-MM-DD')
            )
        )
        
        # Handle DD/MM/YYYY format
        date_conditions.append(
            and_(
                func.length(model_class.created_time) >= 10,
                func.substr(model_class.created_time, 1, 10).op('~')(r'^\d{2}/\d{2}/\d{4}$'),
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
            
            # Query PKB data - get all fields
            query = self.db.query(PKBData).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    date_conditions
                )
            ).order_by(PKBData.created_time, PKBData.no_work_order)
            
            results = query.all()
            
            # Convert to list of dictionaries with all fields
            data = []
            for row in results:
                data.append({
                    'no_work_order': row.no_work_order,
                    'no_sa_form': row.no_sa_form,
                    'tanggal_servis': row.tanggal_servis,
                    'waktu_pkb': row.waktu_pkb,
                    'no_polisi': row.no_polisi,
                    'no_rangka': row.no_rangka,
                    'no_mesin': row.no_mesin,
                    'kode_tipe_unit': row.kode_tipe_unit,
                    'tahun_motor': row.tahun_motor,
                    'informasi_bensin': row.informasi_bensin,
                    'km_terakhir': row.km_terakhir,
                    'tipe_coming_customer': row.tipe_coming_customer,
                    'nama_pemilik': row.nama_pemilik,
                    'alamat_pemilik': row.alamat_pemilik,
                    'kode_propinsi_pemilik': row.kode_propinsi_pemilik,
                    'kode_kota_pemilik': row.kode_kota_pemilik,
                    'kode_kecamatan_pemilik': row.kode_kecamatan_pemilik,
                    'kode_kelurahan_pemilik': row.kode_kelurahan_pemilik,
                    'kode_pos_pemilik': row.kode_pos_pemilik,
                    'nama_pembawa': row.nama_pembawa,
                    'alamat_pembawa': row.alamat_pembawa,
                    'kode_propinsi_pembawa': row.kode_propinsi_pembawa,
                    'kode_kota_pembawa': row.kode_kota_pembawa,
                    'kode_kecamatan_pembawa': row.kode_kecamatan_pembawa,
                    'kode_kelurahan_pembawa': row.kode_kelurahan_pembawa,
                    'kode_pos_pembawa': row.kode_pos_pembawa,
                    'no_telp_pembawa': row.no_telp_pembawa,
                    'hubungan_dengan_pemilik': row.hubungan_dengan_pemilik,
                    'keluhan_konsumen': row.keluhan_konsumen,
                    'rekomendasi_sa': row.rekomendasi_sa,
                    'honda_id_sa': row.honda_id_sa,
                    'honda_id_mekanik': row.honda_id_mekanik,
                    'saran_mekanik': row.saran_mekanik,
                    'asal_unit_entry': row.asal_unit_entry,
                    'id_pit': row.id_pit,
                    'jenis_pit': row.jenis_pit,
                    'waktu_pendaftaran': row.waktu_pendaftaran,
                    'waktu_selesai': row.waktu_selesai,
                    'total_frt': row.total_frt,
                    'set_up_pembayaran': row.set_up_pembayaran,
                    'catatan_tambahan': row.catatan_tambahan,
                    'konfirmasi_pekerjaan_tambahan': row.konfirmasi_pekerjaan_tambahan,
                    'no_buku_claim_c2': row.no_buku_claim_c2,
                    'no_work_order_job_return': row.no_work_order_job_return,
                    'total_biaya_service': float(row.total_biaya_service) if row.total_biaya_service else 0.0,
                    'waktu_pekerjaan': row.waktu_pekerjaan,
                    'status_work_order': row.status_work_order,
                    'created_time': row.created_time,
                    'modified_time': row.modified_time
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
            
            # Query workshop invoice data - get all fields
            query = self.db.query(WorkshopInvoiceData).filter(
                and_(
                    WorkshopInvoiceData.dealer_id == dealer_id,
                    date_conditions
                )
            ).order_by(WorkshopInvoiceData.created_time, WorkshopInvoiceData.no_work_order)
            
            results = query.all()
            
            # Convert to list of dictionaries with all fields
            data = []
            for row in results:
                data.append({
                    'no_work_order': row.no_work_order,
                    'no_njb': row.no_njb,
                    'tanggal_njb': row.tanggal_njb,
                    'total_harga_njb': float(row.total_harga_njb) if row.total_harga_njb else 0.0,
                    'no_nsc': row.no_nsc,
                    'tanggal_nsc': row.tanggal_nsc,
                    'total_harga_nsc': float(row.total_harga_nsc) if row.total_harga_nsc else 0.0,
                    'honda_id_sa': row.honda_id_sa,
                    'honda_id_mekanik': row.honda_id_mekanik,
                    'created_time': row.created_time,
                    'modified_time': row.modified_time
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
            
            # Query HLO data with parts using JOIN - get all fields
            query = self.db.query(
                DPHLOData.id_hlo_document,
                DPHLOData.no_invoice_uang_jaminan,
                DPHLOData.tanggal_pemesanan_hlo,
                DPHLOData.no_work_order,
                DPHLOData.id_customer,
                DPHLOData.created_time,
                DPHLOData.modified_time,
                DPHLOPart.parts_number,
                DPHLOPart.kuantitas,
                DPHLOPart.harga_parts,
                DPHLOPart.total_harga_parts,
                DPHLOPart.uang_muka,
                DPHLOPart.sisa_bayar,
                DPHLOPart.created_time.label('part_created_time'),
                DPHLOPart.modified_time.label('part_modified_time')
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
            
            # Convert to list of dictionaries with all fields
            data = []
            for row in results:
                data.append({
                    'id_hlo_document': row.id_hlo_document,
                    'no_invoice_uang_jaminan': row.no_invoice_uang_jaminan,
                    'tanggal_pemesanan_hlo': row.tanggal_pemesanan_hlo,
                    'no_work_order': row.no_work_order,
                    'id_customer': row.id_customer,
                    'parts_number': row.parts_number,
                    'kuantitas': row.kuantitas,
                    'harga_parts': float(row.harga_parts) if row.harga_parts else 0.0,
                    'total_harga_parts': float(row.total_harga_parts) if row.total_harga_parts else 0.0,
                    'uang_muka': float(row.uang_muka) if row.uang_muka else 0.0,
                    'sisa_bayar': float(row.sisa_bayar) if row.sisa_bayar else 0.0,
                    'created_time': row.created_time,
                    'modified_time': row.modified_time
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