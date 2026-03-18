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
            '/accounts/register/',  # Staff registration (will redirect if needed)
            '/accounts/setup/',
            '/accounts/login/',
            '/accounts/logout/',
            '/admin/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Check if URL is exempt
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)
        
        # Multi-tenant system - no single school restrictions
        # Allow access to all pages, tenant isolation handled at model level
        
        response = self.get_response(request)
        return response
