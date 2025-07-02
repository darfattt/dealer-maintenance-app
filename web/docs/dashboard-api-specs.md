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