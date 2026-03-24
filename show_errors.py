"""
Minimal diagnostic view - shows exact error
"""
from django.http import HttpResponse
import traceback
import sys

def show_errors(request):
    """Display any import or configuration errors"""
    errors = []
    
    # Test imports
    try:
        from workplace_system import urls
        errors.append("✓ URLs import OK")
    except Exception as e:
        errors.append(f"✗ URLs Error: {str(e)}")
        errors.append(traceback.format_exc())
    
    try:
        from system_owner_panel import system_owner_dashboard
        errors.append("✓ system_owner_panel import OK")
    except Exception as e:
        errors.append(f"✗ system_owner_panel Error: {str(e)}")
        errors.append(traceback.format_exc())
    
    try:
        from dev_mode_access import dev_login
        errors.append("✓ dev_mode_access import OK")
    except Exception as e:
        errors.append(f"✗ dev_mode_access Error: {str(e)}")
        errors.append(traceback.format_exc())
    
    # Show Python path
    errors.append(f"\nPython Path: {sys.path}")
    
    return HttpResponse("<pre>" + "\n".join(errors) + "</pre>", content_type="text/html")
