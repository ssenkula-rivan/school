"""
Middleware for school configuration check
"""

from django.shortcuts import redirect
from django.urls import reverse
from .school_config import SchoolConfiguration


class SchoolConfigurationMiddleware:
    """
    Middleware to ensure school is configured before allowing access
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs that don't require configuration
        self.exempt_urls = [
            '/accounts/register-school/',  # Public school registration
            '/accounts/create-admin/',  # Create admin for existing school
            '/accounts/make-superuser/',  # Make superuser (Render free tier)
            '/accounts/db-check/',  # Database diagnostic (Render free tier)
            '/accounts/register/',  # Staff registration
            '/accounts/setup/',
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/password-reset/',
            '/accounts/password-reset-confirm/',
            '/accounts/password-reset-complete/',
            '/accounts/password-reset/done/',
            '/accounts/debug-login/',
            '/accounts/lockout/',
            '/admin/',
            '/static/',
            '/media/',
            '/health/',
            '/sys-admin-2024/',  # System owner panel
        ]
    
    def __call__(self, request):
        # Check if URL is exempt
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)
        
        # Multi-tenant system - no single school restrictions
        # Allow access to all pages, tenant isolation handled at model level
        
        response = self.get_response(request)
        return response
