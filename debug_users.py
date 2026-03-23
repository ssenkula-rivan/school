"""
Direct Database Check - Emergency diagnostic
Shows actual user data without exposing passwords
"""
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
import json

def check_users(request):
    """Check what users exist in database"""
    users = User.objects.all()
    data = []
    
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': str(user.date_joined),
            'has_password': bool(user.password and user.password != ''),
        })
    
    return HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )

def reset_and_create_admin(request):
    """Emergency admin creation with known password"""
    if request.method == 'POST':
        # Delete existing admin if exists
        User.objects.filter(username='systemadmin').delete()
        
        # Create new admin with known password
        user = User.objects.create_superuser(
            username='systemadmin',
            email='admin@school.local',
            password='Admin123!'
        )
        
        return HttpResponse(f"Admin created: {user.username} / Admin123!")
    
    return HttpResponse("POST to create admin user")
