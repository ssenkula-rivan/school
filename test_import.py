#!/usr/bin/env python3
"""Test if accounts.views.register can be imported"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
django.setup()

try:
    from accounts.views import register
    print("✅ SUCCESS: accounts.views.register imported successfully")
    print(f"Function: {register}")
    print(f"Function name: {register.__name__}")
    print(f"Function doc: {register.__doc__}")
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
except AttributeError as e:
    print(f"❌ ATTRIBUTE ERROR: {e}")
except Exception as e:
    print(f"❌ OTHER ERROR: {e}")

# Test all views functions
try:
    from accounts import views
    print("\n📋 Available functions in accounts.views:")
    for attr in dir(views):
        if callable(getattr(views, attr)) and not attr.startswith('_'):
            print(f"  - {attr}")
except Exception as e:
    print(f"❌ Error listing views: {e}")
