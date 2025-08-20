-- Migration: Create whatsapp_template table and populate with initial template data
-- This migration creates the WhatsApp template table and inserts template data
-- based on reminder_target and reminder_type combinations

-- Create the whatsapp_template table
CREATE TABLE IF NOT EXISTS customer.whatsapp_template (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_target VARCHAR(50) NOT NULL,
    reminder_type VARCHAR(100) NOT NULL,
    template TEXT NOT NULL,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_modified_by VARCHAR(100),
    last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create index for efficient template lookup
CREATE INDEX IF NOT EXISTS idx_whatsapp_template_lookup 
ON customer.whatsapp_template (reminder_target, reminder_type);

-- Insert template data based on reminder_target and reminder_type combinations
-- KPB-1 Templates
INSERT INTO customer.whatsapp_template (reminder_target, reminder_type, template, created_by) VALUES
('KPB-1', 'H+30 tanggal beli (by WA)', 
'Halo {nama_pemilik},

Terima kasih telah mempercayai produk Honda. Saatnya untuk melakukan servis KPB-1 kendaraan Anda untuk menjaga performa dan garansi.

Segera hubungi kami untuk membuat jadwal servis KPB-1.

Terima kasih,
{dealer_name}', 'system'),

('KPB-1', 'H-7 dari expired KPB-1 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-1 kendaraan Honda Anda akan berakhir dalam 7 hari. Jangan lewatkan kesempatan untuk mendapatkan servis gratis.

Segera hubungi kami untuk menjadwalkan servis KPB-1.

Terima kasih,
{dealer_name}', 'system'),

-- KPB-2 Templates
('KPB-2', 'H-60 dari expired KPB-2 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-2 kendaraan Honda Anda akan berakhir dalam 60 hari. Pastikan kendaraan Anda mendapatkan perawatan terbaik.

Hubungi kami sekarang untuk menjadwalkan servis KPB-2.

Terima kasih,
{dealer_name}', 'system'),

('KPB-2', 'H-30 dari expired KPB-2 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-2 kendaraan Honda Anda akan berakhir dalam 30 hari. Jangan sampai terlewat untuk mendapatkan servis berkualitas.

Segera hubungi kami untuk menjadwalkan servis KPB-2.

Terima kasih,
{dealer_name}', 'system'),

('KPB-2', 'H-7 dari expired KPB-2 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-2 kendaraan Honda Anda akan berakhir dalam 7 hari. Ini adalah kesempatan terakhir untuk mendapatkan servis gratis.

Segera hubungi kami untuk menjadwalkan servis KPB-2.

Terima kasih,
{dealer_name}', 'system'),

-- KPB-3 Templates
('KPB-3', 'H-60 dari expired KPB-3 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-3 kendaraan Honda Anda akan berakhir dalam 60 hari. Pastikan kendaraan tetap dalam kondisi prima.

Hubungi kami untuk menjadwalkan servis KPB-3.

Terima kasih,
{dealer_name}', 'system'),

('KPB-3', 'H-30 dari expired KPB-3 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-3 kendaraan Honda Anda akan berakhir dalam 30 hari. Manfaatkan kesempatan ini untuk servis berkualitas.

Segera hubungi kami untuk menjadwalkan servis KPB-3.

Terima kasih,
{dealer_name}', 'system'),

('KPB-3', 'H-7 dari expired KPB-3 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-3 kendaraan Honda Anda akan berakhir dalam 7 hari. Jangan lewatkan kesempatan terakhir ini.

Segera hubungi kami untuk menjadwalkan servis KPB-3.

Terima kasih,
{dealer_name}', 'system'),

-- KPB-4 Templates
('KPB-4', 'H-60 dari expired KPB-4 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-4 kendaraan Honda Anda akan berakhir dalam 60 hari. Pastikan kendaraan mendapatkan perawatan terakhir yang optimal.

Hubungi kami untuk menjadwalkan servis KPB-4.

Terima kasih,
{dealer_name}', 'system'),

('KPB-4', 'H-30 dari expired KPB-4 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-4 kendaraan Honda Anda akan berakhir dalam 30 hari. Ini adalah servis terakhir dalam program garansi.

Segera hubungi kami untuk menjadwalkan servis KPB-4.

Terima kasih,
{dealer_name}', 'system'),

('KPB-4', 'H-7 dari expired KPB-4 (by WA)', 
'Halo {nama_pemilik},

Garansi KPB-4 kendaraan Honda Anda akan berakhir dalam 7 hari. Ini adalah kesempatan terakhir untuk servis garansi.

Segera hubungi kami untuk menjadwalkan servis KPB-4.

Terima kasih,
{dealer_name}', 'system'),

-- Non KPB Templates (N/A reminder_type)
('Non KPB', 'N/A', 
'Halo {nama_pemilik},

Saatnya untuk melakukan servis rutin kendaraan Honda Anda. Perawatan berkala sangat penting untuk menjaga performa dan keamanan berkendara.

Hubungi kami untuk menjadwalkan servis kendaraan Anda.

Terima kasih,
{dealer_name}', 'system'),

-- Booking Service Templates
('Booking Service', 'N/A', 
'Halo {nama_pemilik},

Terima kasih telah melakukan booking servis. Kami siap memberikan pelayanan terbaik untuk kendaraan Honda Anda.

Silakan datang sesuai jadwal yang telah ditentukan.

Terima kasih,
{dealer_name}', 'system'),

-- Ultah Konsumen Templates
('Ultah Konsumen', 'N/A', 
'Halo {nama_pemilik},

Selamat ulang tahun! Semoga di usia yang baru ini Anda selalu diberikan kesehatan dan keberkahan.

Sebagai apresiasi, dapatkan promo spesial untuk servis kendaraan Honda Anda.

Terima kasih,
{dealer_name}', 'system');

-- Update the last_modified_date trigger
CREATE OR REPLACE FUNCTION customer.update_whatsapp_template_modified_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_whatsapp_template_modified_time
    BEFORE UPDATE ON customer.whatsapp_template
    FOR EACH ROW
    EXECUTE FUNCTION customer.update_whatsapp_template_modified_time();