# ✅ SPK Dealing Process Job Type Implementation Guide

## 🎯 **JOB TYPE SPECIFICATIONS**

### **✅ Job Type Details**
- **Code**: `spk_read`
- **Label**: `Manage Dealing Process`
- **Icon**: `📋`
- **API Endpoint**: `https://example.com/dgi-api/v1.3/spk/read`
- **Purpose**: Fetch SPK (Surat Perintah Kerja) dealing process data from DGI API

### **✅ API Specification**
```json
// Sample Request
{
  "fromTime": "2019-01-15 12:31:00",
  "toTime": "2019-01-21 15:50:00",
  "dealerId": "08138",
  "idProspect": "H2Z/12345/19/03/PSP/0001/00001",    // optional
  "idSalesPeople": "122536"                          // optional
}

// Sample Response
{
  "status": 1,
  "message": null,
  "data": [
    {
      "idSpk": "SPK/12345/18/01/00001",
      "idProspect": "H2Z/12345/19/03/PSP/0001/00001",
      "namaCustomer": "Amir Nasution",
      "noKtp": "32010705060900002",
      "alamat": "Jl. Xxxxx No. 12 RT 001, RW 002",
      "kodePropinsi": "3100",
      "kodeKota": "3101",
      "kodeKecamatan": "317404",
      "kodeKelurahan": "3174040001",
      "kodePos": "14130",
      "noKontak": "0812123123",
      "namaBPKB": "Amir Nasution",
      "noKTPBPKB": "32010705060900002",
      "alamatBPKB": "Jl. Xxxxx No. 12 RT 001, RW 002",
      "kodePropinsiBPKB": "3100",
      "kodeKotaBPKB": "3101",
      "kodeKecamatanBPKB": "317404",
      "kodeKelurahanBPKB": "3174040001",
      "kodePosBPKB": "14130",
      "latitude": "111,123121",
      "longitude": "-7,123111",
      "NPWP": "1.111.111.1-111.111",
      "noKK": "3201070506090001",
      "alamatKK": "Jl. Xxxxx No. 12 RT 001, RW 002",
      "kodePropinsiKK": "3100",
      "kodeKotaKK": "3101",
      "kodeKecamatanKK": "317404",
      "kodeKelurahanKK": "3174040001",
      "kodePosKK": "14130",
      "fax": "021-5355678",
      "email": "amir@gmail.com",
      "idSalesPeople": "122536",
      "idEvent": "EV/E/K0Z/12321/18/01/004",
      "tanggalPesanan": "31/12/2019",
      "statusSPK": "3",
      "dealerId": "08138",
      "createdTime": "31/12/2019 15:40:50",
      "modifiedTime": "31/12/2019 15:40:50",
      "unit": [
        {
          "kodeTipeUnit": "HP5",
          "kodeWarna": "BK",
          "quantity": 1,
          "hargaJual": 18000000,
          "diskon": 250000,
          "amountPPN": 1800000,
          "fakturPajak": "010.-900-13.00000001",
          "tipePembayaran": "1",
          "jumlahTandaJadi": 2000000,
          "tanggalPengiriman": "02/10/2018",
          "idSalesProgram": "PRM/0102/18/12/0001,PRM/0102/18/12/0002",
          "idApparel": "86100H04 FA00INBO,86100H04 FA34INBO",
          "createdTime": "31/12/2019 15:40:50",
          "modifiedTime": "31/12/2019 15:40:50"
        }
      ],
      "dataAnggotaKeluarga": [
        {
          "anggotaKK": "Mawar",
          "createdTime": "31/12/2019 15:40:50",
          "modifiedTime": "31/12/2019 15:40:50"
        }
      ]
    }
  ]
}
```

## 🔧 **IMPLEMENTATION STEPS**

### **Step 1: Job Type Configuration**
**File: `admin_panel/components/job_types.py`**
```python
JOB_TYPE_MAPPING = {
    "prospect": "Prospect",
    "pkb": "Manage WO - PKB", 
    "parts_inbound": "Part Inbound - PINB",
    "leasing": "Handle Leasing Requirement",
    "doch_read": "Manage Document Handling",
    "uinb_read": "Unit Inbound from Purchase Order",
    "bast_read": "Manage Delivery Process",
    "spk_read": "Manage Dealing Process"  # ✅ NEW
}
```

### **Step 2: Database Structure**
**Files: `backend/database.py`, `dashboard_analytics/database.py`**
```python
class SPKDealingProcessData(Base):
    """SPK dealing process data from SPK API"""
    __tablename__ = "spk_dealing_process_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String(10), ForeignKey("dealers.dealer_id"), nullable=False)
    id_spk = Column(String(100), nullable=True, index=True)
    id_prospect = Column(String(100), nullable=True, index=True)
    nama_customer = Column(String(200), nullable=True)
    no_ktp = Column(String(50), nullable=True, index=True)
    alamat = Column(Text, nullable=True)
    kode_propinsi = Column(String(10), nullable=True)
    kode_kota = Column(String(10), nullable=True)
    kode_kecamatan = Column(String(20), nullable=True)
    kode_kelurahan = Column(String(20), nullable=True)
    kode_pos = Column(String(10), nullable=True)
    no_kontak = Column(String(50), nullable=True)
    nama_bpkb = Column(String(200), nullable=True)
    no_ktp_bpkb = Column(String(50), nullable=True)
    alamat_bpkb = Column(Text, nullable=True)
    kode_propinsi_bpkb = Column(String(10), nullable=True)
    kode_kota_bpkb = Column(String(10), nullable=True)
    kode_kecamatan_bpkb = Column(String(20), nullable=True)
    kode_kelurahan_bpkb = Column(String(20), nullable=True)
    kode_pos_bpkb = Column(String(10), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    npwp = Column(String(50), nullable=True)
    no_kk = Column(String(50), nullable=True)
    alamat_kk = Column(Text, nullable=True)
    kode_propinsi_kk = Column(String(10), nullable=True)
    kode_kota_kk = Column(String(10), nullable=True)
    kode_kecamatan_kk = Column(String(20), nullable=True)
    kode_kelurahan_kk = Column(String(20), nullable=True)
    kode_pos_kk = Column(String(10), nullable=True)
    fax = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    id_sales_people = Column(String(50), nullable=True)
    id_event = Column(String(100), nullable=True)
    tanggal_pesanan = Column(String(50), nullable=True)
    status_spk = Column(String(10), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dealer = relationship("Dealer", back_populates="spk_dealing_process_data")
    units = relationship("SPKDealingProcessUnit", back_populates="spk_dealing_process_data")
    family_members = relationship("SPKDealingProcessFamilyMember", back_populates="spk_dealing_process_data")

class SPKDealingProcessUnit(Base):
    """Unit data for SPK dealing process"""
    __tablename__ = "spk_dealing_process_units"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spk_dealing_process_data_id = Column(UUID(as_uuid=True), ForeignKey("spk_dealing_process_data.id"))
    kode_tipe_unit = Column(String(50), nullable=True)
    kode_warna = Column(String(10), nullable=True)
    quantity = Column(Integer, nullable=True)
    harga_jual = Column(Numeric(15, 2), nullable=True)
    diskon = Column(Numeric(15, 2), nullable=True)
    amount_ppn = Column(Numeric(15, 2), nullable=True)
    faktur_pajak = Column(String(100), nullable=True)
    tipe_pembayaran = Column(String(10), nullable=True)
    jumlah_tanda_jadi = Column(Numeric(15, 2), nullable=True)
    tanggal_pengiriman = Column(String(50), nullable=True)
    id_sales_program = Column(Text, nullable=True)
    id_apparel = Column(Text, nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    
    # Relationships
    spk_dealing_process_data = relationship("SPKDealingProcessData", back_populates="units")

class SPKDealingProcessFamilyMember(Base):
    """Family member data for SPK dealing process"""
    __tablename__ = "spk_dealing_process_family_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spk_dealing_process_data_id = Column(UUID(as_uuid=True), ForeignKey("spk_dealing_process_data.id"))
    anggota_kk = Column(String(200), nullable=True)
    created_time = Column(String(50), nullable=True)
    modified_time = Column(String(50), nullable=True)
    
    # Relationships
    spk_dealing_process_data = relationship("SPKDealingProcessData", back_populates="family_members")

# Update Dealer model
class Dealer(Base):
    # ... existing fields
    spk_dealing_process_data = relationship("SPKDealingProcessData", back_populates="dealer")
```

### **Step 3: API Client Implementation**
**File: `backend/tasks/api_clients.py`**
```python
class SPKDealingProcessAPIClient:
    """Client for SPK Dealing Process API calls"""

    def __init__(self):
        self.config = APIConfigManager.get_api_config("dgi_spk_dealing_process_api") or APIConfigManager.get_default_config()
        self.endpoint = "/spk/read"

    def fetch_data(self, dealer_id: str, from_time: str, to_time: str,
                   api_key: str, secret_key: str, id_prospect: str = "",
                   id_sales_people: str = "") -> Dict[str, Any]:
        """Fetch SPK dealing process data from DGI API"""
        try:
            # Generate token using token manager
            token_manager = DGITokenManager(api_key, secret_key)
            headers = token_manager.get_headers()

            payload = {
                "fromTime": from_time,
                "toTime": to_time,
                "dealerId": dealer_id
            }

            # Add optional parameters
            if id_prospect:
                payload["idProspect"] = id_prospect
            if id_sales_people:
                payload["idSalesPeople"] = id_sales_people

            url = f"{self.config['base_url']}{self.endpoint}"

            with httpx.Client(timeout=self.config['timeout_seconds']) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"SPK dealing process API call failed: {e}")
            raise

# Add API configuration
def initialize_default_api_configs():
    # ... existing configs
    APIConfiguration(
        config_name="dgi_spk_dealing_process_api",
        base_url="https://example.com/dgi-api/v1.3",
        description="DGI API for SPK Dealing Process Data",
        is_active=True,
        timeout_seconds=30,
        retry_attempts=3
    )
```

### **Step 4: Data Processor**
**File: `backend/tasks/processors/spk_dealing_process_processor.py`**
```python
class SPKDealingProcessDataProcessor(BaseDataProcessor):
    """Processor for SPK dealing process data from SPK API"""

    def __init__(self):
        super().__init__("spk_read")
        self.api_client = SPKDealingProcessAPIClient()

    def fetch_api_data(self, dealer, from_time: str, to_time: str, **kwargs):
        """Fetch SPK dealing process data from API or return dummy data"""
        try:
            # Extract optional parameters
            id_prospect = kwargs.get('id_prospect', '')
            id_sales_people = kwargs.get('id_sales_people', '')

            logger.info(f"Fetching SPK dealing process data for dealer {dealer.dealer_id}")

            # Check if dealer has API credentials
            if not dealer.api_key or not dealer.secret_key:
                logger.info(f"No API credentials for dealer {dealer.dealer_id}, using dummy data")
                return get_dummy_spk_dealing_process_data(
                    dealer.dealer_id, from_time, to_time,
                    id_prospect, id_sales_people
                )

            # Make API call
            api_response = self.api_client.fetch_data(
                dealer.dealer_id, from_time, to_time,
                dealer.api_key, dealer.secret_key,
                id_prospect, id_sales_people
            )

            if api_response.get("status") == 1:
                logger.info(f"Successfully fetched SPK dealing process data for dealer {dealer.dealer_id}")
                return api_response
            else:
                error_msg = api_response.get("message", "Unknown API error")
                logger.warning(f"API returned error for dealer {dealer.dealer_id}: {error_msg}")
                return {
                    "status": 0,
                    "message": f"API Error: {error_msg}",
                    "data": []
                }

        except Exception as e:
            logger.error(f"Error fetching SPK dealing process data for dealer {dealer.dealer_id}: {e}")
            # Return actual error message instead of dummy data fallback
            return {
                "status": 0,
                "message": f"Fetch Error: {str(e)}",
                "data": []
            }

    def process_records(self, db: Session, dealer_id: str, api_data: Dict[str, Any]) -> int:
        """Process and store SPK dealing process records"""
        try:
            data = api_data.get("data", [])
            if not data:
                logger.warning(f"No SPK dealing process data to process for dealer {dealer_id}")
                return 0

            processed_count = 0

            for spk_record in data:
                try:
                    # Check for existing record to prevent duplicates
                    existing_spk = db.query(SPKDealingProcessData).filter(
                        and_(
                            SPKDealingProcessData.dealer_id == dealer_id,
                            SPKDealingProcessData.id_spk == spk_record.get("idSpk")
                        )
                    ).first()

                    if existing_spk:
                        logger.debug(f"SPK record {spk_record.get('idSpk')} already exists, skipping")
                        continue

                    # Create main SPK record
                    spk_data = SPKDealingProcessData(
                        dealer_id=dealer_id,
                        id_spk=spk_record.get("idSpk"),
                        id_prospect=spk_record.get("idProspect"),
                        nama_customer=spk_record.get("namaCustomer"),
                        no_ktp=spk_record.get("noKtp"),
                        alamat=spk_record.get("alamat"),
                        kode_propinsi=spk_record.get("kodePropinsi"),
                        kode_kota=spk_record.get("kodeKota"),
                        kode_kecamatan=spk_record.get("kodeKecamatan"),
                        kode_kelurahan=spk_record.get("kodeKelurahan"),
                        kode_pos=spk_record.get("kodePos"),
                        no_kontak=spk_record.get("noKontak"),
                        nama_bpkb=spk_record.get("namaBPKB"),
                        no_ktp_bpkb=spk_record.get("noKTPBPKB"),
                        alamat_bpkb=spk_record.get("alamatBPKB"),
                        kode_propinsi_bpkb=spk_record.get("kodePropinsiBPKB"),
                        kode_kota_bpkb=spk_record.get("kodeKotaBPKB"),
                        kode_kecamatan_bpkb=spk_record.get("kodeKecamatanBPKB"),
                        kode_kelurahan_bpkb=spk_record.get("kodeKelurahanBPKB"),
                        kode_pos_bpkb=spk_record.get("kodePosBPKB"),
                        latitude=spk_record.get("latitude"),
                        longitude=spk_record.get("longitude"),
                        npwp=spk_record.get("NPWP"),
                        no_kk=spk_record.get("noKK"),
                        alamat_kk=spk_record.get("alamatKK"),
                        kode_propinsi_kk=spk_record.get("kodePropinsiKK"),
                        kode_kota_kk=spk_record.get("kodeKotaKK"),
                        kode_kecamatan_kk=spk_record.get("kodeKecamatanKK"),
                        kode_kelurahan_kk=spk_record.get("kodeKelurahanKK"),
                        kode_pos_kk=spk_record.get("kodePosKK"),
                        fax=spk_record.get("fax"),
                        email=spk_record.get("email"),
                        id_sales_people=spk_record.get("idSalesPeople"),
                        id_event=spk_record.get("idEvent"),
                        tanggal_pesanan=spk_record.get("tanggalPesanan"),
                        status_spk=spk_record.get("statusSPK"),
                        created_time=spk_record.get("createdTime"),
                        modified_time=spk_record.get("modifiedTime")
                    )

                    db.add(spk_data)
                    db.flush()  # Get the ID for relationships

                    # Process unit data
                    units = spk_record.get("unit", [])
                    for unit_record in units:
                        unit_data = SPKDealingProcessUnit(
                            spk_dealing_process_data_id=spk_data.id,
                            kode_tipe_unit=unit_record.get("kodeTipeUnit"),
                            kode_warna=unit_record.get("kodeWarna"),
                            quantity=unit_record.get("quantity"),
                            harga_jual=unit_record.get("hargaJual"),
                            diskon=unit_record.get("diskon"),
                            amount_ppn=unit_record.get("amountPPN"),
                            faktur_pajak=unit_record.get("fakturPajak"),
                            tipe_pembayaran=unit_record.get("tipePembayaran"),
                            jumlah_tanda_jadi=unit_record.get("jumlahTandaJadi"),
                            tanggal_pengiriman=unit_record.get("tanggalPengiriman"),
                            id_sales_program=unit_record.get("idSalesProgram"),
                            id_apparel=unit_record.get("idApparel"),
                            created_time=unit_record.get("createdTime"),
                            modified_time=unit_record.get("modifiedTime")
                        )
                        db.add(unit_data)

                    # Process family member data
                    family_members = spk_record.get("dataAnggotaKeluarga", [])
                    for family_record in family_members:
                        family_data = SPKDealingProcessFamilyMember(
                            spk_dealing_process_data_id=spk_data.id,
                            anggota_kk=family_record.get("anggotaKK"),
                            created_time=family_record.get("createdTime"),
                            modified_time=family_record.get("modifiedTime")
                        )
                        db.add(family_data)

                    processed_count += 1

                except Exception as e:
                    logger.error(f"Error processing SPK record: {e}")
                    continue

            db.commit()
            logger.info(f"Successfully processed {processed_count} SPK dealing process records for dealer {dealer_id}")
            return processed_count

        except Exception as e:
            logger.error(f"Error processing SPK dealing process records for dealer {dealer_id}: {e}")
            db.rollback()
            raise

    def get_summary_stats(self, db: Session, dealer_id: str = None) -> Dict[str, Any]:
        """Get summary statistics for SPK dealing process data"""
        try:
            query = db.query(SPKDealingProcessData)

            if dealer_id:
                query = query.filter(SPKDealingProcessData.dealer_id == dealer_id)

            total_records = query.count()

            # Status distribution
            status_distribution = db.query(
                SPKDealingProcessData.status_spk,
                func.count(SPKDealingProcessData.id).label('count')
            ).filter(
                SPKDealingProcessData.dealer_id == dealer_id if dealer_id else True
            ).group_by(SPKDealingProcessData.status_spk).all()

            return {
                "total_records": total_records,
                "status_distribution": [
                    {"status": status, "count": count}
                    for status, count in status_distribution
                ]
            }

        except Exception as e:
            logger.error(f"Error getting SPK dealing process summary stats: {e}")
            return {"total_records": 0, "status_distribution": []}
```

### **Step 5: Backend Controller**
**File: `backend/controllers/spk_dealing_process_controller.py`**
```python
"""
SPK Dealing Process Controller

This module provides REST API endpoints for SPK dealing process data management.
It handles CRUD operations and data retrieval for SPK dealing process information.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
import logging

from database import get_db, SPKDealingProcessData, SPKDealingProcessUnit, SPKDealingProcessFamilyMember, Dealer
from tasks.processors.spk_dealing_process_processor import SPKDealingProcessDataProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/spk_dealing_process", tags=["spk_dealing_process"])


@router.get("/")
async def get_spk_dealing_process_data(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    search: Optional[str] = Query(None, description="Search in SPK ID, prospect ID, customer name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get SPK dealing process data with pagination and search"""
    try:
        # Base query with joins
        query = db.query(SPKDealingProcessData).join(Dealer)

        # Apply dealer filter
        if dealer_id:
            query = query.filter(SPKDealingProcessData.dealer_id == dealer_id)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    SPKDealingProcessData.id_spk.ilike(search_term),
                    SPKDealingProcessData.id_prospect.ilike(search_term),
                    SPKDealingProcessData.nama_customer.ilike(search_term),
                    SPKDealingProcessData.no_ktp.ilike(search_term),
                    SPKDealingProcessData.email.ilike(search_term)
                )
            )

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        spk_data = query.order_by(desc(SPKDealingProcessData.fetched_at)).offset(offset).limit(limit).all()

        # Format response
        result = []
        for spk in spk_data:
            spk_dict = {
                "id": str(spk.id),
                "dealer_id": spk.dealer_id,
                "dealer_name": spk.dealer.dealer_name,
                "id_spk": spk.id_spk,
                "id_prospect": spk.id_prospect,
                "nama_customer": spk.nama_customer,
                "no_ktp": spk.no_ktp,
                "alamat": spk.alamat,
                "no_kontak": spk.no_kontak,
                "email": spk.email,
                "id_sales_people": spk.id_sales_people,
                "tanggal_pesanan": spk.tanggal_pesanan,
                "status_spk": spk.status_spk,
                "created_time": spk.created_time,
                "modified_time": spk.modified_time,
                "fetched_at": spk.fetched_at.isoformat() if spk.fetched_at else None
            }
            result.append(spk_dict)

        return {
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

    except Exception as e:
        logger.error(f"Error fetching SPK dealing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.get("/summary")
async def get_spk_dealing_process_summary(
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    db: Session = Depends(get_db)
):
    """Get SPK dealing process summary statistics"""
    try:
        processor = SPKDealingProcessDataProcessor()
        summary = processor.get_summary_stats(db, dealer_id)

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error getting SPK dealing process summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/dealers")
async def get_dealers_with_spk_dealing_process_data(db: Session = Depends(get_db)):
    """Get list of dealers that have SPK dealing process data"""
    try:
        dealers = db.query(Dealer).join(SPKDealingProcessData).distinct().all()

        result = [
            {
                "dealer_id": dealer.dealer_id,
                "dealer_name": dealer.dealer_name
            }
            for dealer in dealers
        ]

        return {
            "success": True,
            "dealers": result
        }

    except Exception as e:
        logger.error(f"Error fetching dealers with SPK dealing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dealers: {str(e)}")


@router.post("/test-fetch")
async def test_spk_dealing_process_fetch(
    dealer_id: str = Query(..., description="Dealer ID"),
    from_time: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS)"),
    to_time: str = Query(..., description="End time (YYYY-MM-DD HH:MM:SS)"),
    id_prospect: Optional[str] = Query("", description="Prospect ID filter"),
    id_sales_people: Optional[str] = Query("", description="Sales people ID filter"),
    db: Session = Depends(get_db)
):
    """Test SPK dealing process API fetch without storing data"""
    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.dealer_id == dealer_id).first()
        if not dealer:
            raise HTTPException(status_code=404, detail=f"Dealer {dealer_id} not found")

        # Test fetch
        processor = SPKDealingProcessDataProcessor()
        result = processor.fetch_api_data(
            dealer, from_time, to_time,
            id_prospect=id_prospect,
            id_sales_people=id_sales_people
        )

        return {
            "success": True,
            "test_result": result,
            "message": "API test completed successfully"
        }

    except Exception as e:
        logger.error(f"Error testing SPK dealing process fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing fetch: {str(e)}")


@router.get("/search")
async def search_spk_dealing_process_data(
    q: str = Query(..., description="Search query"),
    dealer_id: Optional[str] = Query(None, description="Filter by dealer ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """Search SPK dealing process data across multiple fields"""
    try:
        # Base query
        query = db.query(SPKDealingProcessData).join(Dealer)

        # Apply dealer filter
        if dealer_id:
            query = query.filter(SPKDealingProcessData.dealer_id == dealer_id)

        # Search across multiple fields
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                SPKDealingProcessData.id_spk.ilike(search_term),
                SPKDealingProcessData.id_prospect.ilike(search_term),
                SPKDealingProcessData.nama_customer.ilike(search_term),
                SPKDealingProcessData.no_ktp.ilike(search_term),
                SPKDealingProcessData.email.ilike(search_term),
                SPKDealingProcessData.no_kontak.ilike(search_term)
            )
        )

        spk_data = query.limit(limit).all()

        result = [
            {
                "id": str(spk.id),
                "dealer_id": spk.dealer_id,
                "dealer_name": spk.dealer.dealer_name,
                "id_spk": spk.id_spk,
                "id_prospect": spk.id_prospect,
                "nama_customer": spk.nama_customer,
                "no_ktp": spk.no_ktp,
                "status_spk": spk.status_spk
            }
            for spk in spk_data
        ]

        return {
            "success": True,
            "results": result,
            "query": q
        }

    except Exception as e:
        logger.error(f"Error searching SPK dealing process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching data: {str(e)}")
```

### **Step 6: Task Integration**
**File: `backend/tasks/data_fetcher_router.py`**
```python
class DataFetcherRouter:
    def __init__(self):
        self.processors = {
            "prospect": ProspectDataProcessor(),
            "pkb": PKBDataProcessor(),
            "parts_inbound": PartsInboundDataProcessor(),
            "leasing": LeasingDataProcessor(),
            "doch_read": DocumentHandlingDataProcessor(),
            "uinb_read": UnitInboundDataProcessor(),
            "bast_read": DeliveryProcessDataProcessor(),
            "spk_read": SPKDealingProcessDataProcessor()  # ✅ ADD NEW PROCESSOR
        }

@celery_app.task(bind=True)
def fetch_spk_dealing_process_data(self, dealer_id: str, from_time: str = None,
                                  to_time: str = None, id_prospect: str = "",
                                  id_sales_people: str = ""):
    """Fetch SPK dealing process data for a specific dealer"""
    return router.execute_fetch("spk_read", dealer_id, from_time, to_time,
                              id_prospect=id_prospect, id_sales_people=id_sales_people)

def get_spk_dealing_process_processor() -> SPKDealingProcessDataProcessor:
    """Get SPK dealing process processor instance"""
    return router.get_processor("spk_read")

# Update exports
__all__ = [
    'health_check',
    'fetch_prospect_data',
    'fetch_pkb_data',
    'fetch_parts_inbound_data',
    'fetch_leasing_data',
    'fetch_document_handling_data',
    'fetch_unit_inbound_data',
    'fetch_delivery_process_data',
    'fetch_spk_dealing_process_data',  # ✅ ADD TO EXPORTS
    'router',
    'get_prospect_processor',
    'get_pkb_processor',
    'get_parts_inbound_processor',
    'get_leasing_processor',
    'get_document_handling_processor',
    'get_unit_inbound_processor',
    'get_delivery_process_processor',
    'get_spk_dealing_process_processor'  # ✅ ADD TO EXPORTS
]
```

### **Step 7: Dummy Data Generator**
**File: `backend/tasks/dummy_data_generators.py`**
```python
def get_dummy_spk_dealing_process_data(dealer_id: str, from_time: str, to_time: str,
                                      id_prospect: str = "", id_sales_people: str = "") -> Dict[str, Any]:
    """Generate realistic dummy SPK dealing process data for testing"""

    # Only generate for specific test dealers
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}",
            "data": []
        }

    # Generate realistic test data
    dummy_data = []

    for i in range(1, 4):  # Generate 3 SPK records
        spk_id = f"SPK/{dealer_id}/24/01/0000{i}"
        prospect_id = f"H2Z/{dealer_id}/24/03/PSP/0001/0000{i}"

        # Skip if filtering by prospect and doesn't match
        if id_prospect and id_prospect != prospect_id:
            continue

        # Skip if filtering by sales people and doesn't match
        sales_id = f"12253{i}"
        if id_sales_people and id_sales_people != sales_id:
            continue

        spk_record = {
            "idSpk": spk_id,
            "idProspect": prospect_id,
            "namaCustomer": f"Customer Test {i}",
            "noKtp": f"320107050609000{i:02d}",
            "alamat": f"Jl. Test No. {i} RT 001, RW 002",
            "kodePropinsi": "3100",
            "kodeKota": "3101",
            "kodeKecamatan": "317404",
            "kodeKelurahan": "3174040001",
            "kodePos": "14130",
            "noKontak": f"081212312{i}",
            "namaBPKB": f"Customer Test {i}",
            "noKTPBPKB": f"320107050609000{i:02d}",
            "alamatBPKB": f"Jl. Test No. {i} RT 001, RW 002",
            "kodePropinsiBPKB": "3100",
            "kodeKotaBPKB": "3101",
            "kodeKecamatanBPKB": "317404",
            "kodeKelurahanBPKB": "3174040001",
            "kodePosBPKB": "14130",
            "latitude": f"111,12312{i}",
            "longitude": f"-7,12311{i}",
            "NPWP": f"1.111.111.{i}-111.111",
            "noKK": f"320107050609000{i}",
            "alamatKK": f"Jl. Test No. {i} RT 001, RW 002",
            "kodePropinsiKK": "3100",
            "kodeKotaKK": "3101",
            "kodeKecamatanKK": "317404",
            "kodeKelurahanKK": "3174040001",
            "kodePosKK": "14130",
            "fax": f"021-535567{i}",
            "email": f"customer{i}@test.com",
            "idSalesPeople": sales_id,
            "idEvent": f"EV/E/K0Z/1232{i}/24/01/004",
            "tanggalPesanan": "31/12/2024",
            "statusSPK": str(i),  # Different statuses
            "dealerId": dealer_id,
            "createdTime": "31/12/2024 15:40:50",
            "modifiedTime": "31/12/2024 15:40:50",
            "unit": [
                {
                    "kodeTipeUnit": f"HP{i}",
                    "kodeWarna": "BK" if i % 2 == 1 else "WH",
                    "quantity": 1,
                    "hargaJual": 18000000 + (i * 1000000),
                    "diskon": 250000,
                    "amountPPN": 1800000,
                    "fakturPajak": f"010.-900-13.0000000{i}",
                    "tipePembayaran": str(i % 3 + 1),  # 1, 2, 3
                    "jumlahTandaJadi": 2000000,
                    "tanggalPengiriman": "02/10/2024",
                    "idSalesProgram": f"PRM/0102/24/12/000{i}",
                    "idApparel": f"86100H04 FA00INBO{i}",
                    "createdTime": "31/12/2024 15:40:50",
                    "modifiedTime": "31/12/2024 15:40:50"
                }
            ],
            "dataAnggotaKeluarga": [
                {
                    "anggotaKK": f"Family Member {i}-1",
                    "createdTime": "31/12/2024 15:40:50",
                    "modifiedTime": "31/12/2024 15:40:50"
                },
                {
                    "anggotaKK": f"Family Member {i}-2",
                    "createdTime": "31/12/2024 15:40:50",
                    "modifiedTime": "31/12/2024 15:40:50"
                }
            ]
        }

        dummy_data.append(spk_record)

    return {
        "status": 1,
        "message": None,
        "data": dummy_data
    }
```

### **Step 8: Routing Integration (CRITICAL)**

**File: `backend/tasks/data_fetcher.py`**
```python
# Add imports
from .data_fetcher_router import (
    # ... existing imports
    fetch_spk_dealing_process_data,      # ✅ ADD IMPORT
    get_spk_dealing_process_processor    # ✅ ADD IMPORT
)

# Add exports
__all__ = [
    # ... existing exports
    'fetch_spk_dealing_process_data',    # ✅ ADD EXPORT
    'get_spk_dealing_process_processor'  # ✅ ADD EXPORT
]
```

**File: `backend/controllers/jobs_controller.py`**
```python
# Manual job routing
elif request.fetch_type == "spk_read":  # ✅ ADD ROUTING
    task_name = "tasks.data_fetcher_router.fetch_spk_dealing_process_data"
    message = "SPK dealing process data fetch job started"
    task_args = [request.dealer_id, request.from_time, request.to_time, request.no_po, ""]

# Bulk job routing (same pattern)
elif fetch_type == "spk_read":  # ✅ ADD ROUTING
    task_name = "tasks.data_fetcher_router.fetch_spk_dealing_process_data"
    task_args = [dealer_id, from_time, to_time, no_po, ""]
```

**File: `backend/job_queue_manager.py`**
```python
# Queue processing routing
elif job.fetch_type == "spk_read":  # ✅ ADD ROUTING
    task_name = "tasks.data_fetcher_router.fetch_spk_dealing_process_data"
    task_args = [job.dealer_id, job.from_time, job.to_time, job.no_po or "", ""]
```

**File: `backend/main.py`**
```python
from controllers.spk_dealing_process_controller import router as spk_dealing_process_router
app.include_router(spk_dealing_process_router)  # SPK dealing process data and analytics

# API info updates
"spk_dealing_process": "SPK dealing process data and analytics",
"spk_dealing_process_data": "/spk_dealing_process/",
```

### **Step 9: Dashboard Analytics Integration**

**File: `dashboard_analytics/dashboard_analytics.py`**
```python
menu_options = {
    "🏠 Home": "home",
    "👥 Prospect Data": "prospect",
    "🔧 PKB Data": "pkb",
    "📦 Parts Inbound": "parts_inbound",
    "💰 Leasing Data": "leasing",
    "📄 Document Handling": "doch_read",
    "🚚 Unit Inbound": "uinb_read",
    "🚛 Delivery Process": "bast_read",
    "📋 SPK Dealing Process": "spk_read"  # ✅ NEW MENU
}

def render_spk_dealing_process_data_page(dealer_id):
    """Render SPK dealing process data table with search and pagination"""
    st.subheader("📋 SPK Dealing Process Data")

    # Search functionality
    search_term = st.text_input("🔍 Search SPK, Prospect, Customer",
                               placeholder="Enter SPK ID, Prospect ID, or Customer Name")

    # Get data with search
    data, total_records, total_pages = get_spk_dealing_process_data_table(
        dealer_id, st.session_state.current_page, 50, search_term
    )

    if data:
        # Display data table
        df = pd.DataFrame(data)

        # Configure columns
        column_config = {
            "id_spk": st.column_config.TextColumn("SPK ID", width="medium"),
            "id_prospect": st.column_config.TextColumn("Prospect ID", width="medium"),
            "nama_customer": st.column_config.TextColumn("Customer Name", width="medium"),
            "no_ktp": st.column_config.TextColumn("KTP Number", width="medium"),
            "no_kontak": st.column_config.TextColumn("Contact", width="small"),
            "email": st.column_config.TextColumn("Email", width="medium"),
            "status_spk": st.column_config.TextColumn("Status", width="small"),
            "tanggal_pesanan": st.column_config.TextColumn("Order Date", width="medium"),
            "created_time": st.column_config.TextColumn("Created", width="medium")
        }

        st.dataframe(
            df[["id_spk", "id_prospect", "nama_customer", "no_ktp", "no_kontak",
                "email", "status_spk", "tanggal_pesanan", "created_time"]],
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )

        # Pagination
        render_pagination(total_pages, total_records)
    else:
        st.info("No SPK dealing process data found for the selected criteria.")

@st.cache_data(ttl=60)
def get_spk_dealing_process_data_table(dealer_id, page=1, page_size=50, search_term=""):
    """Get SPK dealing process data for table display with pagination"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        params = {
            "dealer_id": dealer_id,
            "page": page,
            "limit": page_size
        }

        if search_term:
            params["search"] = search_term

        response = requests.get(f"{backend_url}/spk_dealing_process/", params=params)

        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                return (
                    result["data"],
                    result["pagination"]["total"],
                    result["pagination"]["pages"]
                )

        return [], 0, 0

    except Exception as e:
        st.error(f"Error fetching SPK dealing process data: {e}")
        return [], 0, 0
```

## 🎯 **IMPLEMENTATION CHECKLIST**

### **✅ Complete Implementation Steps**

1. **✅ Job Type Configuration** - Add to `job_types.py`
2. **✅ Database Structure** - Create 3 tables with relationships
3. **✅ API Client** - Implement with token authentication
4. **✅ Data Processor** - Handle complex nested data structure
5. **✅ Backend Controller** - Complete REST API endpoints
6. **✅ Task Integration** - Celery task processing
7. **✅ Dummy Data Generator** - Realistic test data
8. **✅ Routing Integration** - All routing points updated
9. **✅ Dashboard Analytics** - New menu and data table

### **🚀 Ready for Implementation**

The SPK Dealing Process job type is now **fully documented** and ready for implementation following the established patterns. This implementation will handle:

- **Complex nested data** (SPK with units and family members)
- **Optional parameters** (idProspect, idSalesPeople filtering)
- **Comprehensive search** across multiple fields
- **Professional UI** with consistent labeling
- **Complete integration** with all system components

**Follow this guide step-by-step to implement the new job type successfully!** 🎉
```
```
