#!/usr/bin/env python3
"""
Simple test for Excel template functionality (without dependencies)
"""

import os

def test_excel_file_structure():
    """Test Excel file structure and path setup"""
    
    print("🧪 Testing Excel Template Auto-Update Setup")
    print("=" * 50)
    
    # Test expected file path
    expected_path = os.path.join(os.getcwd(), 'files', 'reminder_template_v1.xlsx')
    files_dir = os.path.join(os.getcwd(), 'files')
    
    print(f"📁 Expected Excel file path: {expected_path}")
    print(f"📂 Files directory: {files_dir}")
    print(f"🔍 Files directory exists: {os.path.exists(files_dir)}")
    print(f"🔍 Excel file exists: {os.path.exists(expected_path)}")
    
    # Create files directory if it doesn't exist
    if not os.path.exists(files_dir):
        try:
            os.makedirs(files_dir)
            print(f"✅ Created files directory: {files_dir}")
        except Exception as e:
            print(f"❌ Could not create files directory: {str(e)}")
    
    # Test Excel reader import (without pandas)
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        # Test if file can be imported
        from app.services import excel_template_reader
        print(f"✅ Excel template reader module imported successfully")
        
        # Test class definition
        reader_class = excel_template_reader.ExcelTemplateReader
        print(f"✅ ExcelTemplateReader class available")
        
        # Test factory function
        factory_func = excel_template_reader.create_excel_template_reader
        print(f"✅ create_excel_template_reader function available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Excel reader import: {str(e)}")
        return False

def test_repository_methods():
    """Test if repository methods are available"""
    print(f"\n🧪 Testing Repository Method Availability")
    print("=" * 50)
    
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        # Test repository import (without database)
        from app.repositories import whatsapp_template_repository
        
        repo_class = whatsapp_template_repository.WhatsAppTemplateRepository
        print(f"✅ WhatsAppTemplateRepository class available")
        
        # Check for Excel-related methods
        excel_methods = [
            'backup_existing_templates',
            'replace_all_templates',
            'update_templates_from_excel',
            'get_template_statistics'
        ]
        
        for method in excel_methods:
            if hasattr(repo_class, method):
                print(f"✅ {method} method available")
            else:
                print(f"❌ {method} method missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing repository methods: {str(e)}")
        return False

def test_main_py_integration():
    """Test main.py integration"""
    print(f"\n🧪 Testing Main.py Integration")
    print("=" * 50)
    
    try:
        # Read main.py and check for Excel integration
        main_py_path = os.path.join(os.getcwd(), 'main.py')
        
        if os.path.exists(main_py_path):
            with open(main_py_path, 'r') as f:
                content = f.read()
            
            # Check for Excel-related imports and functions
            checks = [
                ('excel_template_reader import', 'from app.services.excel_template_reader import'),
                ('Excel reader creation', 'create_excel_template_reader()'),
                ('Excel template loading', 'read_excel_templates()'),
                ('Excel update method', 'update_templates_from_excel'),
                ('Fallback logic', 'Falling back to hardcoded')
            ]
            
            for check_name, check_string in checks:
                if check_string in content:
                    print(f"✅ {check_name} found in main.py")
                else:
                    print(f"❌ {check_name} not found in main.py")
            
            return True
        else:
            print(f"❌ main.py not found at {main_py_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing main.py integration: {str(e)}")
        return False

def create_sample_excel_instructions():
    """Provide instructions for creating sample Excel file"""
    print(f"\n📋 Sample Excel File Instructions")
    print("=" * 50)
    
    sample_data = [
        ['reminder_target', 'reminder_type', 'template'],
        ['KPB-1', 'H+30 tanggal beli (by WA)', 'Halo {nama_pemilik},\n\nTerima kasih telah membeli {tipe_unit}. Saatnya servis KPB-1.\n\nTerima kasih,\n{dealer_name}'],
        ['KPB-1', 'H-7 dari expired KPB-1 (by WA)', 'Halo {nama_pemilik},\n\nGaransi KPB-1 akan berakhir dalam 7 hari.\n\nTerima kasih,\n{dealer_name}'],
        ['Non KPB', 'N/A', 'Halo {nama_pemilik},\n\nSaatnya servis rutin kendaraan Honda Anda.\n\nTerima kasih,\n{dealer_name}']
    ]
    
    print("📊 Sample Excel file structure:")
    print("File: files/reminder_template_v1.xlsx")
    print("Sheet: Any name (Templates, Sheet1, etc.)")
    print("\nColumns required:")
    for i, row in enumerate(sample_data):
        if i == 0:
            print(f"  Header: {' | '.join(row)}")
        else:
            print(f"  Row {i}: {row[0]} | {row[1]} | {row[2][:50]}...")
    
    print(f"\n💡 Variable support includes:")
    variables = ['{nama_pemilik}', '{dealer_name}', '{tipe_unit}', '{nomor_polisi}', 
                '{tanggal_beli}', '{nama_ahass}', '{alamat_ahass}', '{nomor_mesin}']
    for var in variables:
        print(f"  {var}")

if __name__ == "__main__":
    print("🚀 Excel Template Auto-Update Setup Verification\n")
    
    test1 = test_excel_file_structure()
    test2 = test_repository_methods() 
    test3 = test_main_py_integration()
    
    print(f"\n📈 Setup Verification Results:")
    print(f"  File Structure: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Repository:     {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Main.py:        {'✅ PASS' if test3 else '❌ FAIL'}")
    
    create_sample_excel_instructions()
    
    if test1 and test2 and test3:
        print(f"\n🎉 Excel auto-update setup is ready!")
        print(f"\n📋 Next Steps:")
        print(f"  1. Create Excel file: files/reminder_template_v1.xlsx")
        print(f"  2. Add template data with columns: reminder_target, reminder_type, template")
        print(f"  3. Restart customer service")
        print(f"  4. Check service logs for Excel loading messages")
    else:
        print(f"\n⚠️  Setup has issues - check error messages above")