"""
Dashboard schemas for API responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class UnitInboundStatusItem(BaseModel):
    """Individual status item for unit inbound data"""
    status_shipping_list: Optional[str] = Field(None, description="Original status of shipping list")
    status_label: Optional[str] = Field(None, description="Human-readable status label in Indonesian")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class UnitInboundStatusResponse(BaseModel):
    """Response schema for unit inbound status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[UnitInboundStatusItem] = Field(..., description="List of status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class PaymentTypeItem(BaseModel):
    """Individual payment type item for billing process data"""
    tipe_pembayaran: Optional[str] = Field(None, description="Payment type (CASH, CREDIT, etc.)")
    count: int = Field(..., description="Number of records with this payment type")
    total_amount: Optional[Decimal] = Field(None, description="Total amount for this payment type")

    class Config:
        from_attributes = True


class PaymentTypeResponse(BaseModel):
    """Response schema for payment type statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[PaymentTypeItem] = Field(..., description="List of payment type counts and amounts")
    total_records: int = Field(..., description="Total number of records")
    total_amount: Optional[Decimal] = Field(None, description="Grand total amount across all payment types")

    class Config:
        from_attributes = True


class DeliveryProcessStatusItem(BaseModel):
    """Individual status item for delivery process data"""
    status_delivery_document: Optional[str] = Field(None, description="Original status of delivery document")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class DeliveryProcessStatusResponse(BaseModel):
    """Response schema for delivery process status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[DeliveryProcessStatusItem] = Field(..., description="List of delivery status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class ProspectFollowUpItem(BaseModel):
    """Individual follow-up status item for prospect data"""
    status_follow_up_prospecting: Optional[str] = Field(None, description="Original status follow up prospecting code")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class ProspectFollowUpResponse(BaseModel):
    """Response schema for prospect follow-up status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[ProspectFollowUpItem] = Field(..., description="List of prospect follow-up status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class SPKStatusItem(BaseModel):
    """Individual status item for SPK dealing process data"""
    status_spk: Optional[str] = Field(None, description="Original SPK status code")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class SPKStatusResponse(BaseModel):
    """Response schema for SPK status statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[SPKStatusItem] = Field(..., description="List of SPK status counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class TopLeasingItem(BaseModel):
    """Individual leasing company item for top leasing data"""
    nama_finance_company: Optional[str] = Field(None, description="Finance company name")
    count: int = Field(..., description="Number of PO records for this finance company")

    class Config:
        from_attributes = True


class TopLeasingResponse(BaseModel):
    """Response schema for top leasing company statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[TopLeasingItem] = Field(..., description="List of top leasing companies")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class DocumentHandlingCountResponse(BaseModel):
    """Response schema for document handling count statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    count: int = Field(..., description="Count of SPK records matching criteria")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class StatusProspectItem(BaseModel):
    """Individual status item for prospect data grouped by status_prospect"""
    status_prospect: Optional[str] = Field(None, description="Original status prospect code")
    status_label: Optional[str] = Field(None, description="Human-readable status label")
    count: int = Field(..., description="Number of records with this status")

    class Config:
        from_attributes = True


class StatusProspectResponse(BaseModel):
    """Response schema for status prospect statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[StatusProspectItem] = Field(..., description="List of status prospect counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class MetodeFollowUpItem(BaseModel):
    """Individual metode item for prospect data grouped by metode_follow_up"""
    metode_follow_up: Optional[str] = Field(None, description="Original metode follow up code")
    metode_label: Optional[str] = Field(None, description="Human-readable metode label")
    count: int = Field(..., description="Number of records with this metode")

    class Config:
        from_attributes = True


class MetodeFollowUpResponse(BaseModel):
    """Response schema for metode follow up statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[MetodeFollowUpItem] = Field(..., description="List of metode follow up counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class SumberProspectItem(BaseModel):
    """Individual sumber item for prospect data grouped by sumber_prospect"""
    sumber_prospect: Optional[str] = Field(None, description="Original sumber prospect code")
    sumber_label: Optional[str] = Field(None, description="Human-readable sumber label")
    count: int = Field(..., description="Number of records with this sumber")

    class Config:
        from_attributes = True


class SumberProspectResponse(BaseModel):
    """Response schema for top sumber prospect statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[SumberProspectItem] = Field(..., description="List of top 5 sumber prospect counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class SebaranProspectItem(BaseModel):
    """Individual kecamatan item for prospect data grouped by kode_kecamatan"""
    kode_kecamatan: Optional[str] = Field(None, description="Kode kecamatan")
    nama_kecamatan: Optional[str] = Field(None, description="Nama kecamatan")
    count: int = Field(..., description="Number of prospect records in this kecamatan")
    latitude: Optional[str] = Field(None, description="Latitude coordinate for mapping")
    longitude: Optional[str] = Field(None, description="Longitude coordinate for mapping")

    class Config:
        from_attributes = True


class SebaranProspectResponse(BaseModel):
    """Response schema for sebaran prospect by kecamatan statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[SebaranProspectItem] = Field(..., description="List of top 5 kecamatan prospect counts")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class ProspectDataTableItem(BaseModel):
    """Individual prospect data item for table display"""
    id_prospect: Optional[str] = Field(None, description="Prospect ID")
    nama_lengkap: Optional[str] = Field(None, description="Full name of prospect")
    alamat: Optional[str] = Field(None, description="Address")
    no_kontak: Optional[str] = Field(None, description="Contact number")
    tanggal_prospect: Optional[str] = Field(None, description="Prospect date")
    status_prospect: Optional[str] = Field(None, description="Prospect status")
    sumber_prospect: Optional[str] = Field(None, description="Prospect source")
    tanggal_appointment: Optional[str] = Field(None, description="Appointment date")
    no_ktp: Optional[str] = Field(None, description="KTP number")
    kode_kecamatan: Optional[str] = Field(None, description="Kecamatan code")
    metode_follow_up: Optional[str] = Field(None, description="Follow up method")

    class Config:
        from_attributes = True


class ProspectDataTableRequest(BaseModel):
    """Request schema for prospect data table with filters"""
    dealer_id: str = Field(..., description="Dealer ID to filter by")
    date_from: str = Field(..., description="Start date in YYYY-MM-DD format")
    date_to: str = Field(..., description="End date in YYYY-MM-DD format")
    page: int = Field(1, description="Page number (1-based)")
    per_page: int = Field(20, description="Number of records per page")
    id_prospect: Optional[str] = Field(None, description="Filter by prospect ID")
    nama_lengkap: Optional[str] = Field(None, description="Filter by name (partial match)")
    alamat: Optional[str] = Field(None, description="Filter by address (partial match)")
    no_kontak: Optional[str] = Field(None, description="Filter by contact number")
    tanggal_prospect: Optional[str] = Field(None, description="Filter by prospect date (YYYY-MM-DD)")
    status_prospect: Optional[str] = Field(None, description="Filter by prospect status")

    class Config:
        from_attributes = True


class ProspectDataTableResponse(BaseModel):
    """Response schema for prospect data table with pagination"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[ProspectDataTableItem] = Field(..., description="List of prospect data records")
    total_records: int = Field(..., description="Total number of records matching filters")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")

    class Config:
        from_attributes = True


class TopDealingUnitItem(BaseModel):
    """Individual unit type item for top dealing units"""
    kode_tipe_unit: Optional[str] = Field(None, description="Unit type code")
    nama_unit: Optional[str] = Field(None, description="Unit name/label")
    total_quantity: int = Field(..., description="Total quantity of units sold")

    class Config:
        from_attributes = True


class TopDealingUnitsResponse(BaseModel):
    """Response schema for top dealing units statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[TopDealingUnitItem] = Field(..., description="List of top 3 dealing units by quantity")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class RevenueResponse(BaseModel):
    """Response schema for revenue statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    total_revenue: Optional[float] = Field(None, description="Total revenue from harga_jual sum")
    total_records: int = Field(..., description="Total number of records contributing to revenue")

    class Config:
        from_attributes = True


class TopDriverItem(BaseModel):
    """Individual driver item for top driver statistics"""
    id_driver: Optional[str] = Field(None, description="Driver ID")
    nama_driver: Optional[str] = Field(None, description="Driver name (if available)")
    total_deliveries: int = Field(..., description="Total number of SPK deliveries by this driver")

    class Config:
        from_attributes = True


class TopDriverResponse(BaseModel):
    """Response schema for top driver statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[TopDriverItem] = Field(..., description="List of top 5 drivers by delivery count")
    total_records: int = Field(..., description="Total number of records")

    class Config:
        from_attributes = True


class DeliveryLocationItem(BaseModel):
    """Individual location item for delivery location statistics"""
    lokasi_pengiriman: Optional[str] = Field(None, description="Delivery location")
    location_name: Optional[str] = Field(None, description="Cleaned location name")
    delivery_count: int = Field(..., description="Number of deliveries to this location")
    percentage: Optional[float] = Field(None, description="Percentage of total deliveries")

    class Config:
        from_attributes = True


class DeliveryLocationResponse(BaseModel):
    """Response schema for delivery location statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[DeliveryLocationItem] = Field(..., description="List of top 5 delivery locations by count")
    total_records: int = Field(..., description="Total number of delivery records")

    class Config:
        from_attributes = True


class DeliveryDataHistoryItem(BaseModel):
    """Individual delivery data item for history table"""
    delivery_document_id: Optional[str] = Field(None, description="Delivery document ID")
    tanggal_pengiriman: Optional[str] = Field(None, description="Delivery date")
    status_delivery_document: Optional[str] = Field(None, description="Delivery status")
    id_driver: Optional[str] = Field(None, description="Driver ID")
    id_spk: Optional[str] = Field(None, description="SPK ID")
    nama_penerima: Optional[str] = Field(None, description="Recipient name")
    no_kontak_penerima: Optional[str] = Field(None, description="Recipient contact number")
    lokasi_pengiriman: Optional[str] = Field(None, description="Delivery location")
    waktu_pengiriman: Optional[str] = Field(None, description="Delivery time")

    class Config:
        from_attributes = True


class DeliveryDataHistoryResponse(BaseModel):
    """Response schema for delivery data history with pagination"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[DeliveryDataHistoryItem] = Field(..., description="List of delivery data records")
    total_records: int = Field(..., description="Total number of records matching filters")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")

    class Config:
        from_attributes = True


class SPKDealingProcessDataItem(BaseModel):
    """Individual SPK dealing process data item for table display"""
    id_spk: Optional[str] = Field(None, description="SPK ID")
    nama_customer: Optional[str] = Field(None, description="Customer name")
    alamat: Optional[str] = Field(None, description="Customer address")
    no_kontak: Optional[str] = Field(None, description="Contact number")
    email: Optional[str] = Field(None, description="Email address")
    status_spk: Optional[str] = Field(None, description="SPK status")
    nama_bpkb: Optional[str] = Field(None, description="BPKB name")
    id_prospect: Optional[str] = Field(None, description="Prospect ID")
    no_ktp: Optional[str] = Field(None, description="KTP number")
    kode_propinsi: Optional[str] = Field(None, description="Province code")
    kode_kota: Optional[str] = Field(None, description="City code")
    kode_kecamatan: Optional[str] = Field(None, description="District code")
    kode_kelurahan: Optional[str] = Field(None, description="Village code")
    kode_pos: Optional[str] = Field(None, description="Postal code")
    no_ktp_bpkb: Optional[str] = Field(None, description="BPKB KTP number")
    alamat_bpkb: Optional[str] = Field(None, description="BPKB address")
    latitude: Optional[str] = Field(None, description="Latitude")
    longitude: Optional[str] = Field(None, description="Longitude")
    npwp: Optional[str] = Field(None, description="NPWP number")
    no_kk: Optional[str] = Field(None, description="KK number")
    alamat_kk: Optional[str] = Field(None, description="KK address")
    fax: Optional[str] = Field(None, description="Fax number")
    id_sales_people: Optional[str] = Field(None, description="Sales person ID")
    id_event: Optional[str] = Field(None, description="Event ID")
    tanggal_pesanan: Optional[str] = Field(None, description="Order date")
    created_time: Optional[str] = Field(None, description="Created time")
    modified_time: Optional[str] = Field(None, description="Modified time")

    class Config:
        from_attributes = True


class SPKDealingProcessDataResponse(BaseModel):
    """Response schema for SPK dealing process data with pagination"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Data retrieved successfully", description="Response message")
    data: List[SPKDealingProcessDataItem] = Field(..., description="List of SPK dealing process data records")
    total_records: int = Field(..., description="Total number of records matching filters")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")

    class Config:
        from_attributes = True
