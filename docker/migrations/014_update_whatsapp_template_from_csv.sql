-- Migration: Update whatsapp_template table with templates from CSV file
-- This migration updates existing WhatsApp templates to match the content from reminder_template_v1.csv

-- Update KPB-1 templates
UPDATE customer.whatsapp_template
SET template = 'Salam Satu Hati,
Selamat Pagi Bapak {nama_pelanggan},

Wah ga kerasa sudah 1 bulan dari pembelian motor {tipe_unit} dengan nopol {nomor_polisi}, jangan lupa gunakan Service Gratis Pertama untuk motor kesayangan Anda ya!
Segera datang dan bawa motor Anda ke AHASS {nama_ahass}

Jangan sampai terlewat!
Dengan memanfaatkan servis gratis ini, Bapak bisa menghemat hingga Rp150.000

Segera datang dan bawa motor {tipe_unit} kesayangan Anda ke AHASS {nama_ahass} agar motor Anda tetap dalam kondisi prima☺️

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'KPB-1' AND reminder_type = 'H+30 tanggal beli (by WA)';

UPDATE customer.whatsapp_template
SET template = 'Salam Satu Hati,
Selamat Pagi Bapak {nama_pelanggan},

Masa Servis Gratis Pertama Anda akan berakhir tanggal {tanggal_expired_kpb} atau maksimal 1.000 KM mana yang lebih dulu dicapai.

Jangan sampai terlewat!
Dengan memanfaatkan servis gratis ini, Bapak bisa menghemat hingga Rp150.000
Segera datang dan bawa motor {tipe_unit} dengan nopol {nomor_polisi} kesayangan Anda ke AHASS {nama_ahass} agar motor Anda tetap dalam kondisi prima☺️

Untuk Kenyamanan Anda, Kami juga menyediakan Layanan Booking Service dan Layanan Servis Kunjung. Booking Service bisa via Daya Auto, silakan download di Google Play Store atau Apps Store (insert kode referral)

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'KPB-1' AND reminder_type = 'H-7 dari expired KPB-1 (by WA)';

-- Update KPB-2 templates and consolidate reminder types
-- Delete separate H-60 and H-30 entries and update H-7 to handle all reminder types
DELETE FROM customer.whatsapp_template
WHERE reminder_target = 'KPB-2' AND reminder_type IN ('H-60 dari expired KPB-2 (by WA)', 'H-30 dari expired KPB-2 (by WA)');

UPDATE customer.whatsapp_template
SET reminder_type = 'H-60 dari expired KPB-2 (by WA);H-30 dari expired KPB-2 (by WA);H-7 dari expired KPB-2 (by WA)',
    template = 'Salam Satu Hati,
Selamat Pagi {nama_pelanggan},

Masa Servis Gratis Ke-2 Anda akan berakhir tanggal {tanggal_expired_kpb} atau maksimal 1.000 KM mana yang lebih dulu dicapai.

Jangan sampai terlewat!
Dengan memanfaatkan servis gratis ini, Bapak bisa menghemat hingga Rp150.000
Segera datang dan bawa motor {tipe_unit} dengan nopol {nomor_polisi} kesayangan Anda ke AHASS {nama_ahass} agar motor Anda tetap dalam kondisi prima☺️

Untuk Kenyamanan Anda, Kami juga menyediakan Layanan Booking Service dan Layanan Servis Kunjung. Booking Service bisa via Daya Auto, silakan download di Google Play Store atau Apps Store (insert kode referral)

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'KPB-2' AND reminder_type = 'H-7 dari expired KPB-2 (by WA)';

-- Update KPB-3 templates and consolidate reminder types
-- Delete separate H-60 and H-30 entries and update H-7 to handle all reminder types
DELETE FROM customer.whatsapp_template
WHERE reminder_target = 'KPB-3' AND reminder_type IN ('H-60 dari expired KPB-3 (by WA)', 'H-30 dari expired KPB-3 (by WA)');

UPDATE customer.whatsapp_template
SET reminder_type = 'H-60 dari expired KPB-3 (by WA);H-30 dari expired KPB-3 (by WA);H-7 dari expired KPB-3 (by WA)',
    template = 'Salam Satu Hati,
Selamat Pagi {nama_pelanggan},

Masa Servis Gratis Ke-3 Anda akan berakhir tanggal {tanggal_expired_kpb} atau maksimal 1.000 KM mana yang lebih dulu dicapai.

Jangan sampai terlewat!
Dengan memanfaatkan servis gratis ini, Bapak bisa menghemat hingga Rp150.000
Segera datang dan bawa motor {tipe_unit} dengan nopol {nomor_polisi} kesayangan Anda ke AHASS {nama_ahass} agar motor Anda tetap dalam kondisi prima☺️

Untuk Kenyamanan Anda, Kami juga menyediakan Layanan Booking Service dan Layanan Servis Kunjung. Booking Service bisa via Daya Auto, silakan download di Google Play Store atau Apps Store (insert kode referral)

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'KPB-3' AND reminder_type = 'H-7 dari expired KPB-3 (by WA)';

-- Update KPB-4 templates and consolidate reminder types
-- Delete separate H-60 and H-30 entries and update H-7 to handle all reminder types
DELETE FROM customer.whatsapp_template
WHERE reminder_target = 'KPB-4' AND reminder_type IN ('H-60 dari expired KPB-4 (by WA)', 'H-30 dari expired KPB-4 (by WA)');

UPDATE customer.whatsapp_template
SET reminder_type = 'H-60 dari expired KPB-4 (by WA);H-30 dari expired KPB-4 (by WA);H-7 dari expired KPB-4 (by WA)',
    template = 'Salam Satu Hati,
Selamat Pagi Bapak {nama_pelanggan},

Masa Servis Gratis Ke-4 Anda akan berakhir tanggal {tanggal_expired_kpb} atau maksimal 1.000 KM mana yang lebih dulu dicapai.

Jangan sampai terlewat!
Dengan memanfaatkan servis gratis ini, Bapak bisa menghemat hingga Rp150.000
Segera datang dan bawa motor {tipe_unit} dengan nopol {nomor_polisi} kesayangan Anda ke AHASS {nama_ahass} agar motor Anda tetap dalam kondisi prima☺️

Untuk Kenyamanan Anda, Kami juga menyediakan Layanan Booking Service dan Layanan Servis Kunjung. Booking Service bisa via Daya Auto, silakan download di Google Play Store atau Apps Store (insert kode referral)

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'KPB-4' AND reminder_type = 'H-7 dari expired KPB-4 (by WA)';

-- Update Non KPB template
UPDATE customer.whatsapp_template
SET reminder_type = 'all',
    template = 'Salam Satu Hati,
Selamat Pagi {nama_pelanggan},

Bulan ini sudah saatnya untuk melakukan servis rutin motor {tipe_unit} kesayangan Anda. Segera datang dan bawa motor Anda ke {nama_ahass} supaya motor Anda tetap awet dan nyaman digunakan sehari-hari.

Untuk Kenyamanan Anda, Kami juga menyediakan Layanan Booking Service dan Layanan Servis Kunjung. Booking Service bisa via Daya Auto, silakan download di Google Play Store atau Apps Store (insert kode referral)

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'Non KPB' AND reminder_type = 'N/A';

-- Update Booking Service template
UPDATE customer.whatsapp_template
SET reminder_type = 'n/a',
    template = 'Salam Satu Hati,
Selamat Pagi {nama_pelanggan},

Ijin kami dari {nama_ahass}. mengingatkan jadwal booking service Bapak pada tgl 21 Agustus 2025
Jam 10.00 untuk motor {tipe_unit} kesayangan Bapak dengan nopol {nomor_polisi}

Nikmati Fasilitas AHASS kami yaitu Wifi, Stop Kontak di setiap kursi tunggu, Free Minuman Dingin, Free Cuci Motor setelah servis

Mohon untuk datang tepat waktu. Maksimum keterlambatan adalah 30 menit.

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih, Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'Booking Service' AND reminder_type = 'N/A';

-- Update Ultah Konsumen template
UPDATE customer.whatsapp_template
SET reminder_type = 'n/a',
    template = 'Salam Satu Hati🙏🏼,

Kami ucapkan Selamat Ulang Tahun kepada {nama_pelanggan}☺️ kiranya di tahun ini dilimpahkan banyak rejeki dan kebahagiaan. Pastinya di hari yang berbahagia ini, ada yang spesial untuk perawatan dan penanganan motor {tipe_unit} kesayangan Bapak.

uk bawa motor Anda ke {nama_ahass} dan jangan sampai telat.
Untuk informasi lebih lanjut silahkan WA/Call di 08112345678 yaa🥳

Alamat AHASS bisa melihat link google map ini :
{alamat_ahass}

Terimakasih,
Salam Satu Hati',
    last_modified_by = 'system',
    last_modified_date = CURRENT_TIMESTAMP
WHERE reminder_target = 'Ultah Konsumen' AND reminder_type = 'N/A';

-- Insert new Selesai Service template
INSERT INTO customer.whatsapp_template (reminder_target, reminder_type, template, created_by) VALUES
('Selesai Service', 'n/a',
'Terima kasih sudah mempercayakan servis motor ke AHASS,

Kak 🙌 Kami ingin tahu apa yang Kakak rasakan selama proses servis. Yuk isi review di sini: [Link Google Review] Feedback Kakak akan bantu kami bikin pengalaman servis di AHASS makin nyaman.', 'system');