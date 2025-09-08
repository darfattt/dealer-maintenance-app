#!/usr/bin/env python3
"""
Test script to validate all required modules can be imported
This script should be run inside the Docker container to verify dependencies
"""

import sys
import os

def test_imports():
    """Test all required module imports"""
    results = []
    
    # Test standard library imports
    try:
        import io
        import datetime
        from typing import List, Dict, Any, Optional
        results.append("✅ Standard library imports - OK")
    except ImportError as e:
        results.append(f"❌ Standard library imports - FAILED: {e}")
    
    # Test pandas import
    try:
        import pandas as pd
        results.append(f"✅ pandas {pd.__version__} - OK")
    except ImportError as e:
        results.append(f"❌ pandas - FAILED: {e}")
    
    # Test openpyxl import
    try:
        import openpyxl
        results.append(f"✅ openpyxl {openpyxl.__version__} - OK")
    except ImportError as e:
        results.append(f"❌ openpyxl - FAILED: {e}")
    
    # Test FastAPI imports
    try:
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.responses import StreamingResponse
        results.append("✅ FastAPI imports - OK")
    except ImportError as e:
        results.append(f"❌ FastAPI imports - FAILED: {e}")
    
    # Test SQLAlchemy imports
    try:
        from sqlalchemy import text, func
        from sqlalchemy.orm import Session
        results.append("✅ SQLAlchemy imports - OK")
    except ImportError as e:
        results.append(f"❌ SQLAlchemy imports - FAILED: {e}")
    
    # Test Pydantic imports
    try:
        from pydantic import BaseModel, Field
        results.append("✅ Pydantic imports - OK")
    except ImportError as e:
        results.append(f"❌ Pydantic imports - FAILED: {e}")
    
    # Test utils import (if available)
    try:
        utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../utils'))
        if utils_path not in sys.path:
            sys.path.append(utils_path)
        
        from utils.logger import setup_logger
        results.append("✅ utils.logger import - OK")
    except ImportError as e:
        results.append(f"❌ utils.logger import - FAILED: {e}")
    
    return results

if __name__ == "__main__":
    print("=" * 50)
    print("Dashboard Dealer Service - Dependencies Test")
    print("=" * 50)
    
    results = test_imports()
    
    for result in results:
        print(result)
    
    print("=" * 50)
    
    # Check if all tests passed
    failed_tests = [r for r in results if "❌" in r]
    if failed_tests:
        print(f"❌ {len(failed_tests)} test(s) failed!")
        sys.exit(1)
    else:
        print("✅ All dependency tests passed!")
        sys.exit(0)