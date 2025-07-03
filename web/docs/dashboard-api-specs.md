following the docs\DASHBOARD_INTEGRATION_GUIDE.md and docs\DASHBOARD_API_EXAMPLES.md docs\DASHBOARD_BEST_PRACTICES.md 


1. create new api that retrieve from prospect_data backend\database.py  ProspectData, that will count data group by status_follow_up_prospecting and filter by dealer_id and date start/end tanggal_appointment (data type already date)\
2. mapping for the status_follow_up_prospecting : \
1 = Low \
2 = Medium \
3 = Hot \
4 = Deal \
5 = Not Deal\
3. apply integration for StatusProspectWidget.vue \


Status SPK


1. create new api that retrieve from spk_dealing_process_data backend\database.py  SPKDealingProcessData, that will count data group by status_spk and filter by dealer_id and date start/end tanggal_pesanan (data type already string, need to convert when filter) \
2. mapping for the status_spk : \ 
1 = Open \
2 = Indent \
3 = Complete \
4= Cancelled \
3. and apply integration for \

Top 5 Leasing

1. create new api that retrieve from leasing_data backend\database.py  LeasingData, that will count idPOFinanceCompany group by nama_finance_company and filter by dealer_id and date start/end tanggal_pengajuan(varchar, need to convert to date while filter) \
2. and apply integration for \

Document Handling
1. create new api that retrieve from document_handling_data backend\database.py  DocumentHandlingData, that will count id_spk and filter by dealer_id and date start/end tanggal_pengajuan_stnk_ke_biro and document_handling_data.status_faktur_stnk == 1 \
3. and apply integration for \




---------- Prospectict activity data
A. Status Prospect \
1. create new api that retrieve from prospect_data backend\database.py  ProspectData, that will count data group by status_prospect and filter by dealer_id and date start/end tanggal_appointment (data type already date) \
2. mapping for the status_prospect : \
1 = Low \
2 = Medium \
3 = Hot \
4 = Deal \
5 = Not Deal \
3. apply integration for web\src\components\dashboard\StatusProspectWidgetBar.vue \
\
B. Metode Followup \
1. create new api that retrieve from prospect_data backend\database.py  ProspectData, that will count data group by metode_follow_up and filter by dealer_id and date start/end tanggal_appointment (data type already date) \
2. mapping for the metode_follow_up : \
1 = SMS (WA/Line) \
2 = Call \
3 = Visit \
4 = Direct Touch \
3. apply integration for @MetodeFollowupWidget.vue\
\
C. Sumber Prospect \
1. create new api that retrieve from prospect_data backend\database.py  ProspectData, that will count data group by sumber_prospect and filter by dealer_id and date start/end tanggal_prospect (data type already date) \
2. mapping for the sumber_prospect : \
0001 = Pameran (Joint Promo, Grebek) \
Pasar, Alfamart, Indomart, Mall dll) \
0002 = Showroom Event \
0003 = Roadshow 
0004 = Walk in \
0005 = Customer RO H1 \
0006 = Customer RO H23 \
0007 = Website \
0008 = Social media \
0009 = External parties (leasing, insurance) \
0010 = Mobile Apps MD/Dealer \
0011 = Refferal \
0012 = Contact Center \
9999 = Others \
3. show only top 5 \
3. apply integration for @SumberProspectWidget.vue

Sebaran Prospect \n
1. create new api that retrieve from prospect_data backend\database.py  ProspectData, that will count data group by kodeKecamatan and filter by dealer_id and date start/end tanggal_appointment (data type already date) and get latitude, longitude to map into map chart \n
2. show only top 5 \n
3. apply integration for 

Data history
1. create new api that retrieve from prospect_data backend\database.py  ProspectData, get all fields for tabular data with request param filter (id_prospect, nama_lengkap, alamat,no_kontak,tanggal_prospect,status_prospect)
2. got pagination, per page default 20
3. apply integration for 

---- Dealing process

Dealing top unit \
1. create new api that retrieve from spk_dealing_process_units @database.py  SPKDealingProcessUnit, that will sum(quantity)  group by kode_tipe_unit and filter by dealer_id and date start/end tanggal_pengiriman (data type  string, need to convert when filter) \
2. mapping data : None and \
3. and apply integration for \ 

Revenue \
1. create new api that retrieve from spk_dealing_process_units @database.py  SPKDealingProcessUnit, that will sum(harga_jual)  filter by dealer_id and date start/end tanggal_pengiriman (data type  string, need to convert when filter) \
2. mapping data : None \
3. and apply integration for \ 


TODO   Data history \
1. create new api that retrieve from spk_dealing_process_data database.py  SPKDealingProcessData, get all fields for tabular data with request param filter (id_spk, nama_customer, alamat,no_kontak,email,status_prospect,nama_bpkbp)
2. got pagination, per page default 20 \
3. apply integration for \



-- Delivery Process -- 
Driver \
1. create new api that retrieve from delivery_process_data @database.py  DeliveryProcessData join with DeliveryProcessDetail, that will count(DeliveryProcessDetail.id_spk) group by id_driver and filter by dealer_id and date start/end tanggal_pengiriman (data type  string, need to convert when filter) \
2. mapping data : None, only show top 5 \ 
3. and apply integration for \  

Lokasi Pengiriman \
1. create new api that retrieve from delivery_process_data @database.py  DeliveryProcessData join with DeliveryProcessDetail, that will count(DeliveryProcessDetail.lokasi_pengiriman) group by lokasi_pengiriman and filter by dealer_id and date start/end tanggal_pengiriman (data type  string, need to convert when filter) \
2. Show top 5 only \
3. and apply integration for  \

Data history \
1. create new api that retrieve from delivery_process_data database.py  DeliveryProcessData join with DeliveryProcessDetail, get fields :delivery_document_id,tanggal_pengiriman,status_delivery_document,id_driver,id_spk,nama_pengerima,no_kontak_penerima, lokasi_pengiriman,waktu_pengiriman for tabular data with request param filter (delivery_document_id,tanggal_pengiriman,status_delivery_document,id_driver,id_spk,nama_pengerima,no_kontak_penerima, lokasi_pengiriman,waktu_pengiriman) \
2. got pagination, per page default 20 \
3. apply integration for \










-----------------------

Cara Bayar 

1. create new api that retrieve from billing_process_data backend/database.py  BillingProcessData, that will count(cara_bayar)  group by cara_bayar and filter by dealer_id and date start/end created_time (data type  string, need to convert when filter)
2. mapping data : 1 = Cash 2 = Transfer 
3. and apply integration for  

Status Bayar 
1. create new api that retrieve from billing_process_data backend/database.py  BillingProcessData, that will count(status)  group by status and filter by dealer_id and date start/end created_time (data type  string, need to convert when filter)
2. mapping data : 1 = New 2 = Process 3 = Accepted 4 = Close
3. and apply integration for  

Revenue 
billing_process_data backend/database.py  BillingProcessData, that will sum(amount)  filter by dealer_id and date start/end created_time (data type  string, need to convert when filter) nd filter by dealer_id and date start/end created_time (data type  string, need to convert when filter)
2. mapping data : None 
3. and apply integration for 

Data History
1. create new api that retrieve from billing_process_data backend/database.py  BillingProcessData join with DeliveryProcessDetail, get fields :No,id invoice, id customer, amount, tipe pembayaran (show mapping label), cara bayar(show mapping label) , status (show mapping label) 
2. got pagination, per page default 20 
3. Cara Bayar : 1 = Cash 2 = Transfer 
   Status : 1 = New 2 = Process 3 = Accepted 4 = Close
   Tipe Pembayaran : 1 = Credit 2 = Cash
4. apply integration for 

Tren Revenue 

1. create new api that retrieve from billing_process_data backend/database.py  BillingProcessData, that will sum(amount)  group by periodmonth of created_time (MMM) and filter by dealer_id and date start/end yyyy(created_time) = now (this year only) (data type  string, need to convert when filter), sort from jan to dec.
2. mapping data : None
3. and apply integration for  

----------
leasing

Leasing
Data History
1. create new api that retrieve from leasing_data backend/database.py  LeasingData, get all fields (for the api)
and filter by dealer_id and date start/end created_time (data type  string, need to convert when filter)
2. got pagination, per page default 20
3. apply integration for 

Status Dokumen PO
1. create new api that retrieve from leasing_data backend/database.py  LeasingData, that will 
count(id) with case
if tanggal_pengiriman_po_finance_company not null > pengirimanPO++
else if tanggal_pembuatan_po not null > pembuatanPO++
else if tanggal_pengajuan not null > pengajuanPO++
group by and filter by dealer_id and date start/end tanggal_pengiriman_po_finance_company or tanggal_pembuatan_po or tanggal_pengajuan (data type  string, need to convert when filter) \
2. and apply integration for  \

Pembuatan PO
1. create new api that retrieve from leasing_data backend/database.py  LeasingData, that will count(id_po_finance_company)  group by periodmonth of tanggal_pembuatan_po (MMM) and filter by dealer_id and date start/end yyyy(creattanggal_pembuatan_poed_time) = now (this year only) (data type  string, need to convert when filter), sort from jan to dec.
2. mapping data : None
3. and apply integration for  


------
Document Handling

1. create new api that retrieve from billing_process_data backend/database.py  BillingProcessData, that will count(cara_bayar)  group by cara_bayar and filter by dealer_id and date start/end created_time (data type  string, need to convert when filter)
2. mapping data : 1 = Cash 2 = Transfer 
3. and apply integration for  

Permohonan Faktur
1. create new api that retrieve from document_handling_data backend/database.py  count(DocumentHandlingUnit.id)DocumentHandlingData join with DocumentHandlingUnit no grouping just count all, 
and filter by dealer_id and date start/end tanggal_pengajuan_stnk_ke_biro (data type  string, need to convert when filter)
2. include the indicator with same calculation but date minus 1 month, for example : filter date from 02/01/2024 to 01/02/2024, then the indicator will be filter date from 02/12/2023 to 01/01/2024 , indicator will be compare with the current date filter value will show up/down/remain and percentage value.
3. apply integration for 


1. STNK Diterima
1. create new api that retrieve from document_handling_data backend/database.py  count(DocumentHandlingUnit.id)DocumentHandlingData join with DocumentHandlingUnit no grouping just count all, 
and filter by dealer_id and date start/end tanggal_penerimaan_bpkb_dari_biro (data type  string, need to convert when filter)
2. include the indicator with same calculation but date minus 1 month, for example : filter date from 02/01/2024 to 01/02/2024, then the indicator will be filter date from 02/12/2023 to 01/01/2024 , indicator will be compare with the current date filter value will show up/down/remain and percentage value.
3. apply integration for @STNKDIterimaKonsumenWidget.vue

2. BPKB Diterima
1. create new api that retrieve from document_handling_data backend/database.py  count(DocumentHandlingUnit.id)DocumentHandlingData join with DocumentHandlingUnit no grouping just count all, 
and filter by dealer_id and date start/end tanggal_terima_bpkb_oleh_konsumen (data type  string, need to convert when filter)
2. include the indicator with same calculation but date minus 1 month, for example : filter date from 02/01/2024 to 01/02/2024, then the indicator will be filter date from 02/12/2023 to 01/01/2024 , indicator will be compare with the current date filter value will show up/down/remain and percentage value.
3. apply integration for @BPKBDiterimaKonsumenWidget.vue
-------

Unit Inbound (Done all)
Data History
1. create new api that retrieve from unit_inbound_data backend/database.py  UnitInboundData join with UnitInboundUnit, get all fields (for the api), 
and filter by dealer_id and date start/end created_time (data type  string, need to convert when filter)
2. got pagination, per page default 20
3. apply integration for , since api return all columns, but dashboard only show certain fields then follow the dashboard to show on UI

Top Penerimaan unit
1. create new api that retrieve from unit_inbound_data backend/database.py  UnitInboundData join with UnitInboundUnit, that will sum(kuantitas_diterima), item_desc (concat kode_tipe_unit,kode_warna) group by kode_tipe_unit,kode_warna and filter by dealer_id and date start/end created_time (data type  string, need to convert when filter) \
2. Show top 5 only \
3. and apply integration for  \
