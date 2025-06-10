-- Insert sample data for dealer 00999 to demonstrate dashboard
-- Run this script directly in PostgreSQL to add sample data

-- Ensure dealer 00999 exists
INSERT INTO dealers (dealer_id, dealer_name, api_key, api_token, is_active, created_at, updated_at) 
VALUES (
    '00999', 
    'Default Dealer', 
    '6c796097-a453-420f-9a19-155a2a24513e', 
    '81d7fd22c95ba5385e05563a515868905d20419df06190ab035cf8be307a1e0c',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (dealer_id) DO NOTHING;

-- Insert sample prospect data (multiple records for better charts)
INSERT INTO prospect_data (
    id, dealer_id, id_prospect, sumber_prospect, tanggal_prospect, tagging_prospect,
    nama_lengkap, no_kontak, no_ktp, alamat, kode_propinsi, kode_kota, kode_kecamatan,
    kode_kelurahan, kode_pos, latitude, longitude, kode_pekerjaan, tanggal_appointment,
    waktu_appointment, metode_follow_up, test_ride_preference, status_follow_up_prospecting,
    status_prospect, id_sales_people, id_event, created_time, modified_time, fetched_at
) VALUES 
-- Record 1 - Today
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00001', '0001', CURRENT_DATE, 'Yes',
    'Ahmad Wijaya', '081234567890', '3201070506090001', 'Jl. Sudirman No. 123, Jakarta Pusat',
    '3100', '3101', '317404', '3174040001', '14130', '-6.208763', '106.845599', '1',
    CURRENT_DATE + INTERVAL '3 days', '15:30:00', '1', '1', '1', '2', 'SP001',
    'EV/00999/2312/001', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
-- Record 2 - Yesterday
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00002', '0002', CURRENT_DATE - INTERVAL '1 day', 'Yes',
    'Siti Nurhaliza', '081234567891', '3201070506090002', 'Jl. Thamrin No. 456, Jakarta Pusat',
    '3100', '3101', '317404', '3174040001', '14130', '-6.195000', '106.822000', '2',
    CURRENT_DATE + INTERVAL '2 days', '14:00:00', '2', '1', '2', '1', 'SP002',
    'EV/00999/2312/002', CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP
),
-- Record 3 - 2 days ago
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00003', '0001', CURRENT_DATE - INTERVAL '2 days', 'No',
    'Budi Santoso', '081234567892', '3201070506090003', 'Jl. Gatot Subroto No. 789, Jakarta Selatan',
    '3100', '3102', '317405', '3174050001', '12190', '-6.225000', '106.800000', '3',
    CURRENT_DATE + INTERVAL '1 day', '16:30:00', '1', '2', '1', '3', 'SP003',
    'EV/00999/2312/003', CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP
),
-- Record 4 - 3 days ago
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00004', '0003', CURRENT_DATE - INTERVAL '3 days', 'Yes',
    'Dewi Sartika', '081234567893', '3201070506090004', 'Jl. Kuningan No. 321, Jakarta Selatan',
    '3100', '3102', '317405', '3174050002', '12190', '-6.230000', '106.830000', '1',
    CURRENT_DATE + INTERVAL '4 days', '10:00:00', '3', '1', '3', '2', 'SP004',
    'EV/00999/2312/004', CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_TIMESTAMP
),
-- Record 5 - 4 days ago
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00005', '0001', CURRENT_DATE - INTERVAL '4 days', 'Yes',
    'Eko Prasetyo', '081234567894', '3201070506090005', 'Jl. Kemang No. 654, Jakarta Selatan',
    '3100', '3102', '317406', '3174060001', '12560', '-6.240000', '106.815000', '4',
    CURRENT_DATE + INTERVAL '5 days', '11:30:00', '2', '2', '2', '1', 'SP005',
    'EV/00999/2312/005', CURRENT_TIMESTAMP - INTERVAL '4 days', CURRENT_TIMESTAMP - INTERVAL '4 days', CURRENT_TIMESTAMP
),
-- Record 6 - 5 days ago
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00006', '0002', CURRENT_DATE - INTERVAL '5 days', 'No',
    'Fitri Handayani', '081234567895', '3201070506090006', 'Jl. Senopati No. 987, Jakarta Selatan',
    '3100', '3102', '317406', '3174060002', '12560', '-6.235000', '106.810000', '2',
    CURRENT_DATE + INTERVAL '6 days', '13:00:00', '1', '1', '1', '4', 'SP006',
    'EV/00999/2312/006', CURRENT_TIMESTAMP - INTERVAL '5 days', CURRENT_TIMESTAMP - INTERVAL '5 days', CURRENT_TIMESTAMP
),
-- Record 7 - 6 days ago
(
    uuid_generate_v4(), '00999', 'PSP/00999/2312/00007', '0001', CURRENT_DATE - INTERVAL '6 days', 'Yes',
    'Gunawan Susanto', '081234567896', '3201070506090007', 'Jl. Menteng No. 147, Jakarta Pusat',
    '3100', '3101', '317407', '3174070001', '10310', '-6.200000', '106.835000', '5',
    CURRENT_DATE + INTERVAL '7 days', '09:30:00', '2', '2', '3', '2', 'SP007',
    'EV/00999/2312/007', CURRENT_TIMESTAMP - INTERVAL '6 days', CURRENT_TIMESTAMP - INTERVAL '6 days', CURRENT_TIMESTAMP
);

-- Insert prospect units for each prospect
INSERT INTO prospect_units (id, prospect_data_id, kode_tipe_unit, sales_program_id, created_time, modified_time)
SELECT 
    uuid_generate_v4(),
    pd.id,
    CASE 
        WHEN pd.id_prospect LIKE '%00001' THEN 'PCX160'
        WHEN pd.id_prospect LIKE '%00002' THEN 'VARIO125'
        WHEN pd.id_prospect LIKE '%00003' THEN 'VARIO150'
        WHEN pd.id_prospect LIKE '%00004' THEN 'BEAT'
        WHEN pd.id_prospect LIKE '%00005' THEN 'SCOOPY'
        WHEN pd.id_prospect LIKE '%00006' THEN 'PCX160'
        WHEN pd.id_prospect LIKE '%00007' THEN 'VARIO125'
        ELSE 'PCX160'
    END,
    'PRM/0001/2312/001',
    pd.created_time,
    pd.modified_time
FROM prospect_data pd 
WHERE pd.dealer_id = '00999';

-- Insert sample fetch logs
INSERT INTO fetch_logs (
    id, dealer_id, fetch_type, status, records_fetched, error_message,
    fetch_duration_seconds, started_at, completed_at
) VALUES 
(
    uuid_generate_v4(), '00999', 'prospect_data', 'success', 7, NULL,
    25, CURRENT_TIMESTAMP - INTERVAL '1 hour', CURRENT_TIMESTAMP - INTERVAL '1 hour' + INTERVAL '25 seconds'
),
(
    uuid_generate_v4(), '00999', 'prospect_data', 'success', 3, NULL,
    15, CURRENT_TIMESTAMP - INTERVAL '6 hours', CURRENT_TIMESTAMP - INTERVAL '6 hours' + INTERVAL '15 seconds'
),
(
    uuid_generate_v4(), '00999', 'prospect_data', 'success', 2, NULL,
    12, CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '12 seconds'
);

-- Verify the data was inserted
SELECT 
    'Dealers' as table_name,
    COUNT(*) as record_count
FROM dealers 
WHERE dealer_id = '00999'

UNION ALL

SELECT 
    'Prospect Data' as table_name,
    COUNT(*) as record_count
FROM prospect_data 
WHERE dealer_id = '00999'

UNION ALL

SELECT 
    'Prospect Units' as table_name,
    COUNT(*) as record_count
FROM prospect_units pu
JOIN prospect_data pd ON pu.prospect_data_id = pd.id
WHERE pd.dealer_id = '00999'

UNION ALL

SELECT 
    'Fetch Logs' as table_name,
    COUNT(*) as record_count
FROM fetch_logs 
WHERE dealer_id = '00999';

-- Show sample of the data
SELECT 
    id_prospect,
    nama_lengkap,
    tanggal_prospect,
    status_prospect,
    fetched_at
FROM prospect_data 
WHERE dealer_id = '00999'
ORDER BY tanggal_prospect DESC
LIMIT 5;
