"""
Dummy Data Generators for Testing
Provides sample data for dealers that don't have real API access
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Special dealer IDs that get dummy data (only sample dealers)
DUMMY_DATA_DEALER_IDS = ["12284"]
DUMMY_DATA_DEALER_UUID = "e3a18c82-c500-450f-b6e1-5c5fbe68bf41"

def should_use_dummy_data(dealer_id: str) -> bool:
    """Check if dealer should use dummy data"""
    return dealer_id in DUMMY_DATA_DEALER_IDS or dealer_id == DUMMY_DATA_DEALER_UUID

def get_dummy_prospect_data(dealer_id: str, from_time: str, to_time: str) -> Dict[str, Any]:
    """Generate dummy prospect data for demonstration"""
    
    # Only generate dummy data for specific dealer
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}. Please configure real API credentials.",
            "data": []
        }
    
    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate multiple prospects for the date range
    prospects = []
    current_date = start_date

    names = ["Ahmad Wijaya", "Siti Nurhaliza", "Budi Santoso", "Dewi Sartika", "Eko Prasetyo"]
    unit_types = ["PCX160", "VARIO125", "VARIO150", "BEAT", "SCOOPY"]

    while current_date <= end_date:
        # Generate 1-3 prospects per day
        for i in range(random.randint(1, 3)):
            prospect_id = f"PSP/{dealer_id}/{current_date.strftime('%y%m')}/{random.randint(1000, 9999)}"

            prospect = {
                "idProspect": prospect_id,
                "sumberProspect": random.choice(["0001", "0002", "0003"]),
                "tanggalProspect": current_date.strftime("%d/%m/%Y"),
                "taggingProspect": random.choice(["Yes", "No"]),
                "namaLengkap": random.choice(names),
                "noKontak": f"081{random.randint(10000000, 99999999)}",
                "noKtp": f"32{random.randint(10000000000000, 99999999999999)}",
                "alamat": f"Jl. Sample No. {random.randint(1, 999)} RT 001, RW 002",
                "kodePropinsi": "3100",
                "kodeKota": "3101",
                "kodeKecamatan": "317404",
                "kodeKelurahan": "3174040001",
                "kodePos": "14130",
                "latitude": f"{random.uniform(-6.5, -6.0):.6f}",
                "longitude": f"{random.uniform(106.5, 107.0):.6f}",
                "alamatKantor": "",
                "kodePropinsiKantor": "",
                "kodeKotaKantor": "",
                "kodeKecamatanKantor": "",
                "kodeKelurahanKantor": "",
                "kodePosKantor": "",
                "kodePekerjaan": str(random.randint(1, 5)),
                "noKontakKantor": f"021{random.randint(1000000, 9999999)}",
                "tanggalAppointment": (current_date + timedelta(days=random.randint(1, 7))).strftime("%d/%m/%Y"),
                "waktuAppointment": f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}",
                "metodeFollowUp": str(random.randint(1, 3)),
                "testRidePreference": str(random.randint(1, 2)),
                "statusFollowUpProspecting": str(random.randint(1, 3)),
                "statusProspect": str(random.randint(1, 4)),
                "idSalesPeople": f"SP{random.randint(1000, 9999)}",
                "idEvent": f"EV/E/K0Z/{dealer_id}/{current_date.strftime('%y%m')}/{random.randint(1, 100):03d}",
                "dealerId": dealer_id,
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "unit": [
                    {
                        "kodeTipeUnit": random.choice(unit_types),
                        "salesProgramId": f"PRM/{random.randint(1000, 9999)}/{current_date.strftime('%y%m')}/001",
                        "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                        "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
                    }
                ]
            }
            prospects.append(prospect)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": prospects
    }

def get_dummy_pkb_data(dealer_id: str, from_time: str, to_time: str) -> Dict[str, Any]:
    """Generate dummy PKB data for demonstration"""
    
    # Only generate dummy data for specific dealer
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}. Please configure real API credentials.",
            "data": []
        }
    
    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate multiple PKB records for the date range
    pkb_records = []
    current_date = start_date

    names = ["DELIYA OKTAFIANI", "DWI SURAHMA PATLUH", "AHMAD WIJAYA", "SITI NURHALIZA", "BUDI SANTOSO"]
    unit_types = ["AB", "PCX160", "VARIO125", "VARIO150", "BEAT"]
    no_polisi_list = ["E 5807 YBG", "B 0040 DWI", "D 1234 ABC", "F 5678 XYZ", "H 9012 DEF"]

    while current_date <= end_date:
        # Generate 1-2 PKB records per day
        for _ in range(random.randint(1, 2)):
            work_order_num = random.randint(1, 999)
            work_order_type = random.choice(["WO", "JR"])
            
            pkb_record = {
                "noWorkOrder": f"{work_order_type}-{dealer_id}-{current_date.strftime('%y-%m')}-{work_order_num:05d}",
                "noSAForm": f"SAF/{dealer_id}/{current_date.strftime('%y/%m')}/{work_order_num:05d}",
                "tanggalServis": current_date.strftime("%d/%m/%Y"),
                "waktuPKB": current_date.strftime("%d/%m/%Y %H:%M:%S") if random.choice([True, False]) else "",
                "noPolisi": random.choice(no_polisi_list),
                "noRangka": f"KFB117NK{random.randint(100000, 999999)}",
                "noMesin": f"KFB1E1{random.randint(100000, 999999)}",
                "kodeTipeUnit": random.choice(unit_types),
                "tahunMotor": str(random.randint(2019, 2023)),
                "informasiBensin": str(random.randint(0, 1)),
                "kmTerakhir": random.randint(5000, 50000),
                "tipeComingCustomer": "1",
                "namaPemilik": random.choice(names),
                "alamatPemilik": f"DUSUN SAMPLE RT {random.randint(1, 10):03d}/{random.randint(1, 10):03d}",
                "kodePropinsiPemilik": "3200",
                "kodeKotaPemilik": str(random.randint(3201, 3299)),
                "kodeKecamatanPemilik": f"32{random.randint(10, 99)}{random.randint(10, 99)}",
                "kodeKelurahanPemilik": f"32{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(1000, 9999)}",
                "kodePosPemilik": str(random.randint(40000, 49999)),
                "alamatPembawa": f"DUSUN SAMPLE RT {random.randint(1, 10):03d}/{random.randint(1, 10):03d}",
                "kodePropinsiPembawa": "3200",
                "kodeKotaPembawa": str(random.randint(3201, 3299)),
                "kodeKecamatanPembawa": f"32{random.randint(10, 99)}{random.randint(10, 99)}",
                "kodeKelurahanPembawa": f"32{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(1000, 9999)}",
                "kodePosPembawa": str(random.randint(40000, 49999)),
                "namaPembawa": random.choice(names),
                "noTelpPembawa": f"08{random.randint(10000000000, 99999999999)}",
                "hubunganDenganPemilik": "2",
                "keluhanKonsumen": random.choice(["", "Mesin kasar", "Rem blong", "Lampu mati"]),
                "rekomendasiSA": random.choice(["", "Ganti oli", "Service berkala", "Perbaikan rem"]),
                "hondaIdSA": "",
                "hondaIdMekanik": f"MK{random.randint(100000000, 999999999)}",
                "saranMekanik": "",
                "asalUnitEntry": "NP",
                "idPIT": str(random.randint(1, 20)),
                "jenisPIT": "1",
                "waktuPendaftaran": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "waktuSelesai": (current_date + timedelta(hours=random.randint(1, 4))).strftime("%d/%m/%Y %H:%M:%S") if random.choice([True, False]) else "",
                "totalFRT": f"{random.randint(0, 2):02d}:{random.randint(0, 59):02d}",
                "setUpPembayaran": str(random.randint(0, 1)),
                "catatanTambahan": "",
                "konfirmasiPekerjaanTambahan": "0",
                "noBukuClaimC2": str(random.randint(1000000, 9999999)) if random.choice([True, False]) else "",
                "noWorkOrderJobReturn": f"JR-{dealer_id}-{current_date.strftime('%y-%m')}-{work_order_num:05d}" if work_order_type == "JR" else "",
                "totalBiayaService": random.randint(0, 500000),
                "waktuPekerjaan": f"{random.randint(0, 2):02d}:{random.randint(0, 59):02d}",
                "statusWorkOrder": str(random.randint(1, 5)),
                "dealerId": dealer_id,
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "services": [],
                "parts": []
            }
            
            # Add random services
            if random.choice([True, False]):
                service_jobs = ["SL081", "SL082", "SL083", "SL084", "SL085"]
                service_names = ["JASA PASANG 60000", "JASA SERVICE BERKALA", "JASA TUNE UP", "JASA GANTI OLI", "JASA PERBAIKAN REM"]
                
                for _ in range(random.randint(0, 2)):
                    service = {
                        "idJob": random.choice(service_jobs),
                        "namaPekerjaan": random.choice(service_names),
                        "jenisPekerjaan": random.choice(["LIGHT REPAIR", "HEAVY REPAIR", "MAINTENANCE"]),
                        "biayaService": random.randint(50000, 200000),
                        "promoIdJasa": "",
                        "discServiceAmount": 0,
                        "discServicePercentage": 0.0,
                        "totalHargaServis": random.randint(50000, 200000),
                        "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                        "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
                    }
                    pkb_record["services"].append(service)
            
            # Add random parts
            if random.choice([True, False]):
                parts_numbers = ["35010K1TJF0", "15400K1TJF0", "06435K1TJF0", "91201K1TJF0", "42450K1TJF0"]
                
                for _ in range(random.randint(0, 3)):
                    harga_parts = random.randint(50000, 2000000)
                    ppn = int(harga_parts * 0.11)
                    
                    part = {
                        "idJob": "",
                        "partsNumber": random.choice(parts_numbers),
                        "hargaParts": harga_parts,
                        "promoIdParts": "",
                        "discPartsAmount": 0,
                        "discPartsPercentage": 0.0,
                        "ppn": ppn,
                        "totalHargaParts": harga_parts + ppn,
                        "uangMuka": 0,
                        "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                        "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                        "kuantitas": random.randint(1, 3)
                    }
                    pkb_record["parts"].append(part)
            
            pkb_records.append(pkb_record)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": pkb_records
    }

def get_dummy_parts_inbound_data(dealer_id: str, from_time: str, to_time: str, no_po: str = "") -> Dict[str, Any]:
    """Generate dummy Parts Inbound data for demonstration"""

    # Only generate dummy data for specific dealer
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}. Please configure real API credentials.",
            "data": []
        }

    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate multiple Parts Inbound records for the date range
    parts_inbound_records = []
    current_date = start_date

    parts_numbers = [
        "272A0KCJ660", "372A0KCJ660", "15400-KVB-901", "06435-KVB-000",
        "91201-KVB-003", "42450-KVB-000", "35010-KVB-000", "17220-KVB-000"
    ]

    warehouses = ["WH123", "WH124", "WH125", "WH126", "WH127"]
    jenis_orders = ["1", "2", "3"]  # Different order types
    uoms = ["pcs", "set", "unit", "box"]

    while current_date <= end_date:
        # Generate 1-2 Parts Inbound records per day
        for _ in range(random.randint(1, 2)):
            receipt_num = random.randint(1, 999)

            parts_inbound_record = {
                "noPenerimaan": f"RCV/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{receipt_num:04d}",
                "tglPenerimaan": current_date.strftime("%d/%m/%Y"),
                "noShippingList": f"SPL/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{receipt_num:04d}",
                "dealerId": dealer_id,
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "po": []
            }

            # Generate PO items for this receipt
            num_po_items = random.randint(1, 4)
            for po_idx in range(num_po_items):
                po_number = f"PO{dealer_id}{current_date.strftime('%y%m')}{random.randint(1000, 9999)}"

                # Filter by noPO if specified
                if no_po and no_po not in po_number:
                    continue

                po_item = {
                    "noPO": po_number,
                    "jenisOrder": random.choice(jenis_orders),
                    "idWarehouse": random.choice(warehouses),
                    "partsNumber": random.choice(parts_numbers),
                    "kuantitas": random.randint(10, 500),
                    "uom": random.choice(uoms),
                    "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                    "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
                }
                parts_inbound_record["po"].append(po_item)

            # Only add record if it has PO items (in case of noPO filter)
            if parts_inbound_record["po"]:
                parts_inbound_records.append(parts_inbound_record)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": parts_inbound_records
    }


def get_dummy_leasing_data(dealer_id: str, from_time: str, to_time: str, id_spk: str = "") -> Dict[str, Any]:
    """Generate dummy Leasing data for demonstration"""

    # Only generate dummy data for specific dealer
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}. Please configure real API credentials.",
            "data": []
        }

    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate multiple Leasing records for the date range
    leasing_records = []
    current_date = start_date

    finance_companies = [
        {"id": "FC/FIF01", "name": "Astra FIF"},
        {"id": "FC/BAF01", "name": "BAF (Bussan Auto Finance)"},
        {"id": "FC/WOM01", "name": "WOM Finance"},
        {"id": "FC/OTO01", "name": "OTO Finance"},
        {"id": "FC/MCF01", "name": "Mega Central Finance"}
    ]

    tenors = [12, 18, 24, 30, 36, 42, 48]
    dp_amounts = [1500000, 2000000, 2500000, 3000000, 3500000, 4000000]
    cicilan_amounts = [400000, 500000, 600000, 700000, 800000, 900000, 1000000]

    while current_date <= end_date:
        # Generate 1-2 Leasing records per day
        for _ in range(random.randint(1, 2)):
            doc_num = random.randint(1, 999)
            spk_num = random.randint(1, 999)
            finance_company = random.choice(finance_companies)

            spk_id = f"SPK/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{spk_num:05d}"

            # Filter by idSPK if specified
            if id_spk and id_spk not in spk_id:
                continue

            leasing_record = {
                "idDokumenPengajuan": f"{finance_company['id']}/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{doc_num:05d}",
                "idSPK": spk_id,
                "jumlahDP": random.choice(dp_amounts),
                "tenor": random.choice(tenors),
                "jumlahCicilan": random.choice(cicilan_amounts),
                "tanggalPengajuan": current_date.strftime("%d/%m/%Y"),
                "idFinanceCompany": finance_company["id"],
                "namaFinanceCompany": finance_company["name"],
                "idPOFinanceCompany": f"PO/{finance_company['id']}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{doc_num:04d}",
                "tanggalPembuatanPO": current_date.strftime("%d/%m/%Y"),
                "tanggalPengirimanPOFinanceCompany": (current_date + timedelta(days=random.randint(1, 3))).strftime("%d/%m/%Y"),
                "dealerId": dealer_id,
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            leasing_records.append(leasing_record)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": leasing_records
    }


def get_dummy_document_handling_data(dealer_id: str, from_time: str, to_time: str, id_spk: str = "", id_customer: str = "") -> Dict[str, Any]:
    """Generate dummy document handling data for testing"""

    # Only generate for specific test dealers
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}. Please configure real API credentials.",
            "data": []
        }

    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate realistic dummy data
    dummy_data = []
    current_date = start_date

    # Generate 2-4 document handling records
    while current_date <= end_date:
        for i in range(random.randint(1, 2)):
            # Generate SPK and SO IDs
            spk_id = f"SPK/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{str(i+1).zfill(5)}"
            so_id = f"SO/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{str(i+1).zfill(5)}"

            # Filter by idSPK if provided
            if id_spk and id_spk not in spk_id:
                continue

            # Generate units for this document (1-3 units per document)
            units = []
            for j in range(random.randint(1, 3)):
                # Random vehicle data
                chassis_numbers = [
                    "MF139XJ5000001", "MF139XJ5000002", "MF139XJ5000003",
                    "MH1FC1850LK000001", "MH1FC1850LK000002", "MH1FC1850LK000003"
                ]

                # Random status values
                status_values = ["1", "2", "3", "4", "5"]

                # Random names
                names = ["Amir Nasution", "Siti Rahayu", "Budi Santoso", "Dewi Lestari", "Ahmad Fauzi"]

                unit = {
                    "nomorRangka": random.choice(chassis_numbers),
                    "nomorFakturSTNK": f"FH/AA/{random.randint(1580000, 1590000)}/N",
                    "tanggalPengajuanSTNKKeBiro": current_date.strftime("%d/%m/%Y"),
                    "statusFakturSTNK": random.choice(status_values),
                    "nomorSTNK": f"{random.randint(18500000, 18600000)}/MB",
                    "tanggalPenerimaanSTNKDariBiro": (current_date + timedelta(days=5)).strftime("%d/%m/%Y"),
                    "platNomor": f"AB{random.randint(1000, 9999)}XYZ",
                    "nomorBPKB": f"{random.randint(18500000, 18600000)}/MB",
                    "tanggalPenerimaanBPKBDariBiro": (current_date + timedelta(days=5)).strftime("%d/%m/%Y"),
                    "tanggalTerimaSTNKOlehKonsumen": (current_date + timedelta(days=10)).strftime("%d/%m/%Y"),
                    "tanggalTerimaBPKBOlehKonsumen": (current_date + timedelta(days=10)).strftime("%d/%m/%Y"),
                    "namaPenerimaBPKB": random.choice(names),
                    "namaPenerimaSTNK": random.choice(names),
                    "jenisIdPenerimaBPKB": "1",
                    "jenisIdPenerimaSTNK": "1",
                    "noIdPenerimaBPKB": f"32010705060{random.randint(900000, 999999)}",
                    "noIdPenerimaSTNK": f"32010705060{random.randint(900000, 999999)}",
                    "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                    "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
                }
                units.append(unit)

            record = {
                "idSO": so_id,
                "idSPK": spk_id,
                "dealerId": dealer_id,
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "unit": units
            }
            dummy_data.append(record)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": dummy_data
    }


def get_dummy_unit_inbound_data(dealer_id: str, from_time: str, to_time: str, po_id: str = "", no_shipping_list: str = "") -> Dict[str, Any]:
    """Generate dummy unit inbound data for testing"""

    # Only generate for specific test dealers
    if not should_use_dummy_data(dealer_id):
        return {
            "status": 0,
            "message": f"No dummy data available for dealer {dealer_id}. Please configure real API credentials.",
            "data": []
        }

    # Parse time range
    try:
        start_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
        end_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")
    except ValueError:
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()

    # Generate realistic dummy data
    dummy_data = []
    current_date = start_date

    # Generate 1-3 shipments per day
    while current_date <= end_date:
        for i in range(random.randint(1, 2)):
            # Generate shipping list and invoice numbers
            shipping_list_no = f"SL/B10/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{str(i+1).zfill(3)}"
            invoice_no = f"IN/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{str(i+1).zfill(5)}"

            # Filter by noShippingList if provided
            if no_shipping_list and no_shipping_list not in shipping_list_no:
                continue

            # Generate PO ID
            po_number = f"PO/{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{str(i+1).zfill(3)}"

            # Filter by poId if provided
            if po_id and po_id not in po_number:
                continue

            # Generate units for this shipment (1-3 units per shipment)
            units = []
            for j in range(random.randint(1, 3)):
                # Random unit data
                unit_types = ["HP3", "HP5", "CB150R", "PCX160", "VARIO125", "BEAT125"]
                colors = ["BK", "WH", "RD", "BL", "GY"]

                # Random engine and chassis numbers
                engine_no = f"JB{random.choice(['22', '55'])}E{random.randint(1000000, 9999999)}"
                chassis_no = f"{random.choice(['JB', 'TB'])}22136K{random.randint(100000, 999999)}"

                # Random status values
                rfs_status = random.choice(["0", "1"])

                # Goods receipt number
                goods_receipt = f"{dealer_id}/{current_date.strftime('%y')}/{current_date.strftime('%m')}/{random.randint(100, 999)}"

                # NRFS document (only if RFS status is 0)
                nrfs_doc = f"NRFS/{dealer_id}/{current_date.strftime('%y%m')}/{str(j+1).zfill(3)}" if rfs_status == "0" else ""

                unit = {
                    "kodeTipeUnit": random.choice(unit_types),
                    "kodeWarna": random.choice(colors),
                    "kuantitasTerkirim": 1,
                    "kuantitasDiterima": 1,
                    "noMesin": engine_no,
                    "noRangka": chassis_no,
                    "statusRFS": rfs_status,
                    "poId": po_number,
                    "kelengkapanUnit": "Helm, Aki, Spion, BPPSG (Buku Pedoman Pemilik dan Servis Garansi), toolset/toolkit",
                    "noGoodsReceipt": goods_receipt,
                    "docNRFSId": nrfs_doc,
                    "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                    "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S")
                }
                units.append(unit)

            record = {
                "noShippingList": shipping_list_no,
                "tanggalTerima": current_date.strftime("%d/%m/%Y"),
                "mainDealerId": "B10",
                "dealerId": dealer_id,
                "noInvoice": invoice_no,
                "statusShippingList": random.choice(["1", "2", "3"]),
                "createdTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                "unit": units
            }
            dummy_data.append(record)

        current_date += timedelta(days=1)

    return {
        "status": 1,
        "message": None,
        "data": dummy_data
    }


def get_dummy_delivery_process_data(dealer_id: str, from_time: str, to_time: str,
                                   delivery_document_id: str = "", id_spk: str = "",
                                   id_customer: str = "") -> Dict[str, Any]:
    """Generate dummy delivery process data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    deliveries = []

    # Generate 1-3 delivery documents
    num_deliveries = random.randint(1, 3)

    for i in range(num_deliveries):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        delivery_date = from_date + timedelta(days=random_days)

        delivery_doc_id = f"DO/{dealer_id}/{delivery_date.strftime('%d%m%y')}/{1000 + i}"

        # Generate 1-2 delivery details per document
        details = []
        num_details = random.randint(1, 2)

        for j in range(num_details):
            detail = {
                "noSO": f"SO/{dealer_id}/{delivery_date.strftime('%y')}/{delivery_date.strftime('%m')}/{str(j+1).zfill(5)}",
                "idSPK": f"SPK/{dealer_id}/{delivery_date.strftime('%y')}/{delivery_date.strftime('%m')}/{str(j+1).zfill(5)}",
                "noMesin": f"JB22E{random.randint(1000000, 9999999)}",
                "noRangka": f"JB22136K{random.randint(100000, 999999)}",
                "idCustomer": f"{dealer_id}/{delivery_date.strftime('%y')}/{delivery_date.strftime('%m')}/CUS/{str(j+1).zfill(5)}",
                "waktuPengiriman": random.choice(["09.00", "10.30", "14.00", "15.30"]),
                "checklistKelengkapan": random.choice([
                    "Manual Book,Jaket,Kartu Service",
                    "Manual Book,Helm,Toolkit,Kartu Service",
                    "Manual Book,Jaket,Helm,Kartu Service,Toolkit"
                ]),
                "lokasiPengiriman": random.choice([
                    "Jl. Sudirman No. 123 RT 001, RW 002",
                    "Jl. Thamrin No. 456 RT 003, RW 004",
                    "Jl. Gatot Subroto No. 789 RT 005, RW 006"
                ]),
                "latitude": f"{random.uniform(-7.5, -6.0):.6f}",
                "longitude": f"{random.uniform(106.5, 107.5):.6f}",
                "namaPenerima": random.choice([
                    "Amir Nasution", "Budi Santoso", "Citra Dewi",
                    "Dedi Kurniawan", "Eka Sari"
                ]),
                "noKontakPenerima": f"08{random.randint(10000000, 99999999)}",
                "createdTime": delivery_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": delivery_date.strftime("%d/%m/%Y %H:%M:%S")
            }
            details.append(detail)

        delivery = {
            "deliveryDocumentId": delivery_doc_id,
            "tanggalPengiriman": delivery_date.strftime("%d/%m/%Y"),
            "idDriver": random.choice(["Honda ID", "Driver001", "Driver002"]),
            "statusDeliveryDocument": random.choice(["1", "2", "3"]),  # 1=Pending, 2=Delivered, 3=Cancelled
            "dealerId": dealer_id,
            "createdTime": delivery_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": delivery_date.strftime("%d/%m/%Y %H:%M:%S"),
            "detail": details
        }

        deliveries.append(delivery)

    return {
        "status": 1,
        "message": None,
        "data": deliveries
    }


def get_dummy_billing_process_data(dealer_id: str, from_time: str, to_time: str,
                                  id_spk: str = "", id_customer: str = "") -> Dict[str, Any]:
    """Generate dummy billing process data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    invoices = []

    # Generate 1-5 invoices
    num_invoices = random.randint(1, 5)

    for i in range(num_invoices):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        invoice_date = from_date + timedelta(days=random_days)

        invoice = {
            "idInvoice": f"TJ/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(5)}",
            "idSPK": f"SPK/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(5)}",
            "idCustomer": f"{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/CUS/{str(i+1).zfill(5)}",
            "amount": random.randint(15000000, 25000000),  # 15-25 million
            "tipePembayaran": random.choice(["1", "2", "3"]),  # 1=Cash, 2=Credit, 3=Leasing
            "caraBayar": random.choice(["1", "2", "3"]),  # 1=Full, 2=DP, 3=Installment
            "status": random.choice(["1", "2", "3"]),  # 1=Pending, 2=Paid, 3=Cancelled
            "note": random.choice([
                "pembayaran penuh oleh konsumen",
                "pembayaran dengan DP 30%",
                "pembayaran kredit 24 bulan",
                "pembayaran leasing"
            ]),
            "dealerId": dealer_id,
            "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S")
        }

        invoices.append(invoice)

    return {
        "status": 1,
        "message": None,
        "data": invoices
    }


def get_dummy_unit_invoice_data(dealer_id: str, from_time: str, to_time: str,
                               po_id: str = "", no_shipping_list: str = "") -> Dict[str, Any]:
    """Generate dummy unit invoice data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    invoices = []

    # Generate 1-3 invoices
    num_invoices = random.randint(1, 3)

    for i in range(num_invoices):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        invoice_date = from_date + timedelta(days=random_days)
        due_date = invoice_date + timedelta(days=30)  # 30 days payment term

        # Generate 1-3 units per invoice
        units = []
        num_units = random.randint(1, 3)
        total_before_discount = 0
        total_discount = 0

        for j in range(num_units):
            unit_price = random.choice([15000000, 18000000, 20000000, 22000000])  # Various unit prices
            discount = random.randint(100000, 500000)  # 100k-500k discount
            quantity = random.randint(1, 2)

            unit = {
                "kodeTipeUnit": random.choice(["HP3", "HP5", "CB150R", "PCX160"]),
                "kodeWarna": random.choice(["BK", "WH", "RD", "BL"]),  # Black, White, Red, Blue
                "kuantitas": quantity,
                "noMesin": f"JB22E{random.randint(1000000, 9999999)}" if random.choice([True, False]) else "",
                "noRangka": f"JB22136K{random.randint(100000, 999999)}" if random.choice([True, False]) else "",
                "hargaSatuanSebelumDiskon": unit_price,
                "diskonPerUnit": discount,
                "poId": f"PO/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(3)}",
                "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            units.append(unit)
            total_before_discount += unit_price * quantity
            total_discount += discount * quantity

        # Calculate totals
        invoice_discount = random.randint(500000, 1500000)  # Additional invoice discount
        subtotal = total_before_discount - total_discount - invoice_discount
        ppn = subtotal * 0.11  # 11% VAT
        total = subtotal + ppn

        invoice = {
            "noInvoice": f"IN/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(5)}",
            "tanggalInvoice": invoice_date.strftime("%d/%m/%Y"),
            "tanggalJatuhTempo": due_date.strftime("%d/%m/%Y"),
            "mainDealerId": "B10",  # Main dealer code
            "dealerId": dealer_id,
            "totalHargaSebelumDiskon": float(total_before_discount),
            "totalDiskonPerUnit": float(total_discount),
            "potonganPerInvoice": float(invoice_discount),
            "totalPPN": float(ppn),
            "totalHarga": float(total),
            "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "unit": units
        }

        invoices.append(invoice)

    return {
        "status": 1,
        "message": None,
        "data": invoices
    }


def get_dummy_parts_sales_data(dealer_id: str, from_time: str, to_time: str,
                              no_po: str = "") -> Dict[str, Any]:
    """Generate dummy parts sales data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    sales_orders = []

    # Generate 1-3 sales orders
    num_orders = random.randint(1, 3)

    for i in range(num_orders):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        order_date = from_date + timedelta(days=random_days)

        # Generate 1-4 parts per order
        parts = []
        num_parts = random.randint(1, 4)
        total_so = 0

        for j in range(num_parts):
            part_price = random.randint(15000, 50000)  # 15k-50k per part
            quantity = random.randint(1, 3)
            disc_amount = random.randint(0, 5000)  # 0-5k discount
            ppn = int(part_price * quantity * 0.11)  # 11% VAT
            total_part = (part_price * quantity) - disc_amount + ppn

            part = {
                "partsNumber": f"{random.choice(['772A0', '872A0', '972A0'])}{random.choice(['KCJ', 'LDJ', 'MDJ'])}{random.randint(100, 999)}",
                "kuantitas": quantity,
                "hargaParts": part_price,
                "promoIdParts": f"A{random.randint(100000, 999999)}" if random.choice([True, False]) else "",
                "discAmount": disc_amount,
                "discPercentage": f"{(disc_amount/part_price)*100:.1f}" if part_price > 0 else "0.0",
                "ppn": ppn,
                "totalHargaParts": total_part,
                "uangMuka": random.randint(0, total_part//2),  # 0 to half of total
                "bookingIdReference": f"PO/HLO/{random.randint(10000, 99999)}/{order_date.strftime('%y%m')}/{str(j+1).zfill(4)}",
                "createdTime": order_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": order_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            parts.append(part)
            total_so += total_part

        # Calculate SO discount
        so_discount = random.randint(1000, 10000)  # 1k-10k SO discount

        sales_order = {
            "noSO": f"SO/{dealer_id}/{order_date.strftime('%y')}/{order_date.strftime('%m')}/{str(i+1).zfill(5)}",
            "tglSO": order_date.strftime("%d/%m/%Y"),
            "idCustomer": f"{dealer_id}{order_date.strftime('%y%m')}{random.randint(100000, 999999)}",
            "namaCustomer": random.choice([
                "John Doe", "Jane Smith", "Ahmad Rahman", "Siti Nurhaliza",
                "Budi Santoso", "Dewi Sartika", "Eko Prasetyo", "Maya Sari"
            ]),
            "discSO": so_discount,
            "totalHargaSO": total_so - so_discount,
            "dealerId": dealer_id,
            "createdTime": order_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": order_date.strftime("%d/%m/%Y %H:%M:%S"),
            "parts": parts
        }

        sales_orders.append(sales_order)

    return {
        "status": 1,
        "message": None,
        "data": sales_orders
    }


def get_dummy_dp_hlo_data(dealer_id: str, from_time: str, to_time: str,
                         no_work_order: str = "", id_hlo_document: str = "") -> Dict[str, Any]:
    """Generate dummy DP HLO data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    hlo_documents = []

    # Generate 1-2 HLO documents
    num_docs = random.randint(1, 2)

    for i in range(num_docs):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        doc_date = from_date + timedelta(days=random_days)

        # Generate 1-3 parts per document
        parts = []
        num_parts = random.randint(1, 3)

        for j in range(num_parts):
            part_price = random.randint(20000, 60000)  # 20k-60k per part
            quantity = random.randint(1, 2)
            total_part = part_price * quantity
            down_payment = random.randint(0, total_part//3)  # 0 to 1/3 of total
            remaining = total_part - down_payment

            part = {
                "partsNumber": f"{random.choice(['772A0', '872A0', '972A0'])}{random.choice(['KCJ', 'LDJ', 'MDJ'])}{random.randint(100, 999)}",
                "kuantitas": quantity,
                "hargaParts": part_price,
                "totalHargaParts": total_part,
                "uangMuka": down_payment,
                "sisaBayar": remaining,
                "createdTime": doc_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": doc_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            parts.append(part)

        hlo_document = {
            "noInvoiceUangJaminan": f"UJ/{dealer_id}/{doc_date.strftime('%y')}/{doc_date.strftime('%m')}/{str(i+1).zfill(3)}",
            "idHLODocument": f"PO/HLO/{dealer_id}/{doc_date.strftime('%y%m')}/{str(i+1).zfill(4)}",
            "tanggalPemesananHLO": doc_date.strftime("%d/%m/%Y"),
            "noWorkOrder": f"WO/{dealer_id}/{doc_date.strftime('%y')}/{doc_date.strftime('%m')}/{str(i+1).zfill(3)}",
            "idCustomer": f"{dealer_id}{doc_date.strftime('%y%m')}{random.randint(1000, 9999)}",
            "dealerId": dealer_id,
            "createdTime": doc_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": doc_date.strftime("%d/%m/%Y %H:%M:%S"),
            "parts": parts
        }

        hlo_documents.append(hlo_document)

    return {
        "status": 1,
        "message": None,
        "data": hlo_documents
    }


def get_dummy_workshop_invoice_data(dealer_id: str, from_time: str, to_time: str,
                                   no_work_order: str = "") -> Dict[str, Any]:
    """Generate dummy workshop invoice data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    invoices = []

    # Generate 1-2 workshop invoices
    num_invoices = random.randint(1, 2)

    for i in range(num_invoices):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        invoice_date = from_date + timedelta(days=random_days)

        # Generate NJB services (1-3 services)
        njb_services = []
        num_services = random.randint(1, 3)
        total_njb = 0

        for j in range(num_services):
            service_price = random.choice([30000, 50000, 80000, 120000, 180000])  # Common service prices
            disc_amount = random.randint(0, 10000)  # 0-10k discount
            total_service = service_price - disc_amount

            service = {
                "idJob": f"BA{random.randint(100, 999)}",
                "hargaServis": service_price,
                "promoIdJasa": f"PROMO{random.randint(1000, 9999)}" if random.choice([True, False]) else "",
                "discServiceAmount": disc_amount,
                "discServicePercentage": f"{(disc_amount/service_price)*100:.1f}" if service_price > 0 else "0.0",
                "totalHargaServis": total_service,
                "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            njb_services.append(service)
            total_njb += total_service

        # Generate NSC parts (1-4 parts)
        nsc_parts = []
        num_parts = random.randint(1, 4)
        total_nsc = 0

        for k in range(num_parts):
            part_price = random.randint(15000, 50000)  # 15k-50k per part
            quantity = random.randint(1, 3)
            disc_amount = random.randint(0, 5000)  # 0-5k discount
            ppn = int((part_price * quantity - disc_amount) * 0.11)  # 11% VAT
            total_part = (part_price * quantity) - disc_amount + ppn
            down_payment = random.randint(0, total_part//2)  # 0 to half of total

            part = {
                "idJob": njb_services[k % len(njb_services)]["idJob"],  # Link to a service
                "partsNumber": f"{random.choice(['772A0', '872A0', '972A0'])}{random.choice(['KCJ', 'LDJ', 'MDJ'])}{random.randint(100, 999)}",
                "kuantitas": quantity,
                "hargaParts": part_price,
                "promoIdParts": f"{random.randint(10000, 99999)}" if random.choice([True, False]) else "",
                "discPartsAmount": disc_amount,
                "discPartsPercentage": f"{(disc_amount/(part_price*quantity))*100:.1f}" if part_price > 0 else "0.0",
                "ppn": ppn,
                "totalHargaParts": total_part,
                "uangMuka": down_payment,
                "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            nsc_parts.append(part)
            total_nsc += total_part

        invoice = {
            "noWorkOrder": f"WO/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(3)}",
            "noNJB": f"NJB/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(4)}",
            "tanggalNJB": invoice_date.strftime("%d/%m/%Y"),
            "totalHargaNJB": total_njb,
            "noNSC": f"NSC/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(4)}",
            "tanggalNSC": invoice_date.strftime("%d/%m/%Y"),
            "totalHargaNSC": total_nsc,
            "hondaIdSA": f"{random.randint(100000, 999999)}",
            "hondaIdMekanik": f"{random.randint(100000, 999999)}",
            "dealerId": dealer_id,
            "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "njb": njb_services,
            "nsc": nsc_parts
        }

        invoices.append(invoice)

    return {
        "status": 1,
        "message": None,
        "data": invoices
    }


def get_dummy_unpaid_hlo_data(dealer_id: str, from_time: str, to_time: str,
                             no_work_order: str = "", id_hlo_document: str = "") -> Dict[str, Any]:
    """Generate dummy unpaid HLO data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    hlo_documents = []

    # Generate 1-2 unpaid HLO documents
    num_docs = random.randint(1, 2)

    for i in range(num_docs):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        doc_date = from_date + timedelta(days=random_days)

        # Generate customer data
        customer_names = ["Amir Nasution", "Sari Dewi", "Bambang Sutrisno", "Maya Sari", "Andi Rahman"]
        provinces = ["3100", "3200", "3300", "3400", "3500"]  # Jakarta, Jabar, Jateng, DIY, Jatim
        cities = ["3101", "3201", "3301", "3401", "3501"]

        # Generate 1-3 parts per document
        parts = []
        num_parts = random.randint(1, 3)

        for j in range(num_parts):
            part_price = random.randint(20000, 60000)  # 20k-60k per part
            quantity = random.randint(1, 2)
            total_part = part_price * quantity
            down_payment = random.randint(0, total_part//3)  # 0 to 1/3 of total
            remaining = total_part - down_payment

            part = {
                "partsNumber": f"{random.choice(['772A0', '872A0', '972A0'])}{random.choice(['KCJ', 'LDJ', 'MDJ'])}{random.randint(100, 999)}",
                "kuantitas": quantity,
                "hargaParts": part_price,
                "totalHargaParts": total_part,
                "uangMuka": down_payment,
                "sisaBayar": remaining,
                "createdTime": doc_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": doc_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            parts.append(part)

        hlo_document = {
            "idHLODocument": f"PO/HLO/{dealer_id}/{doc_date.strftime('%y%m')}/{str(i+1).zfill(4)}",
            "tanggalPemesananHLO": doc_date.strftime("%d/%m/%Y"),
            "noWorkOrder": f"WO/{dealer_id}/{doc_date.strftime('%y')}/{doc_date.strftime('%m')}/{str(i+1).zfill(3)}",
            "noBukuClaimC2": f"BA{random.randint(100, 999)}",
            "noKTP": f"{random.randint(1000000000000000, 9999999999999999)}",
            "namaCustomer": random.choice(customer_names),
            "alamat": f"Jl. {random.choice(['Sudirman', 'Thamrin', 'Gatot Subroto', 'Kuningan', 'Senayan'])} No. {random.randint(1, 100)} RT {random.randint(1, 10):03d}, RW {random.randint(1, 20):03d}",
            "kodePropinsi": random.choice(provinces),
            "kodeKota": random.choice(cities),
            "kodeKecamatan": f"{random.choice(cities)}{random.randint(10, 99)}",
            "kodeKelurahan": f"{random.choice(cities)}{random.randint(10, 99)}{random.randint(1000, 9999)}",
            "kodePos": f"{random.randint(10000, 99999)}",
            "noKontak": f"081{random.randint(10000000, 99999999)}",
            "kodeTipeUnit": random.choice(["HP5", "PCX160", "VARIO125", "VARIO150", "BEAT"]),
            "tahunMotor": str(random.randint(2020, 2024)),
            "noMesin": f"JB22E{random.randint(1000000, 9999999)}",
            "noRangka": f"JB22136K{random.randint(100000, 999999)}",
            "flagNumbering": str(random.randint(0, 1)),
            "vehicleOffRoad": str(random.randint(0, 1)),
            "jobReturn": str(random.randint(0, 1)),
            "dealerId": dealer_id,
            "createdTime": doc_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": doc_date.strftime("%d/%m/%Y %H:%M:%S"),
            "parts": parts
        }

        hlo_documents.append(hlo_document)

    return {
        "status": 1,
        "message": None,
        "data": hlo_documents
    }


def get_dummy_parts_invoice_data(dealer_id: str, from_time: str, to_time: str,
                                no_po: str = "") -> Dict[str, Any]:
    """Generate dummy parts invoice data for testing"""

    # Parse date range for realistic data generation
    from_date = datetime.strptime(from_time.split()[0], "%Y-%m-%d")
    to_date = datetime.strptime(to_time.split()[0], "%Y-%m-%d")

    invoices = []

    # Generate 1-2 parts invoices
    num_invoices = random.randint(1, 2)

    for i in range(num_invoices):
        # Generate random date within range
        random_days = random.randint(0, (to_date - from_date).days)
        invoice_date = from_date + timedelta(days=random_days)
        due_date = invoice_date + timedelta(days=30)  # 30 days payment term

        # Generate 2-4 parts per invoice
        parts = []
        num_parts = random.randint(2, 4)
        total_before_discount = 0
        total_discount = 0

        for j in range(num_parts):
            unit_price = random.choice([150000, 200000, 250000, 300000])  # Various part prices
            quantity = random.randint(1, 3)
            discount = random.randint(10000, 30000)  # 10k-30k discount per part

            part = {
                "noPO": f"PO{random.randint(100000, 999999)}",
                "jenisOrder": str(random.choice([1, 2, 3])),  # Order type
                "partsNumber": f"{random.choice(['272A0', '372A0', '472A0'])}{random.choice(['KCJ', 'LDJ', 'MDJ'])}{random.randint(100, 999)}",
                "kuantitas": quantity,
                "uom": "pcs",
                "hargaSatuanSebelumDiskon": float(unit_price),
                "diskonPerPartsNumber": float(discount),
                "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
                "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S")
            }

            parts.append(part)
            total_before_discount += unit_price * quantity
            total_discount += discount * quantity

        # Calculate totals
        invoice_discount = random.randint(20000, 50000)  # Additional invoice discount
        subtotal = total_before_discount - total_discount - invoice_discount
        ppn = subtotal * 0.11  # 11% VAT
        total = subtotal + ppn

        invoice = {
            "noInvoice": f"IN/{dealer_id}/{invoice_date.strftime('%y')}/{invoice_date.strftime('%m')}/{str(i+1).zfill(5)}",
            "tglInvoice": invoice_date.strftime("%d/%m/%Y"),
            "tglJatuhTempo": due_date.strftime("%d/%m/%Y"),
            "mainDealerId": "B10",  # Main dealer code
            "dealerId": dealer_id,
            "totalHargaSebelumDiskon": float(total_before_discount),
            "totalDiskonPerPartsNumber": float(total_discount),
            "potonganPerInvoice": float(invoice_discount),
            "totalPPN": float(ppn),
            "totalHarga": float(total),
            "createdTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "modifiedTime": invoice_date.strftime("%d/%m/%Y %H:%M:%S"),
            "parts": parts
        }

        invoices.append(invoice)

    return {
        "status": 1,
        "message": None,
        "data": invoices
    }
