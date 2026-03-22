#!/usr/bin/env python3
"""
Reset system to defaults - remove all password issues
Creates clean admin account with known credentials
"""
import os
import sys
import django

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
    django.setup()

def reset_system_to_defaults():
    """Reset system to clean defaults"""
    try:
        from django.contrib.auth.models import User
        from django.db import connection
        
        print("🔄 RESETTING SYSTEM TO DEFAULTS")
        print("=" * 40)
        
        # Delete all existing users
        User.objects.all().delete()
        print("✅ Deleted all existing users")
        
        # Create clean admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='admin123',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        print("✅ Created clean admin user")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@school.com")
        
        # Clear all sessions
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_session;")
        print("✅ Cleared all sessions")
        
        print("\n🎉 SYSTEM RESET COMPLETE")
        print("=" * 30)
        print("🌐 Login URL: https://school-management-c-8qtq.onrender.com/accounts/login/")
        print("👤 Username: admin")
        print("🔐 Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    setup_django()
    success = reset_system_to_defaults()
    sys.exit(0 if success else 1)
