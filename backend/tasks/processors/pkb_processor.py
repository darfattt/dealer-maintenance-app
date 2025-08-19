"""
PKB data processor - handles PKB (Service Record) data fetching and processing
"""
from datetime import datetime, date
from typing import Dict, Any

from database import Dealer, PKBData, PKBService, PKBPart
from ..api_clients import PKBAPIClient
from ..dummy_data_generators import get_dummy_pkb_data, should_use_dummy_data
from .base_processor import BaseDataProcessor


class PKBDataProcessor(BaseDataProcessor):
    """Processor for PKB (Service Record) data"""
    
    def __init__(self):
        super().__init__("pkb")
    
    def set_default_time_range(self, from_time: str, to_time: str) -> tuple[str, str]:
        """Set default time range for PKB data (different from base)"""
        if not from_time or not to_time:
            today = date.today()
            from_time = f"{today} 01:01:00"
            to_time = f"{today} 23:59:00"
        return from_time, to_time
    
    def fetch_api_data(self, dealer: Dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch PKB data from API or dummy source"""
        try:
            self.logger.info(f"Fetching PKB data for dealer {dealer.dealer_id}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_pkb_data(dealer.dealer_id, from_time, to_time)

            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy PKB data for dealer {dealer.dealer_id}")
                return get_dummy_pkb_data(dealer.dealer_id, from_time, to_time)

            # Make API call
            client = PKBAPIClient()
            api_response = client.fetch_data(dealer.dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key)

            # Validate API response
            if not api_response or not isinstance(api_response, dict):
                raise ValueError("Invalid API response format - response is None or not a dictionary")

            if api_response.get("status") != 1:
                error_message = api_response.get("message", "Unknown API error")
                self.logger.error(f"API returned error status: {error_message}")
                # Return actual error instead of falling back to dummy data
                return {
                    "status": 0,
                    "message": f"API Error: {error_message}",
                    "data": []
                }

            # Safely get data with proper validation
            data = api_response.get('data', [])
            if data is None:
                data = []

            self.logger.info(f"Successfully fetched PKB data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching PKB data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store PKB records using bulk operations"""
        try:
            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No PKB data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} PKB records for dealer {dealer_id}")

            # Prepare bulk data for main records
            pkb_records = []
            service_records = []
            part_records = []

            for pkb in data:
                try:
                    # Prepare main PKB record
                    pkb_data = {
                        'dealer_id': dealer_id,
                        'no_work_order': pkb.get("noWorkOrder"),
                        'no_sa_form': pkb.get("noSAForm"),
                        'tanggal_servis': pkb.get("tanggalServis"),
                        'waktu_pkb': pkb.get("waktuPKB"),
                        'no_polisi': pkb.get("noPolisi"),
                        'no_rangka': pkb.get("noRangka"),
                        'no_mesin': pkb.get("noMesin"),
                        'kode_tipe_unit': pkb.get("kodeTipeUnit"),
                        'tahun_motor': pkb.get("tahunMotor"),
                        'informasi_bensin': pkb.get("informasiBensin"),
                        'km_terakhir': self.safe_int(pkb.get("kmTerakhir")),
                        'tipe_coming_customer': pkb.get("tipeComingCustomer"),
                        'nama_pemilik': pkb.get("namaPemilik"),
                        'alamat_pemilik': pkb.get("alamatPemilik"),
                        'kode_propinsi_pemilik': pkb.get("kodePropinsiPemilik"),
                        'kode_kota_pemilik': pkb.get("kodeKotaPemilik"),
                        'kode_kecamatan_pemilik': pkb.get("kodeKecamatanPemilik"),
                        'kode_kelurahan_pemilik': pkb.get("kodeKelurahanPemilik"),
                        'kode_pos_pemilik': pkb.get("kodePosPemilik"),
                        'alamat_pembawa': pkb.get("alamatPembawa"),
                        'kode_propinsi_pembawa': pkb.get("kodePropinsiPembawa"),
                        'kode_kota_pembawa': pkb.get("kodeKotaPembawa"),
                        'kode_kecamatan_pembawa': pkb.get("kodeKecamatanPembawa"),
                        'kode_kelurahan_pembawa': pkb.get("kodeKelurahanPembawa"),
                        'kode_pos_pembawa': pkb.get("kodePosPembawa"),
                        'nama_pembawa': pkb.get("namaPembawa"),
                        'no_telp_pembawa': pkb.get("noTelpPembawa"),
                        'hubungan_dengan_pemilik': pkb.get("hubunganDenganPemilik"),
                        'keluhan_konsumen': pkb.get("keluhanKonsumen"),
                        'rekomendasi_sa': pkb.get("rekomendasiSA"),
                        'honda_id_sa': pkb.get("hondaIdSA"),
                        'honda_id_mekanik': pkb.get("hondaIdMekanik"),
                        'saran_mekanik': pkb.get("saranMekanik"),
                        'asal_unit_entry': pkb.get("asalUnitEntry"),
                        'id_pit': pkb.get("idPIT"),
                        'jenis_pit': pkb.get("jenisPIT"),
                        'waktu_pendaftaran': pkb.get("waktuPendaftaran"),
                        'waktu_selesai': pkb.get("waktuSelesai"),
                        'total_frt': pkb.get("totalFRT"),
                        'set_up_pembayaran': pkb.get("setUpPembayaran"),
                        'catatan_tambahan': pkb.get("catatanTambahan"),
                        'konfirmasi_pekerjaan_tambahan': pkb.get("konfirmasiPekerjaanTambahan"),
                        'no_buku_claim_c2': pkb.get("noBukuClaimC2"),
                        'no_work_order_job_return': pkb.get("noWorkOrderJobReturn"),
                        'total_biaya_service': pkb.get("totalBiayaService"),
                        'waktu_pekerjaan': pkb.get("waktuPekerjaan"),
                        'status_work_order': pkb.get("statusWorkOrder"),
                        'created_time': pkb.get("createdTime"),
                        'modified_time': pkb.get("modifiedTime"),
                        'fetched_at': datetime.utcnow()
                    }
                    pkb_records.append(pkb_data)

                    # Prepare service records (will be processed after main records)
                    services = self.ensure_list_data(pkb.get("services"))
                    for service in services:
                        service_data = {
                            'id_job': service.get("idJob"),
                            'nama_pekerjaan': service.get("namaPekerjaan"),
                            'jenis_pekerjaan': service.get("jenisPekerjaan"),
                            'biaya_service': service.get("biayaService"),
                            'promo_id_jasa': service.get("promoIdJasa"),
                            'disc_service_amount': service.get("discServiceAmount"),
                            'disc_service_percentage': service.get("discServicePercentage"),
                            'total_harga_servis': service.get("totalHargaServis"),
                            'created_time': service.get("createdTime"),
                            'modified_time': service.get("modifiedTime"),
                            # Will need to link to parent after bulk insert
                            'work_order': pkb.get("noWorkOrder")  # Temporary field for linking
                        }
                        service_records.append(service_data)

                    # Prepare part records (will be processed after main records)
                    parts = self.ensure_list_data(pkb.get("parts"))
                    for part in parts:
                        part_data = {
                            'id_job': part.get("idJob"),
                            'parts_number': part.get("partsNumber"),
                            'harga_parts': part.get("hargaParts"),
                            'promo_id_parts': part.get("promoIdParts"),
                            'disc_parts_amount': part.get("discPartsAmount"),
                            'disc_parts_percentage': part.get("discPartsPercentage"),
                            'ppn': part.get("ppn"),
                            'total_harga_parts': self.safe_numeric(part.get("totalHargaParts")),
                            'uang_muka': self.safe_numeric(part.get("uangMuka")),
                            'kuantitas': self.safe_int(part.get("kuantitas")),
                            'created_time': part.get("createdTime"),
                            'modified_time': part.get("modifiedTime"),
                            # Will need to link to parent after bulk insert
                            'work_order': pkb.get("noWorkOrder")  # Temporary field for linking
                        }
                        part_records.append(part_data)

                except Exception as e:
                    self.logger.error(f"Error preparing PKB record: {e}")
                    continue

            if not pkb_records:
                self.logger.warning(f"No valid PKB records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert main PKB records
            main_processed = self.bulk_upsert(
                db,
                PKBData,
                pkb_records,
                conflict_columns=['dealer_id', 'no_work_order'],
                batch_size=500
            )

            # Process service records if any
            if service_records:
                # First, get the mapping of work order numbers to database IDs
                work_orders = [record['no_work_order'] for record in pkb_records if record['no_work_order']]
                if work_orders:
                    pkb_mapping = {}
                    pkb_query = db.query(PKBData.id, PKBData.no_work_order).filter(
                        PKBData.dealer_id == dealer_id,
                        PKBData.no_work_order.in_(work_orders)
                    ).all()

                    for pkb_id, work_order in pkb_query:
                        pkb_mapping[work_order] = pkb_id

                    # Update service records with correct foreign keys
                    valid_services = []
                    for service in service_records:
                        work_order = service.pop('work_order', None)
                        if work_order and work_order in pkb_mapping:
                            service['pkb_data_id'] = pkb_mapping[work_order]
                            valid_services.append(service)

                    if valid_services:
                        # Bulk upsert services with conflict resolution
                        services_processed = self.bulk_upsert(
                            db,
                            PKBService,
                            valid_services,
                            conflict_columns=['pkb_data_id', 'id_job'],
                            batch_size=500
                        )

                        self.logger.info(f"Processed {services_processed} PKB services for dealer {dealer_id}")

            # Process part records if any
            if part_records:
                # Use the same mapping as services
                work_orders = [record['no_work_order'] for record in pkb_records if record['no_work_order']]
                if work_orders:
                    pkb_mapping = {}
                    pkb_query = db.query(PKBData.id, PKBData.no_work_order).filter(
                        PKBData.dealer_id == dealer_id,
                        PKBData.no_work_order.in_(work_orders)
                    ).all()

                    for pkb_id, work_order in pkb_query:
                        pkb_mapping[work_order] = pkb_id

                    # Update part records with correct foreign keys
                    valid_parts = []
                    for part in part_records:
                        work_order = part.pop('work_order', None)
                        if work_order and work_order in pkb_mapping:
                            part['pkb_data_id'] = pkb_mapping[work_order]
                            valid_parts.append(part)

                    if valid_parts:
                        # Bulk upsert parts with conflict resolution
                        parts_processed = self.bulk_upsert(
                            db,
                            PKBPart,
                            valid_parts,
                            conflict_columns=['pkb_data_id', 'id_job', 'parts_number'],
                            batch_size=500
                        )

                        self.logger.info(f"Processed {parts_processed} PKB parts for dealer {dealer_id}")

            self.logger.info(f"Successfully processed {main_processed} PKB records for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing PKB records for dealer {dealer_id}: {e}")
            raise

    def get_summary_stats(self, db, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for PKB data"""
        try:
            from sqlalchemy import func

            # Base query
            query = db.query(PKBData)
            if dealer_id:
                query = query.filter(PKBData.dealer_id == dealer_id)

            total_pkb = query.count()

            # Count services and parts
            service_query = db.query(PKBService)
            part_query = db.query(PKBPart)
            if dealer_id:
                service_query = service_query.join(PKBData).filter(PKBData.dealer_id == dealer_id)
                part_query = part_query.join(PKBData).filter(PKBData.dealer_id == dealer_id)

            total_services = service_query.count()
            total_parts = part_query.count()

            # Total amounts
            total_amounts = db.query(
                func.sum(PKBData.total_biaya_service).label('total_service_cost'),
                func.sum(PKBPart.total_harga_parts).label('total_parts_cost')
            )
            if dealer_id:
                total_amounts = total_amounts.join(PKBPart, PKBData.id == PKBPart.pkb_data_id, isouter=True).filter(
                    PKBData.dealer_id == dealer_id
                )

            amounts = total_amounts.first()

            # Status distribution
            status_dist = db.query(
                PKBData.status_work_order,
                func.count(PKBData.id).label('count')
            )
            if dealer_id:
                status_dist = status_dist.filter(PKBData.dealer_id == dealer_id)

            status_distribution = [
                {"status": row.status_work_order or "Unknown", "count": row.count}
                for row in status_dist.group_by(PKBData.status_work_order).limit(10).all()
            ]

            # Service type distribution
            service_dist = db.query(
                PKBService.jenis_pekerjaan,
                func.count(PKBService.id).label('count')
            )
            if dealer_id:
                service_dist = service_dist.join(PKBData).filter(PKBData.dealer_id == dealer_id)

            service_distribution = [
                {"service_type": row.jenis_pekerjaan or "Unknown", "count": row.count}
                for row in service_dist.group_by(PKBService.jenis_pekerjaan).limit(10).all()
            ]

            return {
                "total_pkb": total_pkb,
                "total_services": total_services,
                "total_parts": total_parts,
                "total_service_cost": float(amounts.total_service_cost or 0),
                "total_parts_cost": float(amounts.total_parts_cost or 0),
                "status_distribution": status_distribution,
                "service_distribution": service_distribution
            }

        except Exception as e:
            self.logger.error(f"Error getting PKB summary stats: {e}")
            return {
                "total_pkb": 0,
                "total_services": 0,
                "total_parts": 0,
                "total_service_cost": 0.0,
                "total_parts_cost": 0.0,
                "status_distribution": [],
                "service_distribution": []
            }
