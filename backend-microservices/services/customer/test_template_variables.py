#!/usr/bin/env python3
"""
Test script for enhanced WhatsApp template variable support
"""

import sys
import os
from datetime import date

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.whatsapp_template import WhatsAppTemplate
from app.schemas.customer_reminder_request import BulkReminderCustomerData

def test_enhanced_template_variables():
    """Test enhanced template variable support"""
    
    print("🧪 Testing Enhanced WhatsApp Template Variables")
    print("=" * 50)
    
    # Create a sample template with various variables
    template = WhatsAppTemplate(
        reminder_target="KPB-1",
        reminder_type="H+30 tanggal beli (by WA)",
        template="""Halo {nama_pemilik},

Terima kasih telah membeli {tipe_unit} dengan nomor polisi {nomor_polisi} pada tanggal {tanggal_beli}.

Saatnya untuk melakukan servis KPB-1 di {nama_ahass} ({kode_ahass}).
Alamat: {alamat_ahass}

Kendaraan dengan nomor mesin {nomor_mesin} perlu diservies sebelum tanggal {tanggal_expired_kpb}.

Untuk informasi lebih lanjut, silakan hubungi {dealer_name}.

Terima kasih,
Tim {dealer_name}"""
    )
    
    # Create sample customer data
    sample_data = {
        'nama_pemilik': 'Budi Santoso',
        'nama_pembawa': 'Andi Wijaya',
        'nomor_telepon_pelanggan': '081234567890',
        'no_telepon_pembawa': '081987654321',
        'nomor_mesin': 'JB22E1572318',
        'nomor_polisi': 'D 1234 ABC',
        'tipe_unit': 'VARIO 125 CBS ISS',
        'tanggal_beli': date(2024, 6, 15),
        'tanggal_expired_kpb': date(2025, 8, 15),
        'kode_ahass': '00999',
        'nama_ahass': 'Daya Adicipta Motora',
        'alamat_ahass': 'Jl Cibereum no 26',
        'dealer_name': 'Honda Cibinong'
    }
    
    print("📝 Template:")
    print(template.template)
    print("\n" + "=" * 50)
    
    print("📊 Sample Data:")
    for key, value in sample_data.items():
        print(f"  {key}: {value}")
    print("\n" + "=" * 50)
    
    # Test template formatting
    try:
        formatted_message = template.format_template(**sample_data)
        print("✅ Formatted Message:")
        print(formatted_message)
        print("\n" + "=" * 50)
        
        # Test with missing data
        print("🔍 Testing with missing data...")
        incomplete_data = {
            'nama_pemilik': 'John Doe',
            'dealer_name': 'Honda Test'
            # Missing most fields
        }
        
        formatted_with_missing = template.format_template(**incomplete_data)
        print("✅ Formatted Message with Missing Data:")
        print(formatted_with_missing)
        print("\n" + "=" * 50)
        
        # Test date formatting
        print("📅 Testing date formatting...")
        date_test_data = {
            'nama_pemilik': 'Test User',
            'tanggal_beli': '2024-12-25',  # String date
            'tanggal_expired_kpb': date(2025, 3, 15),  # Date object
            'dealer_name': 'Honda Test'
        }
        
        date_template = WhatsAppTemplate(
            reminder_target="Test",
            reminder_type="Date Test",
            template="Halo {nama_pemilik}, tanggal beli: {tanggal_beli}, expired: {tanggal_expired_kpb}"
        )
        
        formatted_dates = date_template.format_template(**date_test_data)
        print("✅ Date Formatting Test:")
        print(formatted_dates)
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_bulk_reminder_customer_data():
    """Test with BulkReminderCustomerData object"""
    print("\n" + "=" * 50)
    print("🧪 Testing with BulkReminderCustomerData object")
    
    try:
        # Create BulkReminderCustomerData object
        customer_data = BulkReminderCustomerData(
            nama_pemilik="Siti Nurhaliza",
            nama_pelanggan="Siti Nurhaliza", 
            nomor_telepon_pelanggan="081234567890",
            nama_pembawa="Ahmad Rahman",
            no_telepon_pembawa="081987654321",
            nomor_mesin="KC12E9876543",
            nomor_polisi="B 5678 XYZ",
            tipe_unit="PCX 160 CBS",
            tanggal_beli="2024-01-15",
            tanggal_expired_kpb="2025-03-15"
        )
        
        template = WhatsAppTemplate(
            reminder_target="KPB-2", 
            reminder_type="H-30 dari expired KPB-2 (by WA)",
            template="""Halo {nama_pemilik},

Kendaraan {tipe_unit} dengan nomor polisi {nomor_polisi} akan habis masa garansi KPB-2 pada {tanggal_expired_kpb}.

Segera lakukan servis di dealer terdekat.

Salam,
{dealer_name}"""
        )
        
        # Test formatting
        from app.repositories.whatsapp_template_repository import WhatsAppTemplateRepository
        
        # Extract data using the repository method
        extracted = WhatsAppTemplateRepository._extract_customer_data_dict(customer_data)
        extracted['dealer_name'] = 'Honda Jakarta'
        
        formatted = template.format_template(**extracted)
        print("✅ BulkReminderCustomerData Formatting:")
        print(formatted)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing BulkReminderCustomerData: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_enhanced_template_variables()
    success2 = test_bulk_reminder_customer_data()
    
    if success1 and success2:
        print("\n🎯 All template variable tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)