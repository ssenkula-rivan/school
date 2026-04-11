from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from accounts.models import UserProfile
from core.models import School


def create_school_admin(request):
    """Create admin for existing school - accessible without login"""
    
    schools = School.objects.all().order_by('name')
    
    if request.method == 'POST':
        try:
            school_id = request.POST.get('school_id')
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            errors = []
            
            if not school_id:
                errors.append('Please select a school.')
            if not username:
                errors.append('Username is required.')
            if not password:
                errors.append('Password is required.')
            if password != confirm_password:
                errors.append('Passwords do not match.')
            if len(password) < 8:
                errors.append('Password must be at least 8 characters.')
            if not email:
                errors.append('Email is required.')
            if User.objects.filter(username=username).exists():
                errors.append(f'Username "{username}" already exists.')
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'accounts/create_school_admin.html', {'schools': schools})
            
            with transaction.atomic():
                school = School.objects.get(id=school_id)
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_active=True,
                )
                
                UserProfile.objects.create(
                    user=user,
                    school=school,
                    employee_id=f'ADM{user.id:04d}',
                    role='admin',
                    phone=phone,
                    is_active_employee=True,
                )
                
                messages.success(
                    request,
                    f'Admin account created successfully for {school.name}. Login with username: {username}'
                )
                return redirect('accounts:login')
                
        except Exception as e:
            messages.error(request, f'Error creating admin: {str(e)}')
            return render(request, 'accounts/create_school_admin.html', {'schools': schools})
    
    return render(request, 'accounts/create_school_admin.html', {'schools': schools})
