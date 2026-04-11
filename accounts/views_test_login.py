from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from accounts.models import UserProfile
from core.models import School


def test_login_debug(request):
    """Debug view to check login issues"""
    
    output = []
    output.append("=== LOGIN DEBUG INFO ===\n")
    
    # Check schools
    schools = School.objects.all()
    output.append(f"\nSchools in database: {schools.count()}")
    for school in schools:
        output.append(f"  - {school.name} (code: {school.code})")
    
    # Check users
    users = User.objects.all()
    output.append(f"\nUsers in database: {users.count()}")
    for user in users:
        output.append(f"\n  Username: {user.username}")
        output.append(f"  Email: {user.email}")
        output.append(f"  Active: {user.is_active}")
        output.append(f"  Staff: {user.is_staff}")
        output.append(f"  Password hash starts: {user.password[:30]}...")
        
        try:
            profile = user.userprofile
            output.append(f"  Profile: YES (role: {profile.role}, school: {profile.school.name})")
        except:
            output.append(f"  Profile: NO")
    
    # Test authentication with a specific user if provided
    if request.GET.get('test_user'):
        test_username = request.GET.get('test_user')
        test_password = request.GET.get('test_pass', '')
        
        output.append(f"\n\n=== TESTING AUTHENTICATION ===")
        output.append(f"Username: {test_username}")
        output.append(f"Password: {'*' * len(test_password)}")
        
        try:
            user = User.objects.get(username=test_username)
            output.append(f"User found: YES")
            output.append(f"User active: {user.is_active}")
            
            # Test password check
            if user.check_password(test_password):
                output.append(f"Password check: CORRECT")
            else:
                output.append(f"Password check: WRONG")
            
            # Test authenticate
            auth_user = authenticate(username=test_username, password=test_password)
            if auth_user:
                output.append(f"Authenticate result: SUCCESS")
            else:
                output.append(f"Authenticate result: FAILED")
                
        except User.DoesNotExist:
            output.append(f"User found: NO")
    
    return HttpResponse('\n'.join(output), content_type='text/plain')
