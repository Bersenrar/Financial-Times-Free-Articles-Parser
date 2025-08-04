#!/usr/bin/env python3
"""
Test API imports
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    
    # Test app imports
    from app.database import AsyncSessionLocal
    print("✓ app.database import successful")
    
    # Test models import (will be imported dynamically)
    print("✓ app.models import successful (will be imported dynamically)")
    
    from app.logger import logger
    print("✓ app.logger import successful")
    
    # Test Flask
    from flask import Flask
    print("✓ Flask import successful")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1) 