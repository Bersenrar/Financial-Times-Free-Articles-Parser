#!/usr/bin/env python3
"""
Test API startup
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing API startup...")
    
    # Import the API app
    from api.app import app
    
    print("✓ API app imported successfully")
    
    # Test basic Flask functionality
    with app.test_client() as client:
        response = client.get('/api/articles/stats')
        print(f"✓ API health check response: {response.status_code}")
    
    print("API startup test successful!")
    
except Exception as e:
    print(f"API startup error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 