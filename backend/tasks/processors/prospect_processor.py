"""
Prospect data processor - handles prospect data fetching and processing
"""
from datetime import datetime
from typing import Dict, Any

from database import Dealer, ProspectData, ProspectUnit
from ..api_clients import ProspectAPIClient
from ..dummy_data_generators import get_dummy_prospect_data, should_use_dummy_data
from .base_processor import BaseDataProcessor


class ProspectDataProcessor(BaseDataProcessor):
    """Processor for prospect data"""
    
    def __init__(self):
        super().__init__("prospect_data")
    
    def fetch_api_data(self, dealer: Dealer, from_time: str, to_time: str, **kwargs) -> Dict[str, Any]:
        """Fetch prospect data from API or dummy source"""
        try:
            self.logger.info(f"Fetching prospect data for dealer {dealer.dealer_id}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                self.logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_prospect_data(dealer.dealer_id, from_time, to_time)

            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy data for dealer {dealer.dealer_id}")
                return get_dummy_prospect_data(dealer.dealer_id, from_time, to_time)

            # Make API call
            client = ProspectAPIClient()
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

            self.logger.info(f"Successfully fetched prospect data: {len(data)} records")
            return api_response

        except Exception as e:
            self.logger.error(f"Error fetching prospect data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }
    
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store prospect records using bulk operations"""
        try:
            data = api_data.get("data", [])
            if not data:
                self.logger.warning(f"No prospect data to process for dealer {dealer_id}")
                return 0

            self.logger.info(f"Processing {len(data)} prospect records for dealer {dealer_id}")

            # Prepare bulk data for main records
            prospect_records = []
            unit_records = []

            for prospect in data:
                try:
                    # Parse dates and times
                    tanggal_prospect = self._parse_date(prospect.get("tanggalProspect"))
                    tanggal_appointment = self._parse_date(prospect.get("tanggalAppointment"))
                    waktu_appointment = self._parse_time(prospect.get("waktuAppointment"))
                    created_time = self._parse_datetime(prospect.get("createdTime"))
                    modified_time = self._parse_datetime(prospect.get("modifiedTime"))

                    # Prepare main prospect record
                    prospect_data = {
                        'dealer_id': dealer_id,
                        'id_prospect': prospect.get("idProspect"),
                        'sumber_prospect': prospect.get("sumberProspect"),
                        'tanggal_prospect': tanggal_prospect,
                        'tagging_prospect': prospect.get("taggingProspect"),
                        'nama_lengkap': prospect.get("namaLengkap"),
                        'no_kontak': prospect.get("noKontak"),
                        'no_ktp': prospect.get("noKtp"),
                        'alamat': prospect.get("alamat"),
                        'kode_propinsi': prospect.get("kodePropinsi"),
                        'kode_kota': prospect.get("kodeKota"),
                        'kode_kecamatan': prospect.get("kodeKecamatan"),
                        'kode_kelurahan': prospect.get("kodeKelurahan"),
                        'kode_pos': prospect.get("kodePos"),
                        'latitude': prospect.get("latitude"),
                        'longitude': prospect.get("longitude"),
                        'alamat_kantor': prospect.get("alamatKantor"),
                        'kode_propinsi_kantor': prospect.get("kodePropinsiKantor"),
                        'kode_kota_kantor': prospect.get("kodeKotaKantor"),
                        'kode_kecamatan_kantor': prospect.get("kodeKecamatanKantor"),
                        'kode_kelurahan_kantor': prospect.get("kodeKelurahanKantor"),
                        'kode_pos_kantor': prospect.get("kodePosKantor"),
                        'kode_pekerjaan': prospect.get("kodePekerjaan"),
                        'no_kontak_kantor': prospect.get("noKontakKantor"),
                        'tanggal_appointment': tanggal_appointment,
                        'waktu_appointment': waktu_appointment,
                        'metode_follow_up': prospect.get("metodeFollowUp"),
                        'test_ride_preference': prospect.get("testRidePreference"),
                        'status_follow_up_prospecting': prospect.get("statusFollowUpProspecting"),
                        'status_prospect': prospect.get("statusProspect"),
                        'id_sales_people': prospect.get("idSalesPeople"),
                        'id_event': prospect.get("idEvent"),
                        'created_time': created_time,
                        'modified_time': modified_time,
                        'fetched_at': datetime.utcnow()
                    }
                    prospect_records.append(prospect_data)

                    # Prepare unit records (will be processed after main records)
                    units = self.ensure_list_data(prospect.get("unit"))
                    for unit in units:
                        unit_created_time = self._parse_datetime(unit.get("createdTime"))
                        unit_modified_time = self._parse_datetime(unit.get("modifiedTime"))

                        unit_data = {
                            'kode_tipe_unit': unit.get("kodeTipeUnit"),
                            'sales_program_id': unit.get("salesProgramId"),
                            'created_time': unit_created_time,
                            'modified_time': unit_modified_time,
                            # Will need to link to parent after bulk insert
                            'prospect_id': prospect.get("idProspect")  # Temporary field for linking
                        }
                        unit_records.append(unit_data)

                except Exception as e:
                    self.logger.error(f"Error preparing prospect record: {e}")
                    continue

            if not prospect_records:
                self.logger.warning(f"No valid prospect records to process for dealer {dealer_id}")
                return 0

            # Bulk upsert main prospect records
            main_processed = self.bulk_upsert(
                db,
                ProspectData,
                prospect_records,
                conflict_columns=['dealer_id', 'id_prospect'],
                batch_size=500
            )

            # Process unit records if any
            if unit_records:
                # First, get the mapping of prospect IDs to database IDs
                prospect_ids = [record['id_prospect'] for record in prospect_records if record['id_prospect']]
                if prospect_ids:
                    prospect_mapping = {}
                    prospect_query = db.query(ProspectData.id, ProspectData.id_prospect).filter(
                        ProspectData.dealer_id == dealer_id,
                        ProspectData.id_prospect.in_(prospect_ids)
                    ).all()

                    for prospect_db_id, prospect_id in prospect_query:
                        prospect_mapping[prospect_id] = prospect_db_id

                    # Update unit records with correct foreign keys
                    valid_units = []
                    for unit in unit_records:
                        prospect_id = unit.pop('prospect_id', None)
                        if prospect_id and prospect_id in prospect_mapping:
                            unit['prospect_data_id'] = prospect_mapping[prospect_id]
                            valid_units.append(unit)

                    if valid_units:
                        # Bulk insert units (no conflict resolution needed as they're child records)
                        for chunk in self.process_in_chunks(valid_units, chunk_size=1000):
                            db.bulk_insert_mappings(ProspectUnit, chunk)

                        self.logger.info(f"Processed {len(valid_units)} prospect units for dealer {dealer_id}")

            self.logger.info(f"Successfully processed {main_processed} prospect records for dealer {dealer_id}")

            return main_processed

        except Exception as e:
            self.logger.error(f"Error processing prospect records for dealer {dealer_id}: {e}")
            raise
    
    def _parse_date(self, date_str: str):
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            self.logger.warning(f"Invalid date format: {date_str}")
            return None
    
    def _parse_time(self, time_str: str):
        """Parse time string to time object"""
        if not time_str:
            return None
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            self.logger.warning(f"Invalid time format: {time_str}")
            return None
    
    def _parse_datetime(self, datetime_str: str):
        """Parse datetime string to datetime object"""
        if not datetime_str:
            return None
        try:
            return datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            self.logger.warning(f"Invalid datetime format: {datetime_str}")
            return None

    def get_summary_stats(self, db, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for prospect data"""
        try:
            from sqlalchemy import func

            # Base query
            query = db.query(ProspectData)
            if dealer_id:
                query = query.filter(ProspectData.dealer_id == dealer_id)

            total_prospects = query.count()

            # Count units
            unit_query = db.query(ProspectUnit)
            if dealer_id:
                unit_query = unit_query.join(ProspectData).filter(
                    ProspectData.dealer_id == dealer_id
                )

            total_units = unit_query.count()

            # Status distribution
            status_dist = db.query(
                ProspectData.status_prospect,
                func.count(ProspectData.id).label('count')
            )
            if dealer_id:
                status_dist = status_dist.filter(ProspectData.dealer_id == dealer_id)

            status_distribution = [
                {"status": row.status_prospect or "Unknown", "count": row.count}
                for row in status_dist.group_by(ProspectData.status_prospect).limit(10).all()
            ]

            # Source distribution
            source_dist = db.query(
                ProspectData.sumber_prospect,
                func.count(ProspectData.id).label('count')
            )
            if dealer_id:
                source_dist = source_dist.filter(ProspectData.dealer_id == dealer_id)

            source_distribution = [
                {"source": row.sumber_prospect or "Unknown", "count": row.count}
                for row in source_dist.group_by(ProspectData.sumber_prospect).limit(10).all()
            ]

            return {
                "total_prospects": total_prospects,
                "total_units": total_units,
                "status_distribution": status_distribution,
                "source_distribution": source_distribution
            }

        except Exception as e:
            self.logger.error(f"Error getting prospect summary stats: {e}")
            return {
                "total_prospects": 0,
                "total_units": 0,
                "status_distribution": [],
                "source_distribution": []
            }
