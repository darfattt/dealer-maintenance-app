"""
Repository for Excel export data operations
"""

import os
import sys
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text, String, Integer, Float, Numeric

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
    
    def get_work_order_detail_export_data(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Get work order detail data for Excel export from PKB data with services and parts

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            List of dictionaries containing work order detail data
        """
        try:
            logger.info(f"Getting work order detail export data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions
            date_conditions = self._build_date_conditions(PKBData, date_from, date_to)

            # Step 1: Get all PKBData records for the date range
            pkb_data_query = self.db.query(PKBData).filter(
                and_(
                    PKBData.dealer_id == dealer_id,
                    date_conditions
                )
            ).order_by(PKBData.created_time, PKBData.no_work_order)

            pkb_data_results = pkb_data_query.all()
            logger.info(f"Found {len(pkb_data_results)} PKBData records for dealer {dealer_id}")

            if not pkb_data_results:
                logger.info("No PKB data found for the given criteria")
                return []

            # Create a mapping of PKBData ID to PKBData object
            pkb_data_map = {pkb.id: pkb for pkb in pkb_data_results}
            pkb_data_ids = list(pkb_data_map.keys())
            logger.info(f"PKBData IDs: {pkb_data_ids}")

            # Step 2: Get all PKBService records for these PKBData IDs
            services_query = self.db.query(PKBService).filter(
                PKBService.pkb_data_id.in_(pkb_data_ids)
            ).order_by(PKBService.pkb_data_id, PKBService.id)

            services_results = services_query.all()
            logger.info(f"Found {len(services_results)} PKBService records")

            # Step 3: Get all PKBPart records for these PKBData IDs
            parts_query = self.db.query(PKBPart).filter(
                PKBPart.pkb_data_id.in_(pkb_data_ids)
            ).order_by(PKBPart.pkb_data_id, PKBPart.id)

            parts_results = parts_query.all()
            logger.info(f"Found {len(parts_results)} PKBPart records")

            # Step 4: Combine data programmatically
            data = []

            # Helper function to create base PKBData dictionary
            def create_pkb_data_dict(pkb_data):
                return {
                    'dealer_id': pkb_data.dealer_id,
                    'no_work_order': pkb_data.no_work_order,
                    'no_sa_form': pkb_data.no_sa_form,
                    'tanggal_servis': pkb_data.tanggal_servis,
                    'waktu_pkb': pkb_data.waktu_pkb,
                    'no_polisi': pkb_data.no_polisi,
                    'no_rangka': pkb_data.no_rangka,
                    'no_mesin': pkb_data.no_mesin,
                    'kode_tipe_unit': pkb_data.kode_tipe_unit,
                    'tahun_motor': pkb_data.tahun_motor,
                    'informasi_bensin': pkb_data.informasi_bensin,
                    'km_terakhir': pkb_data.km_terakhir,
                    'tipe_coming_customer': pkb_data.tipe_coming_customer,
                    'nama_pemilik': pkb_data.nama_pemilik,
                    'alamat_pemilik': pkb_data.alamat_pemilik,
                    'nama_pembawa': pkb_data.nama_pembawa,
                    'no_telp_pembawa': pkb_data.no_telp_pembawa,
                    'keluhan_konsumen': pkb_data.keluhan_konsumen,
                    'rekomendasi_sa': pkb_data.rekomendasi_sa,
                    'honda_id_sa': pkb_data.honda_id_sa,
                    'honda_id_mekanik': pkb_data.honda_id_mekanik,
                    'total_biaya_service': float(pkb_data.total_biaya_service) if pkb_data.total_biaya_service else 0.0,
                    'status_work_order': pkb_data.status_work_order,
                    'created_time': pkb_data.created_time
                }

            # Track which work orders have services or parts
            work_orders_with_details = set()

            # Add service records
            for service in services_results:
                if service.pkb_data_id in pkb_data_map:
                    work_orders_with_details.add(service.pkb_data_id)
                    pkb_data = pkb_data_map[service.pkb_data_id]
                    record = create_pkb_data_dict(pkb_data)

                    # Add service fields
                    record.update({
                        'id_job': service.id_job,
                        'nama_pekerjaan': service.nama_pekerjaan,
                        'jenis_pekerjaan': service.jenis_pekerjaan,
                        'biaya_service': float(service.biaya_service) if service.biaya_service else None,
                        'total_harga_servis': float(service.total_harga_servis) if service.total_harga_servis else None,
                        # Parts fields (null for service records)
                        'parts_number': None,
                        'harga_parts': None,
                        'kuantitas_parts': None,
                        'total_harga_parts': None
                    })

                    data.append(record)

            # Add parts records
            for part in parts_results:
                if part.pkb_data_id in pkb_data_map:
                    work_orders_with_details.add(part.pkb_data_id)
                    pkb_data = pkb_data_map[part.pkb_data_id]
                    record = create_pkb_data_dict(pkb_data)

                    # Add parts fields
                    record.update({
                        # Service fields (null for parts records)
                        'id_job': None,
                        'nama_pekerjaan': None,
                        'jenis_pekerjaan': None,
                        'biaya_service': None,
                        'total_harga_servis': None,
                        # Parts fields
                        'parts_number': part.parts_number,
                        'harga_parts': float(part.harga_parts) if part.harga_parts else None,
                        'kuantitas_parts': part.kuantitas,
                        'total_harga_parts': float(part.total_harga_parts) if part.total_harga_parts else None
                    })

                    data.append(record)

            # Add work orders that have NO services AND NO parts
            work_orders_without_details = set(pkb_data_map.keys()) - work_orders_with_details
            logger.info(f"Work orders with details: {len(work_orders_with_details)}")
            logger.info(f"Work orders without details: {len(work_orders_without_details)}")
            logger.info(f"Work order IDs without details: {list(work_orders_without_details)}")

            for pkb_data_id in work_orders_without_details:
                pkb_data = pkb_data_map[pkb_data_id]
                record = create_pkb_data_dict(pkb_data)

                # Add null service and parts fields
                record.update({
                    # Service fields (null)
                    'id_job': None,
                    'nama_pekerjaan': None,
                    'jenis_pekerjaan': None,
                    'biaya_service': None,
                    'total_harga_servis': None,
                    # Parts fields (null)
                    'parts_number': None,
                    'harga_parts': None,
                    'kuantitas_parts': None,
                    'total_harga_parts': None
                })

                data.append(record)

            # Sort results by created_time and no_work_order
            data.sort(key=lambda x: (x['created_time'] or '', x['no_work_order'] or ''))

            logger.info(f"Total records added: {len(data)} (services: {len(services_results)}, parts: {len(parts_results)}, without details: {len(work_orders_without_details)})")
            logger.info(f"Retrieved {len(data)} work order detail records for export")
            return data

        except Exception as e:
            logger.error(f"Error getting work order detail export data: {str(e)}")
            raise Exception(f"Failed to retrieve work order detail data: {str(e)}")

    def get_njb_nsc_detail_export_data(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Get NJB/NSC detail data for Excel export from WorkshopInvoiceData with NJB and NSC details

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            List of dictionaries containing NJB/NSC detail data
        """
        try:
            logger.info(f"Getting NJB/NSC detail export data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions
            date_conditions = self._build_date_conditions(WorkshopInvoiceData, date_from, date_to)

            # Step 1: Get all WorkshopInvoiceData records for the date range
            workshop_data_query = self.db.query(WorkshopInvoiceData).filter(
                and_(
                    WorkshopInvoiceData.dealer_id == dealer_id,
                    date_conditions
                )
            ).order_by(WorkshopInvoiceData.created_time, WorkshopInvoiceData.no_work_order)

            workshop_data_results = workshop_data_query.all()
            logger.info(f"Found {len(workshop_data_results)} WorkshopInvoiceData records for dealer {dealer_id}")

            if not workshop_data_results:
                logger.info("No WorkshopInvoiceData found for the given criteria")
                return []

            # Create a mapping of WorkshopInvoiceData ID to WorkshopInvoiceData object
            workshop_data_map = {workshop.id: workshop for workshop in workshop_data_results}
            workshop_data_ids = list(workshop_data_map.keys())
            logger.info(f"WorkshopInvoiceData IDs: {workshop_data_ids}")

            # Step 2: Get all WorkshopInvoiceNJB records for these WorkshopInvoiceData IDs
            njb_query = self.db.query(WorkshopInvoiceNJB).filter(
                WorkshopInvoiceNJB.workshop_invoice_data_id.in_(workshop_data_ids)
            ).order_by(WorkshopInvoiceNJB.workshop_invoice_data_id, WorkshopInvoiceNJB.id)

            njb_results = njb_query.all()
            logger.info(f"Found {len(njb_results)} WorkshopInvoiceNJB records")

            # Step 3: Get all WorkshopInvoiceNSC records for these WorkshopInvoiceData IDs
            nsc_query = self.db.query(WorkshopInvoiceNSC).filter(
                WorkshopInvoiceNSC.workshop_invoice_data_id.in_(workshop_data_ids)
            ).order_by(WorkshopInvoiceNSC.workshop_invoice_data_id, WorkshopInvoiceNSC.id)

            nsc_results = nsc_query.all()
            logger.info(f"Found {len(nsc_results)} WorkshopInvoiceNSC records")

            # Step 4: Combine data programmatically
            data = []

            # Helper function to create base WorkshopInvoiceData dictionary
            def create_workshop_data_dict(workshop_data):
                return {
                    'dealer_id': workshop_data.dealer_id,
                    'no_work_order': workshop_data.no_work_order,
                    'no_njb': workshop_data.no_njb,
                    'tanggal_njb': workshop_data.tanggal_njb,
                    'total_harga_njb': float(workshop_data.total_harga_njb) if workshop_data.total_harga_njb else 0.0,
                    'no_nsc': workshop_data.no_nsc,
                    'tanggal_nsc': workshop_data.tanggal_nsc,
                    'total_harga_nsc': float(workshop_data.total_harga_nsc) if workshop_data.total_harga_nsc else 0.0,
                    'honda_id_sa': workshop_data.honda_id_sa,
                    'honda_id_mekanik': workshop_data.honda_id_mekanik,
                    'created_time': workshop_data.created_time,
                    'modified_time': workshop_data.modified_time,
                    'workshop_invoice_data_id': str(workshop_data.id)
                }

            # Track which workshop invoices have NJB or NSC details
            workshop_invoices_with_details = set()

            # Add NJB records
            for njb in njb_results:
                if njb.workshop_invoice_data_id in workshop_data_map:
                    workshop_invoices_with_details.add(njb.workshop_invoice_data_id)
                    workshop_data = workshop_data_map[njb.workshop_invoice_data_id]
                    record = create_workshop_data_dict(workshop_data)

                    # Add NJB fields
                    record.update({
                        'id_job': njb.id_job,
                        'harga_servis': float(njb.harga_servis) if njb.harga_servis else None,
                        'promo_id_jasa': njb.promo_id_jasa,
                        'disc_service_amount': float(njb.disc_service_amount) if njb.disc_service_amount else None,
                        'disc_service_percentage': njb.disc_service_percentage,
                        'total_harga_servis': float(njb.total_harga_servis) if njb.total_harga_servis else None,
                        'njb_created_time': njb.created_time,
                        'njb_modified_time': njb.modified_time,
                        # NSC fields (null for NJB records)
                        'parts_number': None,
                        'kuantitas': None,
                        'harga_parts': None,
                        'promo_id_parts': None,
                        'disc_parts_amount': None,
                        'disc_parts_percentage': None,
                        'ppn': None,
                        'total_harga_parts': None,
                        'uang_muka': None,
                        'nsc_created_time': None,
                        'nsc_modified_time': None
                    })

                    data.append(record)

            # Add NSC records
            for nsc in nsc_results:
                if nsc.workshop_invoice_data_id in workshop_data_map:
                    workshop_invoices_with_details.add(nsc.workshop_invoice_data_id)
                    workshop_data = workshop_data_map[nsc.workshop_invoice_data_id]
                    record = create_workshop_data_dict(workshop_data)

                    # Add NSC fields
                    record.update({
                        # NJB fields (null for NSC records)
                        'id_job': None,
                        'harga_servis': None,
                        'promo_id_jasa': None,
                        'disc_service_amount': None,
                        'disc_service_percentage': None,
                        'total_harga_servis': None,
                        'njb_created_time': None,
                        'njb_modified_time': None,
                        # NSC fields
                        'parts_number': nsc.parts_number,
                        'kuantitas': nsc.kuantitas,
                        'harga_parts': float(nsc.harga_parts) if nsc.harga_parts else None,
                        'promo_id_parts': nsc.promo_id_parts,
                        'disc_parts_amount': float(nsc.disc_parts_amount) if nsc.disc_parts_amount else None,
                        'disc_parts_percentage': nsc.disc_parts_percentage,
                        'ppn': float(nsc.ppn) if nsc.ppn else None,
                        'total_harga_parts': float(nsc.total_harga_parts) if nsc.total_harga_parts else None,
                        'uang_muka': float(nsc.uang_muka) if nsc.uang_muka else None,
                        'nsc_created_time': nsc.created_time,
                        'nsc_modified_time': nsc.modified_time
                    })

                    data.append(record)

            # Add workshop invoices that have NO NJB AND NO NSC details
            workshop_invoices_without_details = set(workshop_data_map.keys()) - workshop_invoices_with_details
            logger.info(f"Workshop invoices with details: {len(workshop_invoices_with_details)}")
            logger.info(f"Workshop invoices without details: {len(workshop_invoices_without_details)}")
            logger.info(f"Workshop invoice IDs without details: {list(workshop_invoices_without_details)}")

            for workshop_invoice_id in workshop_invoices_without_details:
                workshop_data = workshop_data_map[workshop_invoice_id]
                record = create_workshop_data_dict(workshop_data)

                # Add null NJB and NSC fields
                record.update({
                    # NJB fields (null)
                    'id_job': None,
                    'harga_servis': None,
                    'promo_id_jasa': None,
                    'disc_service_amount': None,
                    'disc_service_percentage': None,
                    'total_harga_servis': None,
                    'njb_created_time': None,
                    'njb_modified_time': None,
                    # NSC fields (null)
                    'parts_number': None,
                    'kuantitas': None,
                    'harga_parts': None,
                    'promo_id_parts': None,
                    'disc_parts_amount': None,
                    'disc_parts_percentage': None,
                    'ppn': None,
                    'total_harga_parts': None,
                    'uang_muka': None,
                    'nsc_created_time': None,
                    'nsc_modified_time': None
                })

                data.append(record)

            # Sort results by created_time and no_work_order
            data.sort(key=lambda x: (x['created_time'] or '', x['no_work_order'] or ''))

            logger.info(f"Total records added: {len(data)} (njb: {len(njb_results)}, nsc: {len(nsc_results)}, without details: {len(workshop_invoices_without_details)})")
            logger.info(f"Retrieved {len(data)} NJB/NSC detail records for export")
            return data

        except Exception as e:
            logger.error(f"Error getting NJB/NSC detail export data: {str(e)}")
            raise Exception(f"Failed to retrieve NJB/NSC detail data: {str(e)}")

    def get_hlo_detail_export_data(
        self,
        dealer_id: str,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Get HLO detail data for Excel export from DPHLOData with DPHLOPart details

        Args:
            dealer_id: Dealer ID to filter by
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            List of dictionaries containing HLO detail data
        """
        try:
            logger.info(f"Getting HLO detail export data for dealer_id={dealer_id}, date_from={date_from}, date_to={date_to}")

            # Build date filter conditions
            date_conditions = self._build_date_conditions(DPHLOData, date_from, date_to)

            # Query HLO data with parts using JOIN
            query = self.db.query(
                DPHLOData.dealer_id,
                DPHLOData.no_invoice_uang_jaminan,
                DPHLOData.id_hlo_document,
                DPHLOData.tanggal_pemesanan_hlo,
                DPHLOData.no_work_order,
                DPHLOData.id_customer,
                DPHLOData.created_time,
                DPHLOData.modified_time,
                DPHLOData.fetched_at,
                DPHLOPart.dp_hlo_data_id,
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

            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append({
                    # DPHLOData fields
                    'dealer_id': row.dealer_id,
                    'no_invoice_uang_jaminan': row.no_invoice_uang_jaminan,
                    'id_hlo_document': row.id_hlo_document,
                    'tanggal_pemesanan_hlo': row.tanggal_pemesanan_hlo,
                    'no_work_order': row.no_work_order,
                    'id_customer': row.id_customer,
                    'created_time': row.created_time,
                    'modified_time': row.modified_time,
                    'fetched_at': row.fetched_at.isoformat() if row.fetched_at else None,
                    # DPHLOPart fields
                    'dp_hlo_data_id': str(row.dp_hlo_data_id) if row.dp_hlo_data_id else None,
                    'parts_number': row.parts_number,
                    'kuantitas': row.kuantitas,
                    'harga_parts': float(row.harga_parts) if row.harga_parts else 0.0,
                    'total_harga_parts': float(row.total_harga_parts) if row.total_harga_parts else 0.0,
                    'uang_muka': float(row.uang_muka) if row.uang_muka else 0.0,
                    'sisa_bayar': float(row.sisa_bayar) if row.sisa_bayar else 0.0,
                    'part_created_time': row.part_created_time,
                    'part_modified_time': row.part_modified_time
                })

            logger.info(f"Retrieved {len(data)} HLO detail records for export")
            return data

        except Exception as e:
            logger.error(f"Error getting HLO detail export data: {str(e)}")
            raise Exception(f"Failed to retrieve HLO detail data: {str(e)}")

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
            export_type: Type of export ('work_order', 'work_order_detail', 'njb_nsc', 'njb_nsc_detail', 'hlo', 'hlo_detail')
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

            elif export_type == 'work_order_detail':
                date_conditions = self._build_date_conditions(PKBData, date_from, date_to)
                # Count services + parts
                services_count = self.db.query(PKBService.id).join(
                    PKBData, PKBData.id == PKBService.pkb_data_id
                ).filter(
                    and_(
                        PKBData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()

                parts_count = self.db.query(PKBPart.id).join(
                    PKBData, PKBData.id == PKBPart.pkb_data_id
                ).filter(
                    and_(
                        PKBData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()

                count = services_count + parts_count

            elif export_type == 'njb_nsc':
                date_conditions = self._build_date_conditions(WorkshopInvoiceData, date_from, date_to)
                count = self.db.query(WorkshopInvoiceData.id).filter(
                    and_(
                        WorkshopInvoiceData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()

            elif export_type == 'njb_nsc_detail':
                date_conditions = self._build_date_conditions(WorkshopInvoiceData, date_from, date_to)
                # Count NJB services + NSC parts
                njb_count = self.db.query(WorkshopInvoiceNJB.id).join(
                    WorkshopInvoiceData, WorkshopInvoiceData.id == WorkshopInvoiceNJB.workshop_invoice_data_id
                ).filter(
                    and_(
                        WorkshopInvoiceData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()

                nsc_count = self.db.query(WorkshopInvoiceNSC.id).join(
                    WorkshopInvoiceData, WorkshopInvoiceData.id == WorkshopInvoiceNSC.workshop_invoice_data_id
                ).filter(
                    and_(
                        WorkshopInvoiceData.dealer_id == dealer_id,
                        date_conditions
                    )
                ).count()

                count = njb_count + nsc_count

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

            elif export_type == 'hlo_detail':
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