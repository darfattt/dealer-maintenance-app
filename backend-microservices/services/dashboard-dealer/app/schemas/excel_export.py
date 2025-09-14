"""
Excel Export schemas for request/response models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ExcelExportRequest(BaseModel):
    """Base request schema for Excel export endpoints"""
    dealer_id: str = Field(..., description="Dealer ID to filter by")
    date_from: str = Field(..., description="Start date in YYYY-MM-DD format")
    date_to: str = Field(..., description="End date in YYYY-MM-DD format")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "dealer_id": "12284",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31"
            }
        }


class ExcelExportMetadata(BaseModel):
    """Metadata information about the exported Excel file"""
    filename: str = Field(..., description="Generated filename for the Excel file")
    total_records: int = Field(..., description="Total number of records exported")
    export_type: str = Field(..., description="Type of export (WorkOrder, NJB_NSC, HLO)")
    generated_at: str = Field(..., description="ISO timestamp when file was generated")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    
    class Config:
        from_attributes = True


class WorkOrderExportData(BaseModel):
    """Schema for Work Order export data"""
    no_work_order: Optional[str] = Field(None, description="Work Order Number")
    no_sa_form: Optional[str] = Field(None, description="SA Form Number")
    tanggal_servis: Optional[str] = Field(None, description="Service Date")
    no_polisi: Optional[str] = Field(None, description="License Plate Number")
    no_mesin: Optional[str] = Field(None, description="Engine Number")
    no_rangka: Optional[str] = Field(None, description="Chassis Number")
    nama_pembawa: Optional[str] = Field(None, description="Customer Name")
    no_telp_pembawa: Optional[str] = Field(None, description="Customer Phone Number")
    total_biaya_service: Optional[float] = Field(None, description="Total Service Cost")
    
    class Config:
        from_attributes = True


class NJBNSCExportData(BaseModel):
    """Schema for NJB/NSC export data"""
    honda_id_sa: Optional[str] = Field(None, description="Honda SA ID")
    honda_id_mekanik: Optional[str] = Field(None, description="Honda Mechanic ID")
    no_work_order: Optional[str] = Field(None, description="Work Order Number")
    no_njb: Optional[str] = Field(None, description="NJB Number")
    tanggal_njb: Optional[str] = Field(None, description="NJB Date")
    total_harga_njb: Optional[float] = Field(None, description="Total NJB Price")
    no_nsc: Optional[str] = Field(None, description="NSC Number")
    tanggal_nsc: Optional[str] = Field(None, description="NSC Date")
    total_harga_nsc: Optional[float] = Field(None, description="Total NSC Price")
    
    class Config:
        from_attributes = True


class HLOExportData(BaseModel):
    """Schema for HLO export data"""
    id_hlo_document: Optional[str] = Field(None, description="HLO Document ID")
    tanggal_pemesanan_hlo: Optional[str] = Field(None, description="HLO Order Date")
    no_work_order: Optional[str] = Field(None, description="Work Order Number")
    id_customer: Optional[str] = Field(None, description="Customer ID")
    parts_number: Optional[str] = Field(None, description="Part Number")
    kuantitas: Optional[int] = Field(None, description="Part Quantity")
    total_harga_parts: Optional[float] = Field(None, description="Total Parts Price")
    
    class Config:
        from_attributes = True


class ExcelExportResponse(BaseModel):
    """Response schema for Excel export endpoints"""
    success: bool = Field(True, description="Whether the export was successful")
    message: str = Field("Excel file generated successfully", description="Response message")
    metadata: ExcelExportMetadata = Field(..., description="Export metadata")
    
    class Config:
        from_attributes = True


class ExcelExportError(BaseModel):
    """Error response schema for Excel export endpoints"""
    success: bool = Field(False, description="Export failed")
    message: str = Field(..., description="Error message")
    error_detail: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code for debugging")
    
    class Config:
        from_attributes = True


# Column configurations for each export type
WORK_ORDER_COLUMNS = [
    {"key": "no", "header": "No"},
    {"key": "no_work_order", "header": "No. Work Order"},
    {"key": "no_sa_form", "header": "No. SA Form"},
    {"key": "tanggal_servis", "header": "Tgl Service"},
    {"key": "waktu_pkb", "header": "Waktu PKB"},
    {"key": "no_polisi", "header": "Nomor Polisi"},
    {"key": "no_rangka", "header": "Nomor Rangka"},
    {"key": "no_mesin", "header": "Nomor Mesin"},
    {"key": "kode_tipe_unit", "header": "Kode Tipe Unit"},
    {"key": "tahun_motor", "header": "Tahun Motor"},
    {"key": "informasi_bensin", "header": "Informasi Bensin"},
    {"key": "km_terakhir", "header": "KM Terakhir"},
    {"key": "tipe_coming_customer", "header": "Tipe Coming Customer"},
    {"key": "nama_pemilik", "header": "Nama Pemilik"},
    {"key": "alamat_pemilik", "header": "Alamat Pemilik"},
    {"key": "kode_propinsi_pemilik", "header": "Kode Provinsi Pemilik"},
    {"key": "kode_kota_pemilik", "header": "Kode Kota Pemilik"},
    {"key": "kode_kecamatan_pemilik", "header": "Kode Kecamatan Pemilik"},
    {"key": "kode_kelurahan_pemilik", "header": "Kode Kelurahan Pemilik"},
    {"key": "kode_pos_pemilik", "header": "Kode Pos Pemilik"},
    {"key": "nama_pembawa", "header": "Nama Pembawa"},
    {"key": "alamat_pembawa", "header": "Alamat Pembawa"},
    {"key": "kode_propinsi_pembawa", "header": "Kode Provinsi Pembawa"},
    {"key": "kode_kota_pembawa", "header": "Kode Kota Pembawa"},
    {"key": "kode_kecamatan_pembawa", "header": "Kode Kecamatan Pembawa"},
    {"key": "kode_kelurahan_pembawa", "header": "Kode Kelurahan Pembawa"},
    {"key": "kode_pos_pembawa", "header": "Kode Pos Pembawa"},
    {"key": "no_telp_pembawa", "header": "No Telp Pembawa"},
    {"key": "hubungan_dengan_pemilik", "header": "Hubungan Dengan Pemilik"},
    {"key": "keluhan_konsumen", "header": "Keluhan Konsumen"},
    {"key": "rekomendasi_sa", "header": "Rekomendasi SA"},
    {"key": "honda_id_sa", "header": "Honda ID SA"},
    {"key": "honda_id_mekanik", "header": "Honda ID Mekanik"},
    {"key": "saran_mekanik", "header": "Saran Mekanik"},
    {"key": "asal_unit_entry", "header": "Asal Unit Entry"},
    {"key": "id_pit", "header": "ID PIT"},
    {"key": "jenis_pit", "header": "Jenis PIT"},
    {"key": "waktu_pendaftaran", "header": "Waktu Pendaftaran"},
    {"key": "waktu_selesai", "header": "Waktu Selesai"},
    {"key": "total_frt", "header": "Total FRT"},
    {"key": "set_up_pembayaran", "header": "Set Up Pembayaran"},
    {"key": "catatan_tambahan", "header": "Catatan Tambahan"},
    {"key": "konfirmasi_pekerjaan_tambahan", "header": "Konfirmasi Pekerjaan Tambahan"},
    {"key": "no_buku_claim_c2", "header": "No Buku Claim C2"},
    {"key": "no_work_order_job_return", "header": "No Work Order Job Return"},
    {"key": "total_biaya_service", "header": "Total Biaya Service"},
    {"key": "waktu_pekerjaan", "header": "Waktu Pekerjaan"},
    {"key": "status_work_order", "header": "Status Work Order"},
    {"key": "created_time", "header": "Created Time"},
    {"key": "modified_time", "header": "Modified Time"}
]

NJB_NSC_COLUMNS = [
    {"key": "no", "header": "No"},
    {"key": "no_work_order", "header": "No. Work Order"},
    {"key": "no_njb", "header": "No. NJB"},
    {"key": "tanggal_njb", "header": "Tgl NJB"},
    {"key": "total_harga_njb", "header": "Total Harga NJB"},
    {"key": "no_nsc", "header": "No. NSC"},
    {"key": "tanggal_nsc", "header": "Tgl NSC"},
    {"key": "total_harga_nsc", "header": "Total Harga NSC"},
    {"key": "honda_id_sa", "header": "Honda ID SA"},
    {"key": "honda_id_mekanik", "header": "Honda ID Mekanik"},
    {"key": "created_time", "header": "Created Time"},
    {"key": "modified_time", "header": "Modified Time"}
]

HLO_COLUMNS = [
    {"key": "no", "header": "No"},
    {"key": "id_hlo_document", "header": "ID HLO Document"},
    {"key": "no_invoice_uang_jaminan", "header": "No Invoice Uang Jaminan"},
    {"key": "tanggal_pemesanan_hlo", "header": "Tgl Pemesanan HLO"},
    {"key": "no_work_order", "header": "No Work Order"},
    {"key": "id_customer", "header": "ID Customer"},
    {"key": "parts_number", "header": "Part Number"},
    {"key": "kuantitas", "header": "Kuantitas Part"},
    {"key": "harga_parts", "header": "Harga Parts"},
    {"key": "total_harga_parts", "header": "Total Harga Parts"},
    {"key": "uang_muka", "header": "Uang Muka"},
    {"key": "sisa_bayar", "header": "Sisa Bayar"},
    {"key": "created_time", "header": "Created Time"},
    {"key": "modified_time", "header": "Modified Time"}
]