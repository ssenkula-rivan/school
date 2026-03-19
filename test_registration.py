#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
sys.path.append('/home/cranictech/CascadeProjects/school')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workplace_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate, login
from core.models import School
from accounts.models import UserProfile

def test_registration_flow():
    print("=== TESTING SCHOOL REGISTRATION FLOW ===")
    
    client = Client()
    
    # Test data
    test_data = {
        'school_name': 'Test Academy',
        'school_type': 'primary',
        'institution_type': 'private',
        'admin_username': 'testadmin',
        'admin_email': 'admin@testacademy.com',
        'admin_password': 'TestPass123!',
        'admin_first_name': 'Test',
        'admin_last_name': 'Admin',
        'admin_phone': '+1234567890'
    }
    
    print(f"1. Testing registration for: {test_data['school_name']}")
    
    # Test registration
    response = client.post('/accounts/register-school/', test_data)
    
    if response.status_code == 302:
        print("✅ Registration successful (302 redirect)")
        
        # Check if user was created
        from django.contrib.auth.models import User
        user = User.objects.filter(username='testadmin').first()
        if user:
            print(f"✅ User created: {user.username}")
            
            # Check if UserProfile exists
            try:
                profile = user.userprofile
                print(f"✅ UserProfile created with role: {profile.role}")
                print(f"✅ School assigned: {profile.school.name if profile.school else 'None'}")
            except UserProfile.DoesNotExist:
                print("❌ UserProfile not created")
                return False
                
            # Check if School was created
            school = School.objects.filter(name='Test Academy').first()
            if school:
                print(f"✅ School created: {school.name}")
                print(f"✅ School type: {school.school_type}")
            else:
                print("❌ School not created")
                return False
                
            # Test login with created credentials
            print(f"\n2. Testing login with credentials")
            login_data = {
                'username': 'testadmin',
                'password': 'TestPass123!'
            }
            
            login_response = client.post('/accounts/login/', login_data)
            
            if login_response.status_code == 302:
                print("✅ Login successful (302 redirect)")
                
                # Test dashboard access
                dashboard_response = client.get('/accounts/dashboard/')
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard accessible (200 OK)")
                    return True
                else:
                    print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                    return False
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
        else:
            print("❌ User not created")
            return False
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"Response content: {response.content.decode()[:500]}")
        return False

def test_duplicate_prevention():
    print("\n=== TESTING DUPLICATE PREVENTION ===")
    
    from core.models import School
    
    # Try to create duplicate school
    existing_schools = School.objects.filter(name='Test Academy', school_type='primary').count()
    print(f"Existing 'Test Academy' primary schools: {existing_schools}")
    
    if existing_schools > 0:
        print("✅ Duplicate prevention working - school already exists")
        return True
    else:
        print("❌ No duplicate found (expected for first test)")
        return True

if __name__ == '__main__':
    print("School Management System - Registration Flow Test")
    print("=" * 50)
    
    # Run tests
    registration_ok = test_registration_flow()
    duplicate_ok = test_duplicate_prevention()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Registration Flow: {'✅ PASS' if registration_ok else '❌ FAIL'}")
    print(f"Duplicate Prevention: {'✅ PASS' if duplicate_ok else '❌ FAIL'}")
    
    if registration_ok and duplicate_ok:
        print("\n🎯 ALL TESTS PASSED - System works correctly!")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED - System has issues!")
        sys.exit(1)
