#!/usr/bin/env python3
"""
Fix common pandas DataFrame boolean evaluation issues in Streamlit apps
"""

import re
import os

def fix_pandas_boolean_issues():
    """Fix pandas DataFrame boolean evaluation issues"""
    
    files_to_fix = ['dashboard_analytics.py', 'admin_app.py']
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            continue
            
        print(f"🔧 Checking {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix pattern: if dataframe_variable:
        # Replace with: if len(dataframe_variable) > 0:
        patterns_to_fix = [
            (r'if\s+(\w+):\s*\n(\s+)(\w+\s*=\s*\1\.iloc\[0\])', 
             r'if len(\1) > 0:\n\2\3'),
            
            (r'if\s+(\w+):\s*\n(\s+)(st\.)', 
             r'if len(\1) > 0:\n\2\3'),
             
            (r'(\w+)\s*=\s*(\w+)\.iloc\[0\]\s+if\s+len\(\2\)\s*>\s*0\s+else\s+None\s*\n\s*if\s+\1:',
             r'if len(\2) > 0:\n    \1 = \2.iloc[0]'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Additional specific fixes
        content = content.replace(
            'last_fetch = df_logs.iloc[0] if len(df_logs) > 0 else None\n        if last_fetch:',
            'if len(df_logs) > 0:\n            last_fetch = df_logs.iloc[0]'
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed pandas issues in {file_path}")
        else:
            print(f"✅ No pandas issues found in {file_path}")

def add_pandas_safety_imports():
    """Add safety imports and configurations for pandas"""
    
    safety_code = '''
# Pandas configuration for Streamlit compatibility
import pandas as pd
pd.options.mode.chained_assignment = None  # Disable SettingWithCopyWarning

# Helper function for safe DataFrame boolean evaluation
def is_dataframe_empty(df):
    """Safely check if DataFrame is empty"""
    return df is None or len(df) == 0

def safe_iloc(df, index=0, default=None):
    """Safely get iloc with fallback"""
    if df is None or len(df) == 0:
        return default
    return df.iloc[index]
'''
    
    files_to_update = ['dashboard_analytics.py', 'admin_app.py']
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if safety code already exists
        if 'def is_dataframe_empty' in content:
            print(f"✅ Safety functions already exist in {file_path}")
            continue
        
        # Find the import section and add safety code
        import_section_end = content.find('\n\n# ')
        if import_section_end == -1:
            import_section_end = content.find('\n\n@')
        if import_section_end == -1:
            import_section_end = content.find('\n\n#')
        
        if import_section_end != -1:
            new_content = content[:import_section_end] + safety_code + content[import_section_end:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Added safety functions to {file_path}")

def main():
    """Main function to fix pandas issues"""
    print("🔧 Fixing pandas DataFrame boolean evaluation issues...")
    print("=" * 50)
    
    fix_pandas_boolean_issues()
    print()
    add_pandas_safety_imports()
    
    print()
    print("✅ Pandas fixes completed!")
    print()
    print("🔄 Restart your Streamlit apps to apply the fixes:")
    print("   - Analytics Dashboard: streamlit run dashboard_analytics.py --server.port 8501")
    print("   - Admin Panel: streamlit run admin_app.py --server.port 8502")

if __name__ == "__main__":
    main()
