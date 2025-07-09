-- Initialize database with dealer_integration schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create dealer_integration schema (remove existing data if any)
DROP SCHEMA IF EXISTS dealer_integration CASCADE;
CREATE SCHEMA dealer_integration;

-- Set search path to use dealer_integration schema
SET search_path TO dealer_integration, public;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Dealers table
CREATE TABLE dealers (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    dealer_name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) NULL,
    api_token VARCHAR(255) NULL,
    is_active BOOLEAN NULL DEFAULT true,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    secret_key VARCHAR(255) NULL,
    CONSTRAINT dealers_dealer_id_key UNIQUE (dealer_id),
    CONSTRAINT dealers_pkey PRIMARY KEY (id)
);

-- API Configurations table
CREATE TABLE api_configurations (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    config_name VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    description TEXT NULL,
    is_active BOOLEAN NULL DEFAULT true,
    timeout_seconds INTEGER NULL DEFAULT 30,
    retry_attempts INTEGER NULL DEFAULT 3,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT api_configurations_config_name_key UNIQUE (config_name),
    CONSTRAINT api_configurations_pkey PRIMARY KEY (id)
);

-- Data fetch configurations
CREATE TABLE fetch_configurations (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    schedule_type VARCHAR(20) NOT NULL CHECK (schedule_type IN ('hourly', 'daily', 'custom')),
    cron_expression VARCHAR(100) NULL,
    is_active BOOLEAN NULL DEFAULT true,
    last_fetch_at TIMESTAMP NULL,
    next_fetch_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fetch_configurations_pkey PRIMARY KEY (id),
    CONSTRAINT fetch_configurations_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Fetch logs table
CREATE TABLE fetch_logs (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    fetch_type VARCHAR(50) NULL,
    status VARCHAR(20) NULL CHECK (status IN ('success', 'failed', 'partial')),
    records_fetched INTEGER NULL DEFAULT 0,
    error_message TEXT NULL,
    fetch_duration_seconds INTEGER NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fetch_logs_pkey PRIMARY KEY (id),
    CONSTRAINT fetch_logs_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- ============================================================================
-- PROSPECT DATA TABLES
-- ============================================================================

-- Prospect data table
CREATE TABLE prospect_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    id_prospect VARCHAR(255) NULL,
    sumber_prospect VARCHAR(10) NULL,
    tanggal_prospect DATE NULL,
    tagging_prospect VARCHAR(10) NULL,
    nama_lengkap VARCHAR(255) NULL,
    no_kontak VARCHAR(50) NULL,
    no_ktp VARCHAR(50) NULL,
    alamat TEXT NULL,
    kode_propinsi VARCHAR(10) NULL,
    kode_kota VARCHAR(10) NULL,
    kode_kecamatan VARCHAR(10) NULL,
    kode_kelurahan VARCHAR(10) NULL,
    kode_pos VARCHAR(10) NULL,
    latitude VARCHAR(20) NULL,
    longitude VARCHAR(20) NULL,
    alamat_kantor TEXT NULL,
    kode_propinsi_kantor VARCHAR(10) NULL,
    kode_kota_kantor VARCHAR(10) NULL,
    kode_kecamatan_kantor VARCHAR(10) NULL,
    kode_kelurahan_kantor VARCHAR(10) NULL,
    kode_pos_kantor VARCHAR(10) NULL,
    kode_pekerjaan VARCHAR(10) NULL,
    no_kontak_kantor VARCHAR(50) NULL,
    tanggal_appointment DATE NULL,
    waktu_appointment TIME NULL,
    metode_follow_up VARCHAR(10) NULL,
    test_ride_preference VARCHAR(10) NULL,
    status_follow_up_prospecting VARCHAR(10) NULL,
    status_prospect VARCHAR(10) NULL,
    id_sales_people VARCHAR(50) NULL,
    id_event VARCHAR(100) NULL,
    created_time TIMESTAMP NULL,
    modified_time TIMESTAMP NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT prospect_data_pkey PRIMARY KEY (id),
    CONSTRAINT prospect_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id),
    CONSTRAINT prospect_data_dealer_id_id_prospect_key UNIQUE (dealer_id, id_prospect)
);

-- Prospect units table
CREATE TABLE prospect_units (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    prospect_data_id UUID NOT NULL,
    kode_tipe_unit VARCHAR(20) NULL,
    sales_program_id TEXT NULL,
    created_time TIMESTAMP NULL,
    modified_time TIMESTAMP NULL,
    CONSTRAINT prospect_units_pkey PRIMARY KEY (id),
    CONSTRAINT prospect_units_prospect_data_id_fkey FOREIGN KEY (prospect_data_id) REFERENCES prospect_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- PKB (SERVICE RECORD) DATA TABLES
-- ============================================================================

-- PKB data table
CREATE TABLE pkb_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_work_order VARCHAR(100) NOT NULL,
    no_sa_form VARCHAR(100) NULL,
    tanggal_servis VARCHAR(20) NULL,
    waktu_pkb VARCHAR(50) NULL,
    no_polisi VARCHAR(20) NULL,
    no_rangka VARCHAR(50) NULL,
    no_mesin VARCHAR(50) NULL,
    kode_tipe_unit VARCHAR(20) NULL,
    tahun_motor VARCHAR(10) NULL,
    informasi_bensin VARCHAR(10) NULL,
    km_terakhir INTEGER NULL,
    tipe_coming_customer VARCHAR(10) NULL,
    nama_pemilik VARCHAR(255) NULL,
    alamat_pemilik TEXT NULL,
    kode_propinsi_pemilik VARCHAR(10) NULL,
    kode_kota_pemilik VARCHAR(10) NULL,
    kode_kecamatan_pemilik VARCHAR(10) NULL,
    kode_kelurahan_pemilik VARCHAR(20) NULL,
    kode_pos_pemilik VARCHAR(10) NULL,
    alamat_pembawa TEXT NULL,
    kode_propinsi_pembawa VARCHAR(10) NULL,
    kode_kota_pembawa VARCHAR(10) NULL,
    kode_kecamatan_pembawa VARCHAR(10) NULL,
    kode_kelurahan_pembawa VARCHAR(20) NULL,
    kode_pos_pembawa VARCHAR(10) NULL,
    nama_pembawa VARCHAR(255) NULL,
    no_telp_pembawa VARCHAR(50) NULL,
    hubungan_dengan_pemilik VARCHAR(10) NULL,
    keluhan_konsumen TEXT NULL,
    rekomendasi_sa TEXT NULL,
    honda_id_sa VARCHAR(50) NULL,
    honda_id_mekanik VARCHAR(50) NULL,
    saran_mekanik TEXT NULL,
    asal_unit_entry VARCHAR(10) NULL,
    id_pit VARCHAR(20) NULL,
    jenis_pit VARCHAR(10) NULL,
    waktu_pendaftaran VARCHAR(50) NULL,
    waktu_selesai VARCHAR(50) NULL,
    total_frt VARCHAR(20) NULL,
    set_up_pembayaran VARCHAR(10) NULL,
    catatan_tambahan TEXT NULL,
    konfirmasi_pekerjaan_tambahan VARCHAR(10) NULL,
    no_buku_claim_c2 VARCHAR(50) NULL,
    no_work_order_job_return VARCHAR(100) NULL,
    total_biaya_service REAL NULL,
    waktu_pekerjaan VARCHAR(20) NULL,
    status_work_order VARCHAR(10) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pkb_data_pkey PRIMARY KEY (id),
    CONSTRAINT pkb_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- PKB services table
CREATE TABLE pkb_services (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    pkb_data_id UUID NOT NULL,
    id_job VARCHAR(50) NULL,
    nama_pekerjaan VARCHAR(255) NULL,
    jenis_pekerjaan VARCHAR(100) NULL,
    biaya_service REAL NULL,
    promo_id_jasa VARCHAR(50) NULL,
    disc_service_amount REAL NULL,
    disc_service_percentage REAL NULL,
    total_harga_servis REAL NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT pkb_services_pkey PRIMARY KEY (id),
    CONSTRAINT pkb_services_pkb_data_id_fkey FOREIGN KEY (pkb_data_id) REFERENCES pkb_data(id) ON DELETE CASCADE
);

-- PKB parts table
CREATE TABLE pkb_parts (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    pkb_data_id UUID NOT NULL,
    id_job VARCHAR(50) NULL,
    parts_number VARCHAR(100) NULL,
    harga_parts REAL NULL,
    promo_id_parts VARCHAR(50) NULL,
    disc_parts_amount REAL NULL,
    disc_parts_percentage REAL NULL,
    ppn REAL NULL,
    total_harga_parts REAL NULL,
    uang_muka REAL NULL,
    kuantitas INTEGER NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT pkb_parts_pkey PRIMARY KEY (id),
    CONSTRAINT pkb_parts_pkb_data_id_fkey FOREIGN KEY (pkb_data_id) REFERENCES pkb_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- PARTS INBOUND DATA TABLES
-- ============================================================================

-- Parts inbound data table
CREATE TABLE parts_inbound_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_penerimaan VARCHAR(100) NOT NULL,
    tgl_penerimaan VARCHAR(20) NULL,
    no_shipping_list VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT parts_inbound_data_pkey PRIMARY KEY (id),
    CONSTRAINT parts_inbound_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Parts inbound PO table
CREATE TABLE parts_inbound_po (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    parts_inbound_data_id UUID NOT NULL,
    no_po VARCHAR(100) NULL,
    jenis_order VARCHAR(10) NULL,
    id_warehouse VARCHAR(50) NULL,
    parts_number VARCHAR(100) NULL,
    kuantitas INTEGER NULL,
    uom VARCHAR(20) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT parts_inbound_po_pkey PRIMARY KEY (id),
    CONSTRAINT parts_inbound_po_parts_inbound_data_id_fkey FOREIGN KEY (parts_inbound_data_id) REFERENCES parts_inbound_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- LEASING DATA TABLE
-- ============================================================================

-- Leasing data table
CREATE TABLE leasing_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    id_dokumen_pengajuan VARCHAR(100) NULL,
    id_spk VARCHAR(100) NULL,
    jumlah_dp NUMERIC(15,2) NULL,
    tenor INTEGER NULL,
    jumlah_cicilan NUMERIC(15,2) NULL,
    tanggal_pengajuan VARCHAR(50) NULL,
    id_finance_company VARCHAR(100) NULL,
    nama_finance_company VARCHAR(255) NULL,
    id_po_finance_company VARCHAR(100) NULL,
    tanggal_pembuatan_po VARCHAR(50) NULL,
    tanggal_pengiriman_po_finance_company VARCHAR(50) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT leasing_data_pkey PRIMARY KEY (id),
    CONSTRAINT leasing_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- ============================================================================
-- DOCUMENT HANDLING DATA TABLES
-- ============================================================================

-- Document handling data table
CREATE TABLE document_handling_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    id_so VARCHAR(100) NULL,
    id_spk VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT document_handling_data_pkey PRIMARY KEY (id),
    CONSTRAINT document_handling_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Document handling units table
CREATE TABLE document_handling_units (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    document_handling_data_id UUID NOT NULL,
    nomor_rangka VARCHAR(100) NULL,
    nomor_faktur_stnk VARCHAR(100) NULL,
    tanggal_pengajuan_stnk_ke_biro VARCHAR(50) NULL,
    status_faktur_stnk VARCHAR(10) NULL,
    nomor_stnk VARCHAR(100) NULL,
    tanggal_penerimaan_stnk_dari_biro VARCHAR(50) NULL,
    plat_nomor VARCHAR(50) NULL,
    nomor_bpkb VARCHAR(100) NULL,
    tanggal_penerimaan_bpkb_dari_biro VARCHAR(50) NULL,
    tanggal_terima_stnk_oleh_konsumen VARCHAR(50) NULL,
    tanggal_terima_bpkb_oleh_konsumen VARCHAR(50) NULL,
    nama_penerima_bpkb VARCHAR(255) NULL,
    nama_penerima_stnk VARCHAR(255) NULL,
    jenis_id_penerima_bpkb VARCHAR(10) NULL,
    jenis_id_penerima_stnk VARCHAR(10) NULL,
    no_id_penerima_bpkb VARCHAR(100) NULL,
    no_id_penerima_stnk VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT document_handling_units_pkey PRIMARY KEY (id),
    CONSTRAINT document_handling_units_document_handling_data_id_fkey FOREIGN KEY (document_handling_data_id) REFERENCES document_handling_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- UNIT INBOUND DATA TABLES
-- ============================================================================

-- Unit inbound data table
CREATE TABLE unit_inbound_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_shipping_list VARCHAR(100) NULL,
    tanggal_terima VARCHAR(50) NULL,
    main_dealer_id VARCHAR(10) NULL,
    no_invoice VARCHAR(100) NULL,
    status_shipping_list VARCHAR(10) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unit_inbound_data_pkey PRIMARY KEY (id),
    CONSTRAINT unit_inbound_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Unit inbound units table
CREATE TABLE unit_inbound_units (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    unit_inbound_data_id UUID NOT NULL,
    kode_tipe_unit VARCHAR(50) NULL,
    kode_warna VARCHAR(10) NULL,
    kuantitas_terkirim INTEGER NULL,
    kuantitas_diterima INTEGER NULL,
    no_mesin VARCHAR(100) NULL,
    no_rangka VARCHAR(100) NULL,
    status_rfs VARCHAR(10) NULL,
    po_id VARCHAR(100) NULL,
    kelengkapan_unit TEXT NULL,
    no_goods_receipt VARCHAR(100) NULL,
    doc_nrfs_id VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT unit_inbound_units_pkey PRIMARY KEY (id),
    CONSTRAINT unit_inbound_units_unit_inbound_data_id_fkey FOREIGN KEY (unit_inbound_data_id) REFERENCES unit_inbound_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- DELIVERY PROCESS DATA TABLES
-- ============================================================================

-- Delivery process data table
CREATE TABLE delivery_process_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    delivery_document_id VARCHAR(100) NULL,
    tanggal_pengiriman VARCHAR(50) NULL,
    id_driver VARCHAR(100) NULL,
    status_delivery_document VARCHAR(10) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT delivery_process_data_pkey PRIMARY KEY (id),
    CONSTRAINT delivery_process_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Delivery process details table
CREATE TABLE delivery_process_details (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    delivery_process_data_id UUID NOT NULL,
    no_so VARCHAR(100) NULL,
    id_spk VARCHAR(100) NULL,
    no_mesin VARCHAR(100) NULL,
    no_rangka VARCHAR(100) NULL,
    id_customer VARCHAR(100) NULL,
    waktu_pengiriman VARCHAR(50) NULL,
    checklist_kelengkapan TEXT NULL,
    lokasi_pengiriman TEXT NULL,
    latitude VARCHAR(50) NULL,
    longitude VARCHAR(50) NULL,
    nama_penerima VARCHAR(200) NULL,
    no_kontak_penerima VARCHAR(50) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT delivery_process_details_pkey PRIMARY KEY (id),
    CONSTRAINT delivery_process_details_delivery_process_data_id_fkey FOREIGN KEY (delivery_process_data_id) REFERENCES delivery_process_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- BILLING PROCESS DATA TABLE
-- ============================================================================

-- Billing process data table
CREATE TABLE billing_process_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    id_invoice VARCHAR(100) NULL,
    id_spk VARCHAR(100) NULL,
    id_customer VARCHAR(100) NULL,
    amount NUMERIC(15,2) NULL,
    tipe_pembayaran VARCHAR(10) NULL,
    cara_bayar VARCHAR(10) NULL,
    status VARCHAR(10) NULL,
    note TEXT NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT billing_process_data_pkey PRIMARY KEY (id),
    CONSTRAINT billing_process_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- ============================================================================
-- UNIT INVOICE DATA TABLES
-- ============================================================================

-- Unit invoice data table
CREATE TABLE unit_invoice_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_invoice VARCHAR(100) NULL,
    tanggal_invoice VARCHAR(50) NULL,
    tanggal_jatuh_tempo VARCHAR(50) NULL,
    main_dealer_id VARCHAR(10) NULL,
    total_harga_sebelum_diskon NUMERIC(15,2) NULL,
    total_diskon_per_unit NUMERIC(15,2) NULL,
    potongan_per_invoice NUMERIC(15,2) NULL,
    total_ppn NUMERIC(15,2) NULL,
    total_harga NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unit_invoice_data_pkey PRIMARY KEY (id),
    CONSTRAINT unit_invoice_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Unit invoice units table
CREATE TABLE unit_invoice_units (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    unit_invoice_data_id UUID NOT NULL,
    kode_tipe_unit VARCHAR(50) NULL,
    kode_warna VARCHAR(10) NULL,
    kuantitas INTEGER NULL,
    no_mesin VARCHAR(100) NULL,
    no_rangka VARCHAR(100) NULL,
    harga_satuan_sebelum_diskon NUMERIC(15,2) NULL,
    diskon_per_unit NUMERIC(15,2) NULL,
    po_id VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT unit_invoice_units_pkey PRIMARY KEY (id),
    CONSTRAINT unit_invoice_units_unit_invoice_data_id_fkey FOREIGN KEY (unit_invoice_data_id) REFERENCES unit_invoice_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- PARTS SALES DATA TABLES
-- ============================================================================

-- Parts sales data table
CREATE TABLE parts_sales_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_so VARCHAR(100) NULL,
    tgl_so VARCHAR(50) NULL,
    id_customer VARCHAR(100) NULL,
    nama_customer VARCHAR(200) NULL,
    disc_so NUMERIC(15,2) NULL,
    total_harga_so NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT parts_sales_data_pkey PRIMARY KEY (id),
    CONSTRAINT parts_sales_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Parts sales parts table
CREATE TABLE parts_sales_parts (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    parts_sales_data_id UUID NOT NULL,
    parts_number VARCHAR(100) NULL,
    kuantitas INTEGER NULL,
    harga_parts NUMERIC(15,2) NULL,
    promo_id_parts VARCHAR(100) NULL,
    disc_amount NUMERIC(15,2) NULL,
    disc_percentage VARCHAR(20) NULL,
    ppn NUMERIC(15,2) NULL,
    total_harga_parts NUMERIC(15,2) NULL,
    uang_muka NUMERIC(15,2) NULL,
    booking_id_reference VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT parts_sales_parts_pkey PRIMARY KEY (id),
    CONSTRAINT parts_sales_parts_parts_sales_data_id_fkey FOREIGN KEY (parts_sales_data_id) REFERENCES parts_sales_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- DP HLO DATA TABLES
-- ============================================================================

-- DP HLO data table
CREATE TABLE dp_hlo_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_invoice_uang_jaminan VARCHAR(100) NULL,
    id_hlo_document VARCHAR(100) NULL,
    tanggal_pemesanan_hlo VARCHAR(50) NULL,
    no_work_order VARCHAR(100) NULL,
    id_customer VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dp_hlo_data_pkey PRIMARY KEY (id),
    CONSTRAINT dp_hlo_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- DP HLO parts table
CREATE TABLE dp_hlo_parts (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dp_hlo_data_id UUID NOT NULL,
    parts_number VARCHAR(100) NULL,
    kuantitas INTEGER NULL,
    harga_parts NUMERIC(15,2) NULL,
    total_harga_parts NUMERIC(15,2) NULL,
    uang_muka NUMERIC(15,2) NULL,
    sisa_bayar NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT dp_hlo_parts_pkey PRIMARY KEY (id),
    CONSTRAINT dp_hlo_parts_dp_hlo_data_id_fkey FOREIGN KEY (dp_hlo_data_id) REFERENCES dp_hlo_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- WORKSHOP INVOICE DATA TABLES (INV2 - NJB & NSC)
-- ============================================================================

-- Workshop invoice data table
CREATE TABLE workshop_invoice_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_work_order VARCHAR(100) NULL,
    no_njb VARCHAR(100) NULL,
    tanggal_njb VARCHAR(50) NULL,
    total_harga_njb NUMERIC(15,2) NULL,
    no_nsc VARCHAR(100) NULL,
    tanggal_nsc VARCHAR(50) NULL,
    total_harga_nsc NUMERIC(15,2) NULL,
    honda_id_sa VARCHAR(100) NULL,
    honda_id_mekanik VARCHAR(100) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT workshop_invoice_data_pkey PRIMARY KEY (id),
    CONSTRAINT workshop_invoice_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Workshop invoice NJB (services) table
CREATE TABLE workshop_invoice_njb (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    workshop_invoice_data_id UUID NOT NULL,
    id_job VARCHAR(100) NULL,
    harga_servis NUMERIC(15,2) NULL,
    promo_id_jasa VARCHAR(100) NULL,
    disc_service_amount NUMERIC(15,2) NULL,
    disc_service_percentage VARCHAR(20) NULL,
    total_harga_servis NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT workshop_invoice_njb_pkey PRIMARY KEY (id),
    CONSTRAINT workshop_invoice_njb_workshop_invoice_data_id_fkey FOREIGN KEY (workshop_invoice_data_id) REFERENCES workshop_invoice_data(id) ON DELETE CASCADE
);

-- Workshop invoice NSC (parts) table
CREATE TABLE workshop_invoice_nsc (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    workshop_invoice_data_id UUID NOT NULL,
    id_job VARCHAR(100) NULL,
    parts_number VARCHAR(100) NULL,
    kuantitas INTEGER NULL,
    harga_parts NUMERIC(15,2) NULL,
    promo_id_parts VARCHAR(100) NULL,
    disc_parts_amount NUMERIC(15,2) NULL,
    disc_parts_percentage VARCHAR(20) NULL,
    ppn NUMERIC(15,2) NULL,
    total_harga_parts NUMERIC(15,2) NULL,
    uang_muka NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT workshop_invoice_nsc_pkey PRIMARY KEY (id),
    CONSTRAINT workshop_invoice_nsc_workshop_invoice_data_id_fkey FOREIGN KEY (workshop_invoice_data_id) REFERENCES workshop_invoice_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- UNPAID HLO DATA TABLES
-- ============================================================================

-- Unpaid HLO data table
CREATE TABLE unpaid_hlo_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    id_hlo_document VARCHAR(100) NULL,
    tanggal_pemesanan_hlo VARCHAR(50) NULL,
    no_work_order VARCHAR(100) NULL,
    no_buku_claim_c2 VARCHAR(100) NULL,
    no_ktp VARCHAR(100) NULL,
    nama_customer VARCHAR(200) NULL,
    alamat TEXT NULL,
    kode_propinsi VARCHAR(10) NULL,
    kode_kota VARCHAR(10) NULL,
    kode_kecamatan VARCHAR(20) NULL,
    kode_kelurahan VARCHAR(20) NULL,
    kode_pos VARCHAR(10) NULL,
    no_kontak VARCHAR(50) NULL,
    kode_tipe_unit VARCHAR(50) NULL,
    tahun_motor VARCHAR(10) NULL,
    no_mesin VARCHAR(100) NULL,
    no_rangka VARCHAR(100) NULL,
    flag_numbering VARCHAR(10) NULL,
    vehicle_off_road VARCHAR(10) NULL,
    job_return VARCHAR(10) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unpaid_hlo_data_pkey PRIMARY KEY (id),
    CONSTRAINT unpaid_hlo_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Unpaid HLO parts table
CREATE TABLE unpaid_hlo_parts (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    unpaid_hlo_data_id UUID NOT NULL,
    parts_number VARCHAR(100) NULL,
    kuantitas INTEGER NULL,
    harga_parts NUMERIC(15,2) NULL,
    total_harga_parts NUMERIC(15,2) NULL,
    uang_muka NUMERIC(15,2) NULL,
    sisa_bayar NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT unpaid_hlo_parts_pkey PRIMARY KEY (id),
    CONSTRAINT unpaid_hlo_parts_unpaid_hlo_data_id_fkey FOREIGN KEY (unpaid_hlo_data_id) REFERENCES unpaid_hlo_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- PARTS INVOICE DATA TABLES (MDINVH3)
-- ============================================================================

-- Parts invoice data table
CREATE TABLE parts_invoice_data (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) NOT NULL,
    no_invoice VARCHAR(100) NULL,
    tgl_invoice VARCHAR(50) NULL,
    tgl_jatuh_tempo VARCHAR(50) NULL,
    main_dealer_id VARCHAR(10) NULL,
    total_harga_sebelum_diskon NUMERIC(15,2) NULL,
    total_diskon_per_parts_number NUMERIC(15,2) NULL,
    potongan_per_invoice NUMERIC(15,2) NULL,
    total_ppn NUMERIC(15,2) NULL,
    total_harga NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    fetched_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT parts_invoice_data_pkey PRIMARY KEY (id),
    CONSTRAINT parts_invoice_data_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

-- Parts invoice parts table
CREATE TABLE parts_invoice_parts (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    parts_invoice_data_id UUID NOT NULL,
    no_po VARCHAR(100) NULL,
    jenis_order VARCHAR(10) NULL,
    parts_number VARCHAR(100) NULL,
    kuantitas INTEGER NULL,
    uom VARCHAR(20) NULL,
    harga_satuan_sebelum_diskon NUMERIC(15,2) NULL,
    diskon_per_parts_number NUMERIC(15,2) NULL,
    created_time VARCHAR(50) NULL,
    modified_time VARCHAR(50) NULL,
    CONSTRAINT parts_invoice_parts_pkey PRIMARY KEY (id),
    CONSTRAINT parts_invoice_parts_parts_invoice_data_id_fkey FOREIGN KEY (parts_invoice_data_id) REFERENCES parts_invoice_data(id) ON DELETE CASCADE
);

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert default dealers
INSERT INTO dealers (id, dealer_id, dealer_name, api_key, api_token, secret_key, is_active, created_at, updated_at)
VALUES
    (uuid_generate_v4(), '00999', '00999', '6c796097-a453-420f-9a19-155a2a24513e', '81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c', 'default-secret-key-2024', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('e3a18c82-c500-450f-b6e1-5c5fbe68bf41', '12284', 'Sample Dealer', 'sample-api-key-12284', 'sample-api-token-12284', 'sample-secret-key-12284', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (dealer_id) DO NOTHING;

-- Insert default API configuration
INSERT INTO api_configurations (config_name, base_url, description, is_active)
VALUES ('DGI_API', 'https://dev-gvt-gateway.eksad.com/dgi-api/v1.3', 'Default DGI API configuration', true)
ON CONFLICT (config_name) DO NOTHING;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Prospect data indexes
CREATE INDEX IF NOT EXISTS idx_prospect_data_dealer_id ON prospect_data(dealer_id);
CREATE INDEX IF NOT EXISTS idx_prospect_data_tanggal_prospect ON prospect_data(tanggal_prospect);
CREATE INDEX IF NOT EXISTS idx_prospect_data_fetched_at ON prospect_data(fetched_at);

-- PKB data indexes
CREATE INDEX IF NOT EXISTS idx_pkb_data_dealer_id ON pkb_data(dealer_id);
CREATE INDEX IF NOT EXISTS idx_pkb_data_no_work_order ON pkb_data(no_work_order);
CREATE INDEX IF NOT EXISTS idx_pkb_data_fetched_at ON pkb_data(fetched_at);

-- Parts inbound data indexes
CREATE INDEX IF NOT EXISTS idx_parts_inbound_data_dealer_id ON parts_inbound_data(dealer_id);
CREATE INDEX IF NOT EXISTS idx_parts_inbound_data_no_penerimaan ON parts_inbound_data(no_penerimaan);

-- Fetch logs indexes
CREATE INDEX IF NOT EXISTS idx_fetch_logs_dealer_id ON fetch_logs(dealer_id);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_completed_at ON fetch_logs(completed_at);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_fetch_type ON fetch_logs(fetch_type);

-- Leasing data indexes
CREATE INDEX IF NOT EXISTS idx_leasing_data_dealer_id ON leasing_data(dealer_id);
CREATE INDEX IF NOT EXISTS idx_leasing_data_id_dokumen_pengajuan ON leasing_data(id_dokumen_pengajuan);

-- Document handling data indexes
CREATE INDEX IF NOT EXISTS idx_document_handling_data_dealer_id ON document_handling_data(dealer_id);
CREATE INDEX IF NOT EXISTS idx_document_handling_data_id_so ON document_handling_data(id_so);

-- Unit inbound data indexes
CREATE INDEX IF NOT EXISTS idx_unit_inbound_data_dealer_id ON unit_inbound_data(dealer_id);

-- Delivery process data indexes
CREATE INDEX IF NOT EXISTS idx_delivery_process_data_dealer_id ON delivery_process_data(dealer_id);

-- Billing process data indexes
CREATE INDEX IF NOT EXISTS idx_billing_process_data_dealer_id ON billing_process_data(dealer_id);

-- Unit invoice data indexes
CREATE INDEX IF NOT EXISTS idx_unit_invoice_data_dealer_id ON unit_invoice_data(dealer_id);

-- Parts sales data indexes
CREATE INDEX IF NOT EXISTS idx_parts_sales_data_dealer_id ON parts_sales_data(dealer_id);

-- DP HLO data indexes
CREATE INDEX IF NOT EXISTS idx_dp_hlo_data_dealer_id ON dp_hlo_data(dealer_id);

-- Workshop invoice data indexes
CREATE INDEX IF NOT EXISTS idx_workshop_invoice_data_dealer_id ON workshop_invoice_data(dealer_id);

-- Unpaid HLO data indexes
CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_dealer_id ON unpaid_hlo_data(dealer_id);

-- Parts invoice data indexes
CREATE INDEX IF NOT EXISTS idx_parts_invoice_data_dealer_id ON parts_invoice_data(dealer_id);

-- API configurations indexes
CREATE INDEX IF NOT EXISTS idx_api_configurations_config_name ON api_configurations(config_name);
CREATE INDEX IF NOT EXISTS idx_api_configurations_is_active ON api_configurations(is_active);

-- ============================================================================
-- ENHANCED PERFORMANCE INDEXES FOR BATCH PROCESSING
-- ============================================================================

-- Composite indexes for dealer_id + time-based queries (most critical for batch processing)
CREATE INDEX IF NOT EXISTS idx_prospect_data_dealer_modified ON prospect_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_prospect_data_dealer_created ON prospect_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_pkb_data_dealer_modified ON pkb_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_pkb_data_dealer_created ON pkb_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_parts_inbound_data_dealer_modified ON parts_inbound_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_parts_inbound_data_dealer_created ON parts_inbound_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_leasing_data_dealer_modified ON leasing_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_leasing_data_dealer_created ON leasing_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_document_handling_data_dealer_modified ON document_handling_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_document_handling_data_dealer_created ON document_handling_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_unit_inbound_data_dealer_modified ON unit_inbound_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_unit_inbound_data_dealer_created ON unit_inbound_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_delivery_process_data_dealer_modified ON delivery_process_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_delivery_process_data_dealer_created ON delivery_process_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_billing_process_data_dealer_modified ON billing_process_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_billing_process_data_dealer_created ON billing_process_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_unit_invoice_data_dealer_modified ON unit_invoice_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_unit_invoice_data_dealer_created ON unit_invoice_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_parts_sales_data_dealer_modified ON parts_sales_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_parts_sales_data_dealer_created ON parts_sales_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_dp_hlo_data_dealer_modified ON dp_hlo_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_dp_hlo_data_dealer_created ON dp_hlo_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_workshop_invoice_data_dealer_modified ON workshop_invoice_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_workshop_invoice_data_dealer_created ON workshop_invoice_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_dealer_modified ON unpaid_hlo_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_dealer_created ON unpaid_hlo_data(dealer_id, created_time);
CREATE INDEX IF NOT EXISTS idx_parts_invoice_data_dealer_modified ON parts_invoice_data(dealer_id, modified_time);
CREATE INDEX IF NOT EXISTS idx_parts_invoice_data_dealer_created ON parts_invoice_data(dealer_id, created_time);

-- Indexes for duplicate detection (critical for upsert operations)
CREATE INDEX IF NOT EXISTS idx_prospect_data_dealer_prospect ON prospect_data(dealer_id, id_prospect);
CREATE INDEX IF NOT EXISTS idx_pkb_data_dealer_work_order ON pkb_data(dealer_id, no_work_order);
CREATE INDEX IF NOT EXISTS idx_parts_inbound_data_dealer_penerimaan ON parts_inbound_data(dealer_id, no_penerimaan);
CREATE INDEX IF NOT EXISTS idx_leasing_data_dealer_dokumen ON leasing_data(dealer_id, id_dokumen_pengajuan);
CREATE INDEX IF NOT EXISTS idx_document_handling_data_dealer_spk ON document_handling_data(dealer_id, id_spk);
CREATE INDEX IF NOT EXISTS idx_unit_inbound_data_dealer_shipping ON unit_inbound_data(dealer_id, no_shipping_list);
CREATE INDEX IF NOT EXISTS idx_delivery_process_data_dealer_document ON delivery_process_data(dealer_id, delivery_document_id);
CREATE INDEX IF NOT EXISTS idx_billing_process_data_dealer_invoice ON billing_process_data(dealer_id, id_invoice);
CREATE INDEX IF NOT EXISTS idx_unit_invoice_data_dealer_invoice ON unit_invoice_data(dealer_id, no_invoice);
CREATE INDEX IF NOT EXISTS idx_parts_sales_data_dealer_so ON parts_sales_data(dealer_id, no_so);
CREATE INDEX IF NOT EXISTS idx_dp_hlo_data_dealer_hlo_doc ON dp_hlo_data(dealer_id, id_hlo_document);
CREATE INDEX IF NOT EXISTS idx_workshop_invoice_data_dealer_work_order ON workshop_invoice_data(dealer_id, no_work_order);
CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_dealer_hlo_doc ON unpaid_hlo_data(dealer_id, id_hlo_document);
CREATE INDEX IF NOT EXISTS idx_parts_invoice_data_dealer_invoice ON parts_invoice_data(dealer_id, no_invoice);

-- Indexes for fetched_at field (for cleanup and monitoring)
CREATE INDEX IF NOT EXISTS idx_prospect_data_fetched_at ON prospect_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_pkb_data_fetched_at ON pkb_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_parts_inbound_data_fetched_at ON parts_inbound_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_leasing_data_fetched_at ON leasing_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_document_handling_data_fetched_at ON document_handling_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_unit_inbound_data_fetched_at ON unit_inbound_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_delivery_process_data_fetched_at ON delivery_process_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_billing_process_data_fetched_at ON billing_process_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_unit_invoice_data_fetched_at ON unit_invoice_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_parts_sales_data_fetched_at ON parts_sales_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_dp_hlo_data_fetched_at ON dp_hlo_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_workshop_invoice_data_fetched_at ON workshop_invoice_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_unpaid_hlo_data_fetched_at ON unpaid_hlo_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_parts_invoice_data_fetched_at ON parts_invoice_data(fetched_at);

-- Composite indexes for fetch logs (for monitoring and cleanup)
CREATE INDEX IF NOT EXISTS idx_fetch_logs_dealer_type_completed ON fetch_logs(dealer_id, fetch_type, completed_at);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_status_completed ON fetch_logs(status, completed_at);
