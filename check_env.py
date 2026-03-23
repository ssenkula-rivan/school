#!/usr/bin/env python3
"""
Check environment variables and database configuration
"""
import os

def check_environment():
    """Check all relevant environment variables"""
    print("🔍 Environment Variables Check:")
    print("=" * 50)
    
    # Database settings
    database_url = os.environ.get('DATABASE_URL')
    print(f"DATABASE_URL: {'✅ Set' if database_url else '❌ Not set'}")
    if database_url:
        # Hide password in output
        safe_url = database_url.split('@')[-1] if '@' in database_url else database_url
        print(f"  Connection: ...@{safe_url}")
    
    # Django settings
    debug = os.environ.get('DEBUG', 'Not set')
    secret_key = os.environ.get('SECRET_KEY', 'Not set')
    print(f"DEBUG: {debug}")
    print(f"SECRET_KEY: {'✅ Set' if secret_key != 'Not set' else '❌ Not set'}")
    
    # Production settings
    allowed_hosts = os.environ.get('ALLOWED_HOSTS', 'Not set')
    csrf_trusted = os.environ.get('CSRF_TRUSTED_ORIGINS', 'Not set')
    print(f"ALLOWED_HOSTS: {allowed_hosts}")
    print(f"CSRF_TRUSTED_ORIGINS: {csrf_trusted}")
    
    # Check for local database files
    print("\n🗄️ Local Database Files:")
    import glob
    db_files = glob.glob('*.db')
    if db_files:
        for db_file in db_files:
            size = os.path.getsize(db_file)
            print(f"  ✅ {db_file} ({size} bytes)")
    else:
        print("  ❌ No local SQLite database files found")
    
    # Check if we're in production
    print("\n🚀 Deployment Info:")
    environment = os.environ.get('ENVIRONMENT', 'development')
    print(f"Environment: {environment}")
    
    # Render specific
    render_service_id = os.environ.get('RENDER_SERVICE_ID', 'Not set')
    render_external_url = os.environ.get('RENDER_EXTERNAL_URL', 'Not set')
    print(f"Render Service ID: {render_service_id}")
    print(f"Render External URL: {render_external_url}")

if __name__ == "__main__":
    check_environment()
