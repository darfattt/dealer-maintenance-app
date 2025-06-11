"""
Prospect data processor - handles prospect data fetching and processing
"""
from datetime import datetime
from typing import Dict, Any

from database import Dealer, ProspectData, ProspectUnit, FetchConfiguration
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
            # Check if dealer should use dummy data
            if should_use_dummy_data(dealer.dealer_id):
                self.logger.info(f"Using dummy data for dealer {dealer.dealer_id}")
                return get_dummy_prospect_data(dealer.dealer_id, from_time, to_time)
            else:
                # Use real API client
                client = ProspectAPIClient()
                api_data = client.fetch_data(dealer.dealer_id, from_time, to_time, dealer.api_key, dealer.secret_key)
                self.logger.info(f"Prospect API call successful for dealer {dealer.dealer_id}")
                return api_data
        except Exception as api_error:
            self.logger.warning(f"Prospect API call failed for dealer {dealer.dealer_id}: {api_error}")
            self.logger.info("Falling back to dummy data for demonstration")
            # Fallback to dummy data
            return get_dummy_prospect_data(dealer.dealer_id, from_time, to_time)
    
    def process_records(self, db, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process prospect records and save to database"""
        records_processed = 0
        prospects_data = self.ensure_list_data(api_data.get("data"))
        
        for prospect in prospects_data:
            # Parse dates and times
            tanggal_prospect = self._parse_date(prospect.get("tanggalProspect"))
            tanggal_appointment = self._parse_date(prospect.get("tanggalAppointment"))
            waktu_appointment = self._parse_time(prospect.get("waktuAppointment"))
            created_time = self._parse_datetime(prospect.get("createdTime"))
            modified_time = self._parse_datetime(prospect.get("modifiedTime"))
            
            # Check if prospect already exists
            existing_prospect = db.query(ProspectData).filter(
                ProspectData.dealer_id == dealer_id,
                ProspectData.id_prospect == prospect.get("idProspect")
            ).first()
            
            if existing_prospect:
                # Update existing record
                prospect_record = existing_prospect
                prospect_record.modified_time = modified_time
                prospect_record.fetched_at = datetime.utcnow()
            else:
                # Create new record
                prospect_record = ProspectData(
                    dealer_id=dealer_id,
                    id_prospect=prospect.get("idProspect"),
                    sumber_prospect=prospect.get("sumberProspect"),
                    tanggal_prospect=tanggal_prospect,
                    tagging_prospect=prospect.get("taggingProspect"),
                    nama_lengkap=prospect.get("namaLengkap"),
                    no_kontak=prospect.get("noKontak"),
                    no_ktp=prospect.get("noKtp"),
                    alamat=prospect.get("alamat"),
                    kode_propinsi=prospect.get("kodePropinsi"),
                    kode_kota=prospect.get("kodeKota"),
                    kode_kecamatan=prospect.get("kodeKecamatan"),
                    kode_kelurahan=prospect.get("kodeKelurahan"),
                    kode_pos=prospect.get("kodePos"),
                    latitude=prospect.get("latitude"),
                    longitude=prospect.get("longitude"),
                    alamat_kantor=prospect.get("alamatKantor"),
                    kode_propinsi_kantor=prospect.get("kodePropinsiKantor"),
                    kode_kota_kantor=prospect.get("kodeKotaKantor"),
                    kode_kecamatan_kantor=prospect.get("kodeKecamatanKantor"),
                    kode_kelurahan_kantor=prospect.get("kodeKelurahanKantor"),
                    kode_pos_kantor=prospect.get("kodePosKantor"),
                    kode_pekerjaan=prospect.get("kodePekerjaan"),
                    no_kontak_kantor=prospect.get("noKontakKantor"),
                    tanggal_appointment=tanggal_appointment,
                    waktu_appointment=waktu_appointment,
                    metode_follow_up=prospect.get("metodeFollowUp"),
                    test_ride_preference=prospect.get("testRidePreference"),
                    status_follow_up_prospecting=prospect.get("statusFollowUpProspecting"),
                    status_prospect=prospect.get("statusProspect"),
                    id_sales_people=prospect.get("idSalesPeople"),
                    id_event=prospect.get("idEvent"),
                    created_time=created_time,
                    modified_time=modified_time
                )
                db.add(prospect_record)
            
            # Handle units (only for new records to avoid duplicates)
            if not existing_prospect:
                units = self.ensure_list_data(prospect.get("unit"))
                for unit in units:
                    unit_created_time = self._parse_datetime(unit.get("createdTime"))
                    unit_modified_time = self._parse_datetime(unit.get("modifiedTime"))
                    
                    prospect_unit = ProspectUnit(
                        prospect_data_id=prospect_record.id,
                        kode_tipe_unit=unit.get("kodeTipeUnit"),
                        sales_program_id=unit.get("salesProgramId"),
                        created_time=unit_created_time,
                        modified_time=unit_modified_time
                    )
                    db.add(prospect_unit)
            
            records_processed += 1
        
        # Update fetch configuration
        fetch_config = db.query(FetchConfiguration).filter(
            FetchConfiguration.dealer_id == dealer_id,
            FetchConfiguration.is_active == True
        ).first()
        
        if fetch_config:
            fetch_config.last_fetch_at = datetime.utcnow()
        
        return records_processed
    
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
