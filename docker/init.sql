-- Initialize database with basic tables
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Dealers table
CREATE TABLE IF NOT EXISTS dealers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) UNIQUE NOT NULL,
    dealer_name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255),
    api_token VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data fetch configurations
CREATE TABLE IF NOT EXISTS fetch_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) REFERENCES dealers(dealer_id),
    schedule_type VARCHAR(20) NOT NULL CHECK (schedule_type IN ('hourly', 'daily', 'custom')),
    cron_expression VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    last_fetch_at TIMESTAMP,
    next_fetch_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prospect data table
CREATE TABLE IF NOT EXISTS prospect_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) REFERENCES dealers(dealer_id),
    id_prospect VARCHAR(255),
    sumber_prospect VARCHAR(10),
    tanggal_prospect DATE,
    tagging_prospect VARCHAR(10),
    nama_lengkap VARCHAR(255),
    no_kontak VARCHAR(50),
    no_ktp VARCHAR(50),
    alamat TEXT,
    kode_propinsi VARCHAR(10),
    kode_kota VARCHAR(10),
    kode_kecamatan VARCHAR(10),
    kode_kelurahan VARCHAR(10),
    kode_pos VARCHAR(10),
    latitude VARCHAR(20),
    longitude VARCHAR(20),
    alamat_kantor TEXT,
    kode_propinsi_kantor VARCHAR(10),
    kode_kota_kantor VARCHAR(10),
    kode_kecamatan_kantor VARCHAR(10),
    kode_kelurahan_kantor VARCHAR(10),
    kode_pos_kantor VARCHAR(10),
    kode_pekerjaan VARCHAR(10),
    no_kontak_kantor VARCHAR(50),
    tanggal_appointment DATE,
    waktu_appointment TIME,
    metode_follow_up VARCHAR(10),
    test_ride_preference VARCHAR(10),
    status_follow_up_prospecting VARCHAR(10),
    status_prospect VARCHAR(10),
    id_sales_people VARCHAR(50),
    id_event VARCHAR(100),
    created_time TIMESTAMP,
    modified_time TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dealer_id, id_prospect)
);

-- Prospect units table
CREATE TABLE IF NOT EXISTS prospect_units (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prospect_data_id UUID REFERENCES prospect_data(id) ON DELETE CASCADE,
    kode_tipe_unit VARCHAR(20),
    sales_program_id TEXT,
    created_time TIMESTAMP,
    modified_time TIMESTAMP
);

-- Fetch logs table
CREATE TABLE IF NOT EXISTS fetch_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id VARCHAR(10) REFERENCES dealers(dealer_id),
    fetch_type VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('success', 'failed', 'partial')),
    records_fetched INTEGER DEFAULT 0,
    error_message TEXT,
    fetch_duration_seconds INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default dealer
INSERT INTO dealers (dealer_id, dealer_name, api_key, api_token)
VALUES ('00999', 'Default Dealer', '6c796097-a453-420f-9a19-155a2a24513e', '81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c')
ON CONFLICT (dealer_id) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_prospect_data_dealer_id ON prospect_data(dealer_id);
CREATE INDEX IF NOT EXISTS idx_prospect_data_tanggal_prospect ON prospect_data(tanggal_prospect);
CREATE INDEX IF NOT EXISTS idx_prospect_data_fetched_at ON prospect_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_dealer_id ON fetch_logs(dealer_id);
CREATE INDEX IF NOT EXISTS idx_fetch_logs_completed_at ON fetch_logs(completed_at);
