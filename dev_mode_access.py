"""
Simple Dev Mode Access - No complex authentication
Direct access to system for development/debugging
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse

def dev_login(request):
    """Simple dev mode login - auto-login as admin"""
    # Create or get dev admin user
    try:
        user = User.objects.get(username='devadmin')
    except User.DoesNotExist:
        user = User.objects.create_superuser(
            username='devadmin',
            email='dev@school.local',
            password='dev123'
        )
    
    from django.contrib.auth import login
    login(request, user)
    return redirect('system_owner_dashboard')

def simple_dashboard(request):
    """Simple dev dashboard - no complex checks"""
    if not request.user.is_authenticated:
        return redirect('dev_login')
    
    return render(request, 'dev_mode/dashboard.html')
