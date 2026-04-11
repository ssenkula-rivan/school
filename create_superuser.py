"""
Create Superuser View - For emergency access
Accessible at /create-superuser/
Only works if no superusers exist
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def create_superuser_view(request):
    """Emergency superuser creation - only if no superusers exist"""
    
    # Check if any superusers already exist
    if User.objects.filter(is_superuser=True).exists():
        return render(request, 'accounts/superuser_exists.html')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        errors = []
        
        # Validation
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters')
        elif User.objects.filter(username__iexact=username).exists():
            errors.append('Username already exists')
            
        if not email:
            errors.append('Email is required')
        elif '@' not in email:
            errors.append('Invalid email format')
        elif User.objects.filter(email__iexact=email).exists():
            errors.append('Email already exists')
            
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters')
        elif password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            return render(request, 'accounts/create_superuser.html', {
                'errors': errors,
                'form_data': {
                    'username': username,
                    'email': email,
                }
            })
        
        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Create user profile
            from accounts.models import UserProfile
            profile = UserProfile.objects.create(
                user=user,
                employee_id=f'SU{user.id:04d}',
                role='system_admin',
                is_active_employee=True
            )
            
            # Auto-login the created superuser
            login_user = authenticate(request, username=username, password=password)
            if login_user:
                login(request, login_user)
            
            messages.success(request, f'Superuser "{username}" created successfully!')
            return redirect('/sys-admin-2024/')
            
        except Exception as e:
            errors.append(f'Error creating user: {str(e)}')
            return render(request, 'accounts/create_superuser.html', {
                'errors': errors,
                'form_data': {
                    'username': username,
                    'email': email,
                }
            })
    
    return render(request, 'accounts/create_superuser.html')
