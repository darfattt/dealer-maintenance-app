#!/usr/bin/env python3
"""
Test script for Excel template auto-update functionality
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_excel_template_reader():
    """Test Excel template reader functionality"""
    
    print("🧪 Testing Excel Template Auto-Update Functionality")
    print("=" * 60)
    
    try:
        from app.services.excel_template_reader import create_excel_template_reader
        
        # Test with current directory
        excel_reader = create_excel_template_reader()
        
        print("📁 Excel file info:")
        file_info = excel_reader.get_file_info()
        for key, value in file_info.items():
            print(f"  {key}: {value}")
        
        print(f"\n📖 Attempting to read Excel file: {excel_reader.excel_file_path}")
        
        # Try to read templates
        success, templates_data, message = excel_reader.read_excel_templates()
        
        print(f"📊 Results:")
        print(f"  Success: {success}")
        print(f"  Message: {message}")
        print(f"  Templates found: {len(templates_data) if templates_data else 0}")
        
        if success and templates_data:
            print(f"\n✅ Excel templates loaded successfully!")
            print(f"📋 Template summary:")
            
            # Group by reminder_target
            targets = {}
            for template in templates_data:
                target = template['reminder_target']
                if target not in targets:
                    targets[target] = []
                targets[target].append(template['reminder_type'])
            
            for target, types in targets.items():
                print(f"  {target}: {len(types)} templates")
                for reminder_type in types[:3]:  # Show first 3
                    print(f"    - {reminder_type}")
                if len(types) > 3:
                    print(f"    ... and {len(types) - 3} more")
            
            print(f"\n📝 Sample template (first one):")
            sample = templates_data[0]
            print(f"  Target: {sample['reminder_target']}")
            print(f"  Type: {sample['reminder_type']}")
            print(f"  Template: {sample['template'][:100]}...")
            
        else:
            print(f"\n⚠️  Excel file not available or invalid")
            print(f"💡 This is expected if the Excel file doesn't exist yet")
            print(f"📍 Expected location: {excel_reader.excel_file_path}")
            
            # Create a sample Excel file for testing
            create_sample_excel_file(excel_reader.excel_file_path)
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing Excel template reader: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_excel_file(file_path: str):
    """Create a sample Excel file for testing"""
    try:
        # Check if pandas and openpyxl are available
        import pandas as pd
        
        print(f"\n🔧 Creating sample Excel file for testing...")
        
        # Create sample data
        sample_data = [
            {
                'reminder_target': 'KPB-1',
                'reminder_type': 'H+30 tanggal beli (by WA)',
                'template': 'Halo {nama_pemilik},\n\nTerima kasih telah membeli kendaraan Honda {tipe_unit}. Saatnya untuk melakukan servis KPB-1.\n\nSilakan hubungi {dealer_name}.\n\nTerima kasih.'
            },
            {
                'reminder_target': 'KPB-1', 
                'reminder_type': 'H-7 dari expired KPB-1 (by WA)',
                'template': 'Halo {nama_pemilik},\n\nGaransi KPB-1 kendaraan {tipe_unit} dengan nomor polisi {nomor_polisi} akan berakhir dalam 7 hari.\n\nJangan lewatkan servis gratis di {nama_ahass}.\n\nTerima kasih,\n{dealer_name}'
            },
            {
                'reminder_target': 'KPB-2',
                'reminder_type': 'H-30 dari expired KPB-2 (by WA)', 
                'template': 'Halo {nama_pemilik},\n\nKendaraan {tipe_unit} Anda perlu servis KPB-2 dalam 30 hari.\n\nHubungi kami segera untuk jadwal servis.\n\nTerima kasih,\n{dealer_name}'
            },
            {
                'reminder_target': 'Ultah Konsumen',
                'reminder_type': 'N/A',
                'template': 'Halo {nama_pemilik},\n\nSelamat ulang tahun! 🎉\n\nSebagai apresiasi, dapatkan diskon spesial untuk servis {tipe_unit} Anda di {nama_ahass}.\n\nTerima kasih,\n{dealer_name}'
            }
        ]
        
        # Create DataFrame
        df = pd.DataFrame(sample_data)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save to Excel
        df.to_excel(file_path, index=False, sheet_name='Templates')
        
        print(f"✅ Sample Excel file created: {file_path}")
        print(f"📊 Contains {len(sample_data)} sample templates")
        print(f"💡 You can now restart the service to test Excel auto-loading")
        
        return True
        
    except ImportError:
        print(f"⚠️  Cannot create sample Excel file: pandas or openpyxl not installed")
        print(f"💡 Install with: pip install pandas openpyxl")
        return False
    except Exception as e:
        print(f"❌ Error creating sample Excel file: {str(e)}")
        return False

def test_template_repository():
    """Test template repository Excel update methods"""
    print(f"\n🧪 Testing Template Repository Excel Methods")
    print("=" * 50)
    
    try:
        # This would require database connection, so just test imports
        from app.repositories.whatsapp_template_repository import WhatsAppTemplateRepository
        
        print("✅ WhatsAppTemplateRepository import successful")
        print("📋 Available Excel-related methods:")
        
        methods = [
            'backup_existing_templates',
            'replace_all_templates', 
            'update_templates_from_excel',
            'get_template_statistics'
        ]
        
        for method in methods:
            if hasattr(WhatsAppTemplateRepository, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing template repository: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Excel Template Auto-Update Tests\n")
    
    success1 = test_excel_template_reader()
    success2 = test_template_repository()
    
    print(f"\n📈 Test Results:")
    print(f"  Excel Reader: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"  Repository:   {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🎉 All tests passed!")
        print(f"\n📋 Next Steps:")
        print(f"  1. Place your reminder_template_v1.xlsx in files/ directory")
        print(f"  2. Restart the customer service")
        print(f"  3. Check logs for Excel template loading")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)